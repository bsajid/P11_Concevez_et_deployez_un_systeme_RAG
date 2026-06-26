import pandas as pd
import re
from datetime import datetime, timedelta, timezone

print("NETTOYAGE DES DONNÉES\n")

# Chargement des données
df = pd.read_csv("data/events_gironde_clean.csv", encoding="utf-8-sig")
print(f"Nombre d'événements avant nettoyage : {len(df)}")

# Etape 1 : Supprime les doublons
df = df.drop_duplicates(subset=["uid"])
print(f"Après suppression des doublons         : {len(df)}")

# Etape 2 : Supprime les événements sans titre
df = df[df["titre"].notna() & (df["titre"] != "")]
print(f"Après suppression sans titre           : {len(df)}")

# Etape 3 : Nettoie les balises HTML et caractères mal encodés etc
def remove_html_tags(text):
    """Supprime les balises HTML et nettoie le texte :
    - Supprime les balises HTML
    - Corrige les caractères mal encodés
    - Normalise les espaces, tabulations et sauts de ligne
    - Corrige les textes multi-lignes
    """
    if pd.isna(text) or text == "":
        return ""

    # Étape 1 : Supprime les balises HTML
    clean = re.sub(r"<[^>]+>", " ", str(text))

    # Supprime les entités HTML (&amp; &nbsp; &#9; etc.)
    clean = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", clean)
    
    # Étape 2 : Corrige les caractères mal encodés (ex: Ã©, Â, â€˜)
    try:
        clean = clean.encode("latin1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    # Étape 3 : Normalise les sauts de ligne et tabulations
    clean = clean.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Étape 4 : Supprime les espaces multiples
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean

# Étape 3 : Nettoie les balises HTML et caractères spéciaux sur toutes les colonnes texte
df["titre"] = df["titre"].apply(remove_html_tags)
df["description"] = df["description"].apply(remove_html_tags)
df["description_longue"] = df["description_longue"].apply(remove_html_tags)
df["adresse"] = df["adresse"].apply(remove_html_tags)
df["lieu"] = df["lieu"].apply(remove_html_tags)
df["ville"] = df["ville"].apply(remove_html_tags)
df["date_affichee"] = df["date_affichee"].apply(remove_html_tags)
print("Nettoyage HTML terminé sur toutes les colonnes texte")

# Etape 4 : Remplace les valeurs manquantes par des chaînes vides
df = df.fillna("")

# Etape 5 : Supprime les événements de plus d'un an
today = datetime.now(timezone.utc)
one_year_ago = today - timedelta(days=365)
dates = pd.to_datetime(df["date_fin"], utc=True, errors="coerce")
df = df[dates >= one_year_ago]
df = df.reset_index(drop=True)
print(f"Après filtre date stricte (< 1 an)     : {len(df)}")

# Etape 6 : Construit le texte complet pour la vectorisation
def build_text_content(row):
    """Construit un texte complet pour chaque événement."""
    parts = []
    if row["titre"]:
        parts.append(f"Evénement : {row['titre']}")
    if row["description"]:
        parts.append(f"Description : {row['description']}")
    if row["description_longue"]:
        parts.append(f"Détails : {row['description_longue']}")
    if row["lieu"]:
        parts.append(f"Lieu : {row['lieu']}")
    if row["adresse"]:
        parts.append(f"Adresse : {row['adresse']}")
    if row["ville"]:
        parts.append(f"Ville : {row['ville']}")
    if row["date_affichee"]:
        parts.append(f"Date : {row['date_affichee']}")
    if row["categorie"]:
        parts.append(f"Catégorie : {row['categorie']}")
    if row["mots_cles"]:
        parts.append(f"Mots-clés : {row['mots_cles']}")
    return " | ".join(parts)

df["texte_complet"] = df.apply(build_text_content, axis=1)
print(f"Texte complet construit")

# Etape 7 : Supprime les événements sans contenu
df = df[df["texte_complet"].str.len() > 20]
print(f"Après suppression contenu vide         : {len(df)}")

print(f"\nNombre d'événements après nettoyage : {len(df)}")

# Aperçu
print(f"\nExemple de texte complet (premier événement) :")
print("-" * 60)
print(df["texte_complet"].iloc[0])
print("-" * 60)

# Sauvegarde
df.to_csv("data/events_gironde_processed.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
print(f"\nDonnées sauvegardées dans : data/events_gironde_processed.csv")
print("Nettoyage terminé avec succès !")