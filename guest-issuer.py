# shows how to get the guest issuer token for Webex
from flask import Flask
import os
import jwt
import datetime
import base64
import requests
import pprint


issuer_id = os.getenv("ISSUER")
issuer_secret = base64.b64decode(os.getenv("SECRET"))  # we need to make sure we base64decode the secret obtained from the developer page
print(issuer_secret)
now = datetime.datetime.now(tz=datetime.timezone.utc)
print(int(now.timestamp()))
exp = now + datetime.timedelta(minutes=10)
exp = int(exp.timestamp())
print(exp)
guest_header2 = {"typ": "JWT", "alg": "HS256"}
guest_payload2 = {"sub": "test-Guest-1",
                  "name": "Guest Display name",
                  "iss": issuer_id,
                  "exp": str(exp)}

guest_token = jwt.encode(guest_payload2, issuer_secret, algorithm="HS256", headers=guest_header2)
print(guest_token)
print(jwt.decode(guest_token, issuer_secret, algorithms="HS256", headers=guest_header2))

# with the guest token you can use the SDK directly making sure to pick the token option correctly.
# otherwise you can get a token from
token_url = "https://webexapis.com/v1/jwt/login"
headers = {"Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": f"Bearer {guest_token}"
           }
token_req = requests.post(token_url, headers=headers)
pprint.pprint(token_req.json())
token_json = token_req.json()
ACCESS_TOKEN = token_json['token']
EMAIL = os.getenv("EMAIL")

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def init():
    html = f"""
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://code.s4d.io/widget-space/production/main.css">

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://code.s4d.io/widget-space/production/bundle.js"></script>

    <div id="my-space-widget" />

    <script>
      // Grab DOM element where widget will be attached
      var widgetEl = document.getElementById('my-space-widget');

      // Initialize a new Space widget
      webex.widget(widgetEl).spaceWidget({{
        accessToken: '{ACCESS_TOKEN}',
        destinationType: 'email',
        destinationId: '{EMAIL}'
      }});
    </script> 
    """
    return html


if __name__ == '__main__':
    app.run(host='localhost', port=9090, debug=True)
