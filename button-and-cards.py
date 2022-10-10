import requests
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SPACE_ID = os.getenv("SPACE_ID")

headers = {"Content-Type": "application/json","Authorization": f"Bearer {ACCESS_TOKEN}"}

card_json = """

"""

message = {"roomId": SPACE_ID, "text": "You should see a card and not this",
           "attachments": card_json}

messages_url = "https://webexapis.com/v1/messages"

send_message = requests.post(messages_url,json=message, headers=headers)
print(send_message.text)

