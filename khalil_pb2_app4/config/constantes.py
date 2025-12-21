"""
═══════════════════════════════════════════════════════════════════════════════
CONSTANTES ET CONFIGURATION DU PROJET
Optimisation de l'Approvisionnement Inter-Sites - Programmation Linéaire

Projet Recherche Opérationnelle - INSAT 2025-2026
═══════════════════════════════════════════════════════════════════════════════
Ce module centralise toutes les constantes, paramètres par défaut et messages
de l'application pour faciliter la maintenance et l'internationalisation.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# VERSION ET MÉTADONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "2.1.0"
NOM_APPLICATION = "OptiAppro - Optimisation de l'Approvisionnement Inter-Sites"
NOM_COURT = "OptiAppro"
AUTEUR = "Khalil Chikhaoui"
INSTITUTION = "INSAT"
ANNEE_ACADEMIQUE = "2025-2026"
UNITE_MONETAIRE = "DT"  # Dinar Tunisien

# ═══════════════════════════════════════════════════════════════════════════════
# PARAMÈTRES PAR DÉFAUT DU MODÈLE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ParametresDefaut:
    """Paramètres par défaut du problème d'optimisation"""
    # Dimensions
    NB_SITES_MIN: int = 2
    NB_SITES_MAX: int = 50
    NB_SITES_DEFAUT: int = 5
    
    NB_MATIERES_MIN: int = 1
    NB_MATIERES_MAX: int = 20
    NB_MATIERES_DEFAUT: int = 3
    
    # Résolution Gurobi
    TIME_LIMIT: int = 300  # secondes
    MIP_GAP: float = 0.01  # 1%
    OUTPUT_FLAG: bool = False
    
    # Contraintes
    TAUX_RUPTURE_MAX: float = 0.20  # 20%
    PRIORITE_CRITIQUE: float = 2.0
    RUPTURE_MAX_CRITIQUE: float = 5.0  # tonnes
    
    # Coûts par défaut
    COUT_KILOMETRIQUE_DEFAUT: float = 0.5  # €/tonne/km
    PENALITE_DELAI_DEFAUT: float = 10.0  # €/tonne/jour
    DELAI_MAX_DEFAUT: float = 5.0  # jours
    
    # Seuils d'affichage
    SEUIL_FLUX_SIGNIFICATIF: float = 0.01
    SEUIL_FLUX_MAJEUR: float = 10.0


PARAMS = ParametresDefaut()

# ═══════════════════════════════════════════════════════════════════════════════
# ÉNUMÉRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class StatutResolution(Enum):
    """Statuts possibles de la résolution"""
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    OPTIMAL = "optimal"
    TEMPS_LIMITE = "temps_limite"
    ECHEC = "echec"
    ERREUR = "erreur"


class TypeCout(Enum):
    """Types de composantes de coût"""
    TRANSPORT_DIRECT = "transport_direct"
    KILOMETRIQUE = "kilometrique"
    STOCKAGE = "stockage"
    RUPTURE = "rupture"
    DELAI = "delai"


class NiveauPriorite(Enum):
    """Niveaux de priorité des matières"""
    NORMALE = 1.0
    HAUTE = 2.0
    CRITIQUE = 3.0

# ═══════════════════════════════════════════════════════════════════════════════
# COULEURS DE L'INTERFACE (Format: "#RRGGBB" ou (R, G, B))
# ═══════════════════════════════════════════════════════════════════════════════

