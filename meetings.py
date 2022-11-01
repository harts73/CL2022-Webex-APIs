import requests
import pprint
import os


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}

meetings_url = "https://webexapis.com/v1/meetings"
meeting_start = "2022-12-06T14:00:00+11:00"
meeting_end = "2022-12-06T14:30:00+11:00"
# list of invitees
invitees = [
    {
        "email": "user1@domain",
        "coHost": True
    },
    {
        "email": "user2@domain"
    }
]

# create the meeting JSON payload. Just simple in this case
meeting_payload = {
    "title": "Cisco Live Test Meeting 3",
    "start": meeting_start,
    "end": meeting_end,
    "invitees": invitees,
    "sendEmail": False
}
# Create the meeting.
create_meeting = requests.post(meetings_url, headers=headers, json=meeting_payload)
# check the results
if create_meeting.status_code == 200:
    meeting_json = create_meeting.json()
    meeting_number = meeting_json['meetingNumber']
    pprint.pprint(meeting_json)
    print(f"\n\n\n\nMeeting Number is {meeting_number}")
else:
    # well something went wrong. Dump the returned text. It should be in JSON but using .text will always be there.
    print(create_meeting.text)
