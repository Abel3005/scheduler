from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.store_link import router as store_router
import os
# 디렉토리 준비
os.makedirs("/var/www/html/.well-known/acme-challenge", exist_ok=True)

app = FastAPI()
app.mount("/.well-known", StaticFiles(directory="/var/www/html/.well-known"), name="well-known")

# app.include_router(sync_router)
app.include_router(store_router)
