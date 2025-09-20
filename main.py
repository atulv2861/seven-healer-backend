from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

from app.core.config import settings
from app.routes import router

app = FastAPI(
    title="Seven Healer counsultancy Pvt.Ltd API",
    description="API for Seven Healer counsultancy Pvt.Ltd website",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.get("/")
def startup():
    return {"message": "Server is running"}

# Include all routes
app.include_router(router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

