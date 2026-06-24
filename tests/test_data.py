import unittest
import pandas as pd
from datetime import datetime, timedelta, timezone


class TestDataQuality(unittest.TestCase):
    """Classe de tests pour vérifier la qualité des données pré-processées."""

    @classmethod
    def setUpClass(cls):
        """Charge le fichier de données une seule fois avant tous les tests."""
        cls.df = pd.read_csv("data/events_gironde_processed.csv", encoding="utf-8-sig")
        print(f"\nFichier chargé : {len(cls.df)} événements")

    def test_01_fichier_non_vide(self):
        """Vérifie que le fichier contient bien des événements."""
        self.assertGreater(len(self.df), 0, "ERREUR : Le fichier est vide !")

    def test_02_colonne_departement_existe(self):
        """Vérifie que la colonne departement existe."""
        self.assertIn("departement", self.df.columns, "ERREUR : La colonne departement est absente !")

    def test_03_tous_evenements_gironde(self):
        """Vérifie que tous les événements sont bien en Gironde."""
        non_gironde = self.df[self.df["departement"] != "Gironde"]
        self.assertEqual(len(non_gironde), 0, f"ERREUR : {len(non_gironde)} événements ne sont pas en Gironde !")

    def test_04_colonne_date_fin_existe(self):
        """Vérifie que la colonne date_fin existe."""
        self.assertIn("date_fin", self.df.columns, "ERREUR : La colonne date_fin est absente !")

    def test_05_evenements_moins_un_an(self):
        """Vérifie que tous les événements ont moins d'un an."""
        today = datetime.now(timezone.utc)
        one_year_ago = today - timedelta(days=365)
        dates = pd.to_datetime(self.df["date_fin"], utc=True, errors="coerce")
        trop_anciens = dates[dates < one_year_ago]
        self.assertEqual(len(trop_anciens), 0, f"ERREUR : {len(trop_anciens)} événements ont plus d'un an !")

    def test_06_pas_de_titre_vide(self):
        """Vérifie qu'aucun événement n'a un titre vide."""
        sans_titre = self.df[self.df["titre"].isna() | (self.df["titre"] == "")]
        self.assertEqual(len(sans_titre), 0, f"ERREUR : {len(sans_titre)} événements sans titre !")

    def test_07_texte_complet_existe(self):
        """Vérifie que tous les événements ont un texte complet."""
        self.assertIn("texte_complet", self.df.columns, "ERREUR : La colonne texte_complet est absente !")
        sans_texte = self.df[self.df["texte_complet"].isna() | (self.df["texte_complet"] == "")]
        self.assertEqual(len(sans_texte), 0, f"ERREUR : {len(sans_texte)} événements sans texte complet !")

    def test_08_pas_de_doublons(self):
        """Vérifie qu'il n'y a pas de doublons."""
        doublons = self.df[self.df.duplicated(subset=["uid"])]
        self.assertEqual(len(doublons), 0, f"ERREUR : {len(doublons)} doublons trouvés !")