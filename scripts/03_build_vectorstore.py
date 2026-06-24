import pandas as pd
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

print(" CRÉATION DE LA BASE VECTORIELLE FAISS \n")

# Chargement des données nettoyées
print("Chargement des données")
df = pd.read_csv("data/events_gironde_processed.csv", encoding="utf-8-sig")
print(f"Nombre d'événements chargés : {len(df)}")

# Récupération des textes complets
textes = df["texte_complet"].tolist()

# Chargement du modèle d'embedding
print("\nChargement du modèle d'embedding")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Modèle chargé !")

# Vectorisation de tous les textes
print("\nVectorisation des textes en cours")
print("(Cette étape peut prendre plusieurs minutes)")
vectors = model.encode(textes, show_progress_bar=True)
print(f"\nVectorisation terminée !")
print(f"Dimensions des vecteurs : {vectors.shape}")

# Conversion en float32 (format requis par FAISS)
vectors = np.array(vectors).astype("float32")

# Création de l'index FAISS
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectors)
print(f"\nIndex FAISS créé avec {index.ntotal} vecteurs")

# Sauvegarde de l'index FAISS
faiss.write_index(index, "vectorstore/faiss_index")
print("Index FAISS sauvegardé dans : vectorstore/faiss_index")

# Sauvegarde des métadonnées (infos des événements)
metadata = df[["uid", "titre", "description", "ville", "adresse", "lieu", "date_affichee", "date_debut", "date_fin", "url", "texte_complet"]].to_dict(orient="records")
with open("vectorstore/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
print("Métadonnées sauvegardées dans : vectorstore/metadata.json")

print("\n BASE VECTORIELLE CREEE AVEC SUCCES !")