import sys
import os
import base64
import hashlib
import requests
import urllib.parse
from flask import Flask, session, request

# Example of how to use Login with Webex to authenticate a user. Authorisation Code Flow with PKCE

app = Flask(__name__)
app.secret_key = os.getenv("SESSION-KEY")  # needed for encryption of the session info


@app.route('/int', methods=['GET'])
def init():
    redirect_uri = os.getenv("REDIRECT")
    parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
    client_id = os.getenv("CLIENT-ID")
    client_secret = os.getenv("CLIENT-SECRET")
    code_verifier = os.getenv("CODE-VERIFIER")
    print(len(code_verifier))
    print(code_verifier)
    state = os.getenv("STATE")
    hashed_verifier = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = base64.urlsafe_b64encode(hashed_verifier).decode('ascii')
    code_challenge = code_challenge.rstrip("=")
    print(code_challenge)
    if request.method == "GET":
        try:
            # r_code = request.query_params['code']
            r_code = request.args.get('code')
        except:
            permissionURI = f"https://webexapis.com/v1/authorize?client_id={client_id}&response_type=code&code_challenge_method=S256&code_challenge={code_challenge}&redirect_uri={parsed_redirect_uri}&scope=openid%20email%20profile&state={state}"
            print("it is a GET request and no token")
            print(permissionURI)
            message = f"<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>You need to authenticate with Webex Teams in order to give the Integration permissions to work on your behalf <a href={permissionURI} >Click Here to be redirected.</a></body></html>"
            return message
    if not r_code:
        permissionURI = f"https://webexapis.com/v1/authorize?client_id={client_id}&response_type=code&code_challenge_method=S256&code_challenge={code_challenge}&redirect_uri={parsed_redirect_uri}&scope=openid%20email%20profile&state={state}"
        print("it is a GET request and no token")
        print(permissionURI)
        message = f"<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>You need to authenticate with Webex Teams in order to give the Integration permissions to work on your behalf <a href={permissionURI} >Click Here to be redirected.</a></body></html>"
        return message

    print(f"Code is {r_code}")
    print("trying to get the token")
    data = f"grant_type=authorization_code&redirect_uri={redirect_uri}&code={r_code}&client_id={client_id}&client_secret={client_secret}&code_verifier={code_verifier}"
    print(data)
    url = "https://webexapis.com/v1/access_token"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    myrequest = requests.post(url, headers=headers, params=data, verify=False)
    print(myrequest.text)
    try:
        json_spark = myrequest.json()
    except:
        print("Failed to read JSON response", sys.exc_info())
        message = f"<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>Some error trying to get the token. <p>{myrequest.text}</p></body></html>"
        return message
    print(f"JSON is \n {json_spark}")
    # token = json_spark['access_token']
    # print(f"1 {token}")
    try:
        token = json_spark['access_token']
    except:
        print("Failed to get token from JSON", sys.exc_info())
        message = "<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>Some error.</body></html>"
        return message
    print(f"Token received {token}")
    # lets check the scopes from openid connect
    # need to get the userid
    user_info_url = "https://webexapis.com/v1/userinfo"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {token}"
               }
    print(f"{headers}")
    try:
        who_am_i_req = requests.get(user_info_url, headers=headers)
    except:
        print("Failed in people me request", sys.exc_info())
        print(who_am_i_req)
    print(who_am_i_req.text)
    try:
        who_am_i = who_am_i_req.json()
        if who_am_i['email_verified']:
            emailaddress = who_am_i['email']
        else:
            print("Failed to get email from JSON", sys.exc_info())
            message = f"<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>Some error trying to get my details.<p>{who_am_i_req}</p></body></html>"
            return message
    except:
        print("Failed to get email from JSON", sys.exc_info())
        message = f"<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>Some error trying to get my details.<p>{who_am_i_req}</p></body></html>"
        return message
    session['token'] = token
    session['email'] = emailaddress
    # SEND SUCCESS PAGE WITH OPTIONS.
    message = f"""<html><head>
<style>
code {{
  font-family: Consolas,"courier new";
  color: crimson;
  background-color: #f1f1f1;
  padding: 2px;
  font-size: 105%;
}}
</style>
</head><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>Token retrieved for {emailaddress}<br>
        To view the token <a href="/token"> click here</a></p><p>Information returned for the user<br><code>{who_am_i}</code></p></body></html>"""
    return message


@app.route('/token', methods=['GET', 'POST'])
def show_token():
    the_token = session['token']
    the_user = session['email']
    # blanking parts of the token for the demo
    n = 30
    s = "X" * n
    the_token = s + the_token[n:-n] + s
    message = f"""<html><body><h2>CL22 Integration Auth flow with PKCE Test.</h2><br>Token retrieved for {the_user}</p><p>Token: 
    <br> {the_token}</body></html> """
    return message


if __name__ == '__main__':
    app.run(host='localhost', port=9091, debug=True)
