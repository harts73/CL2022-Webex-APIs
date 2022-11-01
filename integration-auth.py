import sys
import os
import requests
import urllib.parse
from flask import Flask, session, request


# Example of how to obtain a token for a User with an Integration

app = Flask(__name__)
app.secret_key = os.getenv("SESSION-KEY")  # needed for encryption of the session info


@app.route('/int', methods=['GET'])
def init():
    redirect_uri = os.getenv("REDIRECT")
    parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
    client_id = os.getenv("CLIENT-ID")
    client_secret = os.getenv("CLIENT-SECRET")
    if request.method == "GET":
        try:
            # r_code = request.query_params['code']
            r_code = request.args.get('code')
        except:
            permissionURI = f"https://webexapis.com/v1/authorize?client_id={client_id}&response_type=code&redirect_uri={parsed_redirect_uri}&scope=spark%3Akms%20spark%3Apeople_read%20spark%3Arooms_read%20spark%3Amessages_write%20spark%3Arooms_write%20spark%3Amessages_read&state=MySuP3rdu9eRsTATe"
            print("it is a GET request and no token")
            message = f"<html><body><h2>CL22 Integration Test.</h2><br>You need to authenticate with Webex Teams in order to give the Integration permissions to work on your behalf <a href={permissionURI} >Click Here to be redirected.</a></body></html>"
            return message
    if not r_code:
        permissionURI = f"https://webexapis.com/v1/authorize?client_id={client_id}&response_type=code&redirect_uri={parsed_redirect_uri}&scope=spark%3Akms%20spark%3Apeople_read%20spark%3Arooms_read%20spark%3Amessages_write%20spark%3Arooms_write%20spark%3Amessages_read&state=MySuP3rdu9eRsTATe"
        print("it is a GET request and no token")
        message = f"<html><body><h2>CL22 Integration Test.</h2><br>You need to authenticate with Webex Teams in order to give the Integration permissions to work on your behalf <a href={permissionURI} >Click Here to be redirected.</a></body></html>"
        return message

    print(f"Code is {r_code}")
    print("trying to get the token")
    # r_code = request.args.get('code')
    data = f"grant_type=authorization_code&redirect_uri={redirect_uri}&code={r_code}&client_id={client_id}&client_secret={client_secret}"
    url = "https://webexapis.com/v1/access_token"
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    myrequest = requests.post(url, headers=headers, params=data, verify=False)
    print(myrequest.text)
    try:
        json_spark = myrequest.json()
    except:
        print("Failed to read JSON response", sys.exc_info())
        message = f"<html><body><h2>CL22 Integration Test.</h2><br>Some error trying to get the token. <p>{myrequest.text}</p></body></html>"
        return message
    print(f"JSON is \n {json_spark}")
    # token = json_spark['access_token']
    # print(f"1 {token}")
    try:
        token = json_spark['access_token']
    except:
        print("Failed to get token from JSON", sys.exc_info())
        message = "<html><body><h2>CL22 Integration Test.</h2><br>Some error.</body></html>"
        return message
    print(f"Token received {token}")
    # need to get the userid
    people_url = "https://webexapis.com/v1/people/me"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {token}"
               }
    print(f"{headers}")
    try:
        who_am_i_req = requests.get(people_url, headers=headers)
    except:
        print("Failed in people me request", sys.exc_info())
        print(who_am_i_req)
    print(who_am_i_req.text)
    try:
        who_am_i = who_am_i_req.json()
        for email in who_am_i['emails']:
            emailaddress = email
            break
    except:
        print("Failed to get email from JSON", sys.exc_info())
        message = f"<html><body><h2>CL22 Integration Test.</h2><br>Some error trying to get my details.<p>{who_am_i_req}</p></body></html>"
        return message
    session['token'] = token
    session['email'] = emailaddress
    # SEND SUCCESS PAGE WITH OPTIONS.
    message = f"""<html><body><h2>CL22 Integration Test.</h2><br>Token retrieved for {emailaddress}<br>
    To view the token <a href="/token"> click here</a></p></body></html>"""
    return message


@app.route('/token', methods=['GET', 'POST'])
def show_token():
    the_token = session['token']
    the_user = session['email']
    # blanking parts of the token for the demo
    n = 10
    the_token = the_token[:-n] + "XXXXXXXXXX"
    message = f"""<html><body><h2>CL22 Integration Test.</h2><br>Token retrieved for {the_user}</p><p>Token: 
    <br> {the_token}</body></html> """
    return message


if __name__ == '__main__':
    app.run(host='localhost', port=9090, debug=True)
