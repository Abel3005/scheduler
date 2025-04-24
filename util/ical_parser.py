from icalendar import Calendar
import re

def parse_ical_from_bytes(ics_bytes, author):
    cal = Calendar.from_ical(ics_bytes)
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            match = re.search(r'\[(.*?)\]',str(component.get("summary")))
            events.append({
                "summary": match.group(1) if match else author,
                "start": component.get("dtstart").dt.isoformat() if component.get("dtstart") else None,
                "end": component.get("dtend").dt.isoformat() if component.get("dtend") else None,
                "location": str(component.get("location") or ""),
                "description": str(component.get("description") or "")
            })
    return events
