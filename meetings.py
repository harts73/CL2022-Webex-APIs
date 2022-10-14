import requests
import pprint
import os


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}

meetings_url = "https://webexapis.com/v1/meetings"
meeting_start = "2022-10-18T11:00:00+11:00"
meeting_end = "2022-10-18T11:30:00+11:00"
invitees = [
    {
        "email": "user1@domain",
        "coHost": True
    },
    {
        "email": "user2@domain"
    }
]

meeting_payload = {
    "title": "Cisco Live Test Meeting",
    "start": meeting_start,
    "end": meeting_end,
    "invitees": invitees,
    "sendEmail": False
}

create_meeting = requests.post(meetings_url, headers=headers, json=meeting_payload)
if create_meeting.status_code == 200:
    pprint.pprint(create_meeting.json())
else:
    print(create_meeting.text)
