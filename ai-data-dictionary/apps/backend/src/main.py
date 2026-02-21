"""FastAPI application entry point."""

from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    print("Shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Data Dictionary API",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 (PROJECT_RULES)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(databases_router, prefix=settings.api_v1_prefix)
app.include_router(schemas_router, prefix=settings.api_v1_prefix)
app.include_router(tables_router, prefix=settings.api_v1_prefix)
app.include_router(lineage_router, prefix=settings.api_v1_prefix)
app.include_router(tasks_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api": settings.api_v1_prefix,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}
