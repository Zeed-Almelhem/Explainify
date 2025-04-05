from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
from app.core.config import settings
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Explainify API server...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Explainify API server...")
