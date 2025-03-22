import requests
from datetime import datetime, timedelta, timezone
import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
API_KEY = os.getenv("CAL_API_KEY")


def get_event_types():
    url = f"https://api.cal.com/v1/event-types?apiKey={API_KEY}"
    response = requests.get(url).json()
    return response


def get_slots(EVENT_TYPE_ID):
    START_TIME = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    END_TIME = (datetime.now(timezone.utc) + timedelta(days=1)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
    TIMEZONE = "Asia/Kolkata"
    url = f"https://api.cal.com/v1/slots?apiKey={API_KEY}&eventTypeId={EVENT_TYPE_ID}&startTime={START_TIME}&endTime={END_TIME}&timeZone={TIMEZONE}"

    response = requests.get(url)

    return response.json()


def book_slot(event_type_ID, time):
    # utc_datetime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    # formatted_booking_time = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    # print("formatted_booking_time :", formatted_booking_time, event_type_ID)
    url = f"https://api.cal.com/v1/bookings?apiKey={API_KEY}"
    payload = {
        "eventTypeId": int(event_type_ID),  # Ensure it's an integer
        "start": time,  # Correct UTC ISO format
        "timeZone": "Asia/Kolkata",  # Required Timezone
        "language": "en",  # Required language field
        "metadata": {},  # Can be empty but required
        "responses": {  # ✅ Fix: Ensure responses contain valid email and name
            "email": "875596sh@gmail.com",
            "name": "Shubham Saini"
        },
        "invitee": {
            "email": "875596sh@gmail.com",
            "firstName": "Shubham",
            "lastName": "Saini"
        }
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers).json()
    return response
