import subprocess
import sys

print("PIPELINE — Reconstruction de la base vectorielle")

scripts = [
    ("Etape 1 : Récupération des données",    "scripts/01_fetch_data.py"),
    ("Etape 2 : Nettoyage des données",        "scripts/02_preprocess_data.py"),
    ("Etape 3 : Création de la base FAISS",    "scripts/03_build_vectorstore.py"),
]

for titre, script in scripts:
    print(f"\n {titre}")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\nERREUR : Le script {script} a échoué. Pipeline arrêté.")
        sys.exit(1)
    print(f" {titre} terminée avec succès !")

print("PIPELINE TERMINE AVEC SUCCES !")
print("La base vectorielle est prête.")
print("Lancez maintenant : python scripts/04_rag_chatbot.py")
