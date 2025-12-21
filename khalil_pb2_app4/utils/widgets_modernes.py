"""
═══════════════════════════════════════════════════════════════════════════════
WIDGETS MODERNES ET COMPOSANTS UI AVANCÉS
OptiAppro v2.0 - Optimisation de l'Approvisionnement Inter-Sites

Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
═══════════════════════════════════════════════════════════════════════════════
Ce module fournit des composants UI modernes et stylisés pour une interface
professionnelle avec animations et effets visuels.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QGraphicsDropShadowEffect, QSizePolicy, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QLinearGradient, QFont, QPainterPath
import math


# ═══════════════════════════════════════════════════════════════════════════════
# CARTE KPI MODERNE AVEC ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════

class CarteKPI(QFrame):
    """
    Carte KPI moderne avec icône, valeur animée et indicateur de tendance
    
    Usage:
        carte = CarteKPI(
            titre="Coût Total",
            valeur="45,230 €",
            icone="💰",
            couleur="#4CAF50",
            tendance="+5%"
        )
    """
    
    def __init__(self, titre: str, valeur: str, icone: str = "📊", 
                 couleur: str = "#1565c0", tendance: str = None,
                 description: str = None, parent=None):
        super().__init__(parent)
        
        self.titre = titre
        self._valeur = valeur
        self.icone = icone
        self.couleur = couleur
        self.tendance = tendance
        self.description = description
        
        self._setup_ui()
        self._appliquer_style()
        self._ajouter_ombre()
    
    def _setup_ui(self):
        """Configure l'interface de la carte"""
        self.setFixedSize(220, 140)
        self.setObjectName("carteKPI")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Header avec icône et titre
        header = QHBoxLayout()
        
        # Icône dans un cercle coloré
        self.label_icone = QLabel(self.icone)
        self.label_icone.setFixedSize(40, 40)
        self.label_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_icone.setStyleSheet(f"""
            background-color: {self.couleur}20;
            border-radius: 20px;
            font-size: 20px;
        """)
        header.addWidget(self.label_icone)
        
        # Titre
        self.label_titre = QLabel(self.titre)
        self.label_titre.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #64748b;
        """)
        header.addWidget(self.label_titre)
        header.addStretch()
        
        # Tendance (si fournie)
        if self.tendance:
            is_positive = self.tendance.startswith('+')
            tendance_color = "#10b981" if is_positive else "#ef4444"
            tendance_bg = "#10b98120" if is_positive else "#ef444420"
            self.label_tendance = QLabel(self.tendance)
            self.label_tendance.setStyleSheet(f"""
                background-color: {tendance_bg};
                color: {tendance_color};
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
            """)
            header.addWidget(self.label_tendance)
        
        layout.addLayout(header)
        
        # Valeur principale (grande)
        self.label_valeur = QLabel(self._valeur)
        self.label_valeur.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.couleur};
            padding: 5px 0;
        """)
        layout.addWidget(self.label_valeur)
        
        # Description (optionnelle)
        if self.description:
            self.label_desc = QLabel(self.description)
            self.label_desc.setStyleSheet("""
                font-size: 11px;
                color: #94a3b8;
            """)
            layout.addWidget(self.label_desc)
        
        layout.addStretch()
    
    def _appliquer_style(self):
        """Applique le style glassmorphism à la carte"""
        self.setStyleSheet(f"""
            QFrame#carteKPI {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(255, 255, 255, 0.85));
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 16px;
            }}
            QFrame#carteKPI:hover {{
                border: 1px solid {self.couleur}50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 1),
                    stop:1 rgba(255, 255, 255, 0.95));
            }}
        """)
    
    def _ajouter_ombre(self):
        """Ajoute une ombre portée douce"""
        ombre = QGraphicsDropShadowEffect(self)
        ombre.setBlurRadius(20)
        ombre.setXOffset(0)
        ombre.setYOffset(4)
        ombre.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(ombre)
    
    def set_valeur(self, nouvelle_valeur: str):
        """Met à jour la valeur avec animation"""
        self._valeur = nouvelle_valeur
        self.label_valeur.setText(nouvelle_valeur)
    
    def set_tendance(self, nouvelle_tendance: str):
        """Met à jour la tendance"""
        if hasattr(self, 'label_tendance'):
            self.tendance = nouvelle_tendance
            is_positive = nouvelle_tendance.startswith('+')
            tendance_color = "#10b981" if is_positive else "#ef4444"
            tendance_bg = "#10b98120" if is_positive else "#ef444420"
            self.label_tendance.setText(nouvelle_tendance)
            self.label_tendance.setStyleSheet(f"""
                background-color: {tendance_bg};
                color: {tendance_color};
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
            """)


