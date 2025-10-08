from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="erp",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )
    register_cors(app)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_sentry()
    register_router(app)
    yield


def register_sentry():
    sentry_sdk.init(
        settings.SENRTY_URL,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )


def register_router(app: FastAPI):
    from app.api.v1 import router as api_router

    app.include_router(api_router, prefix=settings.API_PREFIX, tags=["api"])


def register_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
