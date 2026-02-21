"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.api.routes import (
    auth_router,
    databases_router,
    schemas_router,
    tables_router,
    lineage_router,
    tasks_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routes (PROJECT_RULES: /api/v1/...)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(databases_router, prefix=settings.api_v1_prefix)
app.include_router(schemas_router, prefix=settings.api_v1_prefix)
app.include_router(tables_router, prefix=settings.api_v1_prefix)
app.include_router(lineage_router, prefix=settings.api_v1_prefix)
app.include_router(tasks_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    """Health check for load balancers and readiness probes."""
    return {"status": "ok", "version": settings.app_version}


@app.get("/")
async def root():
    """Root redirect or API info."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api": settings.api_v1_prefix,
    }
