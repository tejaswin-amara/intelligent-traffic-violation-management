from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organisation_id: UUID
    role: str
    status: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: Optional[EmailStr]
    display_name: str
    status: str
    created_at: datetime
    memberships: List[MembershipResponse]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
