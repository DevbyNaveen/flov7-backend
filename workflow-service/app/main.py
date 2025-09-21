"""
Flov7 Workflow Service
Handles workflow execution using Temporal and CrewAI.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager

# Import API routers
from app.api.endpoints.workflow_execution import router as workflow_router

# Import initialization functions
from app.temporal.client import initialize_temporal_client, close_temporal_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Flov7 Workflow Service...")
    
    # Initialize database connection
    from shared.config.database import db_manager
    logger.info("Initializing database connection...")
    try:
        # Test database connection
        client = db_manager.get_client()
        service_client = db_manager.get_service_client()
        logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connection: {e}")
        raise
    
    # Initialize Temporal client
    await initialize_temporal_client()
    
    logger.info("Flov7 Workflow Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Flov7 Workflow Service...")
    
    # Close Temporal client
    await close_temporal_client()
    
    logger.info("Flov7 Workflow Service shutdown complete")


# Create FastAPI application with lifespan manager
app = FastAPI(
    title="Flov7 Workflow Service",
    description="Workflow execution and orchestration service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Include API routers
app.include_router(workflow_router, prefix="/api/v1")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Flov7 Workflow Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "workflow-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/workflow/")
async def workflow_root():
    """Workflow service root endpoint"""
    return {
        "message": "Flov7 Workflow Service",
        "endpoints": {
            "execute": "/api/v1/workflow/execute/",
            "status": "/api/v1/workflow/status/{execution_id}",
            "history": "/api/v1/workflow/history/{execution_id}"
        }
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = datetime.utcnow()

    response = await call_next(request)

    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms"
    )

    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
