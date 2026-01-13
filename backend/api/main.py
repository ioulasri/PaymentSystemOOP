"""
FastAPI application entry point.
Integrates with existing Payment System OOP models.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import auth, users, orders, items, payments
from src.utils.logger import get_logger

import uvicorn

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Payment System API")
    yield
    logger.info("Shutting down Payment System API")


app = FastAPI(
    title="Payment System API",
    version="1.0.0",
    description="RESTful API for OOP Payment System",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001"
        # "https://yourdomain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])


@app.get("/")
async def root():
    """API health check."""
    return {
        "message": "Payment System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )