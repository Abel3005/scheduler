from icalendar import Calendar

def parse_ical_from_bytes(ics_bytes):
    cal = Calendar.from_ical(ics_bytes)
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            events.append({
                "summary": str(component.get("summary")),
                "start": component.get("dtstart").dt.isoformat() if component.get("dtstart") else None,
                "end": component.get("dtend").dt.isoformat() if component.get("dtend") else None,
                "location": str(component.get("location") or ""),
                "description": str(component.get("description") or "")
            })
    return events
