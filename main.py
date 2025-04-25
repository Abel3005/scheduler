from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.store_link import router as store_router
import os
# 디렉토리 준비

app = FastAPI()
app.mount("/.well-known", StaticFiles(directory="/app/.well-known"), name="well-known")

# app.include_router(sync_router)
app.include_router(store_router)
