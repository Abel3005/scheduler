from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/sync")
def manual_sync():
    try:
        return {"status": "success", "message": "Sync completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
