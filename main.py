from fastapi import FastAPI
from api.sync_route import router as sync_router
from api.store_link import router as store_router
app = FastAPI()

# app.include_router(sync_router)
app.include_router(store_router)
