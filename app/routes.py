from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.services import contact

# Create main router
router = APIRouter()

# Include API routes
router.include_router(contact.router, prefix="/api/v1/contact", tags=["Contact"])

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Error handlers
@router.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found", "detail": "The requested resource was not found"}
    )

@router.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": "An internal server error occurred"}
    )

