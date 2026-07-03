import uvicorn
from fastapi import FastAPI
from loguru import logger
from settings import settings
from starlette.middleware.cors import CORSMiddleware

from src.jwt_auth.auth.endpint import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


if __name__ == "__main__":
    logger.info("")

    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
    )
