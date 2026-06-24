"""
Script du chatbot RAG - Recommandation d'événements culturels en Gironde
Utilise FAISS pour la recherche et Mistral pour la génération de réponses
Entrée : vectorstore/faiss_index + vectorstore/metadata.json
"""

import faiss
import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from langchain_mistralai import ChatMistralAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Chargement de la clé API
load_dotenv()

print("=== CHATBOT RAG — Événements culturels en Gironde ===\n")

# Chargement de l'index FAISS
print("Chargement de la base vectorielle...")
index = faiss.read_index("vectorstore/faiss_index")

# Chargement des métadonnées
with open("vectorstore/metadata.json", encoding="utf-8") as f:
    metadata = json.load(f)

# Chargement du modèle d'embedding
print("Chargement du modèle d'embedding...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connexion à Mistral via LangChain
print("Connexion à Mistral...")
llm = ChatMistralAI(
    model="mistral-small-latest",
    mistral_api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.3
)

print("\nTout est prêt ! Posez vos questions sur les événements culturels en Gironde.")
print("Tapez 'quitter' pour arrêter.\n")
print("-" * 60)


def rechercher_evenements(question, nb_resultats=5):
    """
    Recherche les événements les plus pertinents dans FAISS.
    Filtre uniquement les événements à venir ou en cours.

    Args:
        question (str): La question de l'utilisateur
        nb_resultats (int): Nombre d'événements à récupérer

    Returns:
        str: Texte avec les événements trouvés
    """
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc)

    # Vectorisation de la question
    vector = model.encode([question]).astype("float32")

    # On cherche plus de résultats pour compenser le filtre de date
    distances, indices = index.search(vector, nb_resultats * 5)

    # Construction du contexte avec uniquement les événements à venir
    contexte = ""
    nb_trouves = 0

    for idx in indices[0]:
        if nb_trouves >= nb_resultats:
            break

        event = metadata[idx]

        # Filtre sur la date de fin — on garde uniquement les événements à venir
        date_fin = event.get("date_fin", "")
        if date_fin:
            try:
                date_fin_dt = datetime.fromisoformat(date_fin)
                if date_fin_dt.tzinfo is None:
                    date_fin_dt = date_fin_dt.replace(tzinfo=timezone.utc)
                if date_fin_dt < today:
                    continue  # Événement déjà passé, on passe au suivant
            except Exception:
                continue

        nb_trouves += 1
        contexte += f"\nÉvénement {nb_trouves} :\n"
        contexte += f"  Titre : {event['titre']}\n"
        contexte += f"  Ville : {event['ville']}\n"
        contexte += f"  Date : {event['date_affichee']}\n"
        contexte += f"  Lieu : {event['lieu']}\n"
        contexte += f"  Adresse : {event['adresse']}\n"
        contexte += f"  Description : {event['description']}\n"
        if event['url']:
            contexte += f"  Lien : {event['url']}\n"

    if not contexte:
        contexte = "Aucun événement à venir trouvé pour cette recherche."

    return contexte


def repondre(question):
    """
    Génère une réponse à la question de l'utilisateur
    en combinant FAISS et Mistral.

    Args:
        question (str): La question de l'utilisateur

    Returns:
        str: La réponse générée par Mistral
    """
    # Recherche des événements pertinents
    contexte = rechercher_evenements(question)

    # Construction du prompt
    system_prompt = """Tu es un assistant spécialisé dans les événements culturels 
de la Gironde en France. Tu aides les utilisateurs à découvrir des événements 
adaptés à leurs envies. Réponds toujours en français de manière claire, 
chaleureuse et concise. Utilise uniquement les informations fournies dans 
le contexte pour répondre. Si tu ne trouves pas d'événement correspondant, 
dis-le clairement."""

    user_prompt = f"""Voici des événements culturels en Gironde qui pourraient 
correspondre à la demande :

{contexte}

Question de l'utilisateur : {question}

Réponds de manière naturelle et recommande les événements les plus pertinents."""

    # Appel à Mistral via LangChain
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    return response.content


# Boucle principale du chatbot
while True:
    question = input("\nVotre question : ").strip()

    if question.lower() == "quitter":
        print("Au revoir !")
        break

    if not question:
        print("Veuillez poser une question.")
        continue

    print("\nRecherche en cours...")
    reponse = repondre(question)
    print(f"\nAssistant : {reponse}")
    print("-" * 60)