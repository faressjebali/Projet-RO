"""
═══════════════════════════════════════════════════════════════════════════════
MODULE DE VISUALISATION AVANCÉE
OptiAppro v2.0 - Optimisation de l'Approvisionnement Inter-Sites

Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
═══════════════════════════════════════════════════════════════════════════════
Ce module fournit des visualisations avancées : heatmaps, graphes de flux
améliorés, diagrammes Sankey, et analyses visuelles des résultats.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt

try:
    import seaborn as sns
    SEABORN_DISPONIBLE = True
except ImportError:
    SEABORN_DISPONIBLE = False
    print("⚠️ Seaborn non disponible - heatmaps basiques utilisées")


# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE DE COULEURS PERSONNALISÉE
# ═══════════════════════════════════════════════════════════════════════════════

class PaletteVisualisations:
    """Palettes de couleurs pour les visualisations"""
    
    # Couleurs principales
    BLEU_PRINCIPAL = "#3b82f6"
    VERT_SUCCES = "#10b981"
    ORANGE_WARNING = "#f59e0b"
    ROUGE_ERREUR = "#ef4444"
    VIOLET = "#8b5cf6"
    ROSE = "#ec4899"
    
    # Gradient pour heatmaps
    GRADIENT_BLEU = ["#f0f9ff", "#bae6fd", "#38bdf8", "#0284c7", "#0369a1"]
    GRADIENT_VERT = ["#f0fdf4", "#bbf7d0", "#4ade80", "#22c55e", "#15803d"]
    GRADIENT_ORANGE = ["#fffbeb", "#fde68a", "#fbbf24", "#f59e0b", "#d97706"]
    GRADIENT_ROUGE_VERT = ["#ef4444", "#fbbf24", "#22c55e"]  # Rouge → Jaune → Vert
    
    # Couleurs pour les sites
    SITES = [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
        "#ec4899", "#06b6d4", "#84cc16", "#f97316", "#6366f1"
    ]
    
    @classmethod
    def creer_cmap_personnalise(cls, couleurs: list, nom: str = "custom"):
        """Crée une colormap personnalisée"""
        return LinearSegmentedColormap.from_list(nom, couleurs)


# ═══════════════════════════════════════════════════════════════════════════════
# WIDGET HEATMAP INTERACTIF
# ═══════════════════════════════════════════════════════════════════════════════

class HeatmapWidget(QWidget):
    """
    Widget heatmap interactif avec sélection du type de données
    
    Usage:
        heatmap = HeatmapWidget()
        heatmap.tracer_matrice(matrice, labels_x, labels_y, titre="Coûts")
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Contrôles
        controles = QHBoxLayout()
        
        label_palette = QLabel("Palette:")
        label_palette.setStyleSheet("font-weight: 600;")
        controles.addWidget(label_palette)
        
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(["Bleu", "Vert", "Orange", "Rouge-Vert", "Viridis"])
        self.combo_palette.currentTextChanged.connect(self._changer_palette)
        self.combo_palette.setMinimumWidth(120)
        controles.addWidget(self.combo_palette)
        
        controles.addStretch()
        layout.addLayout(controles)
        
        # Figure matplotlib
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Toolbar de navigation
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Données actuelles (pour redessiner)
        self._donnees_actuelles = None
        self._labels_x = None
        self._labels_y = None
        self._titre = None
    
    def _changer_palette(self, nom_palette: str):
        """Change la palette de couleurs et redessine"""
        if self._donnees_actuelles is not None:
            self.tracer_matrice(
                self._donnees_actuelles,
                self._labels_x,
                self._labels_y,
                self._titre
            )
    
    def _obtenir_cmap(self) -> str:
        """Retourne la colormap selon la sélection"""
        palette = self.combo_palette.currentText()
        if palette == "Bleu":
            return PaletteVisualisations.creer_cmap_personnalise(
                PaletteVisualisations.GRADIENT_BLEU, "bleu_custom"
            )
        elif palette == "Vert":
            return PaletteVisualisations.creer_cmap_personnalise(
                PaletteVisualisations.GRADIENT_VERT, "vert_custom"
            )
        elif palette == "Orange":
            return PaletteVisualisations.creer_cmap_personnalise(
                PaletteVisualisations.GRADIENT_ORANGE, "orange_custom"
            )
        elif palette == "Rouge-Vert":
            return PaletteVisualisations.creer_cmap_personnalise(
                PaletteVisualisations.GRADIENT_ROUGE_VERT, "rg_custom"
            )
        else:
            return "viridis"
    
    def tracer_matrice(self, matrice: np.ndarray, labels_x: list = None,
                       labels_y: list = None, titre: str = "Heatmap",
                       format_valeur: str = ".1f", afficher_valeurs: bool = True):
        """
        Trace une heatmap de la matrice
        
        Args:
            matrice: Matrice 2D numpy
            labels_x: Labels pour l'axe X
            labels_y: Labels pour l'axe Y
            titre: Titre du graphique
            format_valeur: Format d'affichage des valeurs
            afficher_valeurs: Afficher les valeurs dans les cellules
        """
        # Sauvegarder pour redessiner
        self._donnees_actuelles = matrice
        self._labels_x = labels_x
        self._labels_y = labels_y
        self._titre = titre
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        cmap = self._obtenir_cmap()
        
        if SEABORN_DISPONIBLE:
            # Heatmap avec Seaborn (plus joli)
            sns.heatmap(
                matrice,
                ax=ax,
                cmap=cmap,
                annot=afficher_valeurs,
                fmt=format_valeur,
                linewidths=0.5,
                linecolor='white',
                cbar_kws={'label': 'Valeur'},
                xticklabels=labels_x if labels_x else True,
                yticklabels=labels_y if labels_y else True,
                square=True
            )
        else:
            # Heatmap basique avec matplotlib
            im = ax.imshow(matrice, cmap=cmap, aspect='auto')
            self.figure.colorbar(im, ax=ax, label='Valeur')
            
            if afficher_valeurs:
                for i in range(matrice.shape[0]):
                    for j in range(matrice.shape[1]):
                        val = matrice[i, j]
                        couleur_texte = 'white' if val > matrice.max() / 2 else 'black'
                        ax.text(j, i, f'{val:{format_valeur}}',
                               ha='center', va='center', color=couleur_texte,
                               fontsize=9)
            
            if labels_x:
                ax.set_xticks(range(len(labels_x)))
                ax.set_xticklabels(labels_x)
            if labels_y:
                ax.set_yticks(range(len(labels_y)))
                ax.set_yticklabels(labels_y)
        
        ax.set_title(titre, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel("Destination", fontsize=11)
        ax.set_ylabel("Origine", fontsize=11)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def tracer_couts(self, donnees, matiere_index: int = 0):
        """Trace la heatmap des coûts pour une matière"""
        couts = donnees.cout_transport[:, :, matiere_index]
        labels = donnees.noms_sites
        self.tracer_matrice(
            couts, labels, labels,
            titre=f"Coûts de Transport - {donnees.noms_matieres[matiere_index]}",
            format_valeur=".1f"
        )
    
    def tracer_flux(self, donnees, resultats, matiere_index: int = 0):
        """Trace la heatmap des flux pour une matière"""
        n_sites = donnees.n_sites
        flux_matrice = np.zeros((n_sites, n_sites))
        
        for (i, j, m), vol in resultats.get('flux', {}).items():
            if m == matiere_index and vol > 0.1:
                flux_matrice[i, j] = vol
        
        labels = donnees.noms_sites
        self.tracer_matrice(
            flux_matrice, labels, labels,
            titre=f"Flux Optimaux - {donnees.noms_matieres[matiere_index]}",
            format_valeur=".0f"
        )
    
    def tracer_capacites(self, donnees):
        """Trace la heatmap des capacités de transfert"""
        labels = donnees.noms_sites
        self.tracer_matrice(
            donnees.capacite_transfert, labels, labels,
            titre="Capacités de Transfert (tonnes)",
            format_valeur=".0f"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPHE DE FLUX AMÉLIORÉ
# ═══════════════════════════════════════════════════════════════════════════════

class GrapheFluxAmeliore(QWidget):
    """
    Graphe de flux amélioré avec layout NetworkX-like et interactions
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Contrôles
        controles = QHBoxLayout()
        
        label_layout = QLabel("Layout:")
        label_layout.setStyleSheet("font-weight: 600;")
        controles.addWidget(label_layout)
        
        self.combo_layout = QComboBox()
        self.combo_layout.addItems(["Circulaire", "Grille", "Hiérarchique"])
        self.combo_layout.currentTextChanged.connect(self._changer_layout)
        controles.addWidget(self.combo_layout)
        
        controles.addStretch()
        layout.addLayout(controles)
        
        # Figure
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        self._donnees = None
        self._resultats = None
    
    def _changer_layout(self, nom_layout: str):
        """Change le layout et redessine"""
        if self._donnees is not None and self._resultats is not None:
            self.tracer(self._donnees, self._resultats)
    
    def _calculer_positions(self, n_sites: int) -> dict:
        """Calcule les positions des sites selon le layout choisi"""
        layout_type = self.combo_layout.currentText()
        positions = {}
        
        if layout_type == "Circulaire":
            angles = np.linspace(0, 2 * np.pi, n_sites, endpoint=False)
            for i, angle in enumerate(angles):
                positions[i] = (np.cos(angle), np.sin(angle))
        
        elif layout_type == "Grille":
            cols = int(np.ceil(np.sqrt(n_sites)))
            for i in range(n_sites):
                row = i // cols
                col = i % cols
                positions[i] = (col * 2 - (cols - 1), -(row * 2 - (n_sites // cols) / 2))
            # Normaliser
            if positions:
                max_x = max(p[0] for p in positions.values())
                max_y = max(abs(p[1]) for p in positions.values())
                scale = max(max_x, max_y) if max(max_x, max_y) > 0 else 1
                positions = {k: (v[0] / scale, v[1] / scale) for k, v in positions.items()}
        
        elif layout_type == "Hiérarchique":
            # Sites en niveaux
            niveau_1 = n_sites // 2
            niveau_2 = n_sites - niveau_1
            
            for i in range(niveau_1):
                x = (i - (niveau_1 - 1) / 2) * 0.5
                positions[i] = (x, 0.5)
            
            for i in range(niveau_2):
                x = (i - (niveau_2 - 1) / 2) * 0.5
                positions[niveau_1 + i] = (x, -0.5)
        
        return positions
    
    def tracer(self, donnees, resultats):
        """
        Trace le graphe de flux amélioré
        
        Args:
            donnees: Données du modèle
            resultats: Résultats de l'optimisation
        """
        self._donnees = donnees
        self._resultats = resultats
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        n_sites = donnees.n_sites
        flux_totaux = resultats.get('flux_totaux', {})
        
        # Calculer positions
        positions = self._calculer_positions(n_sites)
        
        # Couleurs des sites
        couleurs_sites = PaletteVisualisations.SITES[:n_sites]
        
        # Calculer l'offre/demande totale par site pour la taille
        offre_totale = np.sum(donnees.offre, axis=1)
        demande_totale = np.sum(donnees.demande, axis=1)
        volumes_sites = offre_totale + demande_totale
        tailles_sites = 200 + 600 * (volumes_sites / max(volumes_sites)) if max(volumes_sites) > 0 else [400] * n_sites
        
        # Tracer les flux (arcs)
        if flux_totaux:
            flux_max = max(flux_totaux.values()) if flux_totaux.values() else 1
            
            for (i, j), volume in flux_totaux.items():
                if volume > 0.1:
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    
                    # Épaisseur proportionnelle
                    width = 1 + 8 * (volume / flux_max)
                    alpha = 0.4 + 0.5 * (volume / flux_max)
                    
                    # Couleur gradient
                    couleur = couleurs_sites[i]
                    
                    # Flèche courbe
                    style = "arc3,rad=0.15"
                    arrow = FancyArrowPatch(
                        (x1, y1), (x2, y2),
                        connectionstyle=style,
                        arrowstyle=f"->,head_length=10,head_width=6",
                        linewidth=width,
                        color=couleur,
                        alpha=alpha,
                        zorder=1
                    )
                    ax.add_patch(arrow)
                    
                    # Label du volume (au milieu de l'arc)
                    mx = (x1 + x2) / 2 + 0.1 * (y2 - y1)
                    my = (y1 + y2) / 2 - 0.1 * (x2 - x1)
                    ax.annotate(
                        f'{volume:.0f}t',
                        (mx, my),
                        fontsize=8,
                        fontweight='bold',
                        color='#1e293b',
                        ha='center',
                        va='center',
                        bbox=dict(
                            boxstyle='round,pad=0.3',
                            facecolor='white',
                            edgecolor='#cbd5e1',
                            alpha=0.9
                        ),
                        zorder=5
                    )
        
        # Tracer les sites (nœuds)
        for i in range(n_sites):
            x, y = positions[i]
            
            # Cercle extérieur (ombre)
            cercle_ombre = Circle((x + 0.02, y - 0.02), 0.12,
                                  color='#00000020', zorder=8)
            ax.add_patch(cercle_ombre)
            
            # Cercle principal
            cercle = Circle((x, y), 0.12, color=couleurs_sites[i], zorder=10)
            ax.add_patch(cercle)
            
            # Nom du site
            ax.text(x, y, donnees.noms_sites[i],
                   ha='center', va='center',
                   fontsize=10, fontweight='bold',
                   color='white', zorder=11)
            
            # Info sous le site
            info = f"O:{offre_totale[i]:.0f} | D:{demande_totale[i]:.0f}"
            ax.text(x, y - 0.22, info,
                   ha='center', va='top',
                   fontsize=8, color='#64748b', zorder=11)
        
        # Configuration des axes
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Titre avec métrique
        flux_total = sum(flux_totaux.values()) if flux_totaux else 0
        ax.set_title(
            f'Réseau de Flux Optimisés\nFlux total: {flux_total:,.0f} tonnes',
            fontsize=14, fontweight='bold', pad=20
        )
        
        # Légende
        legend_elements = [
            mpatches.Patch(color=couleurs_sites[i], label=f"{donnees.noms_sites[i]}")
            for i in range(min(n_sites, 6))
        ]
        ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9)
        
        self.figure.tight_layout()
        self.canvas.draw()


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPHIQUES DE RÉPARTITION AMÉLIORÉS
# ═══════════════════════════════════════════════════════════════════════════════

class GraphiquesRepartition(QWidget):
    """
    Ensemble de graphiques de répartition (camembert, barres, etc.)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Sélection du type de graphique
        controles = QHBoxLayout()
        
        label = QLabel("Type de graphique:")
        label.setStyleSheet("font-weight: 600;")
        controles.addWidget(label)
        
        self.combo_type = QComboBox()
        self.combo_type.addItems([
            "Répartition des coûts",
            "Flux par matière",
            "Flux par site d'origine",
            "Satisfaction par site"
        ])
        self.combo_type.currentTextChanged.connect(self._changer_graphique)
        controles.addWidget(self.combo_type)
        
        controles.addStretch()
        layout.addLayout(controles)
        
        # Figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        self._modele = None
    
    def _changer_graphique(self, nom: str):
        """Change le type de graphique"""
        if self._modele is not None:
            self.tracer(self._modele)
    
    def tracer(self, modele):
        """
        Trace le graphique sélectionné
        
        Args:
            modele: Modèle avec données et résultats
        """
        self._modele = modele
        type_graph = self.combo_type.currentText()
        
        self.figure.clear()
        
        if type_graph == "Répartition des coûts":
            self._tracer_repartition_couts(modele)
        elif type_graph == "Flux par matière":
            self._tracer_flux_par_matiere(modele)
        elif type_graph == "Flux par site d'origine":
            self._tracer_flux_par_site(modele)
        elif type_graph == "Satisfaction par site":
            self._tracer_satisfaction_par_site(modele)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _tracer_repartition_couts(self, modele):
        """Camembert des coûts"""
        ax = self.figure.add_subplot(111)
        
        d = modele.donnees
        r = modele.resultats
        
        # Calculer les composantes
        cout_transport = sum(
            d.cout_transport[i, j, m] * vol
            for (i, j, m), vol in r['flux'].items()
        )
        
        cout_km = sum(
            d.cout_kilometrique * d.distance[i, j] * vol
            for (i, j), vol in r['flux_totaux'].items()
        )
        
        cout_stock = sum(
            d.cout_stockage[i, m] * vol
            for (i, m), vol in r['stocks'].items()
        )
        
        cout_rupture = sum(
            d.penalite_rupture[j, m] * vol
            for (j, m), vol in r['ruptures'].items()
        )
        
        # Données
        labels = ['Transport direct', 'Kilométrique', 'Stockage', 'Ruptures']
        sizes = [cout_transport, cout_km, cout_stock, cout_rupture]
        colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']
        explode = [0.02, 0.02, 0.02, 0.08 if cout_rupture > 0 else 0.02]
        
        # Filtrer les zéros
        data = [(l, s, c, e) for l, s, c, e in zip(labels, sizes, colors, explode) if s > 0]
        if data:
            labels, sizes, colors, explode = zip(*data)
            
            wedges, texts, autotexts = ax.pie(
                sizes,
                explode=explode,
                labels=labels,
                colors=colors,
                autopct=lambda p: f'{p:.1f}%\n({p*sum(sizes)/100:,.0f}€)',
                startangle=90,
                textprops={'fontsize': 10},
                wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
            )
            
            for autotext in autotexts:
                autotext.set_fontweight('bold')
        
        ax.set_title('Répartition des Coûts Totaux', fontsize=14, fontweight='bold')
    
    def _tracer_flux_par_matiere(self, modele):
        """Barres horizontales des flux par matière"""
        ax = self.figure.add_subplot(111)
        
        d = modele.donnees
        r = modele.resultats
        
        # Calculer flux par matière
        flux_matieres = np.zeros(d.n_matieres)
        for (i, j, m), vol in r['flux'].items():
            flux_matieres[m] += vol
        
        # Barres horizontales
        y_pos = np.arange(d.n_matieres)
        colors = [PaletteVisualisations.SITES[i % len(PaletteVisualisations.SITES)] 
                  for i in range(d.n_matieres)]
        
        bars = ax.barh(y_pos, flux_matieres, color=colors, height=0.6, edgecolor='white', linewidth=2)
        
        # Valeurs sur les barres
        for bar, val in zip(bars, flux_matieres):
            ax.text(bar.get_width() + max(flux_matieres) * 0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:,.0f} t', va='center', fontweight='bold', fontsize=10)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(d.noms_matieres)
        ax.set_xlabel('Volume transporté (tonnes)', fontsize=11)
        ax.set_title('Flux par Matière Première', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def _tracer_flux_par_site(self, modele):
        """Barres groupées des flux par site (envoyé/reçu)"""
        ax = self.figure.add_subplot(111)
        
        d = modele.donnees
        r = modele.resultats
        
        # Calculer flux sortants et entrants par site
        flux_sortants = np.zeros(d.n_sites)
        flux_entrants = np.zeros(d.n_sites)
        
        for (i, j), vol in r['flux_totaux'].items():
            flux_sortants[i] += vol
            flux_entrants[j] += vol
        
        x = np.arange(d.n_sites)
        width = 0.35
        
        bars1 = ax.bar(x - width/2, flux_sortants, width, label='Flux sortants',
                       color='#3b82f6', edgecolor='white', linewidth=2)
        bars2 = ax.bar(x + width/2, flux_entrants, width, label='Flux entrants',
                       color='#10b981', edgecolor='white', linewidth=2)
        
        ax.set_xticks(x)
        ax.set_xticklabels(d.noms_sites)
        ax.set_ylabel('Volume (tonnes)', fontsize=11)
        ax.set_title('Flux par Site', fontsize=14, fontweight='bold')
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def _tracer_satisfaction_par_site(self, modele):
        """Barres de satisfaction par site avec seuils colorés"""
        ax = self.figure.add_subplot(111)
        
        d = modele.donnees
        r = modele.resultats
        
        # Calculer satisfaction par site
        demande_site = np.sum(d.demande, axis=1)
        rupture_site = np.zeros(d.n_sites)
        
        for (j, m), vol in r['ruptures'].items():
            rupture_site[j] += vol
        
        satisfaction = np.where(
            demande_site > 0,
            100 * (1 - rupture_site / demande_site),
            100
        )
        
        x = np.arange(d.n_sites)
        
        # Couleurs selon le niveau de satisfaction
        colors = []
        for sat in satisfaction:
            if sat >= 95:
                colors.append('#10b981')
            elif sat >= 80:
                colors.append('#f59e0b')
            else:
                colors.append('#ef4444')
        
        bars = ax.bar(x, satisfaction, color=colors, edgecolor='white', linewidth=2)
        
        # Ligne de seuil
        ax.axhline(y=95, color='#10b981', linestyle='--', linewidth=1.5, label='Excellent (95%)')
        ax.axhline(y=80, color='#f59e0b', linestyle='--', linewidth=1.5, label='Acceptable (80%)')
        
        # Valeurs sur les barres
        for bar, sat in zip(bars, satisfaction):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{sat:.1f}%', ha='center', fontweight='bold', fontsize=10)
        
        ax.set_xticks(x)
        ax.set_xticklabels(d.noms_sites)
        ax.set_ylabel('Taux de satisfaction (%)', fontsize=11)
        ax.set_ylim(0, 110)
        ax.set_title('Satisfaction de la Demande par Site', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARAISON OFFRE/DEMANDE
# ═══════════════════════════════════════════════════════════════════════════════

class GraphiqueOffreDemande(QWidget):
    """Graphique comparatif offre/demande par site et matière"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Figure
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
    
    def tracer(self, donnees):
        """
        Trace le graphique comparatif offre/demande
        
        Args:
            donnees: Données du modèle
        """
        self.figure.clear()
        
        n_sites = donnees.n_sites
        n_matieres = donnees.n_matieres
        
        # Créer sous-graphiques
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # 1. Offre vs Demande par site
        offre_site = np.sum(donnees.offre, axis=1)
        demande_site = np.sum(donnees.demande, axis=1)
        
        x = np.arange(n_sites)
        width = 0.35
        
        ax1.bar(x - width/2, offre_site, width, label='Offre', color='#3b82f6')
        ax1.bar(x + width/2, demande_site, width, label='Demande', color='#ef4444')
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(donnees.noms_sites)
        ax1.set_ylabel('Volume (tonnes)')
        ax1.set_title('Offre vs Demande par Site', fontweight='bold')
        ax1.legend()
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # 2. Offre vs Demande par matière
        offre_matiere = np.sum(donnees.offre, axis=0)
        demande_matiere = np.sum(donnees.demande, axis=0)
        
        x = np.arange(n_matieres)
        
        ax2.bar(x - width/2, offre_matiere, width, label='Offre', color='#3b82f6')
        ax2.bar(x + width/2, demande_matiere, width, label='Demande', color='#ef4444')
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(donnees.noms_matieres)
        ax2.set_ylabel('Volume (tonnes)')
        ax2.set_title('Offre vs Demande par Matière', fontweight='bold')
        ax2.legend()
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        self.figure.tight_layout()
        self.canvas.draw()


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'PaletteVisualisations',
    'HeatmapWidget',
    'GrapheFluxAmeliore',
    'GraphiquesRepartition',
    'GraphiqueOffreDemande'
]
