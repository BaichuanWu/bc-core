from fastapi import APIRouter, Depends
from .worldbrain import router as sk_router

router = APIRouter(prefix="/quants", tags=["quants"])

router.include_router(sk_router)
