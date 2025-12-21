# � OptiAppro - Optimisation de l'Approvisionnement Inter-Sites

## 🎓 Projet de Recherche Opérationnelle

**Institution**: INSAT  
**Année universitaire**: 2025-2026  
**Réalisé par**: Khalil Chikhaoui  
**Domaine**: Recherche Opérationnelle - Programmation Linéaire  
**Technologies**: Gurobi Optimizer + PyQt6 + Python

---

## 🎯 Objectif

Optimiser les flux de matières premières entre sites de production pour **minimiser les coûts totaux** (en Dinar Tunisien - DT) tout en respectant les contraintes opérationnelles (capacités, délais, priorités).

## ✨ Fonctionnalités

✅ **Modèle PL riche** avec 13+ paramètres et 9 types de contraintes  
✅ **Interface graphique professionnelle** avec PyQt6  
✅ **Résolution optimale** avec le solveur Gurobi  
✅ **Calculs non-bloquants** via QThread  
✅ **Visualisations graphiques** interactives (Matplotlib)  
✅ **Analyse détaillée** des résultats

## 📦 Installation

### Prérequis
- Python 3.8+
- Licence Gurobi (académique gratuite sur [gurobi.com](https://www.gurobi.com/academia/))

### Étapes

1. **Cloner/télécharger le projet**
```bash
cd Projet
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer Gurobi**
```bash
# Obtenir une licence académique gratuite sur gurobi.com
grbgetkey VOTRE-CLE-DE-LICENCE
```

## 🚀 Utilisation

### Lancer l'interface graphique (RECOMMANDÉ)
```bash
python3 lancer.py
```

### Test rapide de l'interface
```bash
python3 test_interface.py
```

### Tester le modèle en console
```bash
python3 modele_approvisionnement.py
```

## 📊 Données d'Exemple Incluses

Le projet inclut **2 jeux de données prêts à l'emploi** :

### 🎯 Scénario Standard (5 sites, 3 matières)
```
donnees_exemple/
├── offre.csv
├── demande.csv
├── distances.csv
├── couts_matiere_0.csv
├── couts_matiere_1.csv
├── couts_matiere_2.csv
├── capacites.csv
└── README.md (documentation détaillée)
```

**Caractéristiques** :
- ✅ Équilibré (offre = demande)
- ✅ Résolution rapide (< 1s)
- ✅ Idéal pour découvrir l'application

**Résultats attendus** :
- Coût optimal : ~42,000-55,000 DT
- Aucune rupture
- Taux satisfaction : 100%

### 🚀 Scénario Complexe (8 sites, 5 matières)
```
donnees_exemple/scenario_complexe/
├── offre.csv
├── demande.csv
└── README.md
```

**Caractéristiques** :
- ⚠️ Déséquilibré (280t de ruptures attendues)
- 🔥 Réseau étendu (8 sites)
- 🎓 Idéal pour la soutenance

## 📖 Guide Rapide

### Démarrage Ultra-Rapide (30 secondes)
1. **Lancer** : `python3 lancer.py`
2. **Onglet Paramètres** → Cliquer sur "Charger Données Exemple" 📊
3. **Onglet Résolution** → Cliquer sur "Résoudre avec Gurobi" 🚀
4. **Onglet Insights** → Voir l'analyse intelligente 🧠

### Utilisation Standard
1. **Onglet Paramètres** : Configurer sites et matières, OU charger exemple
2. **Onglet Données** : Saisir/Importer les données (offre, demande, coûts, distances, capacités)
3. **Onglet Résolution** : Cliquer sur "RÉSOUDRE AVEC GUROBI"
4. **Onglet Résultats** : Consulter les flux optimaux, ruptures, stocks
5. **Onglet Visualisation** : Explorer les graphiques interactifs
6. **Onglet Insights** : Obtenir une analyse intelligente automatique 🆕

### Import de Vos Propres Données
1. **Menu Fichier** → **Importer Données CSV**
2. Sélectionner le dossier contenant vos fichiers CSV
3. Vérifier que les fichiers respectent le format (voir `donnees_exemple/README.md`)

### Fonctionnalités Avancées v2.0 🆕
- 🌓 **Thème clair/sombre** : Menu Affichage → Basculer Thème (ou Ctrl+T)
- 📤 **Export multi-formats** : CSV, Excel, JSON, TXT
- 🧠 **Analyse intelligente** : Onglet Insights (6 types d'insights automatiques)
- 📥 **Import/Export** : Menu Fichier

## 📊 Modèle Mathématique

### Variables de Décision (continues)
- **x[i,j,m]**: Quantité de matière m transférée du site i vers j
- **s[i,m]**: Stock résiduel au site i
- **r[j,m]**: Rupture au site j
- **y[i,j]**: Flux total entre sites

### Fonction Objectif
Minimiser: Coûts de transport + Stockage + Pénalités rupture + Coûts kilométriques + Pénalités délai

### Contraintes
1. Conservation des flux
2. Satisfaction de la demande (avec rupture possible)
3. Capacités de transfert entre sites
4. Capacités d'expédition et réception
5. Lien flux détaillé/total
6. Limitation des ruptures (≤20%)
7. Priorité des matières critiques
8. Non-autolivraison

## 📁 Structure du Projet

```
Projet/
├── 📦 config/                           # Configuration
│   ├── constantes.py                    # Constantes, messages, icônes
│   └── styles.py                        # Thèmes clair/sombre (QSS)
│
├── 🛠️ utils/                            # Modules utilitaires
│   ├── logger.py                        # Logging professionnel
│   ├── validation.py                    # Validation multi-niveaux
│   ├── import_export.py                 # Import/Export multi-formats
│   └── interpretation.py                # Analyse intelligente
│
├── 📊 donnees_exemple/                  # Données d'exemple 🆕
│   ├── offre.csv                        # 5 sites, 3 matières
│   ├── demande.csv
│   ├── distances.csv
│   ├── couts_matiere_0.csv
│   ├── couts_matiere_1.csv
│   ├── couts_matiere_2.csv
│   ├── capacites.csv
│   ├── README.md                        # Documentation des données
│   └── scenario_complexe/               # Scénario avancé (8 sites, 5 matières)
│
├── 🎨 Interface
│   ├── interface_approvisionnement.py   # Interface PyQt6 v2.0
│   └── lancer.py                        # Script de lancement
│
├── 🧮 Modèle
│   └── modele_approvisionnement.py      # Modèle PL + Gurobi
│
├── 🧪 Tests
│   ├── test_interface.py                # Tests automatisés 🆕
│   └── tests_unitaires.py               # Tests existants
│
├── 📝 Documentation (16 fichiers)
│   ├── README.md                        # Ce fichier
│   ├── DOCUMENTATION.md                 # Doc technique complète
│   ├── GUIDE_UTILISATION_V2.md          # Guide utilisateur v2.0 🆕
│   ├── SYNTHESE_COMPLETE.md             # Rapport de synthèse 🆕
│   ├── ROADMAP.md                       # Feuille de route 🆕
│   ├── CHECKLIST_FINALE.md              # Checklist 145 tâches 🆕
│   ├── PROCHAINES_ETAPES.md             # Guide pour suite 🆕
│   ├── COMMANDES_UTILES.md              # Référence commandes 🆕
│   └── ... (et 8 autres fichiers)
│
└── requirements.txt                     # Dépendances
```

**Total** : ~9,170 lignes de code + 3,500+ lignes de documentation

## 🧪 Tests

Le projet inclut:
- **2 jeux de données d'exemple** (scénario standard + complexe) 🆕
- **Tests automatisés** (6 tests, tous passants ✅) 🆕
- **Validation automatique** des données (5 types de validation) 🆕
- **Tests de cohérence** des résultats

### Lancer les Tests
```bash
python3 test_interface.py
```

**Résultat attendu** : ✅ 6/6 tests passants

## 📈 Exemple de Résultats

### Scénario Standard (5 sites, 3 matières)
- **Coût optimal**: ~42,000-55,000 DT
- **Temps de résolution**: < 1 seconde
- **Volume total**: 1,820 tonnes
- **Taux de satisfaction**: 100% ✅
- **Ruptures**: Aucune

### Scénario Complexe (8 sites, 5 matières)
- **Coût optimal**: ~120,000-150,000 DT
- **Temps de résolution**: 5-15 secondes
- **Volume total**: ~7,200 tonnes
- **Taux de satisfaction**: ~96%
- **Ruptures**: 280 tonnes (déséquilibre volontaire)

## 🎓 Évaluation du Projet

### Points Forts
✅ Modèle strictement PL (pas de variables entières)  
✅ 13+ paramètres d'entrée  
✅ 9 types de contraintes  
✅ Multi-critères (coûts pondérés)  
✅ IHM complète et non-bloquante  
✅ Visualisations professionnelles  
✅ Documentation exhaustive  

### Conformité au Cahier des Charges
- ✅ Programmation Linéaire (PL)
- ✅ Solveur Gurobi
- ✅ Interface PyQt/PySide
- ✅ Résolution non-bloquante (QThread)
- ✅ Visualisation (Matplotlib)
- ✅ Analyse des résultats

## 🔧 Technologies

- **Python**: 3.8+
- **Gurobi**: 10.0+ (solveur d'optimisation)
- **PyQt6**: 6.4+ (interface graphique)
- **NumPy**: 1.21+ (calcul numérique)
- **Matplotlib**: 3.5+ (visualisation)

## 📚 Documentation

- **DOCUMENTATION.md**: Documentation complète du projet
- **ANALYSE_RESULTATS.md**: Analyse détaillée des résultats
- Code source commenté en détail

## 👥 Auteur

**Khalil Chikhaoui**  
Étudiant en ingénierie - INSAT  
Année universitaire 2025-2026

## 📧 Contact

- **Institution**: INSAT - Institut National des Sciences Appliquées et de Technologie
- **Domaine**: Recherche Opérationnelle

## 📄 Licence

Projet académique - INSAT 2025-2026

---

**Pour toute question, consultez la DOCUMENTATION.md complète.**
