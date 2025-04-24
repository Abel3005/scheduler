from fastapi import APIRouter, Response, HTTPException
from util.ical_parser import parse_ical_from_bytes
from icalendar import Calendar, Event
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json, re
import requests

router = APIRouter()

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
    author = Column(String, unique=True, index=True)


Base.metadata.create_all(bind=engine)

@router.post("/store-link")
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

@router.get("/public-calendar")
async def pulic_calendar(link:str):
    db = SessionLocal()
    
    try:
        # Convert webcal:// to https:// if necessary
        if link.startswith("webcal://"):
            link = link.replace("webcal://", "https://", 1)
        existing_link = db.query(PublicLink).filter(PublicLink.link == link).first()
        if existing_link:
            author = existing_link.author
        else:
            author = "TEST"

        response = requests.get(link)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch iCal data: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing iCal data: {e}")
    cal = Calendar.from_ical(response.content)
    r_cal = Calendar()
    r_cal.add("version","2.0")
    r_cal.add("prodid","-//100yaa//iCal Export//KO")
    r_cal.add("x-apple-calendar-color","#CC73E1EF")
    r_cal.add("x-wr-calname",author)
    for component in cal.walk():
        if component.name == "VEVENT":
            match = re.search(r'\[(.*?)\]',str(component.get("summary")))
            event = Event()
            event.add("summary",match.group(1) if match else author)
            event.add("dtstart", component.get("dtstart").dt)
            event.add("dtend", component.get("dtend").dt)
            event.add("dtstamp", component.get("dtstamp").dt)
            event.add("uid", component.get("uid"))
            event.add("location", component.get("location"))
            event.add("description", component.get("description"))
            r_cal.add_component(event)

    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={"Content-Disposition":f'attachment; filename="calendar_{author}.ics"'}
    )


@router.get("/extract-calendar")
async def extract_calendar(link: str, author:str):
    try:
        # Convert webcal:// to https:// if necessary
        if link.startswith("webcal://"):
            link = link.replace("webcal://", "https://", 1)

        # Fetch the iCal data from the link
        response = requests.get(link)
        response.raise_for_status()

        # Parse the iCal data
        events = parse_ical_from_bytes(response.content,author)
        return {"status": "success", "events": events}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch iCal data: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing iCal data: {e}")