from fastapi import APIRouter
from app.api.routes import analysis, auth, games

router = APIRouter()

router.include_router(auth.router)
router.include_router(games.router)
router.include_router(analysis.router)

__all__ = ["router"]