from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.vehicles import router as vehicles_router
from .api.drivers import router as drivers_router
from .api.offences import router as offences_router
from .api.violations import router as violations_router
from .api.evidence import router as evidence_router
from .api.fines import router as fines_router
from .api.appeals import router as appeals_router
from .api.payments import router as payments_router
from .api.analytics import router as analytics_router

app = FastAPI(title="ITVM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(vehicles_router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(drivers_router, prefix="/api/drivers", tags=["drivers"])
app.include_router(offences_router, prefix="/api/offences", tags=["offences"])
app.include_router(violations_router, prefix="/api/violations", tags=["violations"])
app.include_router(evidence_router, prefix="/api", tags=["evidence"])
app.include_router(fines_router, prefix="/api", tags=["fines"])
app.include_router(appeals_router, prefix="/api/appeals", tags=["appeals"])
app.include_router(payments_router, prefix="/api/payments", tags=["payments"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
