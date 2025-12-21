#!/usr/bin/env python3
"""
Script de test pour vérifier l'interface OptiAppro v2.0
Sans interaction utilisateur
"""

import sys
from pathlib import Path

print("\n" + "="*60)
print("🧪 TEST DE L'INTERFACE OPTIAPPRO V2.0")
print("="*60)

# Test 1: Imports des modules
print("\n[1/5] Test des imports...")
try:
    from PyQt6.QtWidgets import QApplication
    from interface_approvisionnement import FenetreApprovisionnement
    from config.styles import StyleManager
    from config.constantes import VERSION, Messages, Icones
    from utils.logger import obtenir_logger
    from utils.validation import ValidateurDonnees
    from utils.import_export import GestionnaireImportExport
    from utils.interpretation import InterpreteurResultats
    print("  ✓ Tous les modules importés avec succès")
except Exception as e:
    print(f"  ✗ Erreur d'import: {e}")
    sys.exit(1)

# Test 2: Création de l'application Qt
print("\n[2/5] Test de l'application Qt...")
try:
    app = QApplication([])
    app.setApplicationName("OptiAppro")
    app.setApplicationVersion(VERSION)
    print(f"  ✓ Application Qt créée (version {VERSION})")
except Exception as e:
    print(f"  ✗ Erreur Qt: {e}")
    sys.exit(1)

# Test 3: Initialisation du StyleManager
print("\n[3/5] Test du StyleManager...")
try:
    StyleManager.initialiser(app)
    theme_actuel = StyleManager.obtenir_theme_actuel()
    print(f"  ✓ StyleManager initialisé (thème: {theme_actuel.value})")
except Exception as e:
    print(f"  ✗ Erreur StyleManager: {e}")
    sys.exit(1)

# Test 4: Création de la fenêtre principale
print("\n[4/5] Test de la fenêtre principale...")
try:
    logger = obtenir_logger(__name__)
    logger.info("Test de création de la fenêtre")
    
    fenetre = FenetreApprovisionnement()
    print(f"  ✓ Fenêtre créée avec {fenetre.tabs.count()} onglets")
    
    # Vérifier les onglets
    onglets = []
    for i in range(fenetre.tabs.count()):
        onglets.append(fenetre.tabs.tabText(i))
    print(f"  ✓ Onglets: {', '.join(onglets)}")
    
except Exception as e:
    print(f"  ✗ Erreur fenêtre: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Vérification des gestionnaires
print("\n[5/5] Test des gestionnaires utilitaires...")
try:
    assert fenetre.gestionnaire_io is not None
    assert fenetre.validateur is not None
    assert fenetre.interpreteur is not None
    print("  ✓ GestionnaireImportExport: OK")
    print("  ✓ ValidateurDonnees: OK")
    print("  ✓ InterpreteurResultats: OK")
except Exception as e:
    print(f"  ✗ Erreur gestionnaires: {e}")
    sys.exit(1)

# Test 6: Basculement de thème
print("\n[6/6] Test du basculement de thème...")
try:
    StyleManager.basculer_theme()
    theme_apres = StyleManager.obtenir_theme_actuel()
    print(f"  ✓ Thème basculé vers: {theme_apres.value}")
    
    # Revenir au thème initial
    StyleManager.basculer_theme()
    print(f"  ✓ Retour au thème initial")
except Exception as e:
    print(f"  ✗ Erreur basculement: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ TOUS LES TESTS RÉUSSIS!")
print("="*60)
print(f"\n💡 L'interface OptiAppro v{VERSION} est fonctionnelle!")
print("💡 Lancez avec: python3 lancer.py")
print("\n📊 Statistiques:")
print(f"  - Onglets: {fenetre.tabs.count()}")
print(f"  - Gestionnaires: 3 (I/O, Validation, Interprétation)")
print(f"  - Thèmes: 2 (clair/sombre)")
print(f"  - Version Qt: PyQt6")
print(f"  - Version Python: {sys.version.split()[0]}")
print()

# Ne pas lancer l'application (test seulement)
sys.exit(0)
