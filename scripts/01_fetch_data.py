import requests
import pandas as pd
import re
from datetime import datetime, timedelta, timezone

# Date d'aujourd'hui et date il y a un an
today = datetime.now(timezone.utc)
one_year_ago = today - timedelta(days=365)
date_min = one_year_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

print(f"Filtre date : événements avec lastdate_end >= {one_year_ago.strftime('%Y-%m-%d')}")
print(f"Filtre lieu : Gironde")


# URL de l'API
API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"

# Fonction de nettoyage des caractères spéciaux
def clean(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", text)
    try:
        text = text.encode("latin1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Fonction pour récupérer les événements avec un filtre donné
def fetch_events(where_filter, label=""):
    records = []
    offset = 0
    limit = 100

    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "lang": "fr",
            "refine": "location_department:Gironde",
            "where": where_filter
        }

        response = requests.get(API_URL, params=params)

        if response.status_code != 200:
            break

        data = response.json()
        results = data.get("results", [])
        total = data.get("total_count", 0)

        if not results:
            break

        for event in results:
            records.append({
                "uid": event.get("uid", ""),
                "titre": clean(event.get("title_fr", "")),
                "description": clean(event.get("description_fr", "")),
                "description_longue": clean(event.get("longdescription_fr", "")),
                "date_debut": event.get("firstdate_begin", ""),
                "date_fin": event.get("lastdate_end", ""),
                "date_affichee": clean(event.get("daterange_fr", "")),
                "ville": clean(event.get("location_city", "")),
                "adresse": clean(event.get("location_address", "")),
                "lieu": clean(event.get("location_name", "")),
                "departement": event.get("location_department", ""),
                "region": event.get("location_region", ""),
                "url": event.get("canonicalurl", ""),
                "image": event.get("image", ""),
                "categorie": event.get("category", ""),
                "mots_cles": event.get("keywords_fr", ""),
            })

        offset += limit

        if offset >= min(total, 9900):
            break

    print(f"  {label} : {len(records)} événements récupérés (total API : {total})")
    return records

# Récupération en deux passes :
# Passe 1 : Bordeaux (ville principale, beaucoup d'événements)
# Passe 2 : Reste de la Gironde (toutes les villes sauf Bordeaux)
print("Passe 1 : Bordeaux")
records_bordeaux = fetch_events(
    f'lastdate_end>="{date_min}" AND location_city="Bordeaux"',
    "Bordeaux"
)

print("Passe 2 : Reste de la Gironde")
records_reste = fetch_events(
    f'lastdate_end>="{date_min}" AND location_city!="Bordeaux"',
    "Reste Gironde"
)

# Fusion et suppression des doublons
all_records = records_bordeaux + records_reste
print(f"\nTotal avant déduplication : {len(all_records)}")

df = pd.DataFrame(all_records)
df = df.drop_duplicates(subset=["uid"])
print(f"Total après déduplication : {len(df)}")

# Sauvegarde
df.to_csv("data/events_gironde_clean.csv", index=False, encoding="utf-8-sig", quoting=1)
print(f"\nDonnées sauvegardées dans : data/events_gironde_clean.csv")
print(f"Nombre de lignes : {len(df)}")