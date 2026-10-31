from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from ..core.database import get_db
from ..core.security import verify_password, create_access_token
from ..core.config import settings
from ..models.auth import User, Membership
from ..schemas.auth import TokenResponse, UserResponse, LoginRequest
from datetime import timedelta
import time
from jose import jwt, JWTError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Simple in-memory rate limiting for login
# In a real distributed system this would use Redis.
_failed_login_attempts = {}

def check_rate_limit(ip: str):
    now = time.time()
    attempts = _failed_login_attempts.get(ip, [])
    # Keep attempts from the last 15 minutes
    attempts = [t for t in attempts if now - t < 900]
    _failed_login_attempts[ip] = attempts

    if len(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later."
        )

def record_failed_login(ip: str):
    now = time.time()
    attempts = _failed_login_attempts.get(ip, [])
    attempts.append(now)
    _failed_login_attempts[ip] = attempts

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Use unique ID instead of email for token subject to avoid duplication issues
    user = db.query(User).options(joinedload(User.memberships)).filter(User.id == user_id).first()
    if user is None or user.status != 'active':
        raise credentials_exception

    return user

def get_current_active_organisation(request: Request, current_user: User = Depends(get_current_user)):
    org_id = request.headers.get("X-Organisation-ID")
    if not org_id:
        # Require explicit selection
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organisation ID header (X-Organisation-ID) is required."
        )

    # Find matching membership that is active
    active_membership = None
    for membership in current_user.memberships:
        if str(membership.organisation_id) == org_id and membership.status == 'active':
            active_membership = membership
            break

    if not active_membership:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have an active membership in the specified organisation."
        )

    # Attach to request state so downstream can access
    request.state.organisation_id = active_membership.organisation_id
    request.state.membership = active_membership

    return active_membership

@router.post("/login", response_model=TokenResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    # In case of duplicate emails, .first() might be non-deterministic, but unique constraints should prevent it.
    user = db.query(User).options(joinedload(User.memberships)).filter(User.email == form_data.username).first()
    if not user or not user.password_hash or not verify_password(form_data.password, user.password_hash):
        record_failed_login(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled or suspended"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/login-json", response_model=TokenResponse)
def login_json(request: Request, login_req: LoginRequest, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    user = db.query(User).options(joinedload(User.memberships)).filter(User.email == login_req.email).first()
    if not user or not user.password_hash or not verify_password(login_req.password, user.password_hash):
        record_failed_login(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if user.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled or suspended"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
