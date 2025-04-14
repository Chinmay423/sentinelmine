from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from jose import JWTError
from typing import List, Optional, Dict, Any
import logging
import time
import os
from datetime import datetime, timedelta

# Custom modules
from core.config import settings
from core.security import verify_token, create_token
from core.logging import setup_logging
from api.routers import auth, users, predictions, alerts, analytics
from api.middleware.logging import RequestLoggingMiddleware
from api.middleware.security import SecurityHeadersMiddleware
from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.auth import JWTAuthMiddleware

# Setup logging
logger = setup_logging()

# Initialize FastAPI application
app = FastAPI(
    title="SentinelMine API",
    description="Predictive Analysis for National Security Operations",
    version="1.0.0",
    docs_url=None,  # Disable docs in production
    redoc_url=None, # Disable redoc in production
    openapi_url=None if settings.API_ENV == "production" else "/openapi.json"
)

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(JWTAuthMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Custom OpenAPI docs with authentication
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    if settings.API_ENV == "production":
        raise HTTPException(status_code=404, detail="Not Found")
    
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SentinelMine API Documentation",
        oauth2_redirect_url="/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Custom error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = f"{int(time.time())}-{id(exc)}"
    logger.error(f"Unhandled exception: {error_id}", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "error_id": error_id,
            "detail": str(exc) if settings.API_DEBUG else "An unexpected error occurred"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting SentinelMine API service")
    # Additional startup tasks like database connections, etc.

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down SentinelMine API service")
    # Cleanup tasks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.API_ENV != "production") 