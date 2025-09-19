from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core import config
from mongoengine import connect
from app.services import auth, contact

# Connect to MongoDB
#connect(db=config.DB_NAME, host=config.DB_URI)

# Create main router
router = APIRouter()

# Include API routes
#router.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
router.include_router(contact.router, prefix="/api/v1", tags=["Contact"])

