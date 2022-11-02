import requests
import pandas as pd
import time
import sys
import os


admin_token = os.getenv("ACCESS_TOKEN")
org_id = os.getenv("ORG_ID")

# Specifying a Start and End date to query for admin audit events
start_date = "2022-01-01T00:00:00.000Z"
end_date = "2022-12-31T23:59:59.000Z"

# compose the URL
url = f"https://webexapis.com/v1/adminAudit/events?orgId={org_id}&from={start_date}&to={end_date}&max=200"
headers = {"Content-Type": "application/json",
           "Accept": "application/json",
           "Authorization": f"Bearer {admin_token}"
           }

# we are going to handle pagination, if there are more than 200 records we need to get the rest
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
        sys.exit()
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
            sys.exit()
    if get_events.status_code != 200:
        print(f"Error getting results {get_events.status_code}  {get_events.text}")
        sys.exit()
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
df = pd.DataFrame(customer_events)
#df.to_csv("./csv/customer-events.csv", index=False)  # we could do this to export to CSV.
print(df.to_markdown())
print("Processing Complete")

