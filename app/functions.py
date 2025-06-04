# app/functions.py

book_meeting_schema = {
    "name": "book_meeting",
    "description": "Create a Google Calendar meeting using the user's account",
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Meeting title"
            },
            "date": {
                "type": "string",
                "description": "YYYY-MM-DD"
            },
            "start_time": {
                "type": "string",
                "description": "HH:MM in 24-hour format"
            },
            "duration_min": {
                "type": "integer",
                "description": "Length in minutes"
            },
            "attendee": {
                "type": "string",
                "description": "Primary attendee's email"
            },
            "location": {
                "type": "string",
                "description": "Meeting location (Google Meet, room, etc.)",
                "default": "Google Meet"
            }
        },
        "required": ["subject", "date", "start_time", "duration_min", "attendee"]
    }
}
