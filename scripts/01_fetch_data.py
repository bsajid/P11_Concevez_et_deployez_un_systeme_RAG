import json
import pandas as pd
from datetime import datetime, timedelta, timezone

# Date d'aujourd'hui et date il y a un an
today = datetime.now(timezone.utc)
one_year_ago = today - timedelta(days=365)

print(f"Filtre date : événements avec date_fin >= {one_year_ago.strftime('%Y-%m-%d')}")
print(f"Filtre lieu : Gironde")

# Chargement du fichier JSON
print("Chargement du fichier JSON")
with open("data/evenements-publics-openagenda.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Fichier chargé. Nombre total d'événements : {len(data)}")
print("Filtrage en cours")

# Filtrage des événements
events_filtered = []
total_lu = 0
total_gironde = 0

for event in data:
    total_lu += 1

    if total_lu % 100000 == 0:
        print(f"  {total_lu} événements lus, {total_gironde} en Gironde trouvés...")

    # Filtre 1 : département = Gironde
    if event.get("location_department", "") != "Gironde":
        continue

    total_gironde += 1

    # Filtre 2 : événement de moins d'un an
    lastdate_end = event.get("lastdate_end", "")
    if not lastdate_end:
        continue

    # Conversion de la date de fin
    date_fin = datetime.fromisoformat(lastdate_end)
    if date_fin.tzinfo is None:
        date_fin = date_fin.replace(tzinfo=timezone.utc)

    if date_fin >= one_year_ago:
        events_filtered.append({
            "uid": event.get("uid", ""),
            "titre": event.get("title_fr", ""),
            "description": event.get("description_fr", ""),
            "description_longue": event.get("longdescription_fr", ""),
            "date_debut": event.get("firstdate_begin", ""),
            "date_fin": lastdate_end,
            "date_affichee": event.get("daterange_fr", ""),
            "ville": event.get("location_city", ""),
            "adresse": event.get("location_address", ""),
            "lieu": event.get("location_name", ""),
            "departement": event.get("location_department", ""),
            "region": event.get("location_region", ""),
            "url": event.get("canonicalurl", ""),
            "image": event.get("image", ""),
            "categorie": event.get("category", ""),
            "mots_cles": event.get("keywords_fr", ""),
        })

print(f"\nRésultats :")
print(f"  Total événements lus       : {total_lu}")
print(f"  Événements en Gironde      : {total_gironde}")
print(f"  Événements < 1 an retenus  : {len(events_filtered)}")

# Sauvegarde
df = pd.DataFrame(events_filtered)
df.to_csv("data/events_gironde_clean.csv", index=False, encoding="utf-8-sig")
print(f"\nDonnées sauvegardées dans : data/events_gironde_clean.csv")
print(f"Nombre de lignes : {len(df)}")