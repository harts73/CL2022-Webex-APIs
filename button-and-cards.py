import requests
import os


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SPACE_ID = os.getenv("SPACE_ID")

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}

# make sure to convert true to True. The below is copied directly from the card designer on developer.webex.com
copied_payload = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Image",
                            "style": "Person",
                            "url": "https://developer.webex.com/images/webex-teams-logo.png",
                            "size": "Medium",
                            "height": "50px"
                        }
                    ],
                    "width": "auto"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Cisco Webex Teams",
                            "weight": "Lighter",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "Buttons and Cards Release",
                            "horizontalAlignment": "Left",
                            "wrap": True,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": 35,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Release Date:",
                            "color": "Light"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Product:",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "OS:",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": 65,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Aug 6, 2019",
                            "color": "Light"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Webex Teams",
                            "color": "Light",
                            "weight": "Lighter",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Mac, Windows, Web",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        }
                    ]
                }
            ],
            "spacing": "Padding",
            "horizontalAlignment": "Center"
        },
        {
            "type": "TextBlock",
            "text": "We're making it easier for you to interact with bots and integrations in Webex Teams. When your bot sends information in a space that includes a card with buttons, you can now easily interact with it.",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": "Buttons and Cards Resources:"
        },

        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Subscribe to Release Notes",
                    "data": {
                        "subscribe": True
                    }
                }
            ],
            "horizontalAlignment": "Left",
            "spacing": "None"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}

# this just makes it easier to create the card in the web interface and copy in
card_json = [{
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": copied_payload
}]

# lets format the JSON message
message = {"roomId": SPACE_ID, "text": "You should see a card and not this",
           "attachments": card_json}

messages_url = "https://webexapis.com/v1/messages"

# post the message
send_message = requests.post(messages_url, json=message, headers=headers)
# dump the results
print(send_message.text)
