#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
LANCEUR PRINCIPAL - OPTIAPPRO V2.1
Optimisation de l'Approvisionnement Inter-Sites

INSAT - Année universitaire 2025-2026 | Réalisé par: Khalil Chikhaoui
═══════════════════════════════════════════════════════════════════════════════
Ce script lance l'application avec un écran de démarrage professionnel.
"""

import sys
import subprocess
import time
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))


def afficher_banniere():
    """Affiche une bannière ASCII au démarrage"""
    banniere = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗ ██████╗ ████████╗██╗ █████╗ ██████╗ ██████╗ ██████╗  ██████╗        ║
║  ██╔═══██╗██╔══██╗╚══██╔══╝██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔═══██╗       ║
║  ██║   ██║██████╔╝   ██║   ██║███████║██████╔╝██████╔╝██████╔╝██║   ██║       ║
║  ██║   ██║██╔═══╝    ██║   ██║██╔══██║██╔═══╝ ██╔═══╝ ██╔══██╗██║   ██║       ║
║  ╚██████╔╝██║        ██║   ██║██║  ██║██║     ██║     ██║  ██║╚██████╔╝       ║
║   ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝        ║
║                                                                               ║
║                    Optimisation de l'Approvisionnement v2.1                   ║
║                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │  📦 Gestion des flux inter-sites        │  🚀 Résolution Gurobi        │  ║
║  │  📊 Visualisations avancées             │  🧠 Analyse intelligente     │  ║
║  │  🎨 Interface moderne PyQt6             │  📁 Import/Export multi      │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
║               INSAT • 2025-2026 • Réalisé par Khalil Chikhaoui                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banniere)


def verifier_dependances():
    """Vérifie que toutes les dépendances sont installées"""
    dependances = {
        'gurobipy': 'Gurobi Optimizer',
        'PyQt6': 'PyQt6',
        'numpy': 'NumPy',
        'matplotlib': 'Matplotlib',
        'pandas': 'Pandas',
        'seaborn': 'Seaborn',
        'openpyxl': 'OpenPyXL'
    }
    
    manquantes = []
    
    print("=" * 60)
    print("🔍 Vérification des dépendances...")
    print("=" * 60)
    
    for module, nom in dependances.items():
        try:
            __import__(module)
            print(f"✓ {nom:20} installé")
        except ImportError:
            print(f"✗ {nom:20} manquant")
            manquantes.append(module)
    
    print("=" * 60)
    return manquantes

def installer_dependances(manquantes):
    """Installe les dépendances manquantes"""
    if not manquantes:
        return True
    
    print(f"\n{len(manquantes)} dépendance(s) manquante(s)")
    reponse = input("Voulez-vous les installer maintenant? (o/n): ")
    
    if reponse.lower() == 'o':
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + manquantes)
            print("\n✓ Installation réussie")
            return True
        except subprocess.CalledProcessError:
            print("\n✗ Échec de l'installation")
            return False
    
    return False

def verifier_gurobi():
    """Vérifie que Gurobi est correctement configuré"""
    try:
        import gurobipy as gp
        env = gp.Env()
        env.dispose()
        print("✓ Licence Gurobi valide")
        return True
    except Exception as e:
        print(f"✗ Problème avec la licence Gurobi: {e}")
        print("\nPour obtenir une licence académique gratuite:")
        print("1. Allez sur https://www.gurobi.com/academia/")
        print("2. Créez un compte et téléchargez votre clé de licence")
        print("3. Exécutez: grbgetkey VOTRE-CLE")
        return False

def lancer_application():
    """Lance l'application principale avec Splash Screen moderne"""
    print("\n" + "="*60)
    print("🚀 LANCEMENT DE L'APPLICATION OPTIAPPRO V2.0")
    print("="*60)
    
    try:
        from PyQt6.QtWidgets import QApplication, QSplashScreen
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QLinearGradient, QPen, QBrush
        from interface_approvisionnement import FenetreApprovisionnement
        from config.styles import StyleManager
        from config.constantes import VERSION
        from utils.logger import obtenir_logger
        
        logger = obtenir_logger(__name__)
        
        print(f"\n✓ Chargement des modules...")
        print(f"✓ Version: {VERSION}")
        
        # Créer l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("OptiAppro")
        app.setApplicationVersion(VERSION)
        app.setOrganizationName("INSAT")
        app.setStyle('Fusion')
        
        print("✓ Application Qt créée")
        
        # ═══════════════════════════════════════════════════════════════
        # SPLASH SCREEN MODERNE
        # ═══════════════════════════════════════════════════════════════
        
        # Créer pixmap pour splash screen
        width, height = 550, 350
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fond avec gradient
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor("#1e3a5f"))
        gradient.setColorAt(0.5, QColor("#0f2744"))
        gradient.setColorAt(1, QColor("#0a1929"))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, width, height, 20, 20)
        
        # Bordure
        pen = QPen(QColor("#3b82f6"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(1, 1, width-2, height-2, 20, 20)
        
        # Icône
        painter.setPen(QColor("#3b82f6"))
        font_icon = QFont("Segoe UI Emoji", 48)
        painter.setFont(font_icon)
        painter.drawText(width // 2 - 30, 80, "📦")
        
        # Titre
        painter.setPen(QColor("#ffffff"))
        font_titre = QFont("Segoe UI", 28, QFont.Weight.Bold)
        painter.setFont(font_titre)
        painter.drawText(0, 120, width, 50, Qt.AlignmentFlag.AlignCenter, "OptiAppro")
        
        # Sous-titre
        painter.setPen(QColor("#94a3b8"))
        font_sous = QFont("Segoe UI", 12)
        painter.setFont(font_sous)
        painter.drawText(0, 165, width, 30, Qt.AlignmentFlag.AlignCenter, 
                        "Optimisation de l'Approvisionnement Inter-Sites")
        
        # Version
        painter.setPen(QColor("#3b82f6"))
        font_version = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font_version)
        painter.drawText(0, 195, width, 25, Qt.AlignmentFlag.AlignCenter, f"Version {VERSION}")
        
        # Info projet - INSAT 2025-2026 - Khalil Chikhaoui
        painter.setPen(QColor("#64748b"))
        font_info = QFont("Segoe UI", 9)
        painter.setFont(font_info)
        painter.drawText(0, 310, width, 20, Qt.AlignmentFlag.AlignCenter,
                        "INSAT • 2025-2026 • Réalisé par Khalil Chikhaoui")
        
        painter.end()
        
        # Afficher le splash screen
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        splash.show()
        
        # Messages de chargement
        etapes = [
            "Chargement des modules...",
            "Initialisation de PyQt6...",
            "Configuration des styles...",
            "Chargement des utilitaires...",
            "Initialisation de Gurobi...",
            "Préparation de l'interface...",
            "Finalisation...",
        ]
        
        for etape in etapes:
            splash.showMessage(
                f"  {etape}",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                QColor("#94a3b8")
            )
            app.processEvents()
            time.sleep(0.2)
        
        print("✓ Splash screen affiché")
        
        # Initialiser le StyleManager
        StyleManager.initialiser(app)
        print("✓ StyleManager initialisé (thème clair)")
        
        logger.info("="*80)
        logger.info(f"🎨 Application OptiAppro v{VERSION} démarrée")
        logger.info("="*80)
        
        # Créer et afficher la fenêtre principale
        fenetre = FenetreApprovisionnement()
        
        # Fermer splash et afficher fenêtre
        splash.finish(fenetre)
        fenetre.show()
        
        # Message de bienvenue
        fenetre.statusBar().showMessage(
            "✨ Bienvenue dans OptiAppro v2.0 - Prêt à optimiser !",
            5000
        )
        
        print("✓ Interface affichée")
        print("\n" + "="*60)
        print("✅ APPLICATION PRÊTE!")
        print("="*60)
        print("\n💡 Raccourcis clavier:")
        print("   • Ctrl+T : Basculer thème clair/sombre")
        print("   • Ctrl+O : Importer des données")
        print("   • Ctrl+S : Exporter les résultats")
        print("   • Ctrl+Q : Quitter\n")
        
        # Lancer la boucle d'événements
        exit_code = app.exec()
        
        logger.info("👋 Application fermée normalement")
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n✗ Erreur au lancement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Point d'entrée principal"""
    # Afficher la bannière ASCII
    afficher_banniere()
    
    print("\n[1/3] Vérification des dépendances...")
    manquantes = verifier_dependances()
    
    if manquantes:
        if not installer_dependances(manquantes):
            print("\n❌ Impossible de continuer sans les dépendances.")
            print("📝 Installez-les manuellement avec: pip install -r requirements.txt")
            sys.exit(1)
    
    print("\n[2/3] Vérification de la licence Gurobi...")
    if not verifier_gurobi():
        reponse = input("\nVoulez-vous continuer sans Gurobi (mode démo)? (o/n): ")
        if reponse.lower() != 'o':
            sys.exit(1)
    
    print("\n[3/3] Tout est prêt!")
    lancer_application()


if __name__ == "__main__":
    main()
