# combined integrations for demo.
import sys
import os
import requests
import time
import random
import urllib.parse
from flask import Flask, session, request

app = Flask(__name__)
app.secret_key = os.getenv("SESSION-KEY")  # needed for encryption of the session info


@app.route('/int', methods=['GET'])
def init():
    redirect_uri = os.getenv("REDIRECT")
    parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
    client_id = os.getenv("CLIENT-ID")
    client_secret = os.getenv("CLIENT-SECRET")
    scopes = os.getenv("SCOPES")
    state = os.getenv("STATE")
    if request.method == "GET":
        try:
            # r_code = request.query_params['code']
            r_code = request.args.get('code')
        except:
            permissionURI = f"https://webexapis.com/v1/authorize?client_id={client_id}&response_type=code&redirect_uri={parsed_redirect_uri}&scope={scopes}&state={state}"
            print("it is a GET request and no token")
            message = f"<html><body><h2>CL22 All in One Test.</h2><br>You need to authenticate with Webex Teams in order to give the Integration permissions to work on your behalf <a href={permissionURI} >Click Here to be redirected.</a></body></html>"
            return message
    if not r_code:
        permissionURI = f"https://webexapis.com/v1/authorize?client_id={client_id}&response_type=code&redirect_uri={parsed_redirect_uri}&scope={scopes}&state={state}"
        print("it is a GET request and no token")
        message = f"<html><body><h2>CL22 All in One Test.</h2><br>You need to authenticate with Webex Teams in order to give the Integration permissions to work on your behalf <a href={permissionURI} >Click Here to be redirected.</a></body></html>"
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
        message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to get the token. <p>{myrequest.text}</p></body></html>"
        return message
    print(f"JSON is \n {json_spark}")
    # token = json_spark['access_token']
    # print(f"1 {token}")
    try:
        token = json_spark['access_token']
    except:
        print("Failed to get token from JSON", sys.exc_info())
        message = "<html><body><h2>CL22 All in One Test.</h2><br>Some error.</body></html>"
        return message
    print(f"Token received {token}")
    # need to get the userid
    people_url = "https://webexapis.com/v1/people/me"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {token}"
               }
    print(f"{headers}")
    n = 30
    s = "X" * n
    blanked_token = s + token[n:-n] + s
    refresh_token = json_spark['refresh_token']
    blanked_refresh = refresh_token = s + token[n:-n] + s
    json_spark['access_token'] = blanked_token
    json_spark['refresh_token'] = blanked_refresh
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
        message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to get my details.<p>{who_am_i_req}</p></body></html>"
        return message
    session['token'] = token
    session['email'] = emailaddress
    print(f"JSON is \n {json_spark}")

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
</head><body><h2>CL22 All in One Test.</h2><br>Token retrieved for {emailaddress}<br>
    <p>To view the room list <a href="/list"> click here</a></p>
    <p>To view the admin audit <a href="/audit"> click here</a></p>
    <p>To view the space widget <a href="/space"> click here</a></p>
    <p>To Create Meeting <a href="/meeting"> click here</a></p>
    <p>To view Historical Analytics - Messaging <a href="/analytics"> click here</a></p>
    <p>To view the token <a href="/token"> click here</a></p>
    <p><code>{json_spark}</code></p>
    </body></html>"""
    return message


@app.route('/home', methods=['GET', 'POST'])
def show_home():
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
    </head><body><h2>CL22 All in One Test.</h2>
        <p>To view the room list <a href="/list"> click here</a></p>
        <p>To view the admin audit <a href="/audit"> click here</a></p>
        <p>To view the space widget <a href="/space"> click here</a></p>
        <p>To Create Meeting <a href="/meeting"> click here</a></p>
        <p>To view Historical Analytics - Messaging <a href="/analytics"> click here</a></p>
        <p>To view the token <a href="/token"> click here</a></p>
        </body></html>"""
    return message


@app.route('/list', methods=['GET', 'POST'])
def show_list():
    the_token = session['token']
    the_user = session['email']
    # let's get the list of rooms going to sort by lastactivity. Title should be fine for this example, in the real world you would want the id
    room_url = "https://webexapis.com/v1/rooms?sortBy=lastactivity"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {the_token}"
               }
    get_rooms = requests.get(room_url, headers=headers)
    if get_rooms.status_code != 200:
        print("Failed to get room list", sys.exc_info())
        message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to get the room list.</body></html>"
        return message
    room_json = get_rooms.json()
    room_list = ""
    for room in room_json["items"]:
        room_list = room_list + f"<li>{room['title']}</li>"
    message = f"""<html><body><h2>CL22 All in One Test.</h2><br>Rooms <b>{the_user}</b> is in</p>
    <p><ul>{room_list}</ul>
    <p>Home <a href="/home"> click here</a></p></body></html>"""
    return message


@app.route('/token', methods=['GET', 'POST'])
def show_token():
    the_token = session['token']
    the_user = session['email']
    # blanking parts of the token for the demo
    n = 30
    s = "X" * n
    the_token = s + the_token[n:-n] + s
    message = f"""<html><body><h2>CL22 All in One Test.</h2><br>Token retrieved for {the_user}</p><p>Token: 
    <br> {the_token}</p><p>Home <a href="/home"> click here</a></p></body></html> """
    return message


@app.route('/space', methods=['GET', 'POST'])
def show_space():
    the_token = session['token']
    the_user = session['email']
    email = os.getenv("EMAIL")
    print(email)

    message = f"""
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://code.s4d.io/widget-space/production/main.css">
    
    <!-- Latest compiled and minified JavaScript -->
    <script src="https://code.s4d.io/widget-space/production/bundle.js"></script>
    <h2>CL22 All in One Test.</h2>
    <p>Home <a href="/home"> click here</a></p>
    <div id="my-space-widget" />
    
    
    <script>
      // Grab DOM element where widget will be attached
      var widgetEl = document.getElementById('my-space-widget');
    
      // Initialize a new Space widget
      webex.widget(widgetEl).spaceWidget({{
        accessToken: '{the_token}',
        destinationType: 'email',
        destinationId: '{email}'
      }});
    </script> 
    """
    print(message)
    return message


@app.route('/audit', methods=['GET', 'POST'])
def show_audit():
    the_token = session['token']
    the_user = session['email']
    org_id = os.getenv("ORG_ID")
    start_date = "2022-01-01T00:00:00.000Z"
    end_date = "2022-12-31T23:59:59.000Z"

    # compose the URL
    url = f"https://webexapis.com/v1/adminAudit/events?orgId={org_id}&from={start_date}&to={end_date}&max=200"
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "Authorization": f"Bearer {the_token}"
               }
    more_results = True
    customer_events = []
    while more_results:
        print("###################")
        print(url)
        print("###################")
        try:
            get_events = requests.get(url, headers=headers)
        except:
            print(f"EXCEPTION: Error getting results {get_events.status_code}  {get_events.text}")
            message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to get events.</body></html>"
            return message
        print(get_events.headers)
        # lets handle rate limiting. Only going to handle it once. In reality it should probably handle for more.
        if get_events.status_code == 429:
            # We got rate limited, so we have to wait. Getting the guidance on waiting and adding 2 seconds.
            timer = get_events.headers["Retry-After"]
            timer = timer + 2
            print(f"\tWe got rate limited. Pausing for {timer} seconds")
            time.sleep(timer)
            try:
                get_events = requests.get(url, headers=headers)
            except:
                print(f"EXCEPTION: During Retry: Error getting results {get_events.status_code}  {get_events.text}")
                message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to get events after rate limiting.</body></html>"
                return message
        if get_events.status_code != 200:
            print("Failed to get events", sys.exc_info())
            message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to get events.</body></html>"
            return message
        events_json = get_events.json()
        for data in events_json['items']:
            event_cat = data["data"]["eventCategory"]
            # just using CUSTOMERS event category.
            # https://www.cisco.com/c/dam/en/us/td/docs/voice_ip_comm/cloudCollaboration/spark/reference/audit-dictionary/wbxch_b_control-hub-audit-events-reference.pdf
            if event_cat == "CUSTOMERS":  # example of how to filter by category
                event_actor = data["data"]["actorEmail"]
                event_description = data["data"]["eventDescription"]
                action_text = data["data"]["actionText"]
                customer_events.append({"actor": event_actor, "description": event_description,
                                        "action": action_text, "category": event_cat})
            else:  # in this scenario i just want everything but we could filter the rest out.
                event_actor = data["data"]["actorEmail"]
                event_description = data["data"]["eventDescription"]
                action_text = data["data"]["actionText"]
                customer_events.append({"actor": event_actor, "description": event_description,
                                        "action": action_text, "category": event_cat})

        # this is the pagination check.
        try:
            link = get_events.headers["Link"]
            start = link.find("<") + 1
            end = link.find(">", start)
            url = link[start:end]
            print(f"getting next lot of records:: {url}")
        except:
            more_results = False
    admin_data = ""
    for event in customer_events:
        admin_data = admin_data + f"<tr><td>{event['actor']}</td><td>{event['description']}</td><td>{event['action']}</td><td>{event['category']}</td></tr>"
    message = f"""<html><body><h2>CL22 All in One Test.</h2><br>Admin Audit Events between <b>{start_date}</b> and <b>{end_date}</b></p>
    <p><table><tr><th>Actor</th><th>Description</th><th>Action</th><th>Category</th></tr>
    {admin_data}
    </table></p>
        <p>Home <a href="/home"> click here</a></p></body></html> """
    return message


