"""
Flov7 AI Service
Handles AI-powered workflow generation using OpenAI GPT-4 and 5-primitives system.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import logging
from datetime import datetime

# Import API routers
from app.api.endpoints.workflow_generation import router as workflow_router
from app.integration.api_gateway_client import api_gateway_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title="Flov7 AI Service",
    description="AI-powered workflow generation service using OpenAI GPT-4 and 5-primitives system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(workflow_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Flov7 AI Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ai/")
async def ai_root():
    """AI service root endpoint"""
    return {
        "message": "Flov7 AI Service",
        "endpoints": {
            "generate": "/ai/generate/",
            "primitives": "/ai/primitives/",
            "validate": "/ai/validate/"
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


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Flov7 AI Service...")
    
    # Register with API Gateway
    try:
        async with api_gateway_client as gateway:
            result = await gateway.register_ai_service()
            if result["success"]:
                logger.info("Successfully registered with API Gateway")
            else:
                logger.warning(f"Failed to register with API Gateway: {result['error']}")
    except Exception as e:
        logger.warning(f"Could not register with API Gateway: {str(e)}")
    
    logger.info("AI Service startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Flov7 AI Service...")
    # Add any cleanup logic here
    logger.info("AI Service shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
