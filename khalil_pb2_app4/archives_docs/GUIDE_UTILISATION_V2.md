# 🚀 GUIDE RAPIDE D'UTILISATION - OPTIAPPRO V2.0

## Table des Matières
1. [Installation](#installation)
2. [Configuration de Base](#configuration)
3. [Utilisation des Modules](#modules)
4. [Exemples de Code](#exemples)
5. [FAQ](#faq)

---

## 📦 Installation {#installation}

### 1. Installer les dépendances

```bash
# Installation minimale
pip install gurobipy PyQt6 numpy matplotlib

# Installation complète (recommandée)
pip install -r requirements.txt
```

### 2. Configurer la licence Gurobi

```bash
# Obtenir une licence académique gratuite
# https://www.gurobi.com/academia/

# Activer la licence
grbgetkey VOTRE-CLE-ACADEMIQUE
```

### 3. Lancer l'application

```bash
python lancer.py
```

---

## ⚙️ Configuration de Base {#configuration}

### Personnaliser les constantes

Éditez `config/constantes.py`:

```python
# Modifier les paramètres par défaut
PARAMS.NB_SITES_DEFAUT = 10  # Au lieu de 5
PARAMS.TIME_LIMIT = 600  # 10 minutes au lieu de 5
PARAMS.TAUX_RUPTURE_MAX = 0.15  # 15% au lieu de 20%
```

### Changer le thème

```python
from config.styles import StyleManager, Theme

# Dans votre application
StyleManager.initialiser(app)

# Basculer vers le mode sombre
StyleManager.appliquer_theme(Theme.SOMBRE)

# Retour au mode clair
StyleManager.appliquer_theme(Theme.CLAIR)
```

---

## 🧩 Utilisation des Modules {#modules}

### 1. Logging

```python
from utils.logger import obtenir_logger, LoggerContextuel, log_performance

# Obtenir un logger
logger = obtenir_logger(__name__)

# Logs simples
logger.debug("Message de debug")
logger.info("Information")
logger.warning("Avertissement")
logger.error("Erreur")
logger.critical("Critique!")

# Context manager pour tracer une opération
with LoggerContextuel("Chargement des données"):
    donnees = charger_donnees()
    # Logs automatiques avec durée

# Décorateur pour mesurer les performances
@log_performance
def fonction_longue():
    # Temps d'exécution automatiquement logué
    pass
```

**Fichiers de log générés**:
- `logs/optiappro_YYYYMMDD.log`
- Rotation automatique à 5 MB
- 3 backups conservés

### 2. Validation des Données

```python
from utils.validation import ValidateurDonnees

# Dans votre classe de données
def valider_donnees(self):
    validateur = ValidateurDonnees()
    
    # Validation complète
    est_valide, messages = validateur.valider_tout(self)
    
    if not est_valide:
        # Afficher les erreurs
        for msg in messages:
            print(msg)
        
        # Générer un rapport HTML
        html = validateur.generer_rapport_html()
        with open("rapport_validation.html", "w") as f:
            f.write(html)
    
    return est_valide, messages
```

**Types de validation**:
- ✅ Dimensions des matrices
- ✅ Non-négativité
- ✅ Équilibre offre-demande
- ✅ Cohérence des capacités
- ✅ Cohérence des distances

### 3. Import/Export

```python
from utils.import_export import GestionnaireImportExport

gio = GestionnaireImportExport()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Import d'une seule matrice
matrice, erreur = gio.importer_matrice_csv("chemin/vers/offre.csv")
if erreur:
    print(f"Erreur: {erreur}")
else:
    print(f"Matrice importée: {matrice.shape}")

# Import d'un jeu complet de données
donnees_dict, erreur = gio.importer_donnees_completes("dossier_donnees/")
if not erreur:
    # Appliquer aux données
    donnees.offre = donnees_dict['offre']
    donnees.demande = donnees_dict['demande']
    # etc.

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Export résultats en CSV
succes = gio.exporter_resultats_csv(modele, "exports/resultats.csv")

# Export résultats en Excel (multiples feuilles)
succes = gio.exporter_resultats_excel(modele, "exports/resultats.xlsx")

# Rapport textuel complet
succes = gio.generer_rapport_textuel(modele, "exports/rapport.txt")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCÉNARIOS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Sauvegarder un scénario complet (données + résultats)
chemin = gio.sauvegarder_scenario(
    donnees=donnees,
    nom_scenario="Production_Hiver_2025",
    resultats=modele.resultats if modele else None
)
print(f"Scénario sauvegardé: {chemin}")
```

**Formats de fichiers CSV attendus**:

```csv
# offre.csv
,Acier,Plastique,Aluminium
Site_Nord,150.0,0.0,100.0
Site_Sud,0.0,200.0,50.0
Site_Est,100.0,80.0,0.0
```

### 4. Interprétation Automatique

```python
from utils.interpretation import InterpreteurResultats

# Créer l'interpréteur
interpreteur = InterpreteurResultats()

# Analyser les résultats
insights = interpreteur.analyser(modele)

# Afficher les insights dans la console
for insight in insights:
    print(insight)
    print("─" * 50)

# Générer un rapport textuel
rapport_txt = interpreteur.generer_rapport_texte()
with open("analyse.txt", "w", encoding="utf-8") as f:
    f.write(rapport_txt)

# Générer un rapport HTML
rapport_html = interpreteur.generer_rapport_html()
with open("analyse.html", "w", encoding="utf-8") as f:
    f.write(rapport_html)
```

**Types d'insights**:
- 🚀 Performance globale
- 🔀 Flux dominants et hubs
- ⚠️ Ruptures et matières critiques
- 💰 Analyse des coûts
- 📊 Utilisation des capacités
- 💡 Recommandations opérationnelles

---

## 💡 Exemples de Code {#exemples}

### Exemple 1: Créer et résoudre un problème avec logs

```python
from utils.logger import obtenir_logger, LoggerContextuel
from config.constantes import PARAMS

logger = obtenir_logger(__name__)

def resoudre_probleme_complet():
    logger.info("="*70)
    logger.info("DÉMARRAGE DE LA RÉSOLUTION")
    logger.info("="*70)
    
    # 1. Créer les données
    with LoggerContextuel("Initialisation des données"):
        donnees = ModeleDonneesApprovisionnement(
            n_sites=PARAMS.NB_SITES_DEFAUT,
            n_matieres=PARAMS.NB_MATIERES_DEFAUT
        )
        donnees.generer_donnees_exemple()
    
    # 2. Valider
    with LoggerContextuel("Validation des données"):
        validateur = ValidateurDonnees()
        valide, messages = validateur.valider_tout(donnees)
        
        if not valide:
            logger.error("Validation échouée!")
            for msg in messages:
                logger.error(str(msg))
            return None
    
    # 3. Construire et résoudre
    with LoggerContextuel("Construction du modèle"):
        modele = ModeleApprovisionnementPL(donnees)
        modele.construire_modele()
    
    with LoggerContextuel("Résolution Gurobi"):
        succes = modele.resoudre(time_limit=PARAMS.TIME_LIMIT)
        
        if not succes:
            logger.error("Résolution échouée!")
            return None
    
    # 4. Analyser
    with LoggerContextuel("Interprétation des résultats"):
        interpreteur = InterpreteurResultats()
        insights = interpreteur.analyser(modele)
        
        logger.info(f"{len(insights)} insights générés")
        for insight in insights[:5]:  # Top 5
            logger.info(str(insight))
    
    # 5. Exporter
    with LoggerContextuel("Export des résultats"):
        gio = GestionnaireImportExport()
        gio.exporter_resultats_csv(modele, "resultats.csv")
        gio.exporter_resultats_excel(modele, "resultats.xlsx")
        gio.generer_rapport_textuel(modele, "rapport.txt")
    
    logger.info("="*70)
    logger.info("RÉSOLUTION TERMINÉE AVEC SUCCÈS")
    logger.info("="*70)
    
    return modele

# Appeler
modele = resoudre_probleme_complet()
```

### Exemple 2: Interface avec thème et tooltips

```python
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from config.styles import StyleManager, Theme
from config.constantes import Icones, Messages, Couleurs

app = QApplication([])

# Appliquer le thème
StyleManager.initialiser(app)

# Créer l'interface
window = QWidget()
layout = QVBoxLayout()

# Bouton principal avec style
btn_resoudre = QPushButton(f"{Icones.RESOLUTION} {Messages.BTN_RESOUDRE}")
btn_resoudre.setProperty("class", "action-principale")  # Style spécial
btn_resoudre.setToolTip(Messages.TIP_RESOUDRE)
btn_resoudre.setMinimumHeight(60)
layout.addWidget(btn_resoudre)

# Bouton de thème
btn_theme = QPushButton("🌓 Basculer le thème")
btn_theme.clicked.connect(lambda: StyleManager.basculer_theme())
layout.addWidget(btn_theme)

window.setLayout(layout)
window.show()

app.exec()
```

### Exemple 3: Import CSV avec validation

```python
from utils.import_export import GestionnaireImportExport
from utils.validation import ValidateurDonnees
from utils.logger import obtenir_logger

logger = obtenir_logger(__name__)
gio = GestionnaireImportExport()

def charger_et_valider(dossier: str):
    """Charge des données CSV et les valide"""
    
    # Import
    logger.info(f"Import depuis: {dossier}")
    donnees_dict, erreur = gio.importer_donnees_completes(dossier)
    
    if erreur:
        logger.error(f"Échec de l'import: {erreur}")
        return None
    
    # Créer l'objet données
    n_sites, n_matieres = donnees_dict['offre'].shape
    donnees = ModeleDonneesApprovisionnement(n_sites, n_matieres)
    
    # Appliquer les données importées
    donnees.offre = donnees_dict['offre']
    donnees.demande = donnees_dict['demande']
    donnees.distance = donnees_dict['distance']
    donnees.cout_transport = donnees_dict['cout_transport']
    
    if 'capacite_transfert' in donnees_dict:
        donnees.capacite_transfert = donnees_dict['capacite_transfert']
    
    # Validation
    validateur = ValidateurDonnees()
    valide, messages = validateur.valider_tout(donnees)
    
    if valide:
        logger.info("✓ Données valides et prêtes")
    else:
        logger.warning(f"⚠ Données avec avertissements: {len(messages)}")
        for msg in messages:
            logger.warning(str(msg))
    
    return donnees if valide else None

# Utilisation
donnees = charger_et_valider("imports/scenario1/")
if donnees:
    # Continuer avec la résolution
    pass
```

### Exemple 4: Génération de rapport complet

```python
def generer_rapport_complet(modele):
    """Génère tous les types de rapports"""
    from utils.import_export import GestionnaireImportExport
    from utils.interpretation import InterpreteurResultats
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gio = GestionnaireImportExport()
    interpreteur = InterpreteurResultats()
    
    # 1. Rapport textuel basique
    gio.generer_rapport_textuel(
        modele, 
        f"exports/rapport_{timestamp}.txt"
    )
    
    # 2. CSV des résultats
    gio.exporter_resultats_csv(
        modele, 
        f"exports/resultats_{timestamp}.csv"
    )
    
    # 3. Excel avec feuilles multiples
    gio.exporter_resultats_excel(
        modele, 
        f"exports/resultats_{timestamp}.xlsx"
    )
    
    # 4. Analyse automatique (texte)
    insights = interpreteur.analyser(modele)
    rapport_analyse = interpreteur.generer_rapport_texte()
    with open(f"exports/analyse_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(rapport_analyse)
    
    # 5. Analyse automatique (HTML)
    rapport_html = interpreteur.generer_rapport_html()
    with open(f"exports/analyse_{timestamp}.html", "w", encoding="utf-8") as f:
        f.write(rapport_html)
    
    print(f"✓ 5 rapports générés dans exports/ avec timestamp {timestamp}")
```

---

## ❓ FAQ {#faq}

### Q: Comment changer la couleur primaire de l'application?

**R**: Éditez `config/styles.py`:

```python
PALETTE_CLAIRE = PaletteTheme(
    accent_primaire="#1565c0",  # Changez cette valeur
    # ...
)
```

Puis régénérez le style:
```python
STYLE_CLAIR = generer_style_qss(PALETTE_CLAIRE)
```

### Q: Où sont stockés les logs?

**R**: Dans le dossier `logs/` à la racine du projet:
- `logs/optiappro_20251217.log` (log du jour)
- Rotation automatique
- 3 backups conservés

### Q: Comment désactiver les logs en console?

**R**: Dans `utils/logger.py`, commentez le handler console:

```python
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(formatter)
# self.logger.addHandler(console_handler)
```

### Q: Les validations sont-elles bloquantes?

**R**: Non! Le validateur distingue:
- **CRITIQUE/ERREUR**: Résolution impossible
- **AVERTISSEMENT**: Résolution possible mais risquée
- **INFO**: Information utile

Vous pouvez choisir d'autoriser la résolution avec des avertissements.

### Q: Puis-je importer des fichiers Excel directement?

**R**: Oui, avec pandas installé:

```python
import pandas as pd

# Lire Excel
df = pd.read_excel("donnees.xlsx", sheet_name="Offre")
matrice_offre = df.values

# Convertir en CSV si besoin
df.to_csv("offre.csv", index=False)
```

### Q: Comment personnaliser les messages de l'interface?

**R**: Éditez `config/constantes.py`:

```python
class Messages:
    BTN_RESOUDRE = "Lancer l'optimisation"  # Au lieu de "Résoudre avec Gurobi"
    # ...
```

### Q: Les insights peuvent-ils être traduits?

**R**: Oui! Modifiez les templates dans `utils/interpretation.py`:

```python
def _analyser_performance(self, modele):
    # ...
    description=f"System satisfies {taux:.1f}% of demand..."  # Traduire ici
```

### Q: Comment exporter les graphiques en haute résolution?

**R**: Utilisez matplotlib directement:

```python
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
# ... tracer
fig.savefig("graphique_HD.png", dpi=300, bbox_inches='tight')
```

### Q: Puis-je utiliser un autre solveur que Gurobi?

**R**: Le code actuel est spécifique à Gurobi, mais l'architecture modulaire facilite l'ajout d'autres solveurs (CPLEX, SCIP, etc.). Il faudrait:

1. Créer un module `utils/solveurs.py`
2. Définir une interface commune
3. Implémenter chaque solveur

---

## 🎯 Bonnes Pratiques

### 1. Toujours logger les opérations importantes

```python
logger.info("Début de l'opération X")
try:
    # Opération
    logger.info("✓ Opération X réussie")
except Exception as e:
    logger.exception(f"✗ Échec de l'opération X: {e}")
```

### 2. Valider avant de résoudre

```python
validateur = ValidateurDonnees()
valide, messages = validateur.valider_tout(donnees)

if not valide:
    # Afficher les erreurs à l'utilisateur
    return

# Continuer avec la résolution
```

### 3. Utiliser les context managers

```python
with LoggerContextuel("Chargement"):
    # Le début et la fin sont automatiquement loggés
    donnees = charger()
```

### 4. Exporter régulièrement les scénarios

```python
# Après chaque résolution réussie
gio.sauvegarder_scenario(donnees, f"scenario_{timestamp}", modele.resultats)
```

### 5. Analyser systématiquement les résultats

```python
# Ne pas se contenter des chiffres bruts
interpreteur = InterpreteurResultats()
insights = interpreteur.analyser(modele)

# Prendre en compte les insights dans les décisions
for insight in insights:
    if insight.importance >= 4:
        # Action requise
        pass
```

---

## 📞 Support

- **Documentation complète**: Voir DOCUMENTATION.md
- **Améliorations v2.0**: Voir AMELIORATIONS_V2.md
- **Code source**: Tous les modules sont commentés
- **Logs**: Consultez `logs/optiappro_*.log` pour le debug

---

**Projet RO - INSA 2024-2025 | Enseignant: I. AJILI**  
**OptiAppro v2.0 - Optimisation de l'Approvisionnement Inter-Sites**
