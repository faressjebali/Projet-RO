"""
═══════════════════════════════════════════════════════════════════════════════
GESTIONNAIRE DE STYLES ET THÈMES PyQt6
Optimisation de l'Approvisionnement Inter-Sites

Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
═══════════════════════════════════════════════════════════════════════════════
Ce module fournit un système de thèmes professionnel pour l'interface PyQt6
avec support des modes clair et sombre.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE DE COULEURS DÉFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PaletteTheme:
    """Définition d'une palette de couleurs pour un thème"""
    # Arrière-plans
    fond_principal: str
    fond_secondaire: str
    fond_carte: str
    fond_input: str
    fond_hover: str
    fond_selectionne: str
    
    # Texte
    texte_principal: str
    texte_secondaire: str
    texte_desactive: str
    texte_lien: str
    
    # Accents
    accent_primaire: str
    accent_secondaire: str
    accent_hover: str
    
    # États
    succes: str
    avertissement: str
    erreur: str
    info: str
    
    # Bordures
    bordure: str
    bordure_focus: str
    bordure_erreur: str
    
    # Ombres (pour QSS)
    ombre: str


# ═══════════════════════════════════════════════════════════════════════════════
# THÈME CLAIR (Mode par défaut - Académique et professionnel)
# ═══════════════════════════════════════════════════════════════════════════════

PALETTE_CLAIRE = PaletteTheme(
    # Arrière-plans
    fond_principal="#f0f4f8",
    fond_secondaire="#e8eef4",
    fond_carte="#ffffff",
    fond_input="#ffffff",
    fond_hover="#e3f2fd",
    fond_selectionne="#bbdefb",
    
    # Texte
    texte_principal="#1e293b",
    texte_secondaire="#64748b",
    texte_desactive="#94a3b8",
    texte_lien="#1565c0",
    
    # Accents - Bleu académique sobre
    accent_primaire="#1565c0",
    accent_secondaire="#1976d2",
    accent_hover="#0d47a1",
    
    # États
    succes="#2e7d32",
    avertissement="#f57c00",
    erreur="#c62828",
    info="#0277bd",
    
    # Bordures
    bordure="#cbd5e1",
    bordure_focus="#1565c0",
    bordure_erreur="#c62828",
    
    # Ombres
    ombre="rgba(0, 0, 0, 0.1)"
)


# ═══════════════════════════════════════════════════════════════════════════════
# THÈME SOMBRE
# ═══════════════════════════════════════════════════════════════════════════════

PALETTE_SOMBRE = PaletteTheme(
    # Arrière-plans
    fond_principal="#0f172a",
    fond_secondaire="#1e293b",
    fond_carte="#1e293b",
    fond_input="#334155",
    fond_hover="#334155",
    fond_selectionne="#3b82f6",
    
    # Texte
    texte_principal="#f1f5f9",
    texte_secondaire="#94a3b8",
    texte_desactive="#64748b",
    texte_lien="#60a5fa",
    
    # Accents - Bleu vif
    accent_primaire="#3b82f6",
    accent_secondaire="#60a5fa",
    accent_hover="#2563eb",
    
    # États
    succes="#4ade80",
    avertissement="#fbbf24",
    erreur="#f87171",
    info="#38bdf8",
    
    # Bordures
    bordure="#475569",
    bordure_focus="#3b82f6",
    bordure_erreur="#f87171",
    
    # Ombres
    ombre="rgba(0, 0, 0, 0.3)"
)


# ═══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEUR DE FEUILLES DE STYLE QSS
# ═══════════════════════════════════════════════════════════════════════════════

