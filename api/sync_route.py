from fastapi import APIRouter, HTTPException
from sync.ical_notion_sync import sync_all

router = APIRouter()

@router.post("/sync")
def manual_sync():
    try:
        sync_all()
        return {"status": "success", "message": "Sync completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
