"""API route modules."""

from .auth import router as auth_router
from .ai import router as ai_router
from .databases import router as databases_router
from .schemas import router as schemas_router
from .tables import router as tables_router
from .lineage import router as lineage_router
from .tasks import router as tasks_router

__all__ = [
    "auth_router",
    "ai_router",
    "databases_router",
    "schemas_router",
    "tables_router",
    "lineage_router",
    "tasks_router",
]
