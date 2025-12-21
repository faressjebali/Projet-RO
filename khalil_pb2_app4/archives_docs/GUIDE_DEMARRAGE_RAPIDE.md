# ⚡ GUIDE DE DÉMARRAGE RAPIDE - OPTIAPPRO V2.0

**Temps de lecture : 3 minutes | Temps de prise en main : 5 minutes**

---

## 🎯 En 30 Secondes

```bash
# 1. Lancer l'application
cd /home/khalil/Desktop/Projet
python3 lancer.py

# 2. Charger l'exemple (bouton dans l'onglet Paramètres)
# 3. Résoudre (bouton dans l'onglet Résolution)
# 4. Voir les résultats (onglets Résultats, Visualisation, Insights)
```

**C'est tout ! Vous avez résolu votre premier problème d'optimisation ! 🎉**

---

## 📋 Checklist de Premier Lancement

### ✅ Étape 1 : Installation (2 minutes)
```bash
# Installer les dépendances
pip install -r requirements.txt
```

**Dépendances nécessaires** :
- ✅ Python 3.8+
- ✅ Gurobi (avec licence académique gratuite)
- ✅ PyQt6
- ✅ NumPy, Matplotlib, Pandas, Seaborn

### ✅ Étape 2 : Lancement (5 secondes)
```bash
python3 lancer.py
```

**Résultat** : Fenêtre de l'application avec 6 onglets

### ✅ Étape 3 : Charger l'Exemple (10 secondes)
1. Aller dans l'onglet **⚙️ Paramètres**
2. Cliquer sur **"Charger Données Exemple"** 📊
3. ✅ Les données sont chargées automatiquement !

### ✅ Étape 4 : Résoudre (5 secondes)
1. Aller dans l'onglet **🚀 Résolution**
2. Cliquer sur **"Résoudre avec Gurobi"**
3. Attendre 1-2 secondes... ⏳
4. ✅ Solution optimale trouvée !

### ✅ Étape 5 : Explorer les Résultats (2 minutes)

#### Onglet 📈 Résultats
- **Tableaux** : Flux optimaux, ruptures, stocks
- **Métriques** : Coût total, satisfaction, temps résolution

#### Onglet 📉 Visualisation
- **Graphique de flux** : Réseau entre sites
- **Diagramme circulaire** : Répartition des coûts

#### Onglet 🧠 Insights (NOUVEAU !)
- **Analyse automatique** : 6 types d'insights
- **Recommandations** : Actions à prendre
- **Points clés** : Performance, flux dominants, ruptures

---

## 🎨 Fonctionnalités Clés

### 1. Thèmes Clair/Sombre 🌓
**Raccourci** : `Ctrl + T`  
**Menu** : Affichage → Basculer Thème

### 2. Import de Données 📥
**Menu** : Fichier → Importer Données CSV  
**Formats** : Dossier contenant offre.csv, demande.csv, etc.  
**Exemple** : `donnees_exemple/`

### 3. Export de Résultats 📤
**Menu** : Fichier → Exporter Résultats  
**Formats disponibles** :
- CSV (simple)
- Excel (multi-feuilles)
- JSON (scénario complet)
- TXT (rapport formaté)

### 4. Analyse Intelligente 🧠
**Onglet** : Insights  
**Bouton** : "Analyser les Résultats"  
**Résultat** : Rapport HTML avec :
- ✅ Taux de satisfaction
- ✅ Flux dominants
- ✅ Ruptures détectées
- ✅ Hubs identifiés
- ✅ Recommandations

---

## 📊 Utiliser Vos Propres Données

### Format des Fichiers CSV

Créez un dossier avec ces fichiers :

```
mes_donnees/
├── offre.csv               # Offre par site et matière
├── demande.csv             # Demande par site et matière
├── distances.csv           # Distances entre sites (km)
├── couts_matiere_0.csv     # Coûts transport matière 1
├── couts_matiere_1.csv     # Coûts transport matière 2
├── ...                     # Un fichier par matière
└── capacites.csv           # Capacités de transfert
```

### Exemple de Contenu (offre.csv)
```csv
,M1,M2,M3
Site_A,150,80,120
Site_B,200,100,90
Site_C,100,120,150
```

**Format** :
- Première ligne = en-têtes (noms des matières)
- Première colonne = noms des sites
- Séparateur = virgule (,)
- Valeurs = nombres positifs

### Importer
1. **Menu** : Fichier → Importer Données CSV
2. **Sélectionner** : Votre dossier `mes_donnees/`
3. **Valider** : Les données sont chargées et validées ✅

---

## ⚠️ Résolution de Problèmes Courants

### Problème : "Module 'gurobipy' not found"
**Solution** :
```bash
pip install gurobipy
# Puis configurer la licence :
grbgetkey VOTRE-CLE-ACADEMIQUE
```

### Problème : "Licence Gurobi invalide"
**Solution** :
1. Obtenir une licence académique gratuite sur [gurobi.com/academia](https://www.gurobi.com/academia/)
2. Exécuter : `grbgetkey VOTRE-CLE`
3. Relancer l'application

### Problème : "Format de fichier CSV invalide"
**Solution** :
- Vérifier que le séparateur est bien une **virgule** (,)
- Vérifier qu'il y a bien une ligne d'en-têtes
- Pas d'espaces dans les noms de colonnes
- Utiliser `donnees_exemple/` comme référence

### Problème : "Offre insuffisante pour satisfaire la demande"
**Solution** :
- C'est normal ! L'application génère des **ruptures**
- Consulter l'onglet **Résultats** pour voir les ruptures
- Augmenter l'offre dans `offre.csv` si souhaité

### Problème : L'interface ne s'affiche pas
**Solution** :
```bash
# Vérifier PyQt6
pip install --upgrade PyQt6

# Tester l'interface
python3 test_interface.py
```

---

## 🚀 Workflow Complet

### Pour un Nouveau Problème

```mermaid
1. Paramètres → Configurer dimensions (sites, matières)
2. Données → Saisir/Importer données
3. Données → Valider (bouton "Valider les Données")
4. Résolution → Résoudre avec Gurobi
5. Résultats → Consulter flux, ruptures, stocks
6. Visualisation → Explorer graphiques
7. Insights → Analyser intelligemment
8. Fichier → Exporter résultats (CSV, Excel, JSON)
```

### Pour Comparer des Scénarios

```mermaid
1. Résoudre scénario 1
2. Fichier → Exporter Résultats → JSON (scenario_1.json)
3. Modifier les données
4. Résoudre scénario 2
5. Fichier → Exporter Résultats → JSON (scenario_2.json)
6. Comparer manuellement les métriques
```

---

## 🎓 Conseils pour la Soutenance

### Démo Live Recommandée (3 minutes)

1. **[30s] Lancement** : `python3 lancer.py`
2. **[20s] Charger exemple** : Bouton "Charger Données Exemple"
3. **[30s] Résolution** : Cliquer sur "Résoudre", montrer la progression
4. **[40s] Résultats** : Parcourir les 3 onglets (Résultats, Visualisation, Insights)
5. **[30s] Fonctionnalités** : 
   - Basculer thème (Ctrl+T)
   - Montrer export (menu Fichier)
   - Montrer analyse intelligente (onglet Insights)
6. **[30s] Questions** : Répondre aux questions

### Points Clés à Mentionner

✅ "Interface professionnelle avec 6 onglets"  
✅ "Résolution en moins d'1 seconde pour 5 sites"  
✅ "Analyse intelligente automatique avec 6 types d'insights"  
✅ "Export multi-formats (CSV, Excel, JSON)"  
✅ "Thèmes clair/sombre pour accessibilité"  
✅ "Architecture modulaire avec 9,000+ lignes de code"

### En Cas de Problème Technique

**Plan B** : Avoir des **captures d'écran** prêtes
- Vue d'ensemble de l'interface
- Résultats d'une résolution réussie
- Graphiques de flux
- Onglet Insights avec analyse

---

## 📚 Documentation Complète

- **[SYNTHESE_COMPLETE.md](SYNTHESE_COMPLETE.md)** - Rapport de synthèse exhaustif (⭐ RECOMMANDÉ)
- **[GUIDE_UTILISATION_V2.md](GUIDE_UTILISATION_V2.md)** - Guide utilisateur détaillé
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Documentation technique
- **[COMMANDES_UTILES.md](COMMANDES_UTILES.md)** - Référence de toutes les commandes

---

## ✅ Checklist Avant la Soutenance

- [ ] Application lance sans erreur
- [ ] Données d'exemple fonctionnent
- [ ] Résolution donne un résultat optimal
- [ ] Tous les onglets s'affichent correctement
- [ ] Export fonctionne (au moins CSV)
- [ ] Captures d'écran de backup prêtes
- [ ] PowerPoint préparé
- [ ] Timing répété (15-20 min)

---

**🎉 Vous êtes prêt ! Bonne chance pour votre soutenance !**

---

**Version** : OptiAppro v2.0.0  
**Date** : 17 Décembre 2025  
**Contact** : Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
