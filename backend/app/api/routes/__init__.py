from fastapi import APIRouter
from app.api.routes.game import router as game_router
from app.api.routes.cards import router as cards_router

router = APIRouter()
router.include_router(game_router)
router.include_router(cards_router)
