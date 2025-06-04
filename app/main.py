import os
import json
from pytz import timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates

from app.functions import book_meeting_schema
from app.auth_google import router as google_auth_router, get_calendar_service

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# FastAPI app initialization
app = FastAPI()
app.include_router(google_auth_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 template setup
templates = Jinja2Templates(directory="static")

# OpenAI setup
client = OpenAI()
today_str = datetime.now().strftime("%Y-%m-%d")

# Serve landing page
@app.get("/")
def serve_landing():
    return FileResponse("static/landing.html")

# Serve chat UI with query params
@app.get("/static/index.html")
def serve_ui(request: Request):
    name = request.query_params.get("name", "User")
    email = request.query_params.get("email", "")
    pic = request.query_params.get("pic", "")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": name,
        "email": email,
        "pic": pic
    })

# Request body schema
class Message(BaseModel):
    message: str
    user_email: str

# Chat endpoint to process and book meetings
@app.post("/chat")
async def chat(request: Message):
    user_input = request.message
    user_email = request.user_email or request.cookies.get("user_email")
    print(f"[CHAT] Incoming user_email: {user_email}")

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a helpful assistant that books meetings using Google Calendar. "
                f"The current date is {today_str}. "
                "Given any user prompt, extract the meeting details such as subject, date, time, duration, attendee, and location. "
                "Then call the appropriate tool to schedule it."
            )
        },
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": book_meeting_schema}],
        tool_choice="auto"
    )

    choice = response.choices[0]

    if choice.finish_reason == "tool_calls":
        tool_call = choice.message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        tz = timezone("Asia/Dubai")
        start_datetime = tz.localize(datetime.fromisoformat(f"{args['date']}T{args['start_time']}:00"))
        end_datetime = start_datetime + timedelta(minutes=args['duration_min'])

        try:
            service = get_calendar_service(user_email)
            print(f"[AUTH] Token valid for: {user_email}")

            calendar_list = service.calendarList().list().execute()
            for calendar in calendar_list["items"]:
                print(calendar["id"])

            # Check calendar availability
            freebusy_query = {
                "timeMin": start_datetime.isoformat(),
                "timeMax": end_datetime.isoformat(),
                "timeZone": "Asia/Dubai",
                "items": [{"id": "primary"}]
            }
            print(f"The freebusy has been fitched")

            busy_slots = service.freebusy().query(body=freebusy_query).execute()
            busy_times = busy_slots["calendars"]["primary"].get("busy", [])
            print(f"The busy_slots has been busy_times has been defined")
            print("Busy slots returned:", busy_times)

            if busy_times:
                print(f"The user should be busy")
                return JSONResponse({
                    "response": (
                        f"⚠️ You're already booked between "
                        f"{start_datetime.strftime('%H:%M')} and {end_datetime.strftime('%H:%M')} on {args['date']}. "
                        "Please choose another time."
                    )
                })

        except Exception as e:
            print(f"❌ ERROR during calendar check: {str(e)}")
            raise HTTPException(status_code=403, detail="User not logged in or token missing")

        # Proceed with booking
        event = {
            "summary": args['subject'],
            "location": args.get('location', 'Google Meet'),
            "start": {"dateTime": start_datetime.isoformat(), "timeZone": "Asia/Dubai"},
            "end": {"dateTime": end_datetime.isoformat(), "timeZone": "Asia/Dubai"},
            "attendees": [{"email": args['attendee']}],
            "reminders": {"useDefault": True}
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        event_id = created_event.get("id")

        tool_response = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps({"event_id": event_id})
        }

        messages += [choice.message, tool_response]

        final = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        return JSONResponse({"response": final.choices[0].message.content})

    return JSONResponse({"response": "I'm designed to help you schedule meetings. Please ask me something relevant!"})
