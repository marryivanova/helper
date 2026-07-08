import os
from os.path import dirname, join

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.bridge.routers import router_login_page

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = FastAPI(
    title="SSO - KK",
    version="0.1.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_login_page.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=str(os.getenv("HOST")),
        port=int(os.getenv("PORT")),
        reload=bool(os.getenv("DEBUG")),
        log_level="debug" if os.getenv("DEBUG") else "info",
    )