def generer_style_qss(palette: PaletteTheme) -> str:
    """
    Génère une feuille de style QSS complète pour PyQt6
    
    Args:
        palette: La palette de couleurs à utiliser
        
    Returns:
        str: Le code QSS complet
    """
    
    return f"""
/* ═══════════════════════════════════════════════════════════════════════════
   OPTIAPPRO - Feuille de Style Professionnelle PyQt6
   Optimisation de l'Approvisionnement Inter-Sites
   ═══════════════════════════════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────────────────────────────────────
   STYLES GLOBAUX
   ───────────────────────────────────────────────────────────────────────────── */

QWidget {{
    font-family: 'Segoe UI', 'SF Pro Display', 'Roboto', Arial, sans-serif;
    font-size: 13px;
    color: {palette.texte_principal};
    background-color: {palette.fond_principal};
}}

QMainWindow {{
    background-color: {palette.fond_principal};
}}

/* ─────────────────────────────────────────────────────────────────────────────
   LABELS ET TEXTES
   ───────────────────────────────────────────────────────────────────────────── */

QLabel {{
    color: {palette.texte_principal};
    padding: 2px;
    background-color: transparent;
}}

QLabel[class="titre-section"] {{
    font-size: 18px;
    font-weight: 600;
    color: {palette.accent_primaire};
    padding: 10px 0;
    border-bottom: 2px solid {palette.accent_primaire};
    margin-bottom: 10px;
}}

QLabel[class="sous-titre"] {{
    font-size: 14px;
    font-weight: 500;
    color: {palette.texte_secondaire};
    padding: 5px 0;
}}

QLabel[class="valeur-importante"] {{
    font-size: 24px;
    font-weight: bold;
    color: {palette.accent_primaire};
}}

QLabel[class="statut-succes"] {{
    color: {palette.succes};
    font-weight: 600;
}}

QLabel[class="statut-erreur"] {{
    color: {palette.erreur};
    font-weight: 600;
}}

QLabel[class="statut-avertissement"] {{
    color: {palette.avertissement};
    font-weight: 600;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   BOUTONS
   ───────────────────────────────────────────────────────────────────────────── */

QPushButton {{
    background-color: {palette.fond_carte};
    color: {palette.texte_principal};
    border: 1px solid {palette.bordure};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {palette.fond_hover};
    border-color: {palette.accent_primaire};
}}

QPushButton:pressed {{
    background-color: {palette.fond_selectionne};
}}

QPushButton:disabled {{
    background-color: {palette.fond_secondaire};
    color: {palette.texte_desactive};
    border-color: {palette.bordure};
}}

/* Bouton primaire (action principale) */
QPushButton[class="primaire"] {{
    background-color: {palette.accent_primaire};
    color: white;
    border: none;
    font-weight: 600;
}}

QPushButton[class="primaire"]:hover {{
    background-color: {palette.accent_hover};
}}

QPushButton[class="primaire"]:pressed {{
    background-color: {palette.accent_hover};
}}

/* Bouton succès */
QPushButton[class="succes"] {{
    background-color: {palette.succes};
    color: white;
    border: none;
}}

QPushButton[class="succes"]:hover {{
    background-color: #1b5e20;
}}

/* Bouton danger */
QPushButton[class="danger"] {{
    background-color: {palette.erreur};
    color: white;
    border: none;
}}

QPushButton[class="danger"]:hover {{
    background-color: #b71c1c;
}}

/* Grand bouton d'action */
QPushButton[class="action-principale"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {palette.accent_primaire}, stop:1 {palette.accent_hover});
    color: white;
    border: none;
    border-radius: 8px;
    padding: 15px 30px;
    font-size: 16px;
    font-weight: bold;
    min-height: 40px;
}}

QPushButton[class="action-principale"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {palette.accent_secondaire}, stop:1 {palette.accent_primaire});
}}

/* ─────────────────────────────────────────────────────────────────────────────
   CHAMPS DE SAISIE
   ───────────────────────────────────────────────────────────────────────────── */

QLineEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {palette.fond_input};
    color: {palette.texte_principal};
    border: 1px solid {palette.bordure};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {palette.accent_primaire};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {palette.bordure_focus};
    padding: 7px 11px;
}}

QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: {palette.fond_secondaire};
    color: {palette.texte_desactive};
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background-color: {palette.fond_secondaire};
    border: none;
    border-radius: 3px;
    width: 20px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {palette.fond_hover};
}}

/* ─────────────────────────────────────────────────────────────────────────────
   LISTES DÉROULANTES
   ───────────────────────────────────────────────────────────────────────────── */

QComboBox {{
    background-color: {palette.fond_input};
    color: {palette.texte_principal};
    border: 1px solid {palette.bordure};
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {palette.accent_primaire};
}}

QComboBox:focus {{
    border: 2px solid {palette.bordure_focus};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {palette.texte_secondaire};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {palette.fond_carte};
    border: 1px solid {palette.bordure};
    border-radius: 6px;
    selection-background-color: {palette.fond_selectionne};
}}

/* ─────────────────────────────────────────────────────────────────────────────
   TABLEAUX
   ───────────────────────────────────────────────────────────────────────────── */

QTableWidget {{
    background-color: {palette.fond_carte};
    alternate-background-color: {palette.fond_secondaire};
    border: 1px solid {palette.bordure};
    border-radius: 8px;
    gridline-color: {palette.bordure};
    selection-background-color: {palette.fond_selectionne};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {palette.bordure};
}}

QTableWidget::item:selected {{
    background-color: {palette.fond_selectionne};
    color: {palette.texte_principal};
}}

QTableWidget::item:hover {{
    background-color: {palette.fond_hover};
}}

QHeaderView::section {{
    background-color: {palette.accent_primaire};
    color: white;
    font-weight: 600;
    padding: 10px 8px;
    border: none;
    border-right: 1px solid {palette.fond_selectionne};
}}

QHeaderView::section:first {{
    border-top-left-radius: 7px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 7px;
    border-right: none;
}}

QTableCornerButton::section {{
    background-color: {palette.accent_primaire};
    border: none;
    border-top-left-radius: 7px;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   ONGLETS
   ───────────────────────────────────────────────────────────────────────────── */

QTabWidget::pane {{
    background-color: {palette.fond_carte};
    border: 1px solid {palette.bordure};
    border-radius: 8px;
    padding: 10px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: {palette.fond_secondaire};
    color: {palette.texte_secondaire};
    border: 1px solid {palette.bordure};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background-color: {palette.fond_carte};
    color: {palette.accent_primaire};
    font-weight: 600;
    border-color: {palette.bordure};
    border-bottom-color: {palette.fond_carte};
}}

QTabBar::tab:hover:!selected {{
    background-color: {palette.fond_hover};
    color: {palette.texte_principal};
}}

/* ─────────────────────────────────────────────────────────────────────────────
   GROUPES
   ───────────────────────────────────────────────────────────────────────────── */

QGroupBox {{
    background-color: {palette.fond_carte};
    border: 1px solid {palette.bordure};
    border-radius: 10px;
    margin-top: 20px;
    padding: 20px 15px 15px 15px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    top: 8px;
    color: {palette.accent_primaire};
    background-color: {palette.fond_carte};
    padding: 0 8px;
    font-size: 14px;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   BARRES DE PROGRESSION
   ───────────────────────────────────────────────────────────────────────────── */

QProgressBar {{
    background-color: {palette.fond_secondaire};
    border: none;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    color: {palette.texte_principal};
    min-height: 20px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {palette.accent_primaire}, stop:1 {palette.accent_secondaire});
    border-radius: 8px;
}}

/* Barre de progression indéterminée */
QProgressBar[class="indeterminate"] {{
    background-color: {palette.fond_secondaire};
}}

/* ─────────────────────────────────────────────────────────────────────────────
   ZONES DE TEXTE
   ───────────────────────────────────────────────────────────────────────────── */

QTextEdit, QPlainTextEdit {{
    background-color: {palette.fond_input};
    color: {palette.texte_principal};
    border: 1px solid {palette.bordure};
    border-radius: 8px;
    padding: 10px;
    selection-background-color: {palette.accent_primaire};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {palette.bordure_focus};
}}

/* Console / Log */
QTextEdit[class="console"] {{
    background-color: {palette.fond_secondaire};
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 12px;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   BARRES DE DÉFILEMENT
   ───────────────────────────────────────────────────────────────────────────── */

QScrollBar:vertical {{
    background-color: {palette.fond_secondaire};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {palette.bordure};
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {palette.accent_primaire};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {palette.fond_secondaire};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {palette.bordure};
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {palette.accent_primaire};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   MENUS
   ───────────────────────────────────────────────────────────────────────────── */

QMenuBar {{
    background-color: {palette.fond_carte};
    border-bottom: 1px solid {palette.bordure};
    padding: 4px;
}}

QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {palette.fond_hover};
}}

QMenu {{
    background-color: {palette.fond_carte};
    border: 1px solid {palette.bordure};
    border-radius: 8px;
    padding: 8px;
}}

QMenu::item {{
    padding: 8px 30px 8px 15px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {palette.fond_selectionne};
}}

QMenu::separator {{
    height: 1px;
    background-color: {palette.bordure};
    margin: 5px 10px;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   BARRE DE STATUT
   ───────────────────────────────────────────────────────────────────────────── */

QStatusBar {{
    background-color: {palette.fond_secondaire};
    border-top: 1px solid {palette.bordure};
    padding: 5px;
    font-size: 12px;
}}

QStatusBar::item {{
    border: none;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   SPLITTERS
   ───────────────────────────────────────────────────────────────────────────── */

QSplitter::handle {{
    background-color: {palette.bordure};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

QSplitter::handle:hover {{
    background-color: {palette.accent_primaire};
}}

/* ─────────────────────────────────────────────────────────────────────────────
   TOOLTIPS
   ───────────────────────────────────────────────────────────────────────────── */

QToolTip {{
    background-color: {palette.fond_carte};
    color: {palette.texte_principal};
    border: 1px solid {palette.accent_primaire};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   DIALOGUES
   ───────────────────────────────────────────────────────────────────────────── */

QDialog {{
    background-color: {palette.fond_principal};
}}

QMessageBox {{
    background-color: {palette.fond_carte};
}}

QMessageBox QLabel {{
    color: {palette.texte_principal};
    font-size: 13px;
}}

/* ─────────────────────────────────────────────────────────────────────────────
   CARTES (WIDGETS PERSONNALISÉS)
   ───────────────────────────────────────────────────────────────────────────── */

QFrame[class="carte"] {{
    background-color: {palette.fond_carte};
    border: 1px solid {palette.bordure};
    border-radius: 12px;
    padding: 15px;
}}

QFrame[class="carte-accentuee"] {{
    background-color: {palette.fond_carte};
    border: 2px solid {palette.accent_primaire};
    border-radius: 12px;
    padding: 15px;
}}

QFrame[class="carte-succes"] {{
    background-color: {palette.fond_carte};
    border-left: 4px solid {palette.succes};
    border-radius: 4px;
    padding: 15px;
}}

QFrame[class="carte-erreur"] {{
    background-color: {palette.fond_carte};
    border-left: 4px solid {palette.erreur};
    border-radius: 4px;
    padding: 15px;
}}

QFrame[class="carte-avertissement"] {{
    background-color: {palette.fond_carte};
    border-left: 4px solid {palette.avertissement};
    border-radius: 4px;
    padding: 15px;
}}

QFrame[class="separateur"] {{
    background-color: {palette.bordure};
    max-height: 1px;
    margin: 10px 0;
}}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# STYLES PRÉ-GÉNÉRÉS
# ═══════════════════════════════════════════════════════════════════════════════

STYLE_CLAIR = generer_style_qss(PALETTE_CLAIRE)
STYLE_SOMBRE = generer_style_qss(PALETTE_SOMBRE)


# ═══════════════════════════════════════════════════════════════════════════════
# GESTIONNAIRE DE STYLES
# ═══════════════════════════════════════════════════════════════════════════════

class Theme(Enum):
    """Énumération des thèmes disponibles"""
    CLAIR = "clair"
    SOMBRE = "sombre"


class StyleManager:
    """
    Gestionnaire de styles pour l'application
    Permet de changer de thème dynamiquement
    """
    
    _instance = None
    _theme_actuel: Theme = Theme.CLAIR
    _application = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialiser(cls, app) -> 'StyleManager':
        """
        Initialise le gestionnaire avec l'application Qt
        
        Args:
            app: L'instance QApplication
            
        Returns:
            StyleManager: L'instance du gestionnaire
        """
        instance = cls()
        instance._application = app
        instance.appliquer_theme(Theme.CLAIR)
        return instance
    
    @classmethod
    def appliquer_theme(cls, theme: Theme) -> None:
        """
        Applique un thème à l'application
        
        Args:
            theme: Le thème à appliquer
        """
        instance = cls()
        instance._theme_actuel = theme
        
        if instance._application is None:
            return
        
        if theme == Theme.CLAIR:
            instance._application.setStyleSheet(STYLE_CLAIR)
        else:
            instance._application.setStyleSheet(STYLE_SOMBRE)
    
    @classmethod
    def basculer_theme(cls) -> Theme:
        """
        Bascule entre les thèmes clair et sombre
        
        Returns:
            Theme: Le nouveau thème actif
        """
        instance = cls()
        nouveau_theme = Theme.SOMBRE if instance._theme_actuel == Theme.CLAIR else Theme.CLAIR
        cls.appliquer_theme(nouveau_theme)
        return nouveau_theme
    
    @classmethod
    def obtenir_theme_actuel(cls) -> Theme:
        """
        Retourne le thème actuellement actif
        
        Returns:
            Theme: Le thème actuel
        """
        return cls()._theme_actuel
    
    @classmethod
    def obtenir_palette(cls) -> PaletteTheme:
        """
        Retourne la palette de couleurs du thème actuel
        
        Returns:
            PaletteTheme: La palette de couleurs
        """
        if cls()._theme_actuel == Theme.CLAIR:
            return PALETTE_CLAIRE
        return PALETTE_SOMBRE
    
    @staticmethod
    def obtenir_style_matplotlib(theme: Optional[Theme] = None) -> dict:
        """
        Retourne les paramètres de style pour Matplotlib
        
        Args:
            theme: Le thème à utiliser (utilise le thème actuel si None)
            
        Returns:
            dict: Dictionnaire de paramètres rcParams
        """
        if theme is None:
            theme = StyleManager.obtenir_theme_actuel()
        
        if theme == Theme.CLAIR:
            palette = PALETTE_CLAIRE
        else:
            palette = PALETTE_SOMBRE
        
        return {
            'figure.facecolor': palette.fond_carte,
            'axes.facecolor': palette.fond_carte,
            'axes.edgecolor': palette.bordure,
            'axes.labelcolor': palette.texte_principal,
            'axes.titlecolor': palette.texte_principal,
            'xtick.color': palette.texte_secondaire,
            'ytick.color': palette.texte_secondaire,
            'text.color': palette.texte_principal,
            'grid.color': palette.bordure,
            'legend.facecolor': palette.fond_carte,
            'legend.edgecolor': palette.bordure,
        }
