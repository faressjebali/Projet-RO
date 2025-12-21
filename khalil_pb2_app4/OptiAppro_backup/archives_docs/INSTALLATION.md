# 🔧 GUIDE D'INSTALLATION

## Prérequis

### Système d'exploitation
- Linux, Windows ou macOS
- Python 3.8 ou supérieur

### Vérifier votre version de Python
```bash
python --version
# ou
python3 --version
```

## Installation Pas-à-Pas

### Étape 1: Obtenir le Projet

Si vous avez le projet dans un dossier:
```bash
cd /chemin/vers/Projet
```

### Étape 2: Créer un Environnement Virtuel (Recommandé)

#### Sur Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Sur Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Étape 3: Installer les Dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dépendances installées:**
- gurobipy (10.0+)
- PyQt6 (6.4+)
- numpy (1.21+)
- matplotlib (3.5+)

### Étape 4: Configurer Gurobi (Licence Académique GRATUITE)

#### 4.1 Créer un Compte Académique

1. Allez sur: https://www.gurobi.com/academia/academic-program-and-licenses/
2. Cliquez sur "Request an Academic License"
3. Créez un compte avec votre email académique (@insat.tn)
4. Connectez-vous

#### 4.2 Télécharger votre Clé de Licence

1. Dans votre compte, allez dans "Academic License"
2. Cliquez sur "Generate License"
3. Vous obtiendrez une commande comme:
   ```
   grbgetkey 12345678-1234-1234-1234-123456789abc
   ```

#### 4.3 Activer la Licence

**Sur Linux/macOS:**
```bash
grbgetkey 12345678-1234-1234-1234-123456789abc
```

**Sur Windows:**
```bash
grbgetkey.exe 12345678-1234-1234-1234-123456789abc
```

La licence sera installée dans votre répertoire personnel.

#### 4.4 Vérifier l'Installation

```bash
python -c "import gurobipy as gp; env = gp.Env(); print('Gurobi OK')"
```

Si vous voyez "Gurobi OK", l'installation est réussie!

### Étape 5: Tester l'Application

#### Test Rapide (Console)
```bash
python modele_approvisionnement.py
```

Vous devriez voir:
```
==================================================
SYSTÈME D'OPTIMISATION DE L'APPROVISIONNEMENT
==================================================
[1/4] Initialisation des données...
[2/4] Validation des données...
...
✓ Solution optimale trouvée
```

#### Lancement de l'Interface Graphique
```bash
python interface_approvisionnement.py
```

**OU** utiliser le script de lancement:
```bash
python lancer.py
```

## Problèmes Courants et Solutions

### Problème 1: "ModuleNotFoundError: No module named 'gurobipy'"

**Solution:**
```bash
pip install gurobipy
```

### Problème 2: "GurobiError: No Gurobi license found"

**Causes possibles:**
1. Licence non installée
2. Licence expirée (les licences académiques durent 1 an)
3. Connexion réseau requise (certaines licences académiques)

**Solutions:**
- Vérifier: `grbprobe` (commande Gurobi de diagnostic)
- Réinstaller la licence avec `grbgetkey`
- Pour licence académique: être connecté au réseau universitaire ou VPN

### Problème 3: "ModuleNotFoundError: No module named 'PyQt6'"

**Solution:**
```bash
pip install PyQt6
```

### Problème 4: L'interface ne s'affiche pas (Linux)

**Cause:** Dépendances système manquantes

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyqt6 libxcb-xinerama0
```

**Solution (Fedora):**
```bash
sudo dnf install python3-pyqt6
```

### Problème 5: Erreur matplotlib sur macOS

**Solution:**
```bash
pip install --upgrade matplotlib
```

Si problème persiste:
```bash
brew install pkg-config
pip install --force-reinstall matplotlib
```

## Installation Alternative (Sans Environnement Virtuel)

Si vous ne pouvez pas créer d'environnement virtuel:

```bash
pip install --user gurobipy PyQt6 numpy matplotlib
```

## Vérification Complète

Script de test:
```bash
python lancer.py
```

Ce script vérifie:
- ✓ Toutes les dépendances installées
- ✓ Licence Gurobi valide
- ✓ Lance l'application

## Support

### Documentation
- `DOCUMENTATION.md`: Documentation complète du projet
- `ANALYSE_RESULTATS.md`: Analyse détaillée des résultats
- `README.md`: Guide rapide

### Ressources Externes
- **Gurobi**: https://www.gurobi.com/documentation/
- **PyQt6**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Python**: https://docs.python.org/3/

### Contact Académique
- **Enseignant**: I. AJILI
- **Institution**: INSA

## Configuration Avancée (Optionnel)

### Augmenter le Temps Limite de Gurobi

Dans `modele_approvisionnement.py`, ligne ~350:
```python
self.modele.setParam('TimeLimit', 300)  # 300 secondes par défaut
```

### Changer le Style de l'Interface

Dans `interface_approvisionnement.py`, fonction `main()`:
```python
app.setStyle('Fusion')  # Styles disponibles: Fusion, Windows, macOS
```

### Exporter les Résultats

Ajouter après la résolution:
```python
# Dans interface_approvisionnement.py
import json
with open('resultats.json', 'w') as f:
    json.dump(modele.resultats, f, indent=2)
```

## Désinstallation

Pour supprimer complètement:

```bash
# Désactiver l'environnement virtuel
deactivate

# Supprimer le dossier
rm -rf venv/

# Désinstaller les packages (si installation globale)
pip uninstall gurobipy PyQt6 numpy matplotlib -y
```

---

**Bon travail sur votre projet! 🚀**
