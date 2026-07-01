import requests
from datetime import datetime, timedelta, timezone

today = datetime.now(timezone.utc)
one_year_ago = today - timedelta(days=365)
date_min = one_year_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

params = {
    "limit": 5,
    "lang": "fr",
    "refine": "location_department:Gironde",
    "where": f'lastdate_end>="{date_min}"'
}

r = requests.get("https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records", params=params)
data = r.json()

print("Status:", r.status_code)
print("Total événements Gironde < 1 an:", data.get("total_count"))
for ev in data.get("results", []):
    print(f"  - {ev.get('title_fr')} | {ev.get('location_city')} | {ev.get('lastdate_end')}")