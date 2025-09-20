from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.services import contact

# Create main router
router = APIRouter()

# Include API routes
router.include_router(contact.router, prefix="/api/v1/contact", tags=["Contact"])
