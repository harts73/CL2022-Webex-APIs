import sys
import os
import requests
import urllib.parse
from flask import Flask, session, request

# Example of how to use Login with Webex to authenticate a device E.g. TV.

app = Flask(__name__)
app.secret_key = os.getenv("SESSION-KEY")  # needed for encryption of the session info
redirect_uri = os.getenv("REDIRECT")
parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
client_id = os.getenv("CLIENT-ID")
client_secret = os.getenv("CLIENT-SECRET")