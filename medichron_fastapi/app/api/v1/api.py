"""
API v1 router combining all endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    doctors,
    medical_records,
    contact,
    qr_codes
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(
    medical_records.router,
    prefix="/medical-records",
    tags=["medical-records"]
)
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(qr_codes.router, prefix="/qr", tags=["qr-codes"])
