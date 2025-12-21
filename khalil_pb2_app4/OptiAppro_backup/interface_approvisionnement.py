"""
═══════════════════════════════════════════════════════════════════════════════
INTERFACE HOMME-MACHINE (IHM) - OptiAppro
Optimisation de l'Approvisionnement Inter-Sites

INSAT - Année universitaire 2025-2026
Réalisé par: Khalil Chikhaoui
Domaine: Recherche Opérationnelle - Programmation Linéaire
═══════════════════════════════════════════════════════════════════════════════
Version 2.1.0 - Interface Professionnelle Modernisée avec PyQt6
"""

import sys
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QSpinBox, QDoubleSpinBox, QGroupBox, QTextEdit, QProgressBar,
    QMessageBox, QSplitter, QHeaderView, QComboBox, QFileDialog,
    QFrame, QMenuBar, QMenu, QStatusBar, QToolBar, QTextBrowser,
    QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QAction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

# Imports des modules de l'application
from modele_approvisionnement import ModeleDonneesApprovisionnement, ModeleApprovisionnementPL
from config.styles import StyleManager
from config.constantes import (
    Messages, Icones, Couleurs, ParametresDefaut,
    VERSION, AUTEUR, INSTITUTION, ANNEE_ACADEMIQUE, UNITE_MONETAIRE
)
from utils.logger import obtenir_logger, LoggerContextuel
from utils.validation import ValidateurDonnees, NiveauGravite
from utils.import_export import GestionnaireImportExport
from utils.interpretation import InterpreteurResultats

# Logger global pour l'interface
logger = obtenir_logger(__name__)


class ThreadResolution(QThread):
    """
    Thread pour exécuter la résolution de manière non-bloquante
    """
    progression = pyqtSignal(str)
    termine = pyqtSignal(bool, str)
    
    def __init__(self, modele):
        super().__init__()
        self.modele = modele
    
    def run(self):
        """Exécute la résolution dans un thread séparé"""
        try:
            self.progression.emit("Construction du modèle...")
            self.modele.construire_modele()
            
            self.progression.emit("Résolution en cours avec Gurobi...")
            succes = self.modele.resoudre(time_limit=300, verbose=False)
            
            if succes:
                self.progression.emit("Solution optimale trouvée !")
                self.termine.emit(True, "Résolution réussie")
            else:
                self.termine.emit(False, "Aucune solution trouvée")
        except Exception as e:
            self.termine.emit(False, f"Erreur: {str(e)}")


class GraphiqueFlux(FigureCanvas):
    """
    Widget Matplotlib pour visualiser les flux d'approvisionnement
    """
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 8))
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = None
    
    def tracer_flux(self, donnees, resultats):
        """
        Trace un graphe des flux entre sites
        """
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        n_sites = donnees.n_sites
        flux_totaux = resultats.get('flux_totaux', {})
        
        # Positions des sites en cercle
        angles = np.linspace(0, 2*np.pi, n_sites, endpoint=False)
        positions = {i: (np.cos(a), np.sin(a)) for i, a in enumerate(angles)}
        
        # Tracer les sites
        for i in range(n_sites):
            x, y = positions[i]
            circle = plt.Circle((x, y), 0.15, color='steelblue', zorder=10)
            self.ax.add_patch(circle)
            self.ax.text(x, y, donnees.noms_sites[i], ha='center', va='center',
                        fontsize=9, fontweight='bold', color='white', zorder=11)
        
        # Tracer les flux
        if flux_totaux:
            flux_max = max(flux_totaux.values())
            for (i, j), volume in flux_totaux.items():
                if volume > 0.1:
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    
                    # Épaisseur proportionnelle au volume
                    width = 1 + 5 * (volume / flux_max)
                    
                    # Flèche incurvée
                    self.ax.annotate('',
                                   xy=(x2, y2), xytext=(x1, y1),
                                   arrowprops=dict(arrowstyle='->', lw=width,
                                                 color='orange', alpha=0.6,
                                                 connectionstyle="arc3,rad=0.2"))
                    
                    # Étiquette du volume
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    self.ax.text(mx, my, f'{volume:.0f}t', 
                               fontsize=8, bbox=dict(boxstyle='round,pad=0.3',
                               facecolor='yellow', alpha=0.7))
        
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title('Flux d\'Approvisionnement entre Sites', fontsize=14, fontweight='bold')
        
        self.fig.tight_layout()
        self.draw()
    
    def tracer_repartition_couts(self, modele):
        """
        Trace un diagramme circulaire de la répartition des coûts
        """
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        # Calculer les composantes de coût
        d = modele.donnees
        r = modele.resultats
        
        cout_transport = 0
        for (i, j, m), vol in r['flux'].items():
            cout_transport += d.cout_transport[i, j, m] * vol
        
        cout_kilometrique = 0
        for (i, j), vol in r['flux_totaux'].items():
            cout_kilometrique += d.cout_kilometrique * d.distance[i, j] * vol
        
        cout_stockage = 0
        for (i, m), vol in r['stocks'].items():
            cout_stockage += d.cout_stockage[i, m] * vol
        
        cout_rupture = 0
        for (j, m), vol in r['ruptures'].items():
            cout_rupture += d.penalite_rupture[j, m] * vol
        
        # Données pour le camembert
        labels = ['Transport direct', 'Kilométrique', 'Stockage', 'Pénalités rupture']
        sizes = [cout_transport, cout_kilometrique, cout_stockage, cout_rupture]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        explode = (0.05, 0.05, 0.05, 0.1)
        
        # Filtrer les valeurs nulles
        data = [(l, s, c, e) for l, s, c, e in zip(labels, sizes, colors, explode) if s > 0]
        if data:
            labels, sizes, colors, explode = zip(*data)
        
        self.ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        self.ax.set_title('Répartition des Coûts', fontsize=14, fontweight='bold')
        
        self.fig.tight_layout()
        self.draw()


class FenetreApprovisionnement(QMainWindow):
    """
    Fenêtre principale de l'application OptiAppro v2.0
    Interface professionnelle avec intégration complète des modules utilitaires
    """
    
    def __init__(self):
        super().__init__()
        
        logger.info("=" * 80)
        logger.info("🚀 Démarrage de l'application OptiAppro v2.0")
        logger.info("=" * 80)
        
        # Données et modèles
        self.donnees = None
        self.modele = None
        self.thread_resolution = None
        
        # Gestionnaires utilitaires
        self.gestionnaire_io = GestionnaireImportExport()
        self.validateur = ValidateurDonnees()
        self.interpreteur = InterpreteurResultats()
        
        logger.info("✓ Gestionnaires utilitaires initialisés")
        
        self.init_ui()
        self.creer_donnees_defaut()
        
        logger.info("✓ Interface initialisée avec succès")
    
    def init_ui(self):
        """Initialise l'interface utilisateur avec styles modernes"""
        with LoggerContextuel("Initialisation de l'interface"):
            self.setWindowTitle(f"{Icones.LOGO} OptiAppro v2.0 - Optimisation de l'Approvisionnement Inter-Sites")
            self.setGeometry(100, 100, 1400, 900)
            
            # Créer la barre de menu
            self.creer_menu()
            
            # Créer la barre d'outils
            self.creer_toolbar()
            
            # Widget central avec onglets
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)
            
            # Onglets principaux
            self.tab_parametres = self.creer_onglet_parametres()
            self.tab_donnees = self.creer_onglet_donnees()
            self.tab_resolution = self.creer_onglet_resolution()
            self.tab_resultats = self.creer_onglet_resultats()
            self.tab_visualisation = self.creer_onglet_visualisation()
            self.tab_insights = self.creer_onglet_insights()
            
            # Ajouter onglets avec icônes et tooltips
            self.tabs.addTab(self.tab_parametres, f"{Icones.PARAMETRES} Paramètres")
            self.tabs.addTab(self.tab_donnees, f"{Icones.DONNEES} Données")
            self.tabs.addTab(self.tab_resolution, f"{Icones.RESOLUTION} Résolution")
            self.tabs.addTab(self.tab_resultats, f"{Icones.RESULTATS} Résultats")
            self.tabs.addTab(self.tab_visualisation, f"{Icones.GRAPHIQUE} Visualisation")
            self.tabs.addTab(self.tab_insights, f"{Icones.ANALYSE} Insights")
            
            self.tabs.setTabToolTip(0, Messages.TIP_TAB_PARAMETRES)
            self.tabs.setTabToolTip(1, Messages.TIP_TAB_DONNEES)
            self.tabs.setTabToolTip(2, Messages.TIP_TAB_RESOLUTION)
            self.tabs.setTabToolTip(3, Messages.TIP_TAB_RESULTATS)
            self.tabs.setTabToolTip(4, Messages.TIP_TAB_VISUALISATION)
            self.tabs.setTabToolTip(5, Messages.TIP_TAB_INSIGHTS)
            
            # Barre de statut avec icône
            self.statusBar().showMessage(f"{Icones.SUCCES} Prêt à optimiser")
            
            logger.info(f"✓ Interface créée avec {self.tabs.count()} onglets")
    
    def creer_menu(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        menu_fichier = menubar.addMenu(f"{Icones.FICHIER} Fichier")
        
        action_importer = QAction(f"{Icones.IMPORTER} Importer Données CSV", self)
        action_importer.setShortcut("Ctrl+O")
        action_importer.setToolTip(Messages.TIP_IMPORTER)
        action_importer.triggered.connect(self.importer_donnees)
        menu_fichier.addAction(action_importer)
        
        action_exporter = QAction(f"{Icones.EXPORTER} Exporter Résultats", self)
        action_exporter.setShortcut("Ctrl+S")
        action_exporter.setToolTip(Messages.TIP_EXPORTER)
        action_exporter.triggered.connect(self.exporter_resultats)
        menu_fichier.addAction(action_exporter)
        
        menu_fichier.addSeparator()
        
        action_quitter = QAction(f"{Icones.ERREUR} Quitter", self)
        action_quitter.setShortcut("Ctrl+Q")
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)
        
        # Menu Affichage
        menu_affichage = menubar.addMenu(f"{Icones.THEME} Affichage")
        
        action_theme = QAction(f"{Icones.THEME} Basculer Thème Clair/Sombre", self)
        action_theme.setShortcut("Ctrl+T")
        action_theme.setToolTip("Basculer entre le thème clair et sombre")
        action_theme.triggered.connect(self.basculer_theme)
        menu_affichage.addAction(action_theme)
        
        # Menu Aide
        menu_aide = menubar.addMenu(f"{Icones.AIDE} Aide")
        
        action_documentation = QAction(f"{Icones.DOCUMENTATION} Documentation", self)
        action_documentation.triggered.connect(self.afficher_documentation)
        menu_aide.addAction(action_documentation)
        
        action_apropos = QAction(f"{Icones.INFO} À propos", self)
        action_apropos.triggered.connect(self.afficher_apropos)
        menu_aide.addAction(action_apropos)
    
    def creer_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = self.addToolBar("Principal")
        toolbar.setMovable(False)
        
        # Action: Importer
        action_importer = QAction(f"{Icones.IMPORTER} Importer", self)
        action_importer.setToolTip(Messages.TIP_IMPORTER)
        action_importer.triggered.connect(self.importer_donnees)
        toolbar.addAction(action_importer)
        
        # Action: Exporter
        action_exporter = QAction(f"{Icones.EXPORTER} Exporter", self)
        action_exporter.setToolTip(Messages.TIP_EXPORTER)
        action_exporter.triggered.connect(self.exporter_resultats)
        toolbar.addAction(action_exporter)
        
        toolbar.addSeparator()
        
        # Action: Résoudre
        action_resoudre = QAction(f"{Icones.RESOLUTION} Résoudre", self)
        action_resoudre.setToolTip(Messages.TIP_RESOUDRE)
        action_resoudre.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        toolbar.addAction(action_resoudre)
        
        toolbar.addSeparator()
        
        # Action: Basculer thème
        action_theme = QAction(f"{Icones.THEME} Thème", self)
        action_theme.setToolTip("Basculer entre thème clair et sombre")
        action_theme.triggered.connect(self.basculer_theme)
        toolbar.addAction(action_theme)
    
    def creer_onglet_parametres(self):
        """Onglet pour définir la taille du problème avec tooltips et styles modernes"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Titre principal
        titre = QLabel(f"{Icones.PARAMETRES} {Messages.TAB_PARAMETRES}")
        titre.setProperty("class", "titre-section")
        layout.addWidget(titre)
        
        # Carte: Dimensions du problème
        carte_dimensions = QFrame()
        carte_dimensions.setProperty("class", "carte")
        layout_carte = QVBoxLayout()
        
        # Sous-titre
        sous_titre = QLabel("Dimensions du Problème")
        sous_titre.setProperty("class", "sous-titre")
        layout_carte.addWidget(sous_titre)
        
        # Nombre de sites
        hlayout_sites = QHBoxLayout()
        label_sites = QLabel(f"{Icones.SITE} Nombre de sites de production:")
        label_sites.setMinimumWidth(250)
        self.spin_sites = QSpinBox()
        self.spin_sites.setRange(ParametresDefaut.NB_SITES_MIN, ParametresDefaut.NB_SITES_MAX)
        self.spin_sites.setValue(ParametresDefaut.NB_SITES_DEFAUT)
        self.spin_sites.setToolTip(Messages.TIP_NB_SITES)
        self.spin_sites.setMinimumWidth(100)
        hlayout_sites.addWidget(label_sites)
        hlayout_sites.addWidget(self.spin_sites)
        hlayout_sites.addStretch()
        layout_carte.addLayout(hlayout_sites)
        
        # Nombre de matières
        hlayout_matieres = QHBoxLayout()
        label_matieres = QLabel(f"{Icones.MATIERE} Nombre de matières premières:")
        label_matieres.setMinimumWidth(250)
        self.spin_matieres = QSpinBox()
        self.spin_matieres.setRange(ParametresDefaut.NB_MATIERES_MIN, ParametresDefaut.NB_MATIERES_MAX)
        self.spin_matieres.setValue(ParametresDefaut.NB_MATIERES_DEFAUT)
        self.spin_matieres.setToolTip(Messages.TIP_NB_MATIERES)
        self.spin_matieres.setMinimumWidth(100)
        hlayout_matieres.addWidget(label_matieres)
        hlayout_matieres.addWidget(self.spin_matieres)
        hlayout_matieres.addStretch()
        layout_carte.addLayout(hlayout_matieres)
        
        # ═══════════════════════════════════════════════════════════════
        # PÉNALITÉ DE RUPTURE (NOUVEAU PARAMÈTRE)
        # ═══════════════════════════════════════════════════════════════
        hlayout_penalite = QHBoxLayout()
        label_penalite = QLabel("💸 Pénalité de rupture (DT/tonne):")
        label_penalite.setMinimumWidth(250)
        self.spin_penalite = QDoubleSpinBox()
        self.spin_penalite.setRange(0.0, 100000.0)
        self.spin_penalite.setValue(100.0)  # Valeur par défaut
        self.spin_penalite.setDecimals(2)
        self.spin_penalite.setSingleStep(10.0)
        self.spin_penalite.setSuffix(" DT/t")
        self.spin_penalite.setToolTip(
            "Coût fictif appliqué pour chaque tonne de demande non satisfaite.\n"
            "• Faible (<10 DT/t): Le solveur préfère les ruptures au transport\n"
            "• Modéré (10-100 DT/t): Compromis économique\n"
            "• Élevé (>100 DT/t): Le solveur évite les ruptures à tout prix\n"
            "Recommandé: 10× le coût de transport maximum"
        )
        self.spin_penalite.setMinimumWidth(150)
        hlayout_penalite.addWidget(label_penalite)
        hlayout_penalite.addWidget(self.spin_penalite)
        hlayout_penalite.addStretch()
        layout_carte.addLayout(hlayout_penalite)
        
        carte_dimensions.setLayout(layout_carte)
        layout.addWidget(carte_dimensions)
        
        # Carte: Actions
        carte_actions = QFrame()
        carte_actions.setProperty("class", "carte")
        layout_actions = QVBoxLayout()
        
        sous_titre_actions = QLabel("Actions Rapides")
        sous_titre_actions.setProperty("class", "sous-titre")
        layout_actions.addWidget(sous_titre_actions)
        
        # Boutons d'action
        hlayout_boutons = QHBoxLayout()
        
        btn_appliquer = QPushButton(f"{Icones.PARAMETRES} {Messages.BTN_APPLIQUER_CONFIG}")
        btn_appliquer.setProperty("class", "action-principale")
        btn_appliquer.setToolTip(Messages.TIP_APPLIQUER_CONFIG)
        btn_appliquer.clicked.connect(self.appliquer_configuration)
        btn_appliquer.setMinimumHeight(40)
        
        btn_exemple = QPushButton(f"{Icones.DONNEES} {Messages.BTN_CHARGER_EXEMPLE}")
        btn_exemple.setToolTip(Messages.TIP_CHARGER_EXEMPLE)
        btn_exemple.clicked.connect(self.charger_donnees_exemple)
        btn_exemple.setMinimumHeight(40)
        
        hlayout_boutons.addWidget(btn_appliquer)
        hlayout_boutons.addWidget(btn_exemple)
        layout_actions.addLayout(hlayout_boutons)
        
        carte_actions.setLayout(layout_actions)
        layout.addWidget(carte_actions)
        
        # Carte: Informations
        carte_info = QFrame()
        carte_info.setProperty("class", "carte-accentuee")
        layout_info = QVBoxLayout()
        
        label_info = QLabel(
            f"{Icones.INFO} <b>Information:</b><br>"
            f"Configurez d'abord les dimensions du problème, puis remplissez "
            f"les données dans l'onglet suivant. Vous pouvez aussi charger "
            f"un exemple pour découvrir l'application."
        )
        label_info.setWordWrap(True)
        layout_info.addWidget(label_info)
        
        carte_info.setLayout(layout_info)
        layout.addWidget(carte_info)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def creer_onglet_donnees(self):
        """Onglet pour saisir les données du problème - Design professionnel"""
        # Widget conteneur principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f1f5f9;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Titre avec icône
        titre = QLabel(f"📊 Saisie des Données du Problème")
        titre.setProperty("class", "titre-section")
        titre.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1e40af;
            padding: 10px;
        """)
        layout.addWidget(titre)
        
        # Instruction
        instruction = QLabel("💡 Remplissez les matrices ci-dessous. Les unités sont indiquées dans chaque en-tête.")
        instruction.setStyleSheet("color: #64748b; font-size: 12px; padding: 5px;")
        layout.addWidget(instruction)
        
        # Onglets secondaires pour les différentes matrices
        self.tabs_donnees = QTabWidget()
        self.tabs_donnees.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-bottom: none;
                color: #1e40af;
            }
            QTabBar::tab:!selected {
                background-color: #f1f5f9;
                color: #64748b;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e2e8f0;
            }
        """)
        
        # Tables pour chaque type de données
        self.table_offre = self.creer_table_donnees("📦 Offre", "tonnes", "#059669")
        self.table_demande = self.creer_table_donnees("📥 Demande", "tonnes", "#dc2626")
        self.table_cout_transport = self.creer_table_couts()
        self.table_distances = self.creer_table_distances()
        self.table_capacites = self.creer_table_capacites()
        
        self.tabs_donnees.addTab(self.table_offre, "📦 Offre (t)")
        self.tabs_donnees.addTab(self.table_demande, "📥 Demande (t)")
        self.tabs_donnees.addTab(self.table_cout_transport, "💰 Coûts (DT/t)")
        self.tabs_donnees.addTab(self.table_distances, "📏 Distances (km)")
        self.tabs_donnees.addTab(self.table_capacites, "⚙️ Capacités (t)")
        
        layout.addWidget(self.tabs_donnees)
        
        # Bouton de validation stylisé
        btn_valider = QPushButton("✅ Valider les Données")
        btn_valider.setMinimumHeight(45)
        btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #047857;
            }
            QPushButton:pressed {
                background-color: #065f46;
            }
        """)
        btn_valider.clicked.connect(self.valider_donnees)
        layout.addWidget(btn_valider)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
    
    def creer_table_donnees(self, titre, unite="tonnes", couleur="#3b82f6"):
        """Crée une table pour offre/demande avec style professionnel"""
        group = QGroupBox(f"{titre} ({unite})")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 13px;
                border: 2px solid {couleur};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #fafafa;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: {couleur};
            }}
        """)
        layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(1)
        table.setRowCount(1)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: right;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #334155;
                font-weight: 600;
                padding: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        table.setAlternatingRowColors(True)
        layout.addWidget(table)
        
        group.setLayout(layout)
        return group
    
    def creer_table_couts(self):
        """Crée les tables pour les coûts de transport (une par matière) - Style professionnel"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # En-tête avec instruction
        header_layout = QHBoxLayout()
        label = QLabel("🔄 Sélectionnez la matière pour voir/éditer les coûts:")
        label.setStyleSheet("font-weight: 600; color: #334155; font-size: 12px;")
        header_layout.addWidget(label)
        
        self.combo_matiere_cout = QComboBox()
        self.combo_matiere_cout.setMinimumWidth(200)
        self.combo_matiere_cout.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        self.combo_matiere_cout.currentIndexChanged.connect(self.actualiser_table_couts)
        header_layout.addWidget(self.combo_matiere_cout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Info unité
        info_unite = QLabel("💰 Unité: DT/tonne (Dinar Tunisien par tonne)")
        info_unite.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        layout.addWidget(info_unite)
        
        self.table_cout_matiere = QTableWidget()
        self.table_cout_matiere.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                border: 2px solid #f59e0b;
                border-radius: 6px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: right;
            }
            QTableWidget::item:selected {
                background-color: #fef3c7;
                color: #92400e;
            }
            QHeaderView::section {
                background-color: #fffbeb;
                color: #92400e;
                font-weight: 600;
                padding: 8px;
                border: 1px solid #fcd34d;
            }
        """)
        self.table_cout_matiere.setAlternatingRowColors(True)
        layout.addWidget(self.table_cout_matiere)
        
        widget.setLayout(layout)
        return widget
    
    def creer_table_distances(self):
        """Crée une table pour les distances entre sites - Style professionnel"""
        group = QGroupBox("📏 Distances entre sites")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 2px solid #8b5cf6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #faf5ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #7c3aed;
            }
        """)
        layout = QVBoxLayout()
        
        # Info unité
        info_unite = QLabel("📏 Unité: kilomètres (km)")
        info_unite.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic; margin-bottom: 5px;")
        layout.addWidget(info_unite)
        
        self.table_distance = QTableWidget()
        self.table_distance.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: right;
            }
            QTableWidget::item:selected {
                background-color: #ede9fe;
                color: #5b21b6;
            }
            QHeaderView::section {
                background-color: #f5f3ff;
                color: #5b21b6;
                font-weight: 600;
                padding: 8px;
                border: 1px solid #ddd6fe;
            }
        """)
        self.table_distance.setAlternatingRowColors(True)
        layout.addWidget(self.table_distance)
        
        group.setLayout(layout)
        return group
    
    def creer_table_capacites(self):
        """Crée les inputs pour les capacités - Style professionnel"""
        group = QGroupBox("⚙️ Capacités de Transfert")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 2px solid #06b6d4;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #f0fdfa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #0891b2;
            }
        """)
        layout = QVBoxLayout()
        
        # Info unité
        info_unite = QLabel("⚙️ Unité: tonnes (t) - Capacité maximale de transfert entre chaque paire de sites")
        info_unite.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic; margin-bottom: 5px;")
        layout.addWidget(info_unite)
        
        self.table_cap_transfert = QTableWidget()
        self.table_cap_transfert.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: right;
            }
            QTableWidget::item:selected {
                background-color: #cffafe;
                color: #0e7490;
            }
            QHeaderView::section {
                background-color: #ecfeff;
                color: #0e7490;
                font-weight: 600;
                padding: 8px;
                border: 1px solid #a5f3fc;
            }
        """)
        self.table_cap_transfert.setAlternatingRowColors(True)
        layout.addWidget(self.table_cap_transfert)
        
        group.setLayout(layout)
        return group
    
    def creer_onglet_resolution(self):
        """
        Onglet pour lancer la résolution - Design moderne avec détails scientifiques
        
        Affiche:
        - Résumé du problème (dimensions, variables, contraintes)
        - Bouton de résolution
        - Journal d'exécution détaillé
        - Informations Gurobi
        """
        # Widget conteneur principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f1f5f9;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Titre avec icône
        titre = QLabel(f"{Icones.RESOLUTION} Résolution du Problème d'Optimisation")
        titre.setProperty("class", "titre-section")
        layout.addWidget(titre)
        
        # ═══════════════════════════════════════════════════════════════
        # PANNEAU RÉSUMÉ DU PROBLÈME (SCIENTIFIQUE)
        # ═══════════════════════════════════════════════════════════════
        
        group_resume_probleme = QGroupBox("📊 Résumé du Problème")
        group_resume_probleme.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #f0f9ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #1e40af;
            }
        """)
        layout_resume_pb = QVBoxLayout()
        
        # Grille d'informations
        self.label_resume_probleme = QLabel()
        self.label_resume_probleme.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: #1e293b;
                padding: 10px;
                background-color: white;
                border-radius: 6px;
            }
        """)
        self._actualiser_resume_probleme()
        layout_resume_pb.addWidget(self.label_resume_probleme)
        
        group_resume_probleme.setLayout(layout_resume_pb)
        layout.addWidget(group_resume_probleme)
        
        # ═══════════════════════════════════════════════════════════════
        # PANNEAU CONTRAINTES DU MODÈLE
        # ═══════════════════════════════════════════════════════════════
        
        group_contraintes = QGroupBox("📐 Contraintes du Modèle Mathématique")
        group_contraintes.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 2px solid #059669;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #f0fdf4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #047857;
            }
        """)
        layout_contraintes = QVBoxLayout()
        
        self.label_contraintes = QLabel()
        self.label_contraintes.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #1e293b;
                padding: 10px;
                background-color: white;
                border-radius: 6px;
            }
        """)
        self.label_contraintes.setWordWrap(True)
        self._actualiser_contraintes_modele()
        layout_contraintes.addWidget(self.label_contraintes)
        
        group_contraintes.setLayout(layout_contraintes)
        layout.addWidget(group_contraintes)
        
        # ═══════════════════════════════════════════════════════════════
        # ZONE DE RÉSOLUTION
        # ═══════════════════════════════════════════════════════════════
        
        zone_centrale = QFrame()
        zone_centrale.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dbeafe, stop:1 #e0e7ff);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout_centrale = QVBoxLayout()
        layout_centrale.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Indicateur de statut
        self.indicateur_statut = QLabel("● Prêt à résoudre")
        self.indicateur_statut.setStyleSheet("""
            color: #059669;
            font-size: 14px;
            font-weight: 600;
        """)
        self.indicateur_statut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_centrale.addWidget(self.indicateur_statut)
        
        # Bouton de résolution principal
        self.btn_resoudre = QPushButton(f"🚀 RÉSOUDRE AVEC GUROBI")
        self.btn_resoudre.setMinimumHeight(60)
        self.btn_resoudre.setMinimumWidth(320)
        self.btn_resoudre.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        self.btn_resoudre.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #7c3aed);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1d4ed8, stop:1 #6d28d9);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e40af, stop:1 #5b21b6);
            }
        """)
        self.btn_resoudre.setToolTip("Lancer l'optimisation avec Gurobi (Ctrl+R)")
        self.btn_resoudre.clicked.connect(self.lancer_resolution)
        self.btn_resoudre.setShortcut("Ctrl+R")
        layout_centrale.addWidget(self.btn_resoudre, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(320)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #e2e8f0;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
            }
        """)
        layout_centrale.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Label temps
        self.label_temps = QLabel("")
        self.label_temps.setStyleSheet("color: #64748b; font-size: 12px;")
        self.label_temps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_centrale.addWidget(self.label_temps)
        
        zone_centrale.setLayout(layout_centrale)
        layout.addWidget(zone_centrale)
        
        # ═══════════════════════════════════════════════════════════════
        # JOURNAL D'EXÉCUTION
        # ═══════════════════════════════════════════════════════════════
        
        group_log = QGroupBox(f"{Icones.DOCUMENTATION} Journal d'Exécution Gurobi")
        group_log.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        layout_log = QVBoxLayout()
        
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMinimumHeight(180)
        self.text_log.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        # Message d'attente initial
        self.text_log.setPlainText("En attente de résolution...\n\nCliquez sur 'RÉSOUDRE AVEC GUROBI' pour lancer l'optimisation.")
        layout_log.addWidget(self.text_log)
        
        group_log.setLayout(layout_log)
        layout.addWidget(group_log)
        
        # Ajouter un stretch pour le scroll
        layout.addStretch()
        
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
    
    def _actualiser_resume_probleme(self):
        """Met à jour le panneau de résumé du problème"""
        if self.donnees is None:
            texte = "⚠️ Aucune donnée chargée. Configurez d'abord les paramètres."
        else:
            d = self.donnees
            offre_totale = d.offre.sum()
            demande_totale = d.demande.sum()
            
            # Calcul du nombre de variables et contraintes prévu
            n = d.n_sites
            m = d.n_matieres
            nb_vars_x = n * (n - 1) * m  # x[i,j,m] pour i≠j
            nb_vars_s = n * m            # s[i,m]
            nb_vars_r = n * m            # r[j,m]
            nb_vars_y = n * (n - 1)      # y[i,j] pour i≠j
            nb_vars_total = nb_vars_x + nb_vars_s + nb_vars_r + nb_vars_y
            
            texte = f"""
