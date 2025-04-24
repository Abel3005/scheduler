from fastapi import FastAPI, UploadFile, File, HTTPException
from utils.ical_parser import parse_ical_from_bytes
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

app = FastAPI()

# Load database configuration from keys.json
with open("keys.json", "r") as f:
    config = json.load(f)

postgresql_config = next(item for item in config["storage"] if item["name"] == "postgresql")
DATABASE_URL = f"postgresql://{postgresql_config['connection']['user']}:{postgresql_config['connection']['password']}@{postgresql_config['connection']['host']}:{postgresql_config['connection']['port']}/{postgresql_config['connection']['database']}"

# Database setup
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class PublicLink(Base):
    __tablename__ = "public_links"
    id = Column(Integer, primary_key=True, index=True)
    link = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

@app.post("/upload-ical")
async def upload_ical(file: UploadFile = File(...)):
    content = await file.read()
    events = parse_ical_from_bytes(content)
    return {"events": events}

@app.post("/store-link")
async def store_link(link: str):
    db = SessionLocal()
    try:
        # Check if the link already exists
        existing_link = db.query(PublicLink).filter(PublicLink.link == link).first()
        if existing_link:
            raise HTTPException(status_code=400, detail="Link already exists")

        # Add the new link
        new_link = PublicLink(link=link)
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        return {"message": "Link stored successfully", "link": new_link.link}
    finally:
        db.close()