# ═══════════════════════════════════════════════════════════════════════════════
# BARRE DE PROGRESSION CIRCULAIRE
# ═══════════════════════════════════════════════════════════════════════════════

class ProgressCirculaire(QWidget):
    """
    Barre de progression circulaire avec animation
    
    Usage:
        progress = ProgressCirculaire(100)
        progress.set_valeur(75)
    """
    
    def __init__(self, maximum: int = 100, parent=None):
        super().__init__(parent)
        self._valeur = 0
        self._maximum = maximum
        self._couleur = QColor("#1565c0")
        self._couleur_fond = QColor("#e2e8f0")
        self._epaisseur = 8
        self._taille = 120
        
        self.setFixedSize(self._taille, self._taille)
        
        # Animation
        self._animation = QPropertyAnimation(self, b"valeur_animee")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(800)
    
    def get_valeur_animee(self):
        return self._valeur
    
    def set_valeur_animee(self, val):
        self._valeur = val
        self.update()
    
    valeur_animee = pyqtProperty(int, get_valeur_animee, set_valeur_animee)
    
    def set_valeur(self, valeur: int, anime: bool = True):
        """Définit la valeur avec animation optionnelle"""
        if anime:
            self._animation.setStartValue(self._valeur)
            self._animation.setEndValue(valeur)
            self._animation.start()
        else:
            self._valeur = valeur
            self.update()
    
    def set_couleur(self, couleur: str):
        """Change la couleur principale"""
        self._couleur = QColor(couleur)
        self.update()
    
    def paintEvent(self, event):
        """Dessine la barre de progression circulaire"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        rect = self.rect()
        center = rect.center()
        rayon = (min(rect.width(), rect.height()) - self._epaisseur) // 2
        
        # Fond du cercle
        pen_fond = QPen(self._couleur_fond, self._epaisseur, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fond)
        painter.drawEllipse(center, rayon, rayon)
        
        # Arc de progression
        if self._valeur > 0:
            angle = int(360 * 16 * self._valeur / self._maximum)
            pen_progress = QPen(self._couleur, self._epaisseur, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_progress)
            rect_arc = rect.adjusted(self._epaisseur//2, self._epaisseur//2, 
                                      -self._epaisseur//2, -self._epaisseur//2)
            painter.drawArc(rect_arc, 90 * 16, -angle)
        
        # Texte au centre
        pourcentage = int(100 * self._valeur / self._maximum) if self._maximum > 0 else 0
        painter.setPen(QPen(self._couleur))
        font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{pourcentage}%")


# ═══════════════════════════════════════════════════════════════════════════════
# BARRE DE PROGRESSION MODERNE HORIZONTALE
# ═══════════════════════════════════════════════════════════════════════════════

class ProgressBarModerne(QProgressBar):
    """
    Barre de progression moderne avec gradient et animation
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setMinimum(0)
        self.setMaximum(100)
        self._appliquer_style()
    
    def _appliquer_style(self):
        """Style moderne avec gradient"""
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #e2e8f0;
                height: 20px;
                text-align: center;
                font-weight: 600;
                color: #1e293b;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6,
                    stop:0.5 #8b5cf6,
                    stop:1 #ec4899);
            }
        """)
    
    def set_couleur(self, couleur_debut: str, couleur_fin: str):
        """Personnalise les couleurs du gradient"""
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 10px;
                background-color: #e2e8f0;
                height: 20px;
                text-align: center;
                font-weight: 600;
                color: #1e293b;
            }}
            QProgressBar::chunk {{
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {couleur_debut},
                    stop:1 {couleur_fin});
            }}
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# BADGE / CHIP MODERNE
# ═══════════════════════════════════════════════════════════════════════════════

class Badge(QLabel):
    """
    Badge/chip coloré pour afficher des statuts
    
    Usage:
        badge = Badge("Optimal", "succes")
        badge = Badge("En attente", "warning")
    """
    
    VARIANTES = {
        "succes": {"bg": "#dcfce7", "text": "#166534", "border": "#86efac"},
        "erreur": {"bg": "#fee2e2", "text": "#991b1b", "border": "#fca5a5"},
        "warning": {"bg": "#fef3c7", "text": "#92400e", "border": "#fcd34d"},
        "info": {"bg": "#dbeafe", "text": "#1e40af", "border": "#93c5fd"},
        "neutre": {"bg": "#f1f5f9", "text": "#475569", "border": "#cbd5e1"},
        "primaire": {"bg": "#ede9fe", "text": "#5b21b6", "border": "#c4b5fd"},
    }
    
    def __init__(self, texte: str, variante: str = "neutre", parent=None):
        super().__init__(texte, parent)
        self._appliquer_style(variante)
    
    def _appliquer_style(self, variante: str):
        """Applique le style selon la variante"""
        style = self.VARIANTES.get(variante, self.VARIANTES["neutre"])
        self.setStyleSheet(f"""
            background-color: {style['bg']};
            color: {style['text']};
            border: 1px solid {style['border']};
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 600;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def set_variante(self, variante: str):
        """Change la variante du badge"""
        self._appliquer_style(variante)


