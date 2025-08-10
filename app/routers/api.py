from fastapi import APIRouter
from .routines import router as routine_router
from .ingredients import router as ingredients_router
from .products import router as products_router
from .treatments import router as treatments_router
from .config import router as config_router

# Create main API router
router = APIRouter()

router.include_router(routine_router)
router.include_router(ingredients_router)
router.include_router(products_router)
router.include_router(treatments_router)
router.include_router(config_router) 