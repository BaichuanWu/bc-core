from fastapi import APIRouter

from .quants import router as quants_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(quants_router)