# ═══════════════════════════════════════════════════════════════════════════════
# PANNEAU DE DASHBOARD KPIs
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardKPIs(QWidget):
    """
    Panneau de dashboard avec plusieurs cartes KPI
    
    Usage:
        dashboard = DashboardKPIs()
        dashboard.mettre_a_jour({
            "cout_total": 45230,
            "satisfaction": 95.5,
            "flux_total": 1250,
            "ruptures": 50
        })
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure le dashboard"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Carte: Coût Total
        self.carte_cout = CarteKPI(
            titre="Coût Total",
            valeur="-- €",
            icone="💰",
            couleur="#059669",
            description="Coût optimal calculé"
        )
        layout.addWidget(self.carte_cout)
        
        # Carte: Satisfaction
        self.carte_satisfaction = CarteKPI(
            titre="Satisfaction",
            valeur="--%",
            icone="✅",
            couleur="#3b82f6",
            description="Demande satisfaite"
        )
        layout.addWidget(self.carte_satisfaction)
        
        # Carte: Flux Total
        self.carte_flux = CarteKPI(
            titre="Flux Total",
            valeur="-- t",
            icone="🚚",
            couleur="#8b5cf6",
            description="Matière transportée"
        )
        layout.addWidget(self.carte_flux)
        
        # Carte: Ruptures
        self.carte_ruptures = CarteKPI(
            titre="Ruptures",
            valeur="-- t",
            icone="⚠️",
            couleur="#f59e0b",
            description="Demande non satisfaite"
        )
        layout.addWidget(self.carte_ruptures)
        
        layout.addStretch()
    
    def mettre_a_jour(self, donnees: dict):
        """
        Met à jour les KPIs
        
        Args:
            donnees: dict avec clés cout_total, satisfaction, flux_total, ruptures
        """
        if "cout_total" in donnees:
            cout = donnees["cout_total"]
            self.carte_cout.set_valeur(f"{cout:,.0f} €".replace(",", " "))
        
        if "satisfaction" in donnees:
            sat = donnees["satisfaction"]
            self.carte_satisfaction.set_valeur(f"{sat:.1f}%")
            # Couleur selon le niveau
            if sat >= 95:
                self.carte_satisfaction.couleur = "#059669"
            elif sat >= 80:
                self.carte_satisfaction.couleur = "#f59e0b"
            else:
                self.carte_satisfaction.couleur = "#ef4444"
        
        if "flux_total" in donnees:
            flux = donnees["flux_total"]
            self.carte_flux.set_valeur(f"{flux:,.0f} t".replace(",", " "))
        
        if "ruptures" in donnees:
            rupt = donnees["ruptures"]
            self.carte_ruptures.set_valeur(f"{rupt:,.0f} t".replace(",", " "))
            # Couleur selon le niveau
            if rupt == 0:
                self.carte_ruptures.couleur = "#059669"
            elif rupt < 100:
                self.carte_ruptures.couleur = "#f59e0b"
            else:
                self.carte_ruptures.couleur = "#ef4444"


# ═══════════════════════════════════════════════════════════════════════════════
# INDICATEUR DE STATUT ANIMÉ
# ═══════════════════════════════════════════════════════════════════════════════

class IndicateurStatut(QWidget):
    """
    Indicateur de statut avec point animé (pulsation)
    
    Usage:
        indicateur = IndicateurStatut("En cours", "actif")
    """
    
    ETATS = {
        "actif": "#10b981",
        "inactif": "#94a3b8",
        "erreur": "#ef4444",
        "warning": "#f59e0b",
        "succes": "#10b981"
    }
    
    def __init__(self, texte: str = "", etat: str = "inactif", parent=None):
        super().__init__(parent)
        self._texte = texte
        self._etat = etat
        self._opacite = 1.0
        self._croissant = False
        
        self._setup_ui()
        
        # Animation de pulsation
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._pulser)
        if etat == "actif":
            self._timer.start(50)
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Point coloré
        self._point = QLabel("●")
        self._point.setStyleSheet(f"color: {self.ETATS.get(self._etat, '#94a3b8')}; font-size: 10px;")
        layout.addWidget(self._point)
        
        # Texte
        self._label = QLabel(self._texte)
        self._label.setStyleSheet("font-size: 13px; color: #64748b;")
        layout.addWidget(self._label)
    
    def _pulser(self):
        """Animation de pulsation"""
        if self._croissant:
            self._opacite += 0.05
            if self._opacite >= 1.0:
                self._croissant = False
        else:
            self._opacite -= 0.05
            if self._opacite <= 0.3:
                self._croissant = True
        
        couleur = self.ETATS.get(self._etat, '#94a3b8')
        self._point.setStyleSheet(f"color: {couleur}; font-size: 10px; opacity: {self._opacite};")
    
    def set_etat(self, etat: str, texte: str = None):
        """Change l'état de l'indicateur"""
        self._etat = etat
        if texte:
            self._texte = texte
            self._label.setText(texte)
        
        couleur = self.ETATS.get(etat, '#94a3b8')
        self._point.setStyleSheet(f"color: {couleur}; font-size: 10px;")
        
        if etat == "actif":
            self._timer.start(50)
        else:
            self._timer.stop()
            self._opacite = 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# BOUTON MODERNE AVEC ICÔNE
# ═══════════════════════════════════════════════════════════════════════════════

class BoutonModerne(QPushButton):
    """
    Bouton moderne avec icône et effets hover
    
    Usage:
        btn = BoutonModerne("Résoudre", "🚀", variante="primaire")
    """
    
    VARIANTES = {
        "primaire": {
            "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #2563eb)",
            "bg_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60a5fa, stop:1 #3b82f6)",
            "text": "#ffffff",
            "border": "none"
        },
        "secondaire": {
            "bg": "#ffffff",
            "bg_hover": "#f1f5f9",
            "text": "#1e293b",
            "border": "1px solid #cbd5e1"
        },
        "succes": {
            "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669)",
            "bg_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34d399, stop:1 #10b981)",
            "text": "#ffffff",
            "border": "none"
        },
        "danger": {
            "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626)",
            "bg_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f87171, stop:1 #ef4444)",
            "text": "#ffffff",
            "border": "none"
        },
        "ghost": {
            "bg": "transparent",
            "bg_hover": "#f1f5f9",
            "text": "#3b82f6",
            "border": "none"
        }
    }
    
    def __init__(self, texte: str, icone: str = None, variante: str = "primaire", parent=None):
        label = f"{icone} {texte}" if icone else texte
        super().__init__(label, parent)
        self._variante = variante
        self._appliquer_style()
        
        # Ombre légère
        ombre = QGraphicsDropShadowEffect(self)
        ombre.setBlurRadius(10)
        ombre.setXOffset(0)
        ombre.setYOffset(2)
        ombre.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(ombre)
    
    def _appliquer_style(self):
        """Applique le style selon la variante"""
        style = self.VARIANTES.get(self._variante, self.VARIANTES["primaire"])
        self.setStyleSheet(f"""
            QPushButton {{
                background: {style['bg']};
                color: {style['text']};
                border: {style['border']};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: {style['bg_hover']};
            }}
            QPushButton:pressed {{
                padding-top: 14px;
                padding-bottom: 10px;
            }}
            QPushButton:disabled {{
                background: #e2e8f0;
                color: #94a3b8;
            }}
        """)
    
    def set_variante(self, variante: str):
        """Change la variante du bouton"""
        self._variante = variante
        self._appliquer_style()


# ═══════════════════════════════════════════════════════════════════════════════
# SÉPARATEUR STYLISÉ
# ═══════════════════════════════════════════════════════════════════════════════

class Separateur(QFrame):
    """Séparateur horizontal ou vertical stylisé"""
    
    def __init__(self, orientation: str = "horizontal", parent=None):
        super().__init__(parent)
        
        if orientation == "horizontal":
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFixedHeight(1)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setFixedWidth(1)
        
        self.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.2 #cbd5e1,
                stop:0.8 #cbd5e1,
                stop:1 transparent);
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# CARTE DE SECTION
# ═══════════════════════════════════════════════════════════════════════════════

class CarteSection(QFrame):
    """
    Carte/conteneur stylisé pour regrouper du contenu
    
    Usage:
        carte = CarteSection("Paramètres", "⚙️")
        carte.layout().addWidget(mon_widget)
    """
    
    def __init__(self, titre: str = None, icone: str = None, parent=None):
        super().__init__(parent)
        self._setup_ui(titre, icone)
        self._appliquer_style()
    
    def _setup_ui(self, titre, icone):
        """Configure l'interface"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(16)
        
        if titre:
            header = QHBoxLayout()
            
            label_titre = QLabel(f"{icone} {titre}" if icone else titre)
            label_titre.setStyleSheet("""
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
            """)
            header.addWidget(label_titre)
            header.addStretch()
            
            self._layout.addLayout(header)
            
            # Ligne de séparation
            self._layout.addWidget(Separateur())
        
        # Widget contenu (pour ajouter des éléments)
        self._contenu = QWidget()
        self._contenu_layout = QVBoxLayout(self._contenu)
        self._contenu_layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._contenu)
    
    def _appliquer_style(self):
        """Style moderne avec ombre"""
        self.setStyleSheet("""
            CarteSection {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        ombre = QGraphicsDropShadowEffect(self)
        ombre.setBlurRadius(20)
        ombre.setXOffset(0)
        ombre.setYOffset(4)
        ombre.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(ombre)
    
    def contenu_layout(self):
        """Retourne le layout pour ajouter du contenu"""
        return self._contenu_layout


# ═══════════════════════════════════════════════════════════════════════════════
# WIDGET STATISTIQUE COMPACT
# ═══════════════════════════════════════════════════════════════════════════════

class StatCompacte(QWidget):
    """
    Widget statistique compact (valeur + label)
    
    Usage:
        stat = StatCompacte("1,250", "tonnes", "🚚")
    """
    
    def __init__(self, valeur: str, label: str, icone: str = None, 
                 couleur: str = "#1e293b", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Valeur
        texte_valeur = f"{icone} {valeur}" if icone else valeur
        self._label_valeur = QLabel(texte_valeur)
        self._label_valeur.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {couleur};
        """)
        self._label_valeur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label_valeur)
        
        # Label
        self._label_desc = QLabel(label)
        self._label_desc.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        self._label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label_desc)
    
    def set_valeur(self, valeur: str, icone: str = None):
        """Met à jour la valeur"""
        texte = f"{icone} {valeur}" if icone else valeur
        self._label_valeur.setText(texte)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'CarteKPI',
    'ProgressCirculaire',
    'ProgressBarModerne',
    'Badge',
    'DashboardKPIs',
    'IndicateurStatut',
    'BoutonModerne',
    'Separateur',
    'CarteSection',
    'StatCompacte'
]
