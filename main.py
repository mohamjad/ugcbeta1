import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ugc_backend.api.routes import router
from ugc_backend.api.dependencies import init_db
from ugc_backend.config import get_settings
from ugc_backend.utils.logging import setup_logging

settings = get_settings()

logger = setup_logging(
    level=settings.logging_level,
    log_file=settings.logging_file,
)

app = FastAPI(
    title="ugc intelligence backend",
    description="transparent social media trend detection system",
    version="1.0.0",
)

if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)

init_db(settings.database_url)


@app.on_event("startup")
async def startup():
    logger.info("starting ugc intelligence backend", version="1.0.0")


@app.on_event("shutdown")
async def shutdown():
    logger.info("shutting down ugc intelligence backend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
