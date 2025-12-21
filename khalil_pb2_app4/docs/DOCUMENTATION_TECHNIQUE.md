# 📚 DOCUMENTATION TECHNIQUE - OptiAppro v2.1.0

## Optimisation de l'Approvisionnement Inter-Sites
### Projet de Recherche Opérationnelle - Programmation Linéaire

---

**INSAT - Année universitaire 2025-2026**  
**Réalisé par:** Khalil Chikhaoui  
**Domaine:** Recherche Opérationnelle - Programmation Linéaire  

---

## 📋 Table des Matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture du Projet](#2-architecture-du-projet)
3. [Modèle Mathématique](#3-modèle-mathématique)
4. [Guide d'Installation](#4-guide-dinstallation)
5. [Guide d'Utilisation](#5-guide-dutilisation)
6. [Visualisation Interactive](#6-visualisation-interactive)
7. [Structure des Données](#7-structure-des-données)
8. [API et Extensibilité](#8-api-et-extensibilité)
9. [Performances](#9-performances)
10. [Dépannage](#10-dépannage)

---

## 1. Vue d'ensemble

### 1.1 Objectif du Projet

OptiAppro est un système d'aide à la décision pour l'optimisation des flux d'approvisionnement entre sites de production. Il résout le problème de **minimisation des coûts logistiques** tout en satisfaisant les contraintes de capacité et de demande.

### 1.2 Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| 🔧 **Modélisation PL** | Modèle de programmation linéaire complet avec Gurobi |
| 📊 **Interface Graphique** | Interface PyQt6 moderne et intuitive |
| 🌐 **Visualisation Interactive** | Graphes de flux avec Plotly (courbes de Bézier) |
| 📁 **Import/Export** | Support CSV, Excel, JSON |
| 📈 **Analyse des Résultats** | KPIs, tableaux détaillés, graphiques |

### 1.3 Technologies Utilisées

```
┌─────────────────────────────────────────────────────────────┐
│  COUCHE PRÉSENTATION                                        │
│  ├── PyQt6 (Interface graphique)                           │
│  ├── Plotly (Visualisation interactive)                    │
│  └── Matplotlib/Seaborn (Graphiques statiques)            │
├─────────────────────────────────────────────────────────────┤
│  COUCHE MÉTIER                                              │
│  ├── Gurobi (Solveur d'optimisation)                       │
│  ├── NumPy (Calcul matriciel)                              │
│  └── NetworkX (Algorithmes de graphes)                     │
├─────────────────────────────────────────────────────────────┤
│  COUCHE DONNÉES                                             │
│  ├── CSV / Excel (Import/Export)                           │
│  └── JSON (Scénarios complets)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture du Projet

### 2.1 Structure des Fichiers

```
OptiAppro/
├── 📄 lancer.py                    # Point d'entrée principal
├── 📄 modele_approvisionnement.py  # Modèle PL Gurobi
├── 📄 interface_approvisionnement.py # Interface PyQt6
├── 📄 requirements.txt             # Dépendances Python
│
├── 📁 config/                      # Configuration
│   ├── constantes.py              # Paramètres par défaut
│   └── styles.py                  # Thèmes et couleurs
│
├── 📁 utils/                       # Modules utilitaires
│   ├── visualisation.py           # Graphiques Matplotlib
│   ├── visualisation_plotly.py    # Graphiques Plotly (NOUVEAU)
│   ├── import_export.py           # Gestion fichiers
│   ├── validation.py              # Validation données
│   ├── interpretation.py          # Analyse résultats
│   └── logger.py                  # Logging
│
├── 📁 donnees_exemple/             # Jeux de données test
│   ├── offre.csv
│   ├── demande.csv
│   ├── distances.csv
│   └── couts_matiere_*.csv
│
├── 📁 exports/                     # Résultats exportés
├── 📁 logs/                        # Journaux d'exécution
└── 📁 docs/                        # Documentation
```

### 2.2 Diagramme de Classes Simplifié

```
┌─────────────────────────────────────┐
│    FenetreApprovisionnement         │  ← Interface principale
│  ├─ donnees: ModeleDonnees          │
│  ├─ modele: ModeleApprovisionnement │
│  └─ gestionnaire_io: GestionnaireIO │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  ModeleDonneesApprovisionnement     │  ← Conteneur de données
│  ├─ offre[n_sites, n_matieres]      │
│  ├─ demande[n_sites, n_matieres]    │
│  ├─ cout_transport[n,n,m]           │
│  └─ distance[n_sites, n_sites]      │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│    ModeleApprovisionnementPL        │  ← Modèle d'optimisation
│  ├─ construire_modele()             │
│  ├─ resoudre()                      │
│  └─ extraire_resultats()            │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   VisualisateurFluxInteractif       │  ← Visualisation Plotly
│  ├─ creer_graphe_flux()             │
│  ├─ exporter()                      │
│  └─ afficher()                      │
└─────────────────────────────────────┘
```

---

## 3. Modèle Mathématique

### 3.1 Ensembles et Indices

| Symbole | Description |
|---------|-------------|
| $i, j \in S$ | Sites de production (1 à n) |
| $m \in M$ | Matières premières (1 à m) |

### 3.2 Paramètres

| Symbole | Description | Unité |
|---------|-------------|-------|
| $O_{im}$ | Offre de matière m au site i | tonnes |
| $D_{jm}$ | Demande de matière m au site j | tonnes |
| $c_{ijm}$ | Coût de transport direct | DT/tonne |
| $d_{ij}$ | Distance entre sites | km |
| $\alpha$ | Coût kilométrique | DT/tonne/km |
| $h_{im}$ | Coût de stockage | DT/tonne |
| $p_{jm}$ | Pénalité de rupture | DT/tonne |
| $Cap_{ij}$ | Capacité de transfert | tonnes |

### 3.3 Variables de Décision

| Variable | Description | Domaine |
|----------|-------------|---------|
| $x_{ijm}$ | Flux de matière m de i vers j | $\mathbb{R}^+$ |
| $s_{im}$ | Stock résiduel de m au site i | $\mathbb{R}^+$ |
| $r_{jm}$ | Rupture de m au site j | $\mathbb{R}^+$ |
| $y_{ij}$ | Flux total entre i et j | $\mathbb{R}^+$ |

### 3.4 Fonction Objectif

**Minimiser le coût total Z :**

$$Z = \underbrace{\sum_{i \neq j} \sum_m c_{ijm} \cdot x_{ijm}}_{\text{Coût transport direct}} + \underbrace{\alpha \sum_{i \neq j} d_{ij} \cdot y_{ij}}_{\text{Coût kilométrique}} + \underbrace{\sum_i \sum_m h_{im} \cdot s_{im}}_{\text{Coût stockage}} + \underbrace{\sum_j \sum_m p_{jm} \cdot r_{jm}}_{\text{Pénalités rupture}}$$

### 3.5 Contraintes

#### (1) Conservation des flux (équilibre entrées/sorties)
$$\forall i, m: \quad O_{im} + \sum_{k \neq i} x_{kim} = \sum_{j \neq i} x_{ijm} + s_{im}$$

#### (2) Satisfaction de la demande
$$\forall j, m: \quad \sum_{i \neq j} x_{ijm} + r_{jm} = D_{jm}$$

#### (3) Capacité de transfert
$$\forall i \neq j: \quad \sum_m x_{ijm} \leq Cap_{ij}$$

#### (4) Lien flux total
$$\forall i \neq j: \quad y_{ij} = \sum_m x_{ijm}$$

#### (5) Limitation des ruptures (max 20%)
$$\forall j, m: \quad r_{jm} \leq 0.2 \times D_{jm}$$

#### (6) Non-négativité
$$x_{ijm} \geq 0, \quad s_{im} \geq 0, \quad r_{jm} \geq 0, \quad y_{ij} \geq 0$$

### 3.6 Distinction Coût Direct vs Kilométrique

| Aspect | Coût Direct ($c_{ijm}$) | Coût Kilométrique ($\alpha \cdot d_{ij}$) |
|--------|------------------------|-------------------------------------------|
| **Nature** | Forfaitaire/contractuel | Proportionnel à la distance |
| **Différenciation** | Par matière (lourdeur, fragilité) | Uniforme |
| **Capture** | Tarifs négociés, péages | Carburant, usure, temps |
| **Usage** | Contrats transporteurs | Optimisation "verte" |

**Exemple numérique:**  
Route A→B: 100 km, 50 tonnes d'acier, $c_{AB,acier}$ = 15 DT/t, α = 0.5 DT/t/km

- Coût direct: $15 \times 50 = 750$ DT
- Coût km: $0.5 \times 100 \times 50 = 2500$ DT
- **Total**: 3250 DT

---

## 4. Guide d'Installation

### 4.1 Prérequis

- **Python** 3.9+
- **Gurobi** 10.0+ (licence académique gratuite)
- **Système**: Linux, macOS ou Windows

### 4.2 Installation

```bash
# 1. Cloner ou télécharger le projet
cd /chemin/vers/OptiAppro

# 2. Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Vérifier l'installation Gurobi
python -c "import gurobipy; print(f'Gurobi {gurobipy.gurobi.version()}')"

# 5. Lancer l'application
python lancer.py
```

### 4.3 Dépendances Principales

```
gurobipy>=10.0.0     # Solveur d'optimisation
PyQt6>=6.4.0         # Interface graphique
numpy>=1.21.0        # Calcul matriciel
matplotlib>=3.5.0    # Graphiques statiques
plotly>=5.0.0        # Graphiques interactifs
networkx>=2.6        # Algorithmes de graphes
```

---

## 5. Guide d'Utilisation

### 5.1 Démarrage Rapide

1. **Lancer l'application**: `python lancer.py`
2. **Charger les données exemple**: Menu → Charger Données Exemple
3. **Résoudre**: Onglet Résolution → Bouton "RÉSOUDRE AVEC GUROBI"
4. **Visualiser**: Onglet Visualisation → "Ouvrir dans Navigateur"

### 5.2 Workflow Complet

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Config   │ → │ 2. Données  │ → │ 3. Résoudre │ → │ 4. Analyser │
│  n sites    │    │  Import CSV │    │  Gurobi     │    │  KPIs       │
│  m matières │    │  ou manuel  │    │             │    │  Graphes    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 5.3 Onglets de l'Interface

| Onglet | Fonction |
|--------|----------|
| ⚙️ **Configuration** | Définir n_sites, n_matieres |
| 📊 **Données** | Saisir/importer offre, demande, coûts |
| 🚀 **Résolution** | Lancer Gurobi, voir logs |
| 📈 **Résultats** | KPIs, tableaux flux/ruptures/stocks |
| 🌐 **Visualisation** | Graphes interactifs Plotly |

---

## 6. Visualisation Interactive

### 6.1 Nouvelle Fonctionnalité: Graphe Plotly

Le module `visualisation_plotly.py` génère des graphes de réseau professionnels avec:

- **Layouts intelligents**: Kamada-Kawai (minimise les croisements)
- **Arêtes courbées**: Courbes de Bézier évitant les superpositions
- **Couleurs par intensité**: Gradient bleu→jaune→rouge
- **Infobulles**: Détails au survol (flux, coûts, matières)
- **Export**: HTML interactif, PNG/SVG HD

### 6.2 Utilisation Programmatique

```python
from utils.visualisation_plotly import (
    VisualisateurFluxInteractif,
    ConfigurationVisualisation,
    LayoutType
)
from modele_approvisionnement import (
    ModeleDonneesApprovisionnement,
    ModeleApprovisionnementPL
)

# 1. Créer et résoudre le modèle
donnees = ModeleDonneesApprovisionnement(5, 3)
donnees.generer_donnees_exemple()

modele = ModeleApprovisionnementPL(donnees)
modele.construire_modele()
modele.resoudre()

# 2. Configurer la visualisation
config = ConfigurationVisualisation(
    layout_type=LayoutType.KAMADA_KAWAI,
    title="Mon Réseau d'Approvisionnement",
    edge_curvature=0.25,
    show_edge_labels=True
)

# 3. Générer et afficher
viz = VisualisateurFluxInteractif(donnees, modele.resultats, config)
fig = viz.creer_graphe_flux()
fig.show()  # Ouvre dans le navigateur

# 4. Exporter
viz.exporter("mon_graphe", format="html")
```

### 6.3 Paramètres de Configuration

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `layout_type` | KAMADA_KAWAI | Algorithme de placement |
| `edge_curvature` | 0.2 | Courbure des arêtes (0-0.5) |
| `node_size_min/max` | 30/80 | Taille des nœuds |
| `edge_width_min/max` | 1/12 | Épaisseur des arêtes |
| `colorscale` | "Viridis" | Échelle de couleurs |
| `width/height` | 1200/800 | Dimensions (pixels) |

---

## 7. Structure des Données

### 7.1 Format CSV

**offre.csv** (n_sites × n_matieres)
```csv
# Offre par site et matière (tonnes)
,Acier,Plastique,Aluminium
Site_Nord,150,0,100
Site_Sud,0,200,50
...
```

**distances.csv** (n_sites × n_sites)
```csv
# Distances entre sites (km)
,Site_Nord,Site_Sud,Site_Est,Site_Ouest,Site_Centre
Site_Nord,0,450,380,320,250
Site_Sud,450,0,520,600,420
...
```

### 7.2 Structure des Résultats

```python
resultats = {
    'valeur_optimale': 178262.50,        # Coût total (DT)
    'flux': {(0,1,0): 50.0, ...},        # x[i,j,m]
    'flux_totaux': {(0,1): 80.0, ...},   # y[i,j]
    'stocks': {(0,0): 10.0, ...},        # s[i,m]
    'ruptures': {(4,2): 5.0, ...},       # r[j,m]
    'taux_satisfaction': 0.917,          # 91.7%
    'temps_resolution': 0.025,           # secondes
    'nb_variables': 110,
    'nb_contraintes': 91
}
```

---

## 8. API et Extensibilité

### 8.1 Ajouter un Nouveau Layout

```python
# Dans visualisation_plotly.py

class LayoutType(Enum):
    # ... existants ...
    MON_LAYOUT = "mon_layout"

def _calculer_positions_basiques(self):
    if layout_type == LayoutType.MON_LAYOUT:
        # Implémenter votre algorithme
        positions = {}
        for i in range(n):
            positions[i] = (x_calculé, y_calculé)
        return positions
```

### 8.2 Ajouter une Contrainte au Modèle

```python
# Dans modele_approvisionnement.py, méthode construire_modele()

# Exemple: Contrainte de temps de livraison max
for i in d.sites:
    for j in d.sites:
        if i != j:
            temps = d.temps_transport[i, j]
            if temps > d.temps_max:
                self.modele.addConstr(
                    y[i, j] == 0,
                    name=f"temps_max_{i}_{j}"
                )
```

---

## 9. Performances

### 9.1 Complexité Algorithmique

| Composant | Complexité | Note |
|-----------|------------|------|
| Construction modèle | O(n² × m) | Variables et contraintes |
| Résolution Gurobi | Polynomial | PL en temps polynomial |
| Layout Kamada-Kawai | O(n³) | Décomposition matricielle |
| Rendu Plotly | O(n + e) | n nœuds, e arêtes |

### 9.2 Benchmarks (5 sites, 3 matières)

```
┌────────────────────────────────────┬───────────┐
│ Opération                          │ Temps     │
├────────────────────────────────────┼───────────┤
│ Construction modèle                │ 0.002 s   │
│ Résolution Gurobi                  │ 0.025 s   │
│ Extraction résultats               │ 0.001 s   │
│ Génération graphe Plotly           │ 0.150 s   │
│ Export HTML                        │ 0.080 s   │
├────────────────────────────────────┼───────────┤
│ TOTAL                              │ ~0.26 s   │
└────────────────────────────────────┴───────────┘
```

---

## 10. Dépannage

### 10.1 Erreurs Courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `GurobiError: No license` | Licence manquante | Installer licence académique |
| `ImportError: plotly` | Module manquant | `pip install plotly` |
| `inequality constraints not supported` | Bug comparaison Gurobi | Utiliser `hasattr(var, 'X')` |

### 10.2 Logs

Les logs sont dans `logs/optiappro_YYYYMMDD.log`:

```
2025-12-18 11:50:00 | INFO | DÉMARRAGE DE L'APPLICATION
2025-12-18 11:50:05 | INFO | Données chargées: 5 sites, 3 matières
2025-12-18 11:50:10 | INFO | Solution optimale: 178262.50 DT
```

---

## 📞 Support

**Auteur:** Khalil Chikhaoui  
**Institution:** INSAT  
**Année:** 2025-2026  

---

*Documentation générée le 18/12/2025 - OptiAppro v2.1.0*
