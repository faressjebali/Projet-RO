# 🎯 PROCHAINES ÉTAPES - OPTIAPPRO V2.0

## 📅 Session Suivante (Estimée: 3-4 heures)

---

## 🔴 PRIORITÉ 1: Finaliser les Onglets Existants (2-3h)

### 1️⃣ Onglet Données (1h)
**Objectif**: Appliquer le design moderne aux tables de saisie

#### Tâches:
- [ ] Appliquer classe CSS aux QTableWidget
- [ ] Ajouter tooltips sur en-têtes de colonnes
- [ ] Styliser les QGroupBox avec classe "carte"
- [ ] Ajouter bouton "Valider" avec validation avant résolution
- [ ] Afficher les messages de validation dans une QTextEdit stylée

#### Code à ajouter:
```python
# Dans creer_onglet_donnees()
self.table_offre.setProperty("class", "table-donnees")
self.table_offre.horizontalHeaderItem(0).setToolTip(Messages.TIP_OFFRE)

# Bouton de validation
btn_valider = QPushButton(f"{Icones.VALIDER} {Messages.BTN_VALIDER}")
btn_valider.setProperty("class", "action-principale")
btn_valider.clicked.connect(self.valider_donnees_avancee)

# Méthode de validation
def valider_donnees_avancee(self):
    """Valide les données avec le ValidateurDonnees"""
    if self.donnees is None:
        return
    
    valide, messages = self.validateur.valider_tout(self.donnees)
    
    # Afficher les messages dans une zone de texte
    rapport_html = self.validateur.generer_rapport_html()
    # ... afficher dans QTextBrowser
```

### 2️⃣ Onglet Résolution (30 min)
**Objectif**: Moderniser l'interface de résolution

#### Tâches:
- [ ] Styliser le bouton "Résoudre" (classe "action-principale")
- [ ] Ajouter icône et tooltip
- [ ] Progress bar avec classe CSS
- [ ] Zone de logs avec classe "console"
- [ ] Indicateurs d'état avec icônes (⏳, ✅, ❌)

#### Code à ajouter:
```python
# Bouton résoudre modernisé
btn_resoudre = QPushButton(f"{Icones.RESOLUTION} {Messages.BTN_RESOUDRE}")
btn_resoudre.setProperty("class", "action-principale")
btn_resoudre.setMinimumHeight(50)
btn_resoudre.setToolTip(Messages.TIP_RESOUDRE)

# Zone de logs
self.text_logs = QTextEdit()
self.text_logs.setProperty("class", "console")
self.text_logs.setReadOnly(True)

# Statut avec icône
self.label_statut.setText(f"{Icones.EN_COURS} Résolution en cours...")
```

### 3️⃣ Onglet Résultats (30 min)
**Objectif**: Tables lisibles avec export rapide

#### Tâches:
- [ ] Styliser les tables de résultats
- [ ] Valeurs importantes avec classe "valeur-importante"
- [ ] Coloriser les lignes (ruptures en rouge, stocks en vert)
- [ ] Bouton "Exporter" rapide dans l'onglet
- [ ] Résumé en haut avec cartes KPI

#### Code à ajouter:
```python
# Carte résumé
carte_resume = QFrame()
carte_resume.setProperty("class", "carte-accentuee")

label_cout = QLabel(f"{Icones.COUT} Coût total:")
valeur_cout = QLabel(f"{cout_total:.2f} €")
valeur_cout.setProperty("class", "valeur-importante")

# Table avec colorisation
for row in range(table.rowCount()):
    rupture = table.item(row, col_rupture).text()
    if float(rupture) > 0:
        for col in range(table.columnCount()):
            table.item(row, col).setBackground(QColor(Couleurs.ERREUR_BG))
```

---

## 🟡 PRIORITÉ 2: Ajouter Heatmaps (1-2h)

### 4️⃣ Module Heatmaps avec Seaborn
**Objectif**: Visualisations professionnelles de matrices

#### Tâches:
- [ ] Créer `utils/visualisation.py` (nouveau fichier)
- [ ] Classe `GraphiqueHeatmap(FigureCanvas)`
- [ ] Méthode `tracer_heatmap_couts(donnees, matiere_idx)`
- [ ] Méthode `tracer_heatmap_flux(resultats)`
- [ ] Méthode `tracer_heatmap_capacites(donnees, resultats)`
- [ ] Intégrer dans l'onglet Visualisation

