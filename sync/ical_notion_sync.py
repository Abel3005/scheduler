import requests
from icalendar import Calendar
from notion_client import Client
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

def get_existing_uids():
    existing = set()
    query = notion.databases.query(database_id=DATABASE_ID)
    for result in query["results"]:
        uid = result["properties"].get("UID", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
        if uid:
            existing.add(uid)
    return existing

def fetch_ical_events(ical_url):
    res = requests.get(ical_url)
    cal = Calendar.from_ical(res.content)
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            events.append({
                "uid": str(component.get("uid")),
                "summary": str(component.get("summary")),
                "start": component.get("dtstart").dt.isoformat(),
                "end": component.get("dtend").dt.isoformat(),
                "location": str(component.get("location") or "")
            })
    return events

def push_to_notion(event):
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "UID": {"rich_text": [{"text": {"content": event["uid"]}}]},
            "Summary": {"title": [{"text": {"content": event["summary"]}}]},
            "Start": {"date": {"start": event["start"]}},
            "End": {"date": {"start": event["end"]}},
            "Location": {"rich_text": [{"text": {"content": event["location"]}}]},
        }
    )

def sync_all():
    existing_uids = get_existing_uids()
    cur.execute("SELECT link FROM public_links;")
    links = cur.fetchall()
    for (link,) in links:
        try:
            events = fetch_ical_events(link)
            for event in events:
                if event["uid"] not in existing_uids:
                    push_to_notion(event)
        except Exception as e:
            print(f"❌ Error syncing {link}: {e}")