@app.route('/meeting', methods=['GET', 'POST'])
def show_meeting():
    the_token = session['token']
    the_user = session['email']
    list_invitees = os.getenv("INVITEES").split(",")  # this is comma separated in the env.
    print(list_invitees)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {the_token}"}
    meetings_url = "https://webexapis.com/v1/meetings"
    meeting_start = "2022-12-06T13:00:00+11:00"
    meeting_end = "2022-12-06T13:30:00+11:00"

    invitees = []
    for email in list_invitees:
        invitees.append({
            "email": email
        })
    # create the meeting JSON payload. Just simple in this case
    meeting_payload = {
        "title": f"Cisco Live Test Meeting {random.randint(0,10000)}",
        "start": meeting_start,
        "end": meeting_end,
        "invitees": invitees,
        "sendEmail": False
    }
    # Create the meeting.
    create_meeting = requests.post(meetings_url, headers=headers, json=meeting_payload)
    # check the results
    if create_meeting.status_code != 200:
        print("Failed to create meeting", sys.exc_info())
        message = f"<html><body><h2>CL22 All in One Test.</h2><br>Some error trying to create meeting.<br>{create_meeting.text}</body></html>"
        return message

    meeting_json = create_meeting.json()
    meeting_number = meeting_json['meetingNumber']
    meeting_start = meeting_json['start']
    meeting_title = meeting_json['title']
    meeting_id = meeting_json['id']
    meeting_password = meeting_json['password']
    meeting_sip = meeting_json['sipAddress']
    print(f"Meeting Number is {meeting_number}")

    message = f"""<html><body><h2>CL22 All in One Test.</h2><br><b><h3>Meeting Information:</h3>
        <table>
        <tr><td><b>Meeting ID</b></td><td>{meeting_id}</td></tr>
        <tr><td><b>Meeting Number</b></td><td>{meeting_number}</td></tr>
        <tr><td><b>Meeting Title</b></td><td>{meeting_title}</td></tr>
        <tr><td><b>Meeting Start</b></td><td>{meeting_start}</td></tr>
        <tr><td><b>Meeting Password</b></td><td>{meeting_password}</td></tr>
        <tr><td><b>Meeting SIP Address</b></td><td>{meeting_sip}</td></tr>
        </table>
        <p>Home <a href="/home"> click here</a></p></body></html> """
    return message


@app.route('/analytics', methods=['GET', 'POST'])
def show_analytics():
    the_token = session['token']
    the_user = session['email']
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {the_token}"}
    start = "2022-10-06"
    end = "2022-11-01"
    url = f"https://analytics.webexapis.com/v1/analytics/messagingMetrics/dailyTotals?from={start}&to={end}"
    get_messaging_totals = requests.get(url, headers=headers)

    if get_messaging_totals.status_code != 200:
        print(f"We had an error getting the totals.\n{get_messaging_totals.text}")
        html_tables = f"<h4>We had an error getting the totals.\n{get_messaging_totals.text}</h4>"
    else:
        totals_json = get_messaging_totals.json()
        print(totals_json)
        a = 0
        the_dates = totals_json["metrics"]["dates"]
        a = 0
        html_tables = ""
        while a < len(the_dates):
            html_tables = html_tables + f"""<h4>Date: {totals_json['metrics']['dates'][a]}</h4>
            <table>
                <tr><td>Daily Active Users</td><td>{totals_json['metrics']['dailyActiveUsers'][a]}</td></tr>
                <tr><td>Total Active Spaces</td><td>{totals_json['metrics']['totalActiveSpaces'][a]}</td></tr>
                <tr><td>Total Messages Sent</td><td>{totals_json['metrics']['totalMessagesSent'][a]}</td></tr>
            </table><br>
            """
            print(f"DATE: {totals_json['metrics']['dates'][a]}")
            print(f"\tDaily Active Users:  {totals_json['metrics']['dailyActiveUsers'][a]}")
            print(f"\tTotal Active Spaces: {totals_json['metrics']['totalActiveSpaces'][a]}")
            print(f"\tTotal Messages Sent: {totals_json['metrics']['totalMessagesSent'][a]}")
            a = a + 1
    message = f"""<html><body><h2>CL22 All in One Test.</h2><br><b><h3>Historical Analytics - Messaging:</h3>
            {html_tables}
            <p>Home <a href="/home"> click here</a></p></body></html> """
    return message


if __name__ == '__main__':
    app.run(host='localhost', port=9090, debug=True)