┌─────────────────────────────────────────────────────────────┐
│  DIMENSIONS DU PROBLÈME                                     │
├─────────────────────────────────────────────────────────────┤
│  Nombre de sites (n)       : {n:>6}                          │
│  Nombre de matières (m)    : {m:>6}                          │
├─────────────────────────────────────────────────────────────┤
│  DONNÉES                                                    │
├─────────────────────────────────────────────────────────────┤
│  Offre totale              : {offre_totale:>10.1f} tonnes             │
│  Demande totale            : {demande_totale:>10.1f} tonnes             │
│  Balance offre/demande     : {offre_totale - demande_totale:>+10.1f} tonnes             │
├─────────────────────────────────────────────────────────────┤
│  VARIABLES DE DÉCISION (estimées)                           │
├─────────────────────────────────────────────────────────────┤
│  x[i,j,m] (flux)           : {nb_vars_x:>6} variables continues      │
│  s[i,m] (stocks)           : {nb_vars_s:>6} variables continues      │
│  r[j,m] (ruptures)         : {nb_vars_r:>6} variables continues      │
│  y[i,j] (flux totaux)      : {nb_vars_y:>6} variables continues      │
│  ─────────────────────────────────────────────────────────  │
│  TOTAL                     : {nb_vars_total:>6} variables              │
└─────────────────────────────────────────────────────────────┘
"""
        self.label_resume_probleme.setText(texte.strip())
    
    def _actualiser_contraintes_modele(self):
        """Affiche les contraintes mathématiques du modèle"""
        texte = """