class Couleurs:
    """Palette de couleurs académique et sobre"""
    
    # Couleurs primaires
    PRIMAIRE = "#1a5276"        # Bleu académique
    PRIMAIRE_CLAIR = "#2980b9"  # Bleu clair
    PRIMAIRE_FONCE = "#154360"  # Bleu foncé
    
    # Couleurs secondaires
    SECONDAIRE = "#27ae60"      # Vert succès
    ACCENT = "#e67e22"          # Orange accent
    
    # Couleurs d'état
    SUCCES = "#27ae60"          # Vert
    AVERTISSEMENT = "#f39c12"   # Orange
    ERREUR = "#e74c3c"          # Rouge
    INFO = "#3498db"            # Bleu info
    
    # Couleurs de fond
    FOND_CLAIR = "#f8f9fa"
    FOND_CARTE = "#ffffff"
    FOND_SOMBRE = "#2c3e50"
    
    # Texte
    TEXTE_PRIMAIRE = "#2c3e50"
    TEXTE_SECONDAIRE = "#7f8c8d"
    TEXTE_CLAIR = "#ffffff"
    
    # Tableaux
    HEADER_TABLE = "#ecf0f1"
    LIGNE_PAIRE = "#ffffff"
    LIGNE_IMPAIRE = "#f8f9fa"
    BORDURE = "#bdc3c7"
    
    # Graphiques matplotlib
    PALETTE_GRAPHIQUES = [
        "#3498db",  # Bleu
        "#e74c3c",  # Rouge
        "#27ae60",  # Vert
        "#f39c12",  # Orange
        "#9b59b6",  # Violet
        "#1abc9c",  # Turquoise
        "#34495e",  # Gris foncé
        "#e91e63",  # Rose
    ]
    
    # Heatmap
    HEATMAP_MIN = "#ffffff"
    HEATMAP_MAX = "#1a5276"


# ═══════════════════════════════════════════════════════════════════════════════
# ICÔNES UNICODE (Sans dépendance externe)
# ═══════════════════════════════════════════════════════════════════════════════

class Icones:
    """Icônes Unicode pour l'interface"""
    # Application
    LOGO = "📦"
    
    # Navigation
    PARAMETRES = "⚙️"
    DONNEES = "📊"
    RESOLUTION = "🚀"
    RESULTATS = "📈"
    VISUALISATION = "📉"
    SCENARIOS = "📁"
    ANALYSE = "🧠"
    
    # Actions
    CHARGER = "📂"
    SAUVEGARDER = "💾"
    EXPORTER = "📤"
    IMPORTER = "📥"
    RAFRAICHIR = "🔄"
    SUPPRIMER = "🗑️"
    AJOUTER = "➕"
    VALIDER = "✅"
    ANNULER = "❌"
    FICHIER = "📁"
    
    # États
    SUCCES = "✓"
    ERREUR = "✗"
    ATTENTION = "⚠️"
    AVERTISSEMENT = "⚠️"
    INFO = "ℹ️"
    EN_COURS = "⏳"
    TERMINE = "✔️"
    
    # Données
    SITE = "🏭"
    MATIERE = "📦"
    COUT = "💰"
    DISTANCE = "📏"
    CAPACITE = "📐"
    FLUX = "➡️"
    STOCK = "📦"
    RUPTURE = "⚠️"
    
    # Graphiques
    GRAPHIQUE = "📊"
    CAMEMBERT = "🥧"
    HEATMAP = "🌡️"
    RESEAU = "🕸️"
    
    # Interface
    THEME = "🌓"
    AIDE = "❓"
    DOCUMENTATION = "📚"


# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGES DE L'INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class Messages:
    """Messages textuels de l'application (facilitant l'internationalisation)"""
    
    # Titres d'onglets
    TAB_PARAMETRES = "Paramètres"
    TAB_DONNEES = "Données"
    TAB_RESOLUTION = "Résolution"
    TAB_RESULTATS = "Résultats"
    TAB_VISUALISATION = "Visualisation"
    TAB_SCENARIOS = "Scénarios"
    
    # Boutons
    BTN_APPLIQUER = "Appliquer"
    BTN_CHARGER_EXEMPLE = "Charger Exemple"
    BTN_IMPORTER_CSV = "Importer CSV"
    BTN_EXPORTER_RESULTATS = "Exporter Résultats"
    BTN_RESOUDRE = "Résoudre avec Gurobi"
    BTN_VALIDER = "Valider les Données"
    BTN_REINITIALISER = "Réinitialiser"
    BTN_SAUVEGARDER_SCENARIO = "Sauvegarder Scénario"
    BTN_COMPARER = "Comparer Scénarios"
    
    # Labels
    LBL_NB_SITES = "Nombre de sites de production:"
    LBL_NB_MATIERES = "Nombre de matières premières:"
    LBL_OFFRE = "Offre disponible (tonnes)"
    LBL_DEMANDE = "Demande (tonnes)"
    LBL_COUTS = "Coûts de transport (€/tonne)"
    LBL_DISTANCES = "Distances inter-sites (km)"
    LBL_CAPACITES = "Capacités de transfert (tonnes)"
    
    # Statuts
    STATUT_PRET = "Prêt"
    STATUT_CHARGEMENT = "Chargement en cours..."
    STATUT_RESOLUTION = "Résolution en cours..."
    STATUT_TERMINE = "Résolution terminée"
    STATUT_ERREUR = "Erreur"
    
    # Messages d'erreur
    ERR_DONNEES_MANQUANTES = "Données manquantes ou invalides"
    ERR_OFFRE_NEGATIVE = "Les offres doivent être non négatives"
    ERR_DEMANDE_NEGATIVE = "Les demandes doivent être non négatives"
    ERR_OFFRE_INSUFFISANTE = "Offre totale insuffisante pour la demande"
    ERR_CAPACITE_NEGATIVE = "Les capacités doivent être non négatives"
    ERR_FORMAT_CSV = "Format de fichier CSV invalide"
    ERR_GUROBI_LICENSE = "Licence Gurobi invalide ou absente"
    
    # Messages de succès
    SUC_VALIDATION = "Toutes les données sont valides"
    SUC_CHARGEMENT = "Données chargées avec succès"
    SUC_RESOLUTION = "Solution optimale trouvée"
    SUC_EXPORT = "Export réussi"
    SUC_IMPORT = "Import réussi"
    
    # Tooltips (conseils contextuels)
    TIP_NB_SITES = "Nombre de sites industriels dans le réseau logistique (2-50)"
    TIP_NB_MATIERES = "Nombre de matières premières différentes à gérer (1-20)"
    TIP_OFFRE = "Quantité de matière disponible à ce site (en tonnes)"
    TIP_DEMANDE = "Quantité de matière nécessaire à ce site (en tonnes)"
    TIP_COUT = "Coût unitaire de transport entre les deux sites (€/tonne)"
    TIP_DISTANCE = "Distance entre les deux sites (km)"
    TIP_CAPACITE = "Capacité maximale de transfert entre les deux sites (tonnes)"
    TIP_RESOUDRE = "Lance l'optimisation avec le solveur Gurobi"
    TIP_VALIDER = "Vérifie la cohérence de toutes les données"
    TIP_IMPORTER = "Importer des données depuis des fichiers CSV"
    TIP_EXPORTER = "Exporter les résultats en CSV, Excel ou autres formats"
    TIP_APPLIQUER_CONFIG = "Appliquer la configuration et créer les tables de données"
    TIP_CHARGER_EXEMPLE = "Charger un jeu de données d'exemple pour tester l'application"
    
    # Tooltips des onglets
    TIP_TAB_PARAMETRES = "Configurer les dimensions du problème"
    TIP_TAB_DONNEES = "Saisir ou importer les données (offre, demande, coûts, distances, capacités)"
    TIP_TAB_RESOLUTION = "Lancer la résolution du problème d'optimisation"
    TIP_TAB_RESULTATS = "Consulter les résultats détaillés (flux, coûts, ruptures)"
    TIP_TAB_VISUALISATION = "Visualiser les flux et la répartition des coûts"
    TIP_TAB_INSIGHTS = "Obtenir une analyse intelligente des résultats"
    
    # Titres des dialogues
    ERR_TITRE = "Erreur"
    SUC_TITRE = "Succès"
    INFO_TITRE = "Information"
    CONFIRM_TITRE = "Confirmation"
    
    # Messages de validation
    ERR_AUCUN_RESULTAT = "Aucun résultat disponible. Veuillez d'abord résoudre le problème."
    
    # Autres boutons
    BTN_APPLIQUER_CONFIG = "Appliquer la Configuration"
    BTN_CHARGER_EXEMPLE = "Charger Données Exemple"


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATS D'EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

