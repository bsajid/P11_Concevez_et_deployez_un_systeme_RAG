# Système RAG — Recommandation d'événements culturels en Gironde

## Présentation

Ce projet est un Proof of Concept (POC) d'un système de recommandation d'événements culturels en Gironde, développé pour l'entreprise Puls-Events.

Il s'appuie sur un système RAG (Retrieval Augmented Generation) qui combine :
- FAISS pour la recherche vectorielle
- LangChain pour l'orchestration
- Mistral AI pour la génération de réponses
- SentenceTransformers pour la vectorisation des textes

Les données proviennent de la plateforme Open Agenda et couvrent les événements culturels de la Gironde de moins d'un an.

---

## Objectifs

- Récupérer et nettoyer les données d'événements culturels en Gironde
- Créer une base vectorielle FAISS pour la recherche sémantique
- Développer un chatbot capable de répondre aux questions sur les événements culturels
- Évaluer la qualité des réponses du système RAG

---

## Prérequis

- Python 3.11.9
- Une clé API Mistral (https://console.mistral.ai)
- Le fichier de données Open Agenda : evenements-publics-openagenda.json à placer dans le dossier data/

---

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/ton-username/P11_Concevez_et_deployez_un_systeme_RAG.git
cd P11_Concevez_et_deployez_un_systeme_RAG
```

### 2. Créer et activer l'environnement virtuel
```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer la clé API Mistral
Crée un fichier .env à la racine du projet :
```
MISTRAL_API_KEY=ta_clé_api_mistral
```

---

## Utilisation

### Reconstruire la base vectorielle
Si tu veux reconstruire toute la base vectorielle depuis zéro :
```bash
python pipeline.py
```

### Lancer le chatbot
```bash
python scripts/04_rag_chatbot.py
```
Tape ta question et appuie sur Entrée. Tape quitter pour arrêter.

### Lancer les tests unitaires
```bash
python -m pytest tests/test_data.py -v
```

---

## Description des fichiers et dossiers

```
projet/
├── data/
│   ├── evenements-publics-openagenda.json  → Source brute Open Agenda (4.6 Go)
│   ├── events_gironde_clean.csv            → Événements Gironde filtrés (moins d'un an)
│   └── events_gironde_processed.csv        → Événements nettoyés et prêts
├── scripts/
│   ├── 01_fetch_data.py                    → Lecture et filtre des données
│   ├── 02_preprocess_data.py               → Nettoyage et construction du texte
│   ├── 03_build_vectorstore.py             → Vectorisation et création FAISS
│   └── 04_rag_chatbot.py                   → Chatbot RAG (LangChain + Mistral)
├── tests/
│   └── test_data.py                        → 8 tests unitaires sur les données
├── vectorstore/
│   ├── faiss_index                         → Index vectoriel FAISS
│   └── metadata.json                       → Métadonnées des événements
├── pipeline.py                             → Pipeline de reconstruction complète
├── requirements.txt                        → Dépendances Python
├── .env                                    → Clé API Mistral (non versionné)
└── .gitignore                              → Fichiers exclus de Git
```

---

## Architecture du système RAG

```
Question utilisateur
        ↓
SentenceTransformer (all-MiniLM-L6-v2)
        ↓ vectorisation de la question
FAISS — recherche des événements les plus proches
        ↓ contexte des événements trouvés
Mistral AI (mistral-small-latest)
        ↓ génération de la réponse
Réponse en français
```

---

## Modèles utilisés

| Modèle | Rôle | Justification |
|---|---|---|
| all-MiniLM-L6-v2 | Vectorisation des textes | Gratuit, léger (90 Mo), efficace en français |
| mistral-small-latest | Génération des réponses | Rapide, économique, excellent en français |

---

## Résultats du POC

- 12435 événements culturels en Gironde indexés
- Recherche sémantique fonctionnelle sur la base FAISS
- Réponses générées en français par Mistral AI
- 8 tests unitaires passent avec succès

---

## Recommandations pour la version finale

- Mettre à jour les données automatiquement via un scheduler
- Utiliser Mistral Embed pour la vectorisation
- Ajouter un historique de conversation
- Déployer le chatbot sur une interface web
- Injecter la date du jour dans le prompt pour des réponses temporelles précises
