# /api/v1/api.py

from fastapi import APIRouter
from api.v1.auth.auth_routes import auth_router
from api.v1.fund_families.fund_families_routes import router as ff_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(ff_router)

