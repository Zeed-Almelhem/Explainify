from fastapi import APIRouter
from app.api.api_v1.endpoints import models, explanations, datasets

api_router = APIRouter()

api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(explanations.router, prefix="/explanations", tags=["explanations"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
