from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import config
from app.services import contact, auth, projects, openings, blog
from mongoengine import connect
connect(config.DB_NAME, host=config.DB_URI)
# Create main router
router = APIRouter()

# Include API routes
router.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
router.include_router(contact.router, prefix="/api/v1", tags=["Contact"])
router.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
router.include_router(openings.router, prefix="/api/v1/jobs", tags=["Job Openings"])
router.include_router(blog.router, prefix="/api/v1/blogs", tags=["Blog"])
@router.get("/")
async def root():
    return {
        "message": "Seven Healer counsultancy Pvt.Ltd API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "Server is running"
    }
