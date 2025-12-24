"""
ChatFlow - Main FastAPI Application
Professional Real-time Chat Platform
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.redis import redis_manager
from app.routers import api_router
from app.websocket.router import router as websocket_router

# Prometheus metrics
REQUEST_COUNT = Counter(
    "chatflow_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "chatflow_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting ChatFlow...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Connect to Redis
    await redis_manager.connect()
    print("✅ Redis connected")
    
    print(f"🎉 ChatFlow is running in {settings.APP_ENV} mode!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down ChatFlow...")
    await redis_manager.disconnect()
    await close_db()
    print("✅ Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="ChatFlow API",
    description="""
    🚀 **ChatFlow** - Professional Real-time Chat Platform
    
    A modern, scalable chat application built with FastAPI, featuring:
    
    - 💬 Real-time messaging with WebSocket
    - 👥 Private chats, groups, and channels
    - 📎 File sharing (images, videos, documents)
    - 😀 Message reactions and replies
    - 🔔 Push notifications
    - 🔐 Secure authentication with JWT
    - 📊 Analytics and monitoring
    
    ## Authentication
    
    Use the `/api/v1/auth/register` or `/api/v1/auth/login` endpoints to get an access token.
    Include the token in the `Authorization` header as `Bearer <token>`.
    
    ## WebSocket
    
    Connect to `/ws?token=<access_token>` for real-time updates.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
# Separate origins and regex patterns for Codespaces support
cors_origins = [origin for origin in settings.CORS_ORIGINS if "*" not in origin]
cors_origin_regex = r"https://.*\.(preview\.)?app\.github\.dev"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex if settings.APP_ENV == "codespaces" else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and track metrics."""
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    # Calculate latency
    latency = (datetime.utcnow() - start_time).total_seconds()
    
    # Track metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(latency)
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Ready check (includes dependency health)
@app.get("/ready", tags=["Health"])
async def ready_check():
    """Readiness check including dependencies."""
    checks = {
        "database": False,
        "redis": False,
    }
    
    # Check Redis
    try:
        if redis_manager.redis:
            await redis_manager.redis.ping()
            checks["redis"] = True
    except Exception:
        pass
    
    # Check if all services are ready
    is_ready = all(checks.values())
    
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if is_ready else "not ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Prometheus metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Expose Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Professional Real-time Chat Platform",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws",
    }

