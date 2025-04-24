from fastapi import FastAPI, UploadFile, File
from utils.ical_parser import parse_ical_from_bytes

app = FastAPI()

@app.post("/upload-ical")
async def upload_ical(file: UploadFile = File(...)):
    content = await file.read()
    events = parse_ical_from_bytes(content)
    return {"events": events}