╔═══════════════════════════════════════════════════════════════════════╗
║  MODÈLE DE PROGRAMMATION LINÉAIRE (PL)                                ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  FONCTION OBJECTIF: Minimiser Z                                       ║
║  ───────────────────────────────────────────────────────────────────  ║
║  Z = Σᵢⱼₘ cᵢⱼₘ·xᵢⱼₘ + Σᵢₘ hᵢₘ·sᵢₘ + Σⱼₘ pⱼₘ·rⱼₘ + α·Σᵢⱼ dᵢⱼ·yᵢⱼ      ║
║                                                                       ║
║  où: c = coût transport, h = coût stockage, p = pénalité rupture      ║
║      α = coût kilométrique, d = distance                              ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║  CONTRAINTES                                                          ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  (1) Conservation des flux ∀i,m:                                      ║
║      Oᵢₘ + Σₖ xₖᵢₘ = Σⱼ xᵢⱼₘ + sᵢₘ                                    ║
║                                                                       ║
║  (2) Satisfaction demande ∀j,m:                                       ║
║      Σᵢ xᵢⱼₘ + rⱼₘ = Dⱼₘ                                               ║
║                                                                       ║
║  (3) Capacité transfert ∀i,j (i≠j):                                   ║
║      Σₘ xᵢⱼₘ ≤ Capᵢⱼ                                                   ║
║                                                                       ║
║  (4) Capacité expédition ∀i:                                          ║
║      Σⱼₘ xᵢⱼₘ ≤ Cap_outᵢ                                               ║
║                                                                       ║
║  (5) Capacité réception ∀j:                                           ║
║      Σᵢₘ xᵢⱼₘ ≤ Cap_inⱼ                                                ║
║                                                                       ║
║  (6) Lien flux total ∀i,j (i≠j):                                      ║
║      yᵢⱼ = Σₘ xᵢⱼₘ                                                     ║
║                                                                       ║
║  (7) Limitation rupture ∀j,m (si Dⱼₘ > 0):                            ║
║      rⱼₘ ≤ 0.2 × Dⱼₘ                                                   ║
║                                                                       ║
║  (8) Non-négativité:                                                  ║
║      xᵢⱼₘ ≥ 0, sᵢₘ ≥ 0, rⱼₘ ≥ 0, yᵢⱼ ≥ 0                               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
"""
        self.label_contraintes.setText(texte.strip())
    
    def creer_onglet_resultats(self):
        """Onglet pour afficher les résultats détaillés - Design moderne avec KPIs"""
        # Widget conteneur principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f1f5f9;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Titre avec icône
        titre = QLabel(f"{Icones.RESULTATS} Résultats de l'Optimisation")
        titre.setProperty("class", "titre-section")
        layout.addWidget(titre)
        
        # ═══════════════════════════════════════════════════════════════
        # DASHBOARD KPIs
        # ═══════════════════════════════════════════════════════════════
        
        # Conteneur pour les cartes KPI
        self.container_kpis = QFrame()
        self.container_kpis.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        layout_kpis = QHBoxLayout(self.container_kpis)
        layout_kpis.setContentsMargins(0, 0, 0, 0)
        layout_kpis.setSpacing(15)
        
        # Carte 1: Coût Total
        self.kpi_cout = self._creer_carte_kpi("💰", "Coût Total", f"-- {UNITE_MONETAIRE}", "#059669")
        layout_kpis.addWidget(self.kpi_cout)
        
        # Carte 2: Satisfaction
        self.kpi_satisfaction = self._creer_carte_kpi("✅", "Satisfaction", "--%", "#3b82f6")
        layout_kpis.addWidget(self.kpi_satisfaction)
        
        # Carte 3: Flux Total
        self.kpi_flux = self._creer_carte_kpi("🚚", "Flux Total", "-- t", "#8b5cf6")
        layout_kpis.addWidget(self.kpi_flux)
        
        # Carte 4: Ruptures
        self.kpi_ruptures = self._creer_carte_kpi("⚠️", "Ruptures", "-- t", "#f59e0b")
        layout_kpis.addWidget(self.kpi_ruptures)
        
        # Carte 5: Temps
        self.kpi_temps = self._creer_carte_kpi("⏱️", "Temps", "-- s", "#06b6d4")
        layout_kpis.addWidget(self.kpi_temps)
        
        layout_kpis.addStretch()
        layout.addWidget(self.container_kpis)
        
        # ═══════════════════════════════════════════════════════════════
        # RÉSUMÉ TEXTUEL
        # ═══════════════════════════════════════════════════════════════
        
        self.group_resume = QGroupBox(f"{Icones.INFO} Résumé de la Solution")
        self.group_resume.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8fafc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        layout_resume = QVBoxLayout()
        self.label_resume = QLabel("Aucune solution disponible. Lancez la résolution pour voir les résultats.")
        self.label_resume.setStyleSheet("color: #64748b; font-size: 13px;")
        self.label_resume.setWordWrap(True)
        layout_resume.addWidget(self.label_resume)
        self.group_resume.setLayout(layout_resume)
        layout.addWidget(self.group_resume)
        
        # ═══════════════════════════════════════════════════════════════
        # TABLES DE RÉSULTATS
        # ═══════════════════════════════════════════════════════════════
        
        self.tabs_resultats = QTabWidget()
        self.tabs_resultats.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-bottom: none;
            }
            QTabBar::tab:!selected {
                background-color: #f1f5f9;
            }
        """)
        
        # Table des flux
        self.table_flux = QTableWidget()
        self.table_flux.setColumnCount(4)
        self.table_flux.setHorizontalHeaderLabels(["📍 Site Source", "📍 Site Dest.", "📦 Matière", "📊 Quantité (t)"])
        self.table_flux.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_flux.setAlternatingRowColors(True)
        self.tabs_resultats.addTab(self.table_flux, "🚚 Flux Optimaux")
        
        # Table des ruptures
        self.table_ruptures = QTableWidget()
        self.table_ruptures.setColumnCount(3)
        self.table_ruptures.setHorizontalHeaderLabels(["📍 Site", "📦 Matière", "⚠️ Rupture (t)"])
        self.table_ruptures.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_ruptures.setAlternatingRowColors(True)
        self.tabs_resultats.addTab(self.table_ruptures, "⚠️ Ruptures")
        
        # Table des stocks
        self.table_stocks = QTableWidget()
        self.table_stocks.setColumnCount(3)
        self.table_stocks.setHorizontalHeaderLabels(["📍 Site", "📦 Matière", "📊 Stock (t)"])
        self.table_stocks.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_stocks.setAlternatingRowColors(True)
        self.tabs_resultats.addTab(self.table_stocks, "📦 Stocks Résiduels")
        
        layout.addWidget(self.tabs_resultats)
        
        # Ajouter un peu d'espace en bas
        layout.addStretch()
        
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
    
    def _creer_carte_kpi(self, icone: str, titre: str, valeur: str, couleur: str) -> QFrame:
        """Crée une carte KPI stylisée"""
        carte = QFrame()
        carte.setFixedSize(140, 100)
        carte.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(255, 255, 255, 0.85));
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {couleur};
            }}
        """)
        
        layout = QVBoxLayout(carte)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        # Header avec icône
        header = QHBoxLayout()
        label_icone = QLabel(icone)
        label_icone.setStyleSheet("font-size: 18px;")
        header.addWidget(label_icone)
        
        label_titre = QLabel(titre)
        label_titre.setStyleSheet("font-size: 10px; color: #64748b;")
        header.addWidget(label_titre)
        header.addStretch()
        layout.addLayout(header)
        
        # Valeur
        label_valeur = QLabel(valeur)
        label_valeur.setObjectName("valeur")
        label_valeur.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {couleur};
        """)
        layout.addWidget(label_valeur)
        
        layout.addStretch()
        return carte
    
    def creer_onglet_visualisation(self):
        """Onglet pour les graphiques - avec visualisation Plotly interactive"""
        # Widget conteneur principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Titre
        titre = QLabel("📊 Visualisation Graphique")
        titre.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1e40af;
            padding: 10px;
        """)
        layout.addWidget(titre)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION GRAPHE INTERACTIF PLOTLY
        # ═══════════════════════════════════════════════════════════════
        
        group_plotly = QGroupBox("🌐 Graphe de Flux Interactif (Plotly)")
        group_plotly.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 2px solid #8b5cf6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #faf5ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #7c3aed;
            }
        """)
        layout_plotly = QVBoxLayout()
        
        # Description
        desc_plotly = QLabel(
            "💡 Génère un graphe de réseau interactif avec :\n"
            "• Placement intelligent des nœuds (Kamada-Kawai)\n"
            "• Arêtes courbées évitant les superpositions\n"
            "• Couleurs par intensité de flux\n"
            "• Infobulles détaillées au survol"
        )
        desc_plotly.setStyleSheet("color: #64748b; font-size: 11px; padding: 5px;")
        layout_plotly.addWidget(desc_plotly)
        
        # Options de layout
        layout_options = QHBoxLayout()
        layout_options.addWidget(QLabel("Layout:"))
        
        self.combo_layout_plotly = QComboBox()
        self.combo_layout_plotly.addItems([
            "Kamada-Kawai (recommandé)",
            "Spring (force-directed)",
            "Circulaire",
            "Hiérarchique"
        ])
        self.combo_layout_plotly.setMinimumWidth(200)
        layout_options.addWidget(self.combo_layout_plotly)
        layout_options.addStretch()
        layout_plotly.addLayout(layout_options)
        
        # Boutons
        layout_btns_plotly = QHBoxLayout()
        
        self.btn_plotly_navigateur = QPushButton("🌐 Ouvrir dans Navigateur")
        self.btn_plotly_navigateur.setMinimumHeight(40)
        self.btn_plotly_navigateur.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.btn_plotly_navigateur.clicked.connect(self.afficher_graphe_plotly)
        layout_btns_plotly.addWidget(self.btn_plotly_navigateur)
        
        self.btn_plotly_export = QPushButton("💾 Exporter HTML")
        self.btn_plotly_export.setMinimumHeight(40)
        self.btn_plotly_export.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        self.btn_plotly_export.clicked.connect(self.exporter_graphe_plotly)
        layout_btns_plotly.addWidget(self.btn_plotly_export)
        
        layout_btns_plotly.addStretch()
        layout_plotly.addLayout(layout_btns_plotly)
        
        group_plotly.setLayout(layout_plotly)
        layout.addWidget(group_plotly)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION GRAPHIQUES MATPLOTLIB (existant)
        # ═══════════════════════════════════════════════════════════════
        
        group_matplotlib = QGroupBox("📈 Graphiques Statiques (Matplotlib)")
        group_matplotlib.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #eff6ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #1e40af;
            }
        """)
        layout_matplotlib = QVBoxLayout()
        
        # Boutons de choix
        hlayout_choix = QHBoxLayout()
        btn_flux = QPushButton("🚚 Graphe des Flux")
        btn_flux.setMinimumHeight(35)
        btn_flux.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_flux.clicked.connect(lambda: self.afficher_graphique('flux'))
        
        btn_couts = QPushButton("💰 Répartition des Coûts")
        btn_couts.setMinimumHeight(35)
        btn_couts.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        btn_couts.clicked.connect(lambda: self.afficher_graphique('couts'))
        
        hlayout_choix.addWidget(btn_flux)
        hlayout_choix.addWidget(btn_couts)
        hlayout_choix.addStretch()
        layout_matplotlib.addLayout(hlayout_choix)
        
        # Canvas matplotlib
        self.canvas = GraphiqueFlux(self)
        layout_matplotlib.addWidget(self.canvas)
        
        group_matplotlib.setLayout(layout_matplotlib)
        layout.addWidget(group_matplotlib)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
    
    def afficher_graphe_plotly(self):
        """Affiche le graphe de flux interactif avec Plotly dans le navigateur"""
        if self.modele is None or not self.modele.resultats:
            QMessageBox.warning(
                self, "Attention",
                "⚠️ Aucun résultat disponible.\n\n"
                "Lancez d'abord la résolution pour visualiser les flux."
            )
            return
        
        try:
            from utils.visualisation_plotly import (
                VisualisateurFluxInteractif,
                ConfigurationVisualisation,
                LayoutType
            )
            
            # Déterminer le layout choisi
            layout_map = {
                "Kamada-Kawai (recommandé)": LayoutType.KAMADA_KAWAI,
                "Spring (force-directed)": LayoutType.SPRING,
                "Circulaire": LayoutType.CIRCULAR,
                "Hiérarchique": LayoutType.HIERARCHICAL
            }
            layout_choice = self.combo_layout_plotly.currentText()
            layout_type = layout_map.get(layout_choice, LayoutType.KAMADA_KAWAI)
            
            # Configuration
            config = ConfigurationVisualisation(
                layout_type=layout_type,
                title="Réseau d'Approvisionnement Optimisé - OptiAppro",
                edge_curvature=0.25,
                show_edge_labels=True,
                width=1400,
                height=900
            )
            
            # Créer le visualisateur
            viz = VisualisateurFluxInteractif(
                donnees=self.donnees,
                resultats=self.modele.resultats,
                config=config
            )
            
            # Afficher
            self.ajouter_log(f"📊 Génération graphe Plotly (layout: {layout_choice})")
            viz.afficher()
            self.ajouter_log("✓ Graphe ouvert dans le navigateur")
            
        except ImportError as e:
            QMessageBox.critical(
                self, "Erreur",
                f"❌ Module de visualisation non disponible:\n{e}\n\n"
                "Installez les dépendances:\npip install plotly networkx"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"❌ Erreur lors de la génération:\n{str(e)}"
            )
            self.ajouter_log(f"❌ Erreur Plotly: {e}")
    
    def exporter_graphe_plotly(self):
        """Exporte le graphe Plotly en HTML"""
        if self.modele is None or not self.modele.resultats:
            QMessageBox.warning(
                self, "Attention",
                "⚠️ Aucun résultat disponible.\n\n"
                "Lancez d'abord la résolution."
            )
            return
        
        try:
            from utils.visualisation_plotly import (
                VisualisateurFluxInteractif,
                ConfigurationVisualisation,
                LayoutType
            )
            
            # Dialogue de sauvegarde
            from pathlib import Path
            dossier_defaut = Path(__file__).parent / "exports"
            dossier_defaut.mkdir(exist_ok=True)
            
            chemin, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter le graphe interactif",
                str(dossier_defaut / "graphe_flux.html"),
                "HTML (*.html);;Tous les fichiers (*)"
            )
            
            if not chemin:
                return
            
            # Générer et exporter
            layout_map = {
                "Kamada-Kawai (recommandé)": LayoutType.KAMADA_KAWAI,
                "Spring (force-directed)": LayoutType.SPRING,
                "Circulaire": LayoutType.CIRCULAR,
                "Hiérarchique": LayoutType.HIERARCHICAL
            }
            layout_choice = self.combo_layout_plotly.currentText()
            layout_type = layout_map.get(layout_choice, LayoutType.KAMADA_KAWAI)
            
            config = ConfigurationVisualisation(
                layout_type=layout_type,
                title="Réseau d'Approvisionnement Optimisé - OptiAppro"
            )
            
            viz = VisualisateurFluxInteractif(
                donnees=self.donnees,
                resultats=self.modele.resultats,
                config=config
            )
            
            # Créer la figure et exporter directement
            fig = viz.creer_graphe_flux()
            fig.write_html(chemin, include_plotlyjs=True, full_html=True)
            
            self.ajouter_log(f"✓ Graphe exporté: {chemin}")
            QMessageBox.information(
                self, "Export réussi",
                f"✅ Graphe exporté avec succès!\n\n{chemin}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"❌ Erreur lors de l'export:\n{str(e)}"
            )
    
    def creer_donnees_defaut(self):
        """Crée une structure de données par défaut"""
        n_sites = self.spin_sites.value()
        n_matieres = self.spin_matieres.value()
        self.donnees = ModeleDonneesApprovisionnement(n_sites, n_matieres)
        # Appliquer la pénalité de rupture
        self.donnees.penalite_rupture_unitaire = self.spin_penalite.value()
        self.actualiser_tables()
        self._actualiser_resume_probleme()
    
    def appliquer_configuration(self):
        """Applique la nouvelle configuration"""
        n_sites = self.spin_sites.value()
        n_matieres = self.spin_matieres.value()
        penalite = self.spin_penalite.value()
        self.donnees = ModeleDonneesApprovisionnement(n_sites, n_matieres)
        # Appliquer la pénalité de rupture depuis l'interface
        self.donnees.penalite_rupture_unitaire = penalite
        self.actualiser_tables()
        self._actualiser_resume_probleme()
        self.ajouter_log(f"Configuration appliquée: {n_sites} sites, {n_matieres} matières, pénalité: {penalite:.2f} DT/t")
        QMessageBox.information(self, "Configuration", 
                               f"Nouvelle configuration créée:\n"
                               f"• {n_sites} sites\n"
                               f"• {n_matieres} matières\n"
                               f"• Pénalité de rupture: {penalite:.2f} DT/tonne")
    
    def charger_donnees_exemple(self):
        """Charge un exemple de données"""
        self.spin_sites.setValue(5)
        self.spin_matieres.setValue(3)
        self.donnees = ModeleDonneesApprovisionnement(5, 3)
        self.donnees.generer_donnees_exemple()
        # Appliquer la pénalité depuis l'interface
        self.donnees.penalite_rupture_unitaire = self.spin_penalite.value()
        self.actualiser_tables()
        self.remplir_tables_avec_donnees()
        self._actualiser_resume_probleme()
        self.ajouter_log("Données d'exemple chargées (5 sites, 3 matières)")
        QMessageBox.information(self, "Données Exemple", 
                               "Données d'exemple chargées avec succès!\n\n"
                               "• 5 sites de production\n"
                               "• 3 matières premières (Acier, Plastique, Aluminium)")
    
    def actualiser_tables(self):
        """Met à jour toutes les tables avec les nouvelles dimensions"""
        if self.donnees is None:
            return
        
        d = self.donnees
        
        # Table offre
        self.actualiser_table_simple(self.table_offre, d.n_sites, d.n_matieres, 
                                     d.noms_sites, d.noms_matieres)
        
        # Table demande
        self.actualiser_table_simple(self.table_demande, d.n_sites, d.n_matieres,
                                     d.noms_sites, d.noms_matieres)
        
        # Combo matières pour coûts
        self.combo_matiere_cout.clear()
        self.combo_matiere_cout.addItems(d.noms_matieres)
        
        # Table distances
        self.actualiser_table_carree(self.table_distance, d.n_sites, d.noms_sites)
        
        # Table capacités transfert
        self.actualiser_table_carree(self.table_cap_transfert, d.n_sites, d.noms_sites)
    
    def actualiser_table_simple(self, group_box, n_lignes, n_cols, noms_lignes, noms_cols):
        """Met à jour une table simple (sites × matières)"""
        table = group_box.findChild(QTableWidget)
        if table:
            table.setRowCount(n_lignes)
            table.setColumnCount(n_cols)
            table.setVerticalHeaderLabels(noms_lignes)
            table.setHorizontalHeaderLabels(noms_cols)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            # Initialiser avec des zéros
            for i in range(n_lignes):
                for j in range(n_cols):
                    table.setItem(i, j, QTableWidgetItem("0"))
    
    def actualiser_table_carree(self, table, n, noms):
        """Met à jour une table carrée (sites × sites)"""
        table.setRowCount(n)
        table.setColumnCount(n)
        table.setVerticalHeaderLabels(noms)
        table.setHorizontalHeaderLabels(noms)
        
        for i in range(n):
            for j in range(n):
                table.setItem(i, j, QTableWidgetItem("0"))
    
    def actualiser_table_couts(self):
        """Actualise la table des coûts pour la matière sélectionnée"""
        if self.donnees is None:
            return
        
        m = self.combo_matiere_cout.currentIndex()
        if m < 0:
            return
        
        d = self.donnees
        self.table_cout_matiere.setRowCount(d.n_sites)
        self.table_cout_matiere.setColumnCount(d.n_sites)
        self.table_cout_matiere.setVerticalHeaderLabels(d.noms_sites)
        self.table_cout_matiere.setHorizontalHeaderLabels(d.noms_sites)
        
        for i in range(d.n_sites):
            for j in range(d.n_sites):
                val = d.cout_transport[i, j, m]
                self.table_cout_matiere.setItem(i, j, QTableWidgetItem(f"{val:.2f}"))
    
    def remplir_tables_avec_donnees(self):
        """Remplit les tables avec les données du modèle"""
        if self.donnees is None:
            return
        
        d = self.donnees
        
        # Offre
        table_offre = self.table_offre.findChild(QTableWidget)
        for i in range(d.n_sites):
            for m in range(d.n_matieres):
                table_offre.setItem(i, m, QTableWidgetItem(f"{d.offre[i, m]:.1f}"))
        
        # Demande
        table_demande = self.table_demande.findChild(QTableWidget)
        for i in range(d.n_sites):
            for m in range(d.n_matieres):
                table_demande.setItem(i, m, QTableWidgetItem(f"{d.demande[i, m]:.1f}"))
        
        # Distances
        for i in range(d.n_sites):
            for j in range(d.n_sites):
                self.table_distance.setItem(i, j, QTableWidgetItem(f"{d.distance[i, j]:.1f}"))
        
        # Capacités transfert
        for i in range(d.n_sites):
            for j in range(d.n_sites):
                val = d.capacite_transfert[i, j] if d.capacite_transfert[i, j] != float('inf') else 999
                self.table_cap_transfert.setItem(i, j, QTableWidgetItem(f"{val:.0f}"))
        
        # Actualiser la table des coûts
        self.actualiser_table_couts()
    
    # ============================================================================
    # NOUVELLES MÉTHODES V2.0 - FONCTIONNALITÉS AVANCÉES
    # ============================================================================
    
    def creer_onglet_insights(self):
        """Crée l'onglet d'analyse et insights automatiques"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Titre
        titre = QLabel(f"{Icones.ANALYSE} Analyse Intelligente des Résultats")
        titre.setProperty("class", "titre-section")
        layout.addWidget(titre)
        
        # Zone de texte pour afficher les insights
        self.text_insights = QTextBrowser()
        self.text_insights.setProperty("class", "console")
        self.text_insights.setMinimumHeight(400)
        self.text_insights.setOpenExternalLinks(False)
        layout.addWidget(self.text_insights)
        
        # Boutons d'action
        hlayout_actions = QHBoxLayout()
        
        btn_analyser = QPushButton(f"{Icones.ANALYSE} Analyser les Résultats")
        btn_analyser.setProperty("class", "action-principale")
        btn_analyser.setToolTip("Générer une analyse intelligente des résultats")
        btn_analyser.clicked.connect(self.generer_insights)
        btn_analyser.setMinimumHeight(40)
        
        btn_exporter_rapport = QPushButton(f"{Icones.EXPORTER} Exporter le Rapport")
        btn_exporter_rapport.setToolTip("Exporter l'analyse en format HTML")
        btn_exporter_rapport.clicked.connect(self.exporter_rapport_insights)
        btn_exporter_rapport.setMinimumHeight(40)
        
        hlayout_actions.addWidget(btn_analyser)
        hlayout_actions.addWidget(btn_exporter_rapport)
        hlayout_actions.addStretch()
        layout.addLayout(hlayout_actions)
        
        widget.setLayout(layout)
        return widget
    
    def generer_insights(self):
        """Génère l'analyse intelligente des résultats"""
        if self.modele is None:
            QMessageBox.warning(
                self, 
                Messages.ERR_TITRE,
                f"{Icones.AVERTISSEMENT} {Messages.ERR_AUCUN_RESULTAT}"
            )
            logger.warning("Tentative d'analyse sans résultats disponibles")
            return
        
        try:
            with LoggerContextuel("Génération des insights"):
                # Analyser les résultats
                insights = self.interpreteur.analyser(self.modele)
                
                # Générer le rapport HTML
                rapport_html = self.interpreteur.generer_rapport_html()
                
                # Afficher dans le navigateur de texte
                self.text_insights.setHtml(rapport_html)
                
                self.statusBar().showMessage(
                    f"{Icones.SUCCES} {len(insights)} insights générés avec succès",
                    5000
                )
                logger.info(f"✓ {len(insights)} insights générés")
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération des insights: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                Messages.ERR_TITRE,
                f"{Icones.ERREUR} Erreur lors de l'analyse: {str(e)}"
            )
    
    def exporter_rapport_insights(self):
        """Exporte le rapport d'insights en HTML"""
        if self.modele is None:
            QMessageBox.warning(
                self,
                Messages.ERR_TITRE,
                f"{Icones.AVERTISSEMENT} {Messages.ERR_AUCUN_RESULTAT}"
            )
            return
        
        try:
            chemin, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter le Rapport d'Analyse",
                "rapport_analyse.html",
                "Fichier HTML (*.html)"
            )
            
            if chemin:
                with LoggerContextuel(f"Export du rapport vers {chemin}"):
                    rapport_html = self.interpreteur.generer_rapport_html()
                    
                    with open(chemin, 'w', encoding='utf-8') as f:
                        f.write(rapport_html)
                    
                    QMessageBox.information(
                        self,
                        Messages.SUC_TITRE,
                        f"{Icones.SUCCES} Rapport exporté avec succès!"
                    )
                    logger.info(f"✓ Rapport exporté: {chemin}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'export du rapport: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                Messages.ERR_TITRE,
                f"{Icones.ERREUR} Erreur lors de l'export: {str(e)}"
            )
    
    def importer_donnees(self):
        """
        Importe des données depuis un dossier contenant les fichiers CSV.
        
        Fichiers attendus:
            - offre.csv         : Matrice (n_sites × n_matieres)
            - demande.csv       : Matrice (n_sites × n_matieres)
            - distances.csv     : Matrice (n_sites × n_sites)
            - couts_matiere_0.csv, couts_matiere_1.csv, ... : Coûts par matière
            - capacites.csv     : Capacités (optionnel)
        """
        try:
            # Proposer d'abord les dossiers d'exemple
            dossier_exemple = Path(__file__).parent / "donnees_exemple"
            dossier_defaut = str(dossier_exemple) if dossier_exemple.exists() else str(Path.home())
            
            dossier = QFileDialog.getExistingDirectory(
                self,
                "📂 Sélectionner le Dossier contenant les Données CSV",
                dossier_defaut
            )
            
            if not dossier:
                return  # Annulé par l'utilisateur
            
            with LoggerContextuel(f"Import des données depuis {dossier}"):
                donnees_dict, message = self.gestionnaire_io.importer_donnees_completes(dossier)
                
                if donnees_dict is None:
                    QMessageBox.warning(
                        self,
                        Messages.ERR_TITRE,
                        f"{Icones.AVERTISSEMENT} Erreur lors de l'import:\n\n{message}\n\n"
                        f"Vérifiez que le dossier contient les fichiers:\n"
                        f"• offre.csv\n• demande.csv\n• distances.csv\n• couts_matiere_0.csv, ..."
                    )
                    logger.warning(f"Import échoué: {message}")
                    return
                
                # Vérifier que les clés nécessaires sont présentes
                cles_requises = ['n_sites', 'n_matieres', 'offre', 'demande', 'distance']
                for cle in cles_requises:
                    if cle not in donnees_dict:
                        QMessageBox.warning(
                            self,
                            Messages.ERR_TITRE,
                            f"{Icones.AVERTISSEMENT} Données incomplètes:\n\nLa clé '{cle}' est manquante."
                        )
                        return
                
                n_sites = donnees_dict['n_sites']
                n_matieres = donnees_dict['n_matieres']
                
                # Mettre à jour les spinbox
                self.spin_sites.setValue(n_sites)
                self.spin_matieres.setValue(n_matieres)
                
                # Créer l'objet ModeleDonneesApprovisionnement
                self.donnees = ModeleDonneesApprovisionnement(n_sites, n_matieres)
                
                # Appliquer la pénalité de rupture depuis l'interface
                self.donnees.penalite_rupture_unitaire = self.spin_penalite.value()
                
                # Copier les données
                self.donnees.offre = donnees_dict['offre']
                self.donnees.demande = donnees_dict['demande']
                self.donnees.distance = donnees_dict['distance']
                
                if 'cout_transport' in donnees_dict:
                    self.donnees.cout_transport = donnees_dict['cout_transport']
                    
                if 'capacite_transfert' in donnees_dict:
                    self.donnees.capacite_transfert = donnees_dict['capacite_transfert']
                
                # Mettre à jour les tables
                self.actualiser_tables()
                self.remplir_tables_avec_donnees()
                
                # Actualiser le résumé du problème
                self._actualiser_resume_probleme()
                
                # Message de succès
                penalite = self.spin_penalite.value()
                QMessageBox.information(
                    self,
                    Messages.SUC_TITRE,
                    f"{Icones.SUCCES} Données importées avec succès!\n\n"
                    f"• {n_sites} sites de production\n"
                    f"• {n_matieres} matières premières\n"
                    f"• Pénalité de rupture: {penalite:.2f} DT/t\n\n"
                    f"Vous pouvez maintenant lancer la résolution."
                )
                self.statusBar().showMessage(
                    f"{Icones.SUCCES} Import réussi: {n_sites} sites, {n_matieres} matières",
                    5000
                )
                logger.info(f"✓ Données importées: {n_sites} sites, {n_matieres} matières depuis {dossier}")
                
                # Basculer vers l'onglet Données pour vérification
                self.tabs.setCurrentIndex(1)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'import: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                Messages.ERR_TITRE,
                f"{Icones.ERREUR} Erreur lors de l'import: {str(e)}"
            )
    
    def exporter_resultats(self):
        """Exporte les résultats dans différents formats"""
        if self.modele is None:
            QMessageBox.warning(
                self,
                Messages.ERR_TITRE,
                f"{Icones.AVERTISSEMENT} {Messages.ERR_AUCUN_RESULTAT}"
            )
            return
        
        # Dialogue de sélection du format
        formats = ["CSV", "Excel (xlsx)", "Texte (txt)", "Scénario complet (json)"]
        format_choisi, ok = QComboBox(), False
        
        # Créer dialogue personnalisé
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Exporter les Résultats")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Choisissez le format d'export:"))
        combo = QComboBox()
        combo.addItems(formats)
        layout.addWidget(combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            format_idx = combo.currentIndex()
            
            try:
                if format_idx == 0:  # CSV
                    chemin, _ = QFileDialog.getSaveFileName(
                        self, "Exporter en CSV", "resultats.csv", "Fichier CSV (*.csv)"
                    )
                    if chemin:
                        with LoggerContextuel(f"Export CSV vers {chemin}"):
                            self.gestionnaire_io.exporter_resultats_csv(self.modele, chemin)
                            
                elif format_idx == 1:  # Excel
                    chemin, _ = QFileDialog.getSaveFileName(
                        self, "Exporter en Excel", "resultats.xlsx", "Fichier Excel (*.xlsx)"
                    )
                    if chemin:
                        with LoggerContextuel(f"Export Excel vers {chemin}"):
                            self.gestionnaire_io.exporter_resultats_excel(self.modele, chemin)
                            
                elif format_idx == 2:  # Texte
                    chemin, _ = QFileDialog.getSaveFileName(
                        self, "Exporter en Texte", "rapport.txt", "Fichier Texte (*.txt)"
                    )
                    if chemin:
                        with LoggerContextuel(f"Export TXT vers {chemin}"):
                            self.gestionnaire_io.generer_rapport_textuel(self.modele, chemin)
                            
                elif format_idx == 3:  # JSON
                    chemin, _ = QFileDialog.getSaveFileName(
                        self, "Sauvegarder Scénario", "scenario.json", "Fichier JSON (*.json)"
                    )
                    if chemin:
                        with LoggerContextuel(f"Sauvegarde scénario vers {chemin}"):
                            donnees_dict = {
                                'n_sites': self.donnees.n_sites,
                                'n_matieres': self.donnees.n_matieres,
                                'offre': self.donnees.offre.tolist(),
                                'demande': self.donnees.demande.tolist(),
                                'cout_transport': self.donnees.cout_transport.tolist(),
                                'distance': self.donnees.distance.tolist(),
                                'capacite_transfert': self.donnees.capacite_transfert.tolist()
                            }
                            self.gestionnaire_io.sauvegarder_scenario(
                                donnees_dict,
                                Path(chemin).stem,
                                self.modele.resultats
                            )
                
                if chemin:
                    QMessageBox.information(
                        self,
                        Messages.SUC_TITRE,
                        f"{Icones.SUCCES} Export réussi!"
                    )
                    self.statusBar().showMessage(
                        f"{Icones.SUCCES} Résultats exportés",
                        5000
                    )
                    logger.info(f"✓ Export réussi: {chemin}")
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'export: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    Messages.ERR_TITRE,
                    f"{Icones.ERREUR} Erreur lors de l'export: {str(e)}"
                )
    
    def basculer_theme(self):
        """Bascule entre le thème clair et sombre"""
        try:
            with LoggerContextuel("Basculement de thème"):
                StyleManager.basculer_theme()
                theme_actuel = StyleManager.obtenir_theme_actuel()
                
                self.statusBar().showMessage(
                    f"{Icones.THEME} Thème {theme_actuel.value} appliqué",
                    3000
                )
                logger.info(f"✓ Thème basculé vers: {theme_actuel.value}")
                
        except Exception as e:
            logger.error(f"Erreur lors du basculement de thème: {e}", exc_info=True)
    
    def afficher_documentation(self):
        """Affiche la documentation de l'application"""
        msg = QMessageBox(self)
        msg.setWindowTitle(f"{Icones.DOCUMENTATION} Documentation")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<h3>OptiAppro v2.0 - Documentation</h3>"
            "<p><b>Optimisation de l'Approvisionnement Inter-Sites</b></p>"
            "<p>Cette application permet de résoudre des problèmes d'approvisionnement "
            "entre sites de production en utilisant la programmation linéaire (Gurobi).</p>"
            "<h4>Utilisation:</h4>"
            "<ol>"
            "<li><b>Paramètres:</b> Définir les dimensions du problème</li>"
            "<li><b>Données:</b> Saisir ou importer les données (offre, demande, coûts...)</li>"
            "<li><b>Résolution:</b> Lancer l'optimisation</li>"
            "<li><b>Résultats:</b> Consulter les résultats détaillés</li>"
            "<li><b>Visualisation:</b> Analyser les graphiques</li>"
            "<li><b>Insights:</b> Obtenir une analyse intelligente</li>"
            "</ol>"
            "<p>Consultez les fichiers DOCUMENTATION.md et GUIDE_UTILISATION_V2.md pour plus de détails.</p>"
        )
        msg.exec()
        logger.info("Documentation affichée")
    
    def afficher_apropos(self):
        """Affiche les informations À propos - Design académique et professionnel"""
        # Les constantes sont déjà importées en haut du fichier
        
        msg = QMessageBox(self)
        msg.setWindowTitle("À propos de OptiAppro")
        msg.setIcon(QMessageBox.Icon.Information)
        
        # Design sobre et académique avec hiérarchie visuelle claire
        contenu_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 10px;">
            
            <!-- Titre principal -->
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #1e3a5f; margin: 0; font-size: 24px;">
                    📦 OptiAppro
                </h1>
                <p style="color: #64748b; margin: 5px 0; font-size: 14px;">
                    Optimisation de l'Approvisionnement Inter-Sites
                </p>
                <span style="background-color: #3b82f6; color: white; padding: 3px 12px; 
                       border-radius: 12px; font-size: 11px; font-weight: bold;">
                    Version {VERSION}
                </span>
            </div>
            
            <!-- Séparateur -->
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 15px 0;">
            
            <!-- Informations académiques -->
            <div style="background-color: #f8fafc; border-radius: 8px; padding: 15px; margin: 10px 0;">
                <table style="width: 100%; font-size: 13px;">
                    <tr>
                        <td style="color: #64748b; padding: 4px 0;">Institution :</td>
                        <td style="color: #1e293b; font-weight: 600; text-align: right;">{INSTITUTION}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b; padding: 4px 0;">Année universitaire :</td>
                        <td style="color: #1e293b; font-weight: 600; text-align: right;">{ANNEE_ACADEMIQUE}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b; padding: 4px 0;">Réalisé par :</td>
                        <td style="color: #1e293b; font-weight: 600; text-align: right;">{AUTEUR}</td>
                    </tr>
                    <tr>
                        <td style="color: #64748b; padding: 4px 0;">Domaine :</td>
                        <td style="color: #1e293b; font-weight: 600; text-align: right;">Recherche Opérationnelle</td>
                    </tr>
                </table>
            </div>
            
            <!-- Séparateur -->
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 15px 0;">
            
            <!-- Technologies -->
            <div style="margin: 10px 0;">
                <p style="color: #374151; font-weight: 600; margin-bottom: 8px; font-size: 12px;">
                    TECHNOLOGIES UTILISÉES
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                    <span style="background: #dbeafe; color: #1e40af; padding: 3px 10px; 
                           border-radius: 4px; font-size: 11px;">Python 3.8+</span>
                    <span style="background: #dcfce7; color: #166534; padding: 3px 10px; 
                           border-radius: 4px; font-size: 11px;">Gurobi Optimizer</span>
                    <span style="background: #fef3c7; color: #92400e; padding: 3px 10px; 
                           border-radius: 4px; font-size: 11px;">PyQt6</span>
                    <span style="background: #fce7f3; color: #9d174d; padding: 3px 10px; 
                           border-radius: 4px; font-size: 11px;">NumPy</span>
                    <span style="background: #e0e7ff; color: #3730a3; padding: 3px 10px; 
                           border-radius: 4px; font-size: 11px;">Matplotlib</span>
                </div>
            </div>
            
            <!-- Description -->
            <div style="margin-top: 15px; padding: 12px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                    border-radius: 8px; border-left: 3px solid #0284c7;">
                <p style="color: #0c4a6e; font-size: 11px; margin: 0; line-height: 1.5;">
                    <b>Description :</b> Application d'optimisation par programmation linéaire 
                    pour la gestion des flux d'approvisionnement inter-sites. 
                    Résolution exacte via le solveur Gurobi.
                </p>
            </div>
            
        </div>
        """
        
        msg.setText(contenu_html)
        msg.setMinimumWidth(420)
        msg.exec()
        logger.info("Fenêtre À propos affichée")
    
    def valider_donnees(self):
        """Valide les données saisies"""
        try:
            self.lire_donnees_depuis_tables()
            valide, erreurs = self.donnees.valider_donnees()
            
            if valide:
                QMessageBox.information(self, "Validation", "✓ Toutes les données sont valides!")
                self.ajouter_log("✓ Validation réussie")
            else:
                msg = "Erreurs détectées:\n\n" + "\n".join(f"• {err}" for err in erreurs)
                QMessageBox.warning(self, "Validation", msg)
                self.ajouter_log("✗ Erreurs de validation")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la validation:\n{str(e)}")
    
    def lire_donnees_depuis_tables(self):
        """Lit les données depuis les tables de l'interface"""
        if self.donnees is None:
            return
        
        d = self.donnees
        
        # Lire offre
        table_offre = self.table_offre.findChild(QTableWidget)
        for i in range(d.n_sites):
            for m in range(d.n_matieres):
                item = table_offre.item(i, m)
                if item:
                    d.offre[i, m] = float(item.text())
        
        # Lire demande
        table_demande = self.table_demande.findChild(QTableWidget)
        for i in range(d.n_sites):
            for m in range(d.n_matieres):
                item = table_demande.item(i, m)
                if item:
                    d.demande[i, m] = float(item.text())
        
        # Lire distances
        for i in range(d.n_sites):
            for j in range(d.n_sites):
                item = self.table_distance.item(i, j)
                if item:
                    d.distance[i, j] = float(item.text())
    
    def lancer_resolution(self):
        """Lance la résolution dans un thread séparé"""
        if self.donnees is None:
            QMessageBox.warning(self, "Attention", "Aucune donnée chargée!")
            return
        
        # Lire les données des tables
        self.lire_donnees_depuis_tables()
        
        # Valider
        valide, erreurs = self.donnees.valider_donnees()
        if not valide:
            QMessageBox.warning(self, "Données invalides", 
                               "Veuillez corriger les erreurs:\n" + "\n".join(erreurs))
            return
        
        # Créer le modèle
        self.modele = ModeleApprovisionnementPL(self.donnees)
        
        # Désactiver le bouton
        self.btn_resoudre.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        
        # Lancer le thread
        self.thread_resolution = ThreadResolution(self.modele)
        self.thread_resolution.progression.connect(self.ajouter_log)
        self.thread_resolution.termine.connect(self.resolution_terminee)
        self.thread_resolution.start()
        
        self.ajouter_log("="*50)
        self.ajouter_log("DÉBUT DE LA RÉSOLUTION")
        self.ajouter_log("="*50)
    
    def resolution_terminee(self, succes, message):
        """Appelé quand la résolution est terminée"""
        self.btn_resoudre.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.ajouter_log(message)
        
        if succes:
            self.ajouter_log(f"Temps de résolution: {self.modele.temps_resolution:.2f}s")
            self.ajouter_log(f"Coût optimal: {self.modele.resultats['valeur_optimale']:.2f} {UNITE_MONETAIRE}")
            self.afficher_resultats()
            QMessageBox.information(self, "Succès", "Solution optimale trouvée!")
            self.tabs.setCurrentIndex(3)  # Aller à l'onglet résultats
        else:
            QMessageBox.warning(self, "Échec", message)
    
    def afficher_resultats(self):
        """Affiche les résultats dans l'interface avec KPIs modernes"""
        if self.modele is None or not self.modele.resultats:
            return
        
        r = self.modele.resultats
        d = self.modele.donnees
        
        # ═══════════════════════════════════════════════════════════════
        # MISE À JOUR DES CARTES KPI
        # ═══════════════════════════════════════════════════════════════
        
        # Fonction helper pour mettre à jour une carte KPI
        def maj_kpi(carte, valeur_str, couleur=None):
            label = carte.findChild(QLabel, "valeur")
            if label:
                label.setText(valeur_str)
                if couleur:
                    label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {couleur};")
        
        # KPI Coût Total
        cout_formate = f"{r['valeur_optimale']:,.0f} {UNITE_MONETAIRE}".replace(",", " ")
        maj_kpi(self.kpi_cout, cout_formate, "#059669")
        
        # KPI Satisfaction
        satisfaction = r['taux_satisfaction'] * 100
        couleur_sat = "#059669" if satisfaction >= 95 else ("#f59e0b" if satisfaction >= 80 else "#ef4444")
        maj_kpi(self.kpi_satisfaction, f"{satisfaction:.1f}%", couleur_sat)
        
        # KPI Flux Total
        flux_formate = f"{r['volume_total']:,.0f} t".replace(",", " ")
        maj_kpi(self.kpi_flux, flux_formate, "#8b5cf6")
        
        # KPI Ruptures
        total_ruptures = sum(r['ruptures'].values()) if r['ruptures'] else 0
        couleur_rupt = "#059669" if total_ruptures == 0 else ("#f59e0b" if total_ruptures < 100 else "#ef4444")
        maj_kpi(self.kpi_ruptures, f"{total_ruptures:,.0f} t".replace(",", " "), couleur_rupt)
        
        # KPI Temps
        maj_kpi(self.kpi_temps, f"{self.modele.temps_resolution:.2f} s", "#06b6d4")
        
        # ═══════════════════════════════════════════════════════════════
        # RÉSUMÉ TEXTUEL
        # ═══════════════════════════════════════════════════════════════
        
        texte_resume = f"""
        <div style="font-size: 13px; line-height: 1.6;">
        <p><span style="color: #059669; font-size: 16px;">✓</span> <b>Solution optimale trouvée</b></p>
        <p><b>💰 Coût Total Optimisé:</b> <span style="color: #059669; font-weight: bold;">{r['valeur_optimale']:,.2f} DT</span></p>
        <p><b>⏱ Temps de calcul:</b> {self.modele.temps_resolution:.3f} secondes</p>
        <p><b>� Volume total transféré:</b> {r['volume_total']:,.1f} tonnes</p>
        <p><b>🔢 Nombre de transferts actifs:</b> {r['nb_transferts']} routes utilisées</p>
        <p><b>✅ Taux de satisfaction:</b> <span style="color: {couleur_sat}; font-weight: bold;">{satisfaction:.1f}%</span></p>
        </div>
        """
        self.label_resume.setText(texte_resume)
        
        # ═══════════════════════════════════════════════════════════════
        # TABLE DES FLUX
        # ═══════════════════════════════════════════════════════════════
        
        flux = r['flux']
        self.table_flux.setRowCount(len(flux))
        for idx, ((i, j, m), vol) in enumerate(sorted(flux.items(), key=lambda x: x[1], reverse=True)):
            self.table_flux.setItem(idx, 0, QTableWidgetItem(d.noms_sites[i]))
            self.table_flux.setItem(idx, 1, QTableWidgetItem(d.noms_sites[j]))
            self.table_flux.setItem(idx, 2, QTableWidgetItem(d.noms_matieres[m]))
            item_vol = QTableWidgetItem(f"{vol:.1f}")
            item_vol.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            # Colorer selon le volume
            if vol > 100:
                item_vol.setBackground(QColor("#dcfce7"))  # Vert clair pour gros flux
            self.table_flux.setItem(idx, 3, item_vol)
        
        # ═══════════════════════════════════════════════════════════════
        # TABLE DES RUPTURES
        # ═══════════════════════════════════════════════════════════════
        
        ruptures = r['ruptures']
        self.table_ruptures.setRowCount(len(ruptures))
        for idx, ((j, m), vol) in enumerate(ruptures.items()):
            self.table_ruptures.setItem(idx, 0, QTableWidgetItem(d.noms_sites[j]))
            self.table_ruptures.setItem(idx, 1, QTableWidgetItem(d.noms_matieres[m]))
            item_vol = QTableWidgetItem(f"{vol:.1f}")
            item_vol.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_vol.setBackground(QColor("#fee2e2"))  # Rouge clair
            item_vol.setForeground(QColor("#991b1b"))  # Texte rouge foncé
            self.table_ruptures.setItem(idx, 2, item_vol)
        
        # ═══════════════════════════════════════════════════════════════
        # TABLE DES STOCKS
        # ═══════════════════════════════════════════════════════════════
        
        stocks = r['stocks']
        self.table_stocks.setRowCount(len(stocks))
        for idx, ((i, m), vol) in enumerate(stocks.items()):
            self.table_stocks.setItem(idx, 0, QTableWidgetItem(d.noms_sites[i]))
            self.table_stocks.setItem(idx, 1, QTableWidgetItem(d.noms_matieres[m]))
            item_vol = QTableWidgetItem(f"{vol:.1f}")
            item_vol.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if vol > 0:
                item_vol.setBackground(QColor("#fef3c7"))  # Jaune clair
            self.table_stocks.setItem(idx, 2, item_vol)
        
        logger.info(f"✓ Résultats affichés: coût={r['valeur_optimale']:.2f}DT, satisfaction={satisfaction:.1f}%")
    
    def afficher_graphique(self, type_graphique):
        """Affiche un graphique"""
        if self.modele is None or not self.modele.resultats:
            QMessageBox.warning(self, "Attention", "Aucun résultat disponible!")
            return
        
        if type_graphique == 'flux':
            self.canvas.tracer_flux(self.modele.donnees, self.modele.resultats)
        elif type_graphique == 'couts':
            self.canvas.tracer_repartition_couts(self.modele)
    
    def ajouter_log(self, message):
        """Ajoute un message au journal"""
        self.text_log.append(message)
        self.text_log.verticalScrollBar().setValue(
            self.text_log.verticalScrollBar().maximum()
        )


def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Style moderne
    
    fenetre = FenetreApprovisionnement()
    fenetre.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
