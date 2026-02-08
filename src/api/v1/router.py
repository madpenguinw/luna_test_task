from fastapi import APIRouter

from src.api.v1.buildings import router as buildings_router
from src.api.v1.organizations import router as organizations_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(buildings_router)
