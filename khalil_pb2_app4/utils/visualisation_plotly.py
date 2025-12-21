"""
═══════════════════════════════════════════════════════════════════════════════
MODULE DE VISUALISATION INTERACTIVE AVANCÉE
OptiAppro v2.1.0 - Optimisation de l'Approvisionnement Inter-Sites

INSAT - Année universitaire 2025-2026
Réalisé par: Khalil Chikhaoui
═══════════════════════════════════════════════════════════════════════════════

Ce module fournit des visualisations interactives de niveau publication :
- Graphe de flux avec Plotly (courbes de Bézier, interactivité)
- Layouts optimisés (Kamada-Kawai, Spring, Circulaire)
- Export haute qualité (HTML interactif, PNG/SVG HD)

Dépendances:
    - plotly >= 5.0.0
    - networkx >= 2.6
    - numpy >= 1.20.0
    - scipy >= 1.7.0 (pour Kamada-Kawai)

Complexité algorithmique:
    - Layout Kamada-Kawai: O(n³) où n = nombre de sites
    - Layout Spring: O(n² × iterations)
    - Rendu Plotly: O(n + e) où e = nombre d'arêtes
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS AVEC GESTION DES DÉPENDANCES OPTIONNELLES
# ═══════════════════════════════════════════════════════════════════════════════

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_DISPONIBLE = True
except ImportError:
    PLOTLY_DISPONIBLE = False
    logger.warning("⚠️ Plotly non installé. Installez avec: pip install plotly")

try:
    import networkx as nx
    NETWORKX_DISPONIBLE = True
except ImportError:
    NETWORKX_DISPONIBLE = False
    logger.warning("⚠️ NetworkX non installé. Installez avec: pip install networkx")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION ET TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class LayoutType(Enum):
    """Types de layouts disponibles pour le graphe"""
    KAMADA_KAWAI = "kamada_kawai"      # Minimise l'énergie du système ressort
    SPRING = "spring"                   # Force-directed layout
    CIRCULAR = "circular"               # Disposition circulaire
    HIERARCHICAL = "hierarchical"       # Disposition en niveaux
    SPECTRAL = "spectral"               # Basé sur les valeurs propres


@dataclass
class ConfigurationVisualisation:
    """
    Configuration complète pour la visualisation du graphe de flux.
    
    Tous les paramètres sont documentés et ajustables pour personnaliser
    l'apparence et le comportement de la visualisation.
    
    Attributes:
        layout_type: Algorithme de placement des nœuds
        layout_iterations: Nombre d'itérations pour layouts itératifs
        layout_k: Paramètre de répulsion pour spring layout
        node_size_min/max: Taille des nœuds (proportionnelle au volume)
        edge_width_min/max: Épaisseur des arêtes (proportionnelle au flux)
        edge_curvature: Courbure des arêtes (0=droite, 0.3=courbée)
        colorscale: Échelle de couleurs pour l'intensité des flux
        show_edge_labels: Afficher les volumes sur les arêtes
        show_node_info: Afficher offre/demande sous les nœuds
        title: Titre du graphique
        width/height: Dimensions en pixels
        export_dpi: Résolution pour export image
    """
    # Layout
    layout_type: LayoutType = LayoutType.KAMADA_KAWAI
    layout_iterations: int = 500
    layout_k: float = 2.0
    layout_seed: int = 42
    
    # Nœuds
    node_size_min: int = 30
    node_size_max: int = 80
    node_color_palette: List[str] = field(default_factory=lambda: [
        "#3b82f6",  # Bleu
        "#10b981",  # Vert
        "#f59e0b",  # Orange
        "#ef4444",  # Rouge
        "#8b5cf6",  # Violet
        "#ec4899",  # Rose
        "#06b6d4",  # Cyan
        "#84cc16",  # Lime
        "#f97316",  # Orange foncé
        "#6366f1",  # Indigo
    ])
    node_border_width: int = 2
    node_border_color: str = "#ffffff"
    
    # Arêtes
    edge_width_min: float = 1.0
    edge_width_max: float = 12.0
    edge_curvature: float = 0.2
    edge_opacity_min: float = 0.4
    edge_opacity_max: float = 0.9
    colorscale: str = "Viridis"  # ou "RdYlGn", "Blues", "Plasma"
    show_edge_labels: bool = True
    edge_label_font_size: int = 10
    
    # Nœuds - Info
    show_node_info: bool = True
    node_label_font_size: int = 12
    node_info_font_size: int = 9
    
    # Figure
    title: str = "Réseau de Flux Optimisés"
    width: int = 1200
    height: int = 800
    background_color: str = "#fafafa"
    margin: Dict[str, int] = field(default_factory=lambda: {
        "l": 50, "r": 50, "t": 80, "b": 50
    })
    
    # Export
    export_dpi: int = 300
    export_format: str = "html"  # html, png, svg, pdf


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPALE DE VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════════

class VisualisateurFluxInteractif:
    """
    Générateur de visualisations interactives pour les flux d'approvisionnement.
    
    Cette classe crée des graphiques de réseau de qualité publication avec :
    - Placement intelligent des nœuds (algorithmes de layout)
    - Arêtes courbées évitant les superpositions
    - Couleurs proportionnelles à l'intensité des flux
    - Interactivité (zoom, pan, infobulles)
    - Export haute qualité
    
    Example:
        >>> donnees = ModeleDonneesApprovisionnement(5, 3)
        >>> donnees.generer_donnees_exemple()
        >>> resultats = {...}  # Résultats de l'optimisation
        >>> 
        >>> viz = VisualisateurFluxInteractif(donnees, resultats)
        >>> fig = viz.creer_graphe_flux()
        >>> fig.show()  # Affichage interactif
        >>> viz.exporter("mon_graphe", format="html")
    
    Attributes:
        donnees: Données du problème d'optimisation
        resultats: Résultats de la résolution
        config: Configuration de la visualisation
        positions: Positions calculées des nœuds
    """
    
    def __init__(
        self,
        donnees: Any,  # ModeleDonneesApprovisionnement
        resultats: Dict[str, Any],
        config: Optional[ConfigurationVisualisation] = None
    ) -> None:
        """
        Initialise le visualisateur.
        
        Args:
            donnees: Instance de ModeleDonneesApprovisionnement
            resultats: Dictionnaire des résultats d'optimisation
            config: Configuration optionnelle (défaut si None)
        
        Raises:
            ImportError: Si Plotly ou NetworkX non installés
        """
        if not PLOTLY_DISPONIBLE:
            raise ImportError(
                "Plotly requis pour la visualisation interactive. "
                "Installez avec: pip install plotly"
            )
        
        self.donnees = donnees
        self.resultats = resultats
        self.config = config or ConfigurationVisualisation()
        self.positions: Dict[int, Tuple[float, float]] = {}
        self._figure: Optional[go.Figure] = None
        
        # Pré-calcul des métriques
        self._calculer_metriques()
    
    def _calculer_metriques(self) -> None:
        """
        Pré-calcule les métriques nécessaires pour la visualisation.
        
        Calcule:
        - Volume total traité par site (offre + demande)
        - Flux maximum et minimum
        - Statistiques pour la normalisation
        """
        d = self.donnees
        r = self.resultats
        
        # Volume traité par site
        self.volumes_sites = np.sum(d.offre, axis=1) + np.sum(d.demande, axis=1)
        self.volume_max = max(self.volumes_sites) if max(self.volumes_sites) > 0 else 1
        
        # Flux
        flux_totaux = r.get('flux_totaux', {})
        self.flux_values = list(flux_totaux.values()) if flux_totaux else [0]
        self.flux_max = max(self.flux_values) if self.flux_values else 1
        self.flux_min = min(self.flux_values) if self.flux_values else 0
        self.flux_total = sum(self.flux_values)
        
        logger.debug(f"Métriques: {d.n_sites} sites, flux max={self.flux_max:.1f}")
    
    def _calculer_positions(self) -> Dict[int, Tuple[float, float]]:
        """
        Calcule les positions optimales des nœuds selon l'algorithme choisi.
        
        Returns:
            Dictionnaire {site_id: (x, y)} avec positions normalisées [-1, 1]
        
        Note:
            - Kamada-Kawai: O(n³), optimal pour graphes moyens
            - Spring: O(n² × iterations), bon pour grands graphes
            - Circulaire: O(n), positions déterministes
        """
        n = self.donnees.n_sites
        layout_type = self.config.layout_type
        
        if NETWORKX_DISPONIBLE and layout_type in [
            LayoutType.KAMADA_KAWAI, LayoutType.SPRING, LayoutType.SPECTRAL
        ]:
            return self._calculer_positions_networkx()
        else:
            return self._calculer_positions_basiques()
    
    def _calculer_positions_networkx(self) -> Dict[int, Tuple[float, float]]:
        """
        Calcule les positions avec les algorithmes NetworkX avancés.
        
        Utilise la matrice de distances comme poids pour un placement
        plus réaliste (sites proches géographiquement = proches visuellement).
        """
        n = self.donnees.n_sites
        G = nx.Graph()
        
        # Ajouter les nœuds
        G.add_nodes_from(range(n))
        
        # Ajouter les arêtes avec poids (inverse de la distance)
        for i in range(n):
            for j in range(i + 1, n):
                dist = self.donnees.distance[i, j]
                if dist > 0:
                    # Poids inversé : distance faible = attraction forte
                    weight = 1.0 / (dist + 1)
                    G.add_edge(i, j, weight=weight)
        
        # Calculer le layout
        layout_type = self.config.layout_type
        seed = self.config.layout_seed
        
        try:
            if layout_type == LayoutType.KAMADA_KAWAI:
                # Kamada-Kawai : minimise l'énergie du système
                # Complexité: O(n³)
                pos = nx.kamada_kawai_layout(G, scale=1.0)
            
            elif layout_type == LayoutType.SPRING:
                # Spring layout (Fruchterman-Reingold)
                # Complexité: O(n² × iterations)
                pos = nx.spring_layout(
                    G,
                    k=self.config.layout_k / np.sqrt(n),
                    iterations=self.config.layout_iterations,
                    seed=seed,
                    scale=1.0
                )
            
            elif layout_type == LayoutType.SPECTRAL:
                # Spectral layout : basé sur les valeurs propres
                # Complexité: O(n³) pour décomposition
                pos = nx.spectral_layout(G, scale=1.0)
            
            else:
                pos = nx.circular_layout(G, scale=1.0)
            
            # Convertir en dictionnaire
            return {i: (pos[i][0], pos[i][1]) for i in range(n)}
        
        except Exception as e:
            logger.warning(f"Erreur layout NetworkX: {e}. Fallback circulaire.")
            return self._calculer_positions_basiques()
    
    def _calculer_positions_basiques(self) -> Dict[int, Tuple[float, float]]:
        """
        Calcule les positions avec des algorithmes basiques (sans NetworkX).
        
        Implémente :
        - Circulaire : positions sur un cercle
        - Hiérarchique : disposition en niveaux
        """
        n = self.donnees.n_sites
        layout_type = self.config.layout_type
        
        if layout_type == LayoutType.HIERARCHICAL:
            # Disposition en 2 niveaux : producteurs en haut, consommateurs en bas
            positions = {}
            offre_totale = np.sum(self.donnees.offre, axis=1)
            demande_totale = np.sum(self.donnees.demande, axis=1)
            
            # Classer les sites par ratio offre/demande
            ratios = []
            for i in range(n):
                if demande_totale[i] > 0:
                    ratio = offre_totale[i] / demande_totale[i]
                else:
                    ratio = float('inf') if offre_totale[i] > 0 else 1.0
                ratios.append((i, ratio))
            
            ratios.sort(key=lambda x: x[1], reverse=True)
            
            # Niveau supérieur : sites à forte offre
            n_top = (n + 1) // 2
            for idx, (i, _) in enumerate(ratios[:n_top]):
                x = (idx - (n_top - 1) / 2) * (2.0 / max(n_top - 1, 1))
                positions[i] = (x * 0.8, 0.6)
            
            # Niveau inférieur : sites à forte demande
            n_bottom = n - n_top
            for idx, (i, _) in enumerate(ratios[n_top:]):
                x = (idx - (n_bottom - 1) / 2) * (2.0 / max(n_bottom - 1, 1))
                positions[i] = (x * 0.8, -0.6)
            
            return positions
        
        else:
            # Layout circulaire par défaut
            positions = {}
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
            # Rotation pour avoir le premier site en haut
            angles = angles - np.pi / 2
            
            for i, angle in enumerate(angles):
                positions[i] = (np.cos(angle) * 0.85, np.sin(angle) * 0.85)
            
            return positions
    
    def _generer_courbe_bezier(
        self,
        x0: float, y0: float,
        x1: float, y1: float,
        courbure: float = 0.2,
        n_points: int = 50
    ) -> Tuple[List[float], List[float]]:
        """
        Génère une courbe de Bézier quadratique entre deux points.
        
        Args:
            x0, y0: Point de départ
            x1, y1: Point d'arrivée
            courbure: Facteur de courbure (0 = ligne droite)
            n_points: Nombre de points pour la courbe
        
        Returns:
            Tuple (liste_x, liste_y) des points de la courbe
        
        Note:
            La courbure est perpendiculaire à la droite source-destination,
            ce qui permet de séparer visuellement les flux bidirectionnels.
        """
        # Vecteur direction
        dx = x1 - x0
        dy = y1 - y0
        
        # Point de contrôle perpendiculaire au milieu
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        
        # Perpendiculaire normalisée
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            nx_perp = -dy / length
            ny_perp = dx / length
        else:
            nx_perp, ny_perp = 0, 0
        
        # Point de contrôle décalé
        cx = mx + courbure * length * nx_perp
        cy = my + courbure * length * ny_perp
        
        # Génération de la courbe de Bézier quadratique
        t = np.linspace(0, 1, n_points)
        x_bezier = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
        y_bezier = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
        
        return x_bezier.tolist(), y_bezier.tolist()
    
    def _couleur_flux(self, valeur: float) -> str:
        """
        Calcule la couleur d'un flux selon son intensité.
        
        Args:
            valeur: Volume du flux
        
        Returns:
            Couleur au format "rgba(r,g,b,a)"
        
        Note:
            Utilise un gradient du bleu (faible) au rouge (fort)
            pour une lecture intuitive de l'intensité.
        """
        if self.flux_max == self.flux_min:
            ratio = 0.5
        else:
            ratio = (valeur - self.flux_min) / (self.flux_max - self.flux_min)
        
        # Gradient Bleu → Jaune → Rouge
        if ratio < 0.5:
            # Bleu vers Jaune
            r = int(59 + (250 - 59) * (ratio * 2))
            g = int(130 + (200 - 130) * (ratio * 2))
            b = int(246 - 246 * (ratio * 2))
        else:
            # Jaune vers Rouge
            r = int(250 + (239 - 250) * ((ratio - 0.5) * 2))
            g = int(200 - 132 * ((ratio - 0.5) * 2))
            b = int(0 + 68 * ((ratio - 0.5) * 2))
        
        # Opacité proportionnelle
        opacity = self.config.edge_opacity_min + (
            self.config.edge_opacity_max - self.config.edge_opacity_min
        ) * ratio
        
        return f"rgba({r},{g},{b},{opacity:.2f})"
    
    def creer_graphe_flux(self) -> go.Figure:
        """
        Crée le graphique interactif complet du réseau de flux.
        
        Returns:
            Figure Plotly interactive
        
        Cette méthode :
        1. Calcule les positions optimales des nœuds
        2. Génère les arêtes courbées avec couleurs par intensité
        3. Ajoute les nœuds avec taille proportionnelle au volume
        4. Configure les infobulles interactives
        5. Ajoute la légende et le titre
        """
        # Calculer les positions
        self.positions = self._calculer_positions()
        
        # Créer la figure
        fig = go.Figure()
        
        # 1. Ajouter les arêtes (flux)
        self._ajouter_aretes(fig)
        
        # 2. Ajouter les nœuds (sites)
        self._ajouter_noeuds(fig)
        
        # 3. Ajouter la barre de couleur (légende flux)
        self._ajouter_legende_couleur(fig)
        
        # 4. Configuration du layout
        self._configurer_layout(fig)
        
        self._figure = fig
        return fig
    
    def _ajouter_aretes(self, fig: go.Figure) -> None:
        """
        Ajoute les arêtes (flux) au graphique.
        
        Chaque flux est représenté par :
        - Une courbe de Bézier (évite les superpositions)
        - Une couleur proportionnelle à l'intensité
        - Une épaisseur proportionnelle au volume
        - Une infobulle détaillée
        """
        flux_totaux = self.resultats.get('flux_totaux', {})
        flux_details = self.resultats.get('flux', {})
        d = self.donnees
        
        if not flux_totaux:
            return
        
        # Trier par volume pour dessiner les gros flux au-dessus
        flux_tries = sorted(flux_totaux.items(), key=lambda x: x[1])
        
        for (i, j), volume in flux_tries:
            if volume < 0.1:
                continue
            
            x0, y0 = self.positions[i]
            x1, y1 = self.positions[j]
            
            # Générer la courbe de Bézier
            # Courbure positive ou négative selon le sens pour éviter superposition
            courbure = self.config.edge_curvature
            if i > j:
                courbure = -courbure
            
            x_bezier, y_bezier = self._generer_courbe_bezier(
                x0, y0, x1, y1,
                courbure=courbure
            )
            
            # Épaisseur proportionnelle
            width = self.config.edge_width_min + (
                self.config.edge_width_max - self.config.edge_width_min
            ) * (volume / self.flux_max)
            
            # Couleur
            color = self._couleur_flux(volume)
            
            # Créer le détail des matières pour l'infobulle
            matieres_detail = []
            for (fi, fj, fm), vol in flux_details.items():
                if fi == i and fj == j and vol > 0.1:
                    matieres_detail.append(f"  • {d.noms_matieres[fm]}: {vol:.1f} t")
            detail_str = "<br>".join(matieres_detail) if matieres_detail else "  (détails non disponibles)"
            
            # Coût estimé
            cout_direct = sum(
                d.cout_transport[i, j, m] * flux_details.get((i, j, m), 0)
                for m in d.matieres
            )
            cout_km = d.cout_kilometrique * d.distance[i, j] * volume
            
            # Infobulle riche
            hovertext = (
                f"<b>Flux: {d.noms_sites[i]} → {d.noms_sites[j]}</b><br>"
                f"━━━━━━━━━━━━━━━━━<br>"
                f"<b>Volume total:</b> {volume:.1f} tonnes<br>"
                f"<b>Distance:</b> {d.distance[i, j]:.0f} km<br>"
                f"<b>Coût transport:</b> {cout_direct:.1f} DT<br>"
                f"<b>Coût kilométrique:</b> {cout_km:.1f} DT<br>"
                f"━━━━━━━━━━━━━━━━━<br>"
                f"<b>Détail par matière:</b><br>{detail_str}"
            )
            
            # Trace de l'arête
            fig.add_trace(go.Scatter(
                x=x_bezier,
                y=y_bezier,
                mode='lines',
                line=dict(width=width, color=color),
                hoverinfo='text',
                hovertext=hovertext,
                showlegend=False,
                name=f"{d.noms_sites[i]}→{d.noms_sites[j]}"
            ))
            
            # Label du volume (optionnel)
            if self.config.show_edge_labels and volume > self.flux_max * 0.1:
                # Position au milieu de la courbe
                mid_idx = len(x_bezier) // 2
                
                fig.add_trace(go.Scatter(
                    x=[x_bezier[mid_idx]],
                    y=[y_bezier[mid_idx]],
                    mode='text',
                    text=[f"{volume:.0f}t"],
                    textposition='middle center',
                    textfont=dict(
                        size=self.config.edge_label_font_size,
                        color='#1e293b',
                        family='Arial Black'
                    ),
                    hoverinfo='skip',
                    showlegend=False
                ))
    
    def _ajouter_noeuds(self, fig: go.Figure) -> None:
        """
        Ajoute les nœuds (sites) au graphique.
        
        Chaque site est représenté par :
        - Un cercle de taille proportionnelle au volume traité
        - Une couleur distinctive
        - Une infobulle avec statistiques détaillées
        """
        d = self.donnees
        r = self.resultats
        
        x_nodes = []
        y_nodes = []
        sizes = []
        colors = []
        texts = []
        hovertexts = []
        
        for i in range(d.n_sites):
            x, y = self.positions[i]
            x_nodes.append(x)
            y_nodes.append(y)
            
            # Taille proportionnelle au volume
            volume_ratio = self.volumes_sites[i] / self.volume_max
            size = self.config.node_size_min + (
                self.config.node_size_max - self.config.node_size_min
            ) * volume_ratio
            sizes.append(size)
            
            # Couleur
            color_idx = i % len(self.config.node_color_palette)
            colors.append(self.config.node_color_palette[color_idx])
            
            # Texte affiché
            texts.append(d.noms_sites[i])
            
            # Calcul des flux entrants/sortants
            flux_sortant = sum(
                vol for (fi, fj), vol in r.get('flux_totaux', {}).items()
                if fi == i
            )
            flux_entrant = sum(
                vol for (fi, fj), vol in r.get('flux_totaux', {}).items()
                if fj == i
            )
            
            # Ruptures et stocks pour ce site
            ruptures_site = sum(
                vol for (rj, rm), vol in r.get('ruptures', {}).items()
                if rj == i
            )
            stocks_site = sum(
                vol for (si, sm), vol in r.get('stocks', {}).items()
                if si == i
            )
            
            # Infobulle détaillée
            hovertext = (
                f"<b>🏭 {d.noms_sites[i]}</b><br>"
                f"━━━━━━━━━━━━━━━━━━<br>"
                f"<b>Offre totale:</b> {d.offre[i].sum():.1f} t<br>"
                f"<b>Demande totale:</b> {d.demande[i].sum():.1f} t<br>"
                f"━━━━━━━━━━━━━━━━━━<br>"
                f"<b>Flux sortant:</b> {flux_sortant:.1f} t<br>"
                f"<b>Flux entrant:</b> {flux_entrant:.1f} t<br>"
                f"━━━━━━━━━━━━━━━━━━<br>"
                f"<b>Stock résiduel:</b> {stocks_site:.1f} t<br>"
                f"<b>Ruptures:</b> {ruptures_site:.1f} t"
            )
            hovertexts.append(hovertext)
        
        # Trace des nœuds
        fig.add_trace(go.Scatter(
            x=x_nodes,
            y=y_nodes,
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=colors,
                line=dict(
                    width=self.config.node_border_width,
                    color=self.config.node_border_color
                ),
                symbol='circle'
            ),
            text=texts,
            textposition='middle center',
            textfont=dict(
                size=self.config.node_label_font_size,
                color='white',
                family='Arial Black'
            ),
            hoverinfo='text',
            hovertext=hovertexts,
            showlegend=False,
            name='Sites'
        ))
        
        # Ajouter les infos sous les nœuds (optionnel)
        if self.config.show_node_info:
            info_x = []
            info_y = []
            info_texts = []
            
            for i in range(d.n_sites):
                x, y = self.positions[i]
                info_x.append(x)
                info_y.append(y - 0.15)
                
                offre = d.offre[i].sum()
                demande = d.demande[i].sum()
                info_texts.append(f"O:{offre:.0f} | D:{demande:.0f}")
            
            fig.add_trace(go.Scatter(
                x=info_x,
                y=info_y,
                mode='text',
                text=info_texts,
                textfont=dict(
                    size=self.config.node_info_font_size,
                    color='#64748b'
                ),
                hoverinfo='skip',
                showlegend=False
            ))
    
    def _ajouter_legende_couleur(self, fig: go.Figure) -> None:
        """
        Ajoute une barre de couleur pour indiquer l'échelle des flux.
        """
        # Trace invisible pour créer la colorbar
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(
                size=0,
                color=[self.flux_min, self.flux_max],
                colorscale=[
                    [0, 'rgb(59,130,246)'],      # Bleu
                    [0.5, 'rgb(250,200,0)'],     # Jaune
                    [1, 'rgb(239,68,68)']        # Rouge
                ],
                colorbar=dict(
                    title=dict(
                        text="Flux (tonnes)",
                        font=dict(size=12)
                    ),
                    thickness=15,
                    len=0.5,
                    x=1.02,
                    y=0.5,
                    tickfont=dict(size=10)
                ),
                showscale=True
            ),
            hoverinfo='skip',
            showlegend=False
        ))
    
    def _configurer_layout(self, fig: go.Figure) -> None:
        """
        Configure le layout global de la figure.
        """
        fig.update_layout(
            title=dict(
                text=f"<b>{self.config.title}</b><br>"
                     f"<sup>Flux total: {self.flux_total:,.0f} tonnes | "
                     f"{self.donnees.n_sites} sites | "
                     f"Layout: {self.config.layout_type.value}</sup>",
                x=0.5,
                xanchor='center',
                font=dict(size=18)
            ),
            width=self.config.width,
            height=self.config.height,
            plot_bgcolor=self.config.background_color,
            paper_bgcolor='white',
            margin=self.config.margin,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.3, 1.5]  # Espace pour la colorbar
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                scaleanchor='x',
                scaleratio=1,
                range=[-1.2, 1.2]
            ),
            hovermode='closest',
            showlegend=False
        )
    
    def exporter(
        self,
        nom_fichier: str,
        format: str = "html",
        dossier: Optional[Path] = None
    ) -> Path:
        """
        Exporte la visualisation dans le format spécifié.
        
        Args:
            nom_fichier: Nom du fichier (sans extension)
            format: Format d'export ("html", "png", "svg", "pdf")
            dossier: Dossier de destination (défaut: ./exports)
        
        Returns:
            Chemin du fichier exporté
        
        Raises:
            ValueError: Si le format n'est pas supporté
            RuntimeError: Si la figure n'a pas été créée
        """
        if self._figure is None:
            self._figure = self.creer_graphe_flux()
        
        # Dossier par défaut
        if dossier is None:
            dossier = Path(__file__).parent.parent / "exports"
        dossier = Path(dossier)
        dossier.mkdir(parents=True, exist_ok=True)
        
        # Extension
        format = format.lower()
        if format not in ["html", "png", "svg", "pdf", "jpeg"]:
            raise ValueError(f"Format non supporté: {format}")
        
        chemin = dossier / f"{nom_fichier}.{format}"
        
        if format == "html":
            self._figure.write_html(
                str(chemin),
                include_plotlyjs=True,
                full_html=True
            )
        else:
            # Nécessite kaleido pour les formats image
            try:
                self._figure.write_image(
                    str(chemin),
                    scale=self.config.export_dpi / 100,
                    engine="kaleido"
                )
            except Exception as e:
                logger.error(f"Erreur export image: {e}")
                logger.info("Installez kaleido: pip install kaleido")
                raise
        
        logger.info(f"✓ Exporté: {chemin}")
        return chemin
    
    def afficher(self) -> None:
        """
        Affiche la visualisation dans le navigateur par défaut.
        """
        if self._figure is None:
            self._figure = self.creer_graphe_flux()
        self._figure.show()


# ═══════════════════════════════════════════════════════════════════════════════
# FONCTION DE DÉMONSTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def demo_visualisation():
    """
    Démonstration du module de visualisation.
    
    Crée un jeu de données exemple et génère une visualisation interactive.
    """
    print("="*70)
    print("DÉMONSTRATION - Visualisation Interactive des Flux")
    print("="*70)
    
    # Import du modèle
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from modele_approvisionnement import (
            ModeleDonneesApprovisionnement,
            ModeleApprovisionnementPL
        )
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return
    
    # Créer et résoudre un exemple
    print("\n[1/3] Création des données exemple...")
    donnees = ModeleDonneesApprovisionnement(5, 3)
    donnees.generer_donnees_exemple()
    
    print("\n[2/3] Résolution du modèle...")
    modele = ModeleApprovisionnementPL(donnees)
    modele.construire_modele()
    
    if not modele.resoudre(verbose=False):
        print("❌ Échec de la résolution")
        return
    
    print("\n[3/3] Création de la visualisation...")
    
    # Configuration personnalisée
    config = ConfigurationVisualisation(
        layout_type=LayoutType.KAMADA_KAWAI,
        title="Réseau d'Approvisionnement Optimisé",
        edge_curvature=0.25,
        show_edge_labels=True
    )
    
    # Créer le visualisateur
    viz = VisualisateurFluxInteractif(
        donnees=donnees,
        resultats=modele.resultats,
        config=config
    )
    
    # Générer et afficher
    fig = viz.creer_graphe_flux()
    
    # Exporter
    chemin = viz.exporter("demo_flux", format="html")
    print(f"\n✓ Visualisation exportée: {chemin}")
    
    # Afficher dans le navigateur
    print("\n🌐 Ouverture dans le navigateur...")
    fig.show()


if __name__ == "__main__":
    demo_visualisation()
