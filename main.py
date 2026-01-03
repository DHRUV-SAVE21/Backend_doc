from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.models.mongodb import mongodb_service
from app.routers import doubt, problem, video, progress, dashboard
from app.schemas.responses import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting AI Education Platform Backend...")
    
    try:
        # Connect to MongoDB
        await mongodb_service.connect()
        logger.info("MongoDB connection established")
        
        # Test n8n connectivity (optional)
        logger.info(f"n8n base URL configured: {settings.N8N_BASE_URL}")
        
        logger.info("✅ AI Education Platform Backend started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Education Platform Backend...")
    await mongodb_service.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered education platform backend that orchestrates 8 n8n agents into 5 user-facing features",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(doubt.router)
app.include_router(problem.router)
app.include_router(video.router)
app.include_router(progress.router)
app.include_router(dashboard.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Education Platform Backend",
        "version": settings.APP_VERSION,
        "features": [
            "Live Doubt Resolution",
            "Guided Problem Solving",
            "Adaptive Video Assistance", 
            "Self-Improving System",
            "Progress & Revision"
        ],
        "endpoints": {
            "doubt": "/api/doubt",
            "problem_solve": "/api/problem/solve",
            "hint": "/api/problem/hint",
            "progress": "/api/problem/progress",
            "video_assist": "/api/video/assist",
            "progress_tracking": "/api/progress",
            "dashboard": "/api/dashboard"
        },
        "docs": "/docs",
        "health": "/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )


# Startup event for backward compatibility
@app.on_event("startup")
async def startup_event():
    """Legacy startup event"""
    logger.info("Application startup event triggered")


# Shutdown event for backward compatibility  
@app.on_event("shutdown")
async def shutdown_event():
    """Legacy shutdown event"""
    logger.info("Application shutdown event triggered")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