#### Code de référence:
```python
import seaborn as sns
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class GraphiqueHeatmap(FigureCanvasQTAgg):
    """Widget pour afficher des heatmaps avec seaborn"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 8))
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = None
    
    def tracer_heatmap_couts(self, donnees, matiere_idx):
        """Trace une heatmap des coûts de transport pour une matière"""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        # Extraire la matrice des coûts
        matrice_couts = donnees.cout_transport[:, :, matiere_idx]
        
        # Créer la heatmap
        sns.heatmap(
            matrice_couts,
            annot=True,  # Afficher les valeurs
            fmt=".1f",   # Format des valeurs
            cmap="YlOrRd",  # Palette de couleurs
            xticklabels=donnees.noms_sites,
            yticklabels=donnees.noms_sites,
            ax=self.ax,
            cbar_kws={'label': 'Coût (€/tonne)'}
        )
        
        self.ax.set_title(
            f"Coûts de Transport - {donnees.noms_matieres[matiere_idx]}",
            fontsize=14, fontweight='bold', pad=20
        )
        self.ax.set_xlabel("Site Destination", fontsize=12)
        self.ax.set_ylabel("Site Origine", fontsize=12)
        
        self.fig.tight_layout()
        self.draw()
    
    def tracer_heatmap_flux(self, resultats):
        """Trace une heatmap des flux totaux optimisés"""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        # Construire matrice des flux totaux
        flux_totaux = resultats.get('flux_totaux', {})
        n_sites = max(max(i, j) for (i, j) in flux_totaux.keys()) + 1
        matrice_flux = np.zeros((n_sites, n_sites))
        
        for (i, j), volume in flux_totaux.items():
            matrice_flux[i, j] = volume
        
        # Créer la heatmap
        sns.heatmap(
            matrice_flux,
            annot=True,
            fmt=".0f",
            cmap="Blues",
            ax=self.ax,
            cbar_kws={'label': 'Volume (tonnes)'}
        )
        
        self.ax.set_title("Flux Optimisés entre Sites", fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        self.draw()
    
    def tracer_heatmap_utilisation_capacites(self, donnees, resultats):
        """Trace une heatmap du taux d'utilisation des capacités"""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        # Calculer taux d'utilisation (flux/capacité)
        flux_totaux = resultats.get('flux_totaux', {})
        n_sites = donnees.n_sites
        matrice_utilisation = np.zeros((n_sites, n_sites))
        
        for (i, j), volume in flux_totaux.items():
            capacite = donnees.capacite_transfert[i, j]
            if capacite != float('inf') and capacite > 0:
                matrice_utilisation[i, j] = (volume / capacite) * 100
        
        # Créer la heatmap
        sns.heatmap(
            matrice_utilisation,
            annot=True,
            fmt=".1f",
            cmap="RdYlGn_r",  # Rouge = saturé, Vert = libre
            vmin=0,
            vmax=100,
            ax=self.ax,
            cbar_kws={'label': 'Utilisation (%)'}
        )
        
        self.ax.set_title("Taux d'Utilisation des Capacités", fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        self.draw()
```

#### Intégration dans l'interface:
```python
# Dans creer_onglet_visualisation()
self.heatmap_widget = GraphiqueHeatmap()

# Boutons de sélection
btn_heatmap_couts = QPushButton(f"{Icones.HEATMAP} Heatmap Coûts")
btn_heatmap_flux = QPushButton(f"{Icones.HEATMAP} Heatmap Flux")
btn_heatmap_capacites = QPushButton(f"{Icones.HEATMAP} Heatmap Capacités")

btn_heatmap_couts.clicked.connect(lambda: self.heatmap_widget.tracer_heatmap_couts(self.donnees, 0))
# ... etc
```

---

## 🟢 PRIORITÉ 3: Fonctionnalités Optionnelles (Si temps)

### 5️⃣ Amélioration des Graphes de Flux (1h)
- [ ] Installer `networkx` si pas déjà fait
- [ ] Layout force-directed (spring_layout)
- [ ] Flèches colorées par matière
- [ ] Labels interactifs au survol

### 6️⃣ Gestion de Scénarios (2h)
- [ ] Nouvel onglet "Scénarios"
- [ ] QListWidget avec scénarios sauvegardés
- [ ] Boutons: Charger, Supprimer, Comparer
- [ ] Dialogue de comparaison côte-à-côte

---

## 📝 CHECKLIST AVANT DE FINALISER

### Code
- [ ] Tous les onglets modernisés
- [ ] Heatmaps fonctionnelles
- [ ] Validation intégrée dans le workflow
- [ ] Aucune erreur pylint/flake8
- [ ] Tests d'intégration passent

### Interface
- [ ] Tous les tooltips présents
- [ ] Toutes les icônes affichées
- [ ] Thèmes clair/sombre cohérents
- [ ] Responsive (redimensionnement)

### Fonctionnalités
- [ ] Import CSV testé
- [ ] Export tous formats testé
- [ ] Résolution avec Gurobi testée
- [ ] Insights générés correctement
- [ ] Validation détecte les erreurs

### Documentation
- [ ] README.md à jour
- [ ] DOCUMENTATION.md complète
- [ ] Captures d'écran ajoutées
- [ ] Code commenté

---

## 🚀 COMMANDES RAPIDES

### Tester l'application
```bash
python3 test_interface.py
```

### Lancer l'application
```bash
python3 lancer.py
```

### Vérifier le code
```bash
python3 -m pylint interface_approvisionnement.py
python3 -m flake8 interface_approvisionnement.py
```

### Installer dépendances manquantes
```bash
pip install networkx  # Pour graphes améliorés
pip install pillow    # Pour export PNG
```

---

## 📊 ESTIMATION DE TEMPS

| Tâche | Temps estimé | Priorité |
|-------|-------------|----------|
| Onglet Données | 1h | 🔴 HAUTE |
| Onglet Résolution | 30min | 🔴 HAUTE |
| Onglet Résultats | 30min | 🔴 HAUTE |
| Heatmaps | 1-2h | 🔴 HAUTE |
| Graphes améliorés | 1h | 🟡 MOYENNE |
| Gestion scénarios | 2h | 🟡 MOYENNE |
| Tests d'intégration | 30min | 🔴 HAUTE |

**TOTAL**: 5-7 heures pour tout compléter

---

## 🎯 OBJECTIF DE LA PROCHAINE SESSION

**Atteindre 95%+ de complétion du projet**

Après cette session, il ne restera que:
- Rapport académique final (3-4h)
- Présentation PowerPoint (2h)
- Tests finaux et peaufinages (1h)

---

**Date**: 17 Décembre 2025  
**Version actuelle**: OptiAppro v2.0.0 (80% complété)  
**Version cible**: OptiAppro v2.0.0 (95% complété)  
**Statut**: 🟢 **PRÊT POUR LA SUITE**

---

*Projet RO - INSA 2024-2025 | Enseignant: I. AJILI*
