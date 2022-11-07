import requests
import os
import pprint


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}

start = "2022-10-06"
end = "2022-11-01"

url = f"https://analytics.webexapis.com/v1/analytics/messagingMetrics/dailyTotals?from={start}&to={end}"

get_messaging_totals = requests.get(url, headers=headers)
if get_messaging_totals.status_code != 200:
    print(f"We had an error getting the totals.\n{get_messaging_totals.text}")
else:
    totals_json = get_messaging_totals.json()
    pprint.pprint(totals_json)
    print("\n\n")
    a = 0
    the_dates = totals_json["metrics"]["dates"]
    a = 0
    while a < len(the_dates):
        print(f"DATE: {totals_json['metrics']['dates'][a]}")
        print(f"\tDaily Active Users:  {totals_json['metrics']['dailyActiveUsers'][a]}")
        print(f"\tTotal Active Spaces: {totals_json['metrics']['totalActiveSpaces'][a]}")
        print(f"\tTotal Messages Sent: {totals_json['metrics']['totalMessagesSent'][a]}")
        a = a + 1

