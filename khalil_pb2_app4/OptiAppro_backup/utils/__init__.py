"""
═══════════════════════════════════════════════════════════════════════════════
MODULES UTILITAIRES - OPTIAPPRO V2.0
Optimisation de l'Approvisionnement Inter-Sites

Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
═══════════════════════════════════════════════════════════════════════════════
"""

from .logger import LoggerApp, obtenir_logger
from .validation import ValidateurDonnees
from .import_export import GestionnaireImportExport
from .interpretation import InterpreteurResultats

# Nouveaux modules v2.0
from .widgets_modernes import (
    CarteKPI,
    ProgressCirculaire,
    ProgressBarModerne,
    Badge,
    DashboardKPIs,
    IndicateurStatut,
    BoutonModerne,
    Separateur,
    CarteSection,
    StatCompacte
)

from .visualisation import (
    PaletteVisualisations,
    HeatmapWidget,
    GrapheFluxAmeliore,
    GraphiquesRepartition,
    GraphiqueOffreDemande
)

__all__ = [
    # Logger
    'LoggerApp',
    'obtenir_logger',
    
    # Validation
    'ValidateurDonnees',
    
    # Import/Export
    'GestionnaireImportExport',
    
    # Interprétation
    'InterpreteurResultats',
    
    # Widgets modernes
    'CarteKPI',
    'ProgressCirculaire',
    'ProgressBarModerne',
    'Badge',
    'DashboardKPIs',
    'IndicateurStatut',
    'BoutonModerne',
    'Separateur',
    'CarteSection',
    'StatCompacte',
    
    # Visualisation
    'PaletteVisualisations',
    'HeatmapWidget',
    'GrapheFluxAmeliore',
    'GraphiquesRepartition',
    'GraphiqueOffreDemande',
]