class FormatsExport:
    """Formats de fichiers supportés pour l'export"""
    CSV = ("CSV", ".csv", "text/csv")
    EXCEL = ("Excel", ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    PDF = ("PDF", ".pdf", "application/pdf")
    PNG = ("Image PNG", ".png", "image/png")
    JSON = ("JSON", ".json", "application/json")
    
    @classmethod
    def tous_formats_donnees(cls) -> str:
        """Retourne le filtre pour les dialogues de fichiers"""
        return "Fichiers CSV (*.csv);;Fichiers Excel (*.xlsx);;Fichiers JSON (*.json)"
    
    @classmethod
    def tous_formats_images(cls) -> str:
        """Retourne le filtre pour les exports d'images"""
        return "Images PNG (*.png);;Documents PDF (*.pdf)"


# ═══════════════════════════════════════════════════════════════════════════════
# NOMS PAR DÉFAUT
# ═══════════════════════════════════════════════════════════════════════════════

# Noms des sites par défaut (inspirés de la géographie)
NOMS_SITES_DEFAUT = [
    "Site_Nord", "Site_Sud", "Site_Est", "Site_Ouest", "Site_Centre",
    "Site_A", "Site_B", "Site_C", "Site_D", "Site_E",
    "Usine_1", "Usine_2", "Usine_3", "Usine_4", "Usine_5",
    "Entrepôt_A", "Entrepôt_B", "Entrepôt_C", "Entrepôt_D", "Entrepôt_E"
]

# Noms de matières par défaut (matières industrielles courantes)
NOMS_MATIERES_DEFAUT = [
    "Acier", "Plastique", "Aluminium", "Cuivre", "Verre",
    "Bois", "Caoutchouc", "Ciment", "Textile", "Composites"
]

# Symboles des matières pour l'affichage compact
SYMBOLES_MATIERES = {
    "Acier": "Fe",
    "Plastique": "PVC",
    "Aluminium": "Al",
    "Cuivre": "Cu",
    "Verre": "SiO₂",
    "Bois": "🪵",
    "Caoutchouc": "NR",
    "Ciment": "Ca",
    "Textile": "🧵",
    "Composites": "C-F"
}


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION GUROBI
# ═══════════════════════════════════════════════════════════════════════════════

class ConfigGurobi:
    """Configuration du solveur Gurobi"""
    TIME_LIMIT = 300
    MIP_GAP = 0.01
    THREADS = 0  # 0 = utiliser tous les threads disponibles
    PRESOLVE = 2  # Agressif
    OUTPUT_FLAG = 0  # Silencieux
    LOG_FILE = "gurobi.log"
    
    # Noms des statuts Gurobi
    STATUTS = {
        1: "LOADED",
        2: "OPTIMAL",
        3: "INFEASIBLE",
        4: "INF_OR_UNBD",
        5: "UNBOUNDED",
        6: "CUTOFF",
        7: "ITERATION_LIMIT",
        8: "NODE_LIMIT",
        9: "TIME_LIMIT",
        10: "SOLUTION_LIMIT",
        11: "INTERRUPTED",
        12: "NUMERIC",
        13: "SUBOPTIMAL",
        14: "INPROGRESS",
        15: "USER_OBJ_LIMIT"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

class ConfigLogging:
    """Configuration des logs de l'application"""
    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    FICHIER = "optiappro.log"
    NIVEAU = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    MAX_BYTES = 5 * 1024 * 1024  # 5 MB
    BACKUP_COUNT = 3
