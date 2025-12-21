# 🛠️ COMMANDES UTILES - OPTIAPPRO V2.0

## 🚀 Lancement de l'Application

### Lancement Normal
```bash
cd /home/khalil/Desktop/Projet
python3 lancer.py
```

### Lancement avec Tests
```bash
python3 test_interface.py
```

---

## 📦 Gestion des Dépendances

### Installer Toutes les Dépendances
```bash
pip install -r requirements.txt
```

### Vérifier les Dépendances Installées
```bash
pip list | grep -E "(gurobipy|PyQt6|numpy|matplotlib|pandas|seaborn|openpyxl)"
```

### Installer Dépendances Manquantes
```bash
# Core
pip install gurobipy PyQt6 numpy matplotlib

# Avancées
pip install pandas seaborn openpyxl xlrd

# Optionnelles
pip install reportlab networkx pillow

# Dev
pip install pytest pytest-qt black pylint flake8
```

---

## 🧪 Tests

### Tests Automatisés Interface
```bash
python3 test_interface.py
```

### Tests Unitaires (existants)
```bash
python3 tests_unitaires.py
```

### Tests avec Pytest (à créer)
```bash
pytest tests/ -v
```

---

## 🔍 Vérification du Code

### Vérifier Syntaxe Python
```bash
python3 -m py_compile interface_approvisionnement.py
python3 -m py_compile modele_approvisionnement.py
python3 -m py_compile lancer.py
```

### Linter avec Pylint
```bash
pylint interface_approvisionnement.py
pylint modele_approvisionnement.py
pylint config/*.py
pylint utils/*.py
```

### Formattage avec Black
```bash
black interface_approvisionnement.py
black modele_approvisionnement.py
black config/ utils/
```

### Vérification Style avec Flake8
```bash
flake8 interface_approvisionnement.py --max-line-length=100
flake8 modele_approvisionnement.py --max-line-length=100
```

---

## 📊 Logs

### Afficher les Logs Récents
```bash
cat logs/optiappro_$(date +%Y%m%d).log
```

### Suivre les Logs en Temps Réel
```bash
tail -f logs/optiappro_$(date +%Y%m%d).log
```

### Rechercher Erreurs dans les Logs
```bash
grep -i "error" logs/*.log
grep -i "erreur" logs/*.log
grep -i "exception" logs/*.log
```

### Nettoyer Anciens Logs
```bash
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 📁 Gestion des Fichiers

### Compter Lignes de Code
```bash
# Total
find . -name "*.py" -not -path "./__pycache__/*" | xargs wc -l

# Par catégorie
wc -l config/*.py
wc -l utils/*.py
wc -l *.py
```

### Rechercher dans le Code
```bash
# Rechercher une fonction
grep -r "def nom_fonction" --include="*.py"

# Rechercher une classe
grep -r "class NomClasse" --include="*.py"

# Rechercher un import
grep -r "from config" --include="*.py"
```

### Créer Archive du Projet
```bash
# ZIP
zip -r OptiAppro_v2.0.zip . -x "*.pyc" "*__pycache__*" "*.log" ".git/*"

# TAR.GZ
tar -czf OptiAppro_v2.0.tar.gz \
  --exclude="*.pyc" \
  --exclude="__pycache__" \
  --exclude="*.log" \
  --exclude=".git" \
  .
```

---

## 🗂️ Structure des Dossiers

### Créer Dossiers Nécessaires
```bash
mkdir -p logs exports imports scenarios
```

### Vérifier Structure
```bash
tree -L 2 -I '__pycache__|*.pyc'
```

### Nettoyer Fichiers Cache
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

---

## 🔧 Gurobi

### Vérifier Licence Gurobi
```bash
python3 -c "import gurobipy as gp; print(gp.gurobi.version())"
```

### Tester Gurobi Simple
```bash
python3 -c "
import gurobipy as gp
m = gp.Model()
x = m.addVar(name='x')
m.setObjective(x, gp.GRB.MAXIMIZE)
m.addConstr(x <= 10)
m.optimize()
print(f'Solution: {x.X}')
"
```

---

## 📸 Captures d'Écran (Linux)

### Capture Fenêtre Active (après 5s)
```bash
sleep 5 && gnome-screenshot -w -f captures/fenetre_principale.png
```

### Capture Zone Sélectionnée
```bash
gnome-screenshot -a -f captures/zone_selection.png
```

### Capture Écran Complet
```bash
gnome-screenshot -f captures/ecran_complet.png
```

---

## 🎥 Enregistrement Vidéo (Linux)

### Avec SimpleScreenRecorder
```bash
simplescreenrecorder
```

### Avec FFmpeg
```bash
ffmpeg -f x11grab -s 1920x1080 -i :0.0 demo_optiappro.mp4
```

---

## 📄 Documentation

### Générer Documentation Sphinx (à créer)
```bash
# Installation
pip install sphinx sphinx-rtd-theme

# Initialisation
sphinx-quickstart docs

# Génération
cd docs && make html
```

### Convertir Markdown en PDF
```bash
# Avec pandoc
pandoc DOCUMENTATION.md -o DOCUMENTATION.pdf

# Avec grip (preview GitHub)
grip DOCUMENTATION.md
```

---

## 🐍 Python Virtual Environment

### Créer Environnement Virtuel
```bash
python3 -m venv venv_optiappro
```

### Activer Environnement
```bash
source venv_optiappro/bin/activate  # Linux/Mac
# ou
venv_optiappro\Scripts\activate  # Windows
```

### Désactiver Environnement
```bash
deactivate
```

### Sauvegarder Dépendances
```bash
pip freeze > requirements_exact.txt
```

---

## 🔄 Git (Si Versioning)

### Initialiser Dépôt
```bash
git init
git add .
git commit -m "Initial commit OptiAppro v2.0"
```

### Créer Tag Version
```bash
git tag -a v2.0.0 -m "Version 2.0.0 - Interface modernisée"
git push origin v2.0.0
```

### Ignorer Fichiers
```bash
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.log
logs/
exports/
imports/
venv_optiappro/
.vscode/
.idea/
*.zip
*.tar.gz
EOF
```

---

## 📊 Statistiques Projet

### Compter Fichiers par Type
```bash
find . -name "*.py" | wc -l
find . -name "*.md" | wc -l
find . -name "*.csv" | wc -l
```

### Statistiques Git (Si Versioning)
```bash
git log --oneline | wc -l  # Nombre de commits
git shortlog -sn            # Contributions par auteur
```

### Taille du Projet
```bash
du -sh .
du -sh --exclude=venv_optiappro .
```

---

## 🚨 Dépannage

### Erreur Import PyQt6
```bash
pip install --upgrade PyQt6 PyQt6-Qt6
```

### Erreur Import Gurobi
```bash
# Vérifier licence
ls -la ~/gurobi.lic

# Réactiver licence
grbgetkey YOUR_LICENSE_KEY
```

### Erreur Matplotlib Backend
```bash
export MPLBACKEND=Qt5Agg
# ou dans le code
import matplotlib
matplotlib.use('Qt5Agg')
```

### Permission Denied
```bash
chmod +x lancer.py
chmod +x test_interface.py
```

---

## 🎯 Commandes de Production

### Lancement Production (Sans Logs Console)
```bash
python3 lancer.py > /dev/null 2>&1 &
```

### Lancement avec Profiling
```bash
python3 -m cProfile -o profiling.stats lancer.py
```

### Analyse Profiling
```bash
python3 -m pstats profiling.stats
# Puis dans l'interpréteur:
# >>> sort time
# >>> stats 10
```

---

## 📦 Export Final pour Remise

### Créer Archive Complète
```bash
# Créer dossier de remise
mkdir -p Remise_OptiAppro_v2.0

# Copier fichiers essentiels
cp -r config utils *.py requirements.txt Remise_OptiAppro_v2.0/
cp -r *.md Remise_OptiAppro_v2.0/

# Créer archive
zip -r Remise_OptiAppro_v2.0.zip Remise_OptiAppro_v2.0/

echo "✅ Archive créée: Remise_OptiAppro_v2.0.zip"
```

### Vérifier Archive
```bash
unzip -l Remise_OptiAppro_v2.0.zip
```

---

## 📝 Commandes Rapides Quotidiennes

```bash
# Routine du matin
cd /home/khalil/Desktop/Projet
python3 test_interface.py  # Tests
python3 lancer.py           # Lancement

# Routine du soir
git add .
git commit -m "Session du $(date +%Y-%m-%d)"
git push
```

---

## 🆘 Commandes d'Urgence

### Backup Rapide
```bash
cp -r . ../Backup_OptiAppro_$(date +%Y%m%d_%H%M%S)
```

### Restaurer Backup
```bash
cp -r ../Backup_OptiAppro_YYYYMMDD_HHMMSS/* .
```

### Réinitialiser Environnement
```bash
rm -rf __pycache__ logs/*.log
pip install -r requirements.txt --force-reinstall
```

---

**Date**: 17 Décembre 2025  
**Version**: OptiAppro v2.0.0  
**Maintenu par**: Projet RO - INSA

---

*📝 Astuce: Créez un alias pour les commandes fréquentes*
```bash
# Ajouter à ~/.bashrc ou ~/.zshrc
alias optiappro='cd /home/khalil/Desktop/Projet && python3 lancer.py'
alias optitest='cd /home/khalil/Desktop/Projet && python3 test_interface.py'
```
