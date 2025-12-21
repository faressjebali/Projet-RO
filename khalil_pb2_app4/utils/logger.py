"""
═══════════════════════════════════════════════════════════════════════════════
SYSTÈME DE LOGGING PROFESSIONNEL
OptiAppro - Optimisation de l'Approvisionnement Inter-Sites

Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
═══════════════════════════════════════════════════════════════════════════════
Ce module fournit un système de logging structuré et professionnel pour
l'application, avec rotation des fichiers et formatage adapté.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys

from config.constantes import ConfigLogging, VERSION


class LoggerApp:
    """
    Gestionnaire de logging centralisé pour l'application
    Implémente le pattern Singleton
    """
    
    _instance: Optional['LoggerApp'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'LoggerApp':
        """Pattern Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialise le système de logging"""
        if LoggerApp._initialized:
            return
        
        # Créer le dossier de logs
        self.dossier_logs = Path("logs")
        self.dossier_logs.mkdir(exist_ok=True)
        
        # Nom du fichier de log avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        self.fichier_log = self.dossier_logs / f"optiappro_{timestamp}.log"
        
        # Configuration du logger racine
        self.logger = logging.getLogger("OptiAppro")
        self.logger.setLevel(logging.DEBUG)
        
        # Éviter les doublons si déjà configuré
        if not self.logger.handlers:
            self._configurer_handlers()
        
        LoggerApp._initialized = True
        
        # Log de démarrage
        self.logger.info("═" * 70)
        self.logger.info(f"DÉMARRAGE DE L'APPLICATION - OptiAppro v{VERSION}")
        self.logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("═" * 70)
    
    def _configurer_handlers(self):
        """Configure les handlers de logging"""
        
        # Formatter commun
        formatter = logging.Formatter(
            fmt=ConfigLogging.FORMAT,
            datefmt=ConfigLogging.DATE_FORMAT
        )
        
        # Handler fichier avec rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.fichier_log,
            maxBytes=ConfigLogging.MAX_BYTES,
            backupCount=ConfigLogging.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler console (seulement INFO et plus)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    @classmethod
    def obtenir_logger(cls, nom: str = "OptiAppro") -> logging.Logger:
        """
        Obtient un logger configuré
        
        Args:
            nom: Nom du logger (généralement le nom du module)
            
        Returns:
            Logger configuré
        """
        cls()  # S'assurer que l'instance est créée
        return logging.getLogger(nom)


def obtenir_logger(nom: str = "OptiAppro") -> logging.Logger:
    """
    Fonction utilitaire pour obtenir un logger
    
    Args:
        nom: Nom du logger
        
    Returns:
        Logger configuré
        
    Exemple:
        >>> from utils.logger import obtenir_logger
        >>> logger = obtenir_logger(__name__)
        >>> logger.info("Message d'information")
    """
    return LoggerApp.obtenir_logger(nom)


class LoggerContextuel:
    """
    Context manager pour le logging d'opérations
    
    Exemple:
        >>> with LoggerContextuel("Chargement des données") as log:
        >>>     # Opération
        >>>     log.info("Données chargées")
    """
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        """
        Args:
            operation: Description de l'opération
            logger: Logger à utiliser (défaut: logger racine)
        """
        self.operation = operation
        self.logger = logger or obtenir_logger()
        self.debut = None
    
    def __enter__(self) -> logging.Logger:
        """Entrée dans le contexte"""
        self.debut = datetime.now()
        self.logger.info(f"▶ Début: {self.operation}")
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sortie du contexte"""
        duree = (datetime.now() - self.debut).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"✓ Terminé: {self.operation} ({duree:.2f}s)")
        else:
            self.logger.error(
                f"✗ Échec: {self.operation} ({duree:.2f}s) - {exc_type.__name__}: {exc_val}"
            )
        
        # Ne pas supprimer l'exception
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# DÉCORATEURS DE LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

def log_appel(fonction):
    """
    Décorateur pour logger automatiquement les appels de fonction
    
    Exemple:
        >>> @log_appel
        >>> def ma_fonction(x, y):
        >>>     return x + y
    """
    import functools
    
    @functools.wraps(fonction)
    def wrapper(*args, **kwargs):
        logger = obtenir_logger(fonction.__module__)
        nom_complet = f"{fonction.__module__}.{fonction.__name__}"
        
        logger.debug(f"→ Appel: {nom_complet}")
        
        try:
            resultat = fonction(*args, **kwargs)
            logger.debug(f"← Retour: {nom_complet}")
            return resultat
        except Exception as e:
            logger.exception(f"✗ Exception dans {nom_complet}: {e}")
            raise
    
    return wrapper


def log_performance(fonction):
    """
    Décorateur pour mesurer et logger le temps d'exécution
    
    Exemple:
        >>> @log_performance
        >>> def calcul_complexe():
        >>>     # ...
    """
    import functools
    import time
    
    @functools.wraps(fonction)
    def wrapper(*args, **kwargs):
        logger = obtenir_logger(fonction.__module__)
        nom_complet = f"{fonction.__module__}.{fonction.__name__}"
        
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        duree = time.perf_counter() - debut
        
        logger.info(f"⏱ Performance {nom_complet}: {duree:.4f}s")
        return resultat
    
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def nettoyer_anciens_logs(jours: int = 30):
    """
    Supprime les fichiers de log plus anciens que X jours
    
    Args:
        jours: Nombre de jours de rétention
    """
    logger = obtenir_logger()
    dossier_logs = Path("logs")
    
    if not dossier_logs.exists():
        return
    
    limite = datetime.now().timestamp() - (jours * 86400)
    supprimes = 0
    
    for fichier in dossier_logs.glob("optiappro_*.log*"):
        if fichier.stat().st_mtime < limite:
            try:
                fichier.unlink()
                supprimes += 1
            except Exception as e:
                logger.warning(f"Impossible de supprimer {fichier}: {e}")
    
    if supprimes > 0:
        logger.info(f"🗑 {supprimes} ancien(s) fichier(s) de log supprimé(s)")


def exporter_logs_session() -> str:
    """
    Exporte les logs de la session actuelle vers un fichier
    
    Returns:
        Chemin du fichier exporté
    """
    logger_app = LoggerApp()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fichier_export = logger_app.dossier_logs / f"session_{timestamp}.log"
    
    # Copier le fichier de log actuel
    import shutil
    shutil.copy2(logger_app.fichier_log, fichier_export)
    
    logger = obtenir_logger()
    logger.info(f"📋 Logs exportés vers: {fichier_export}")
    
    return str(fichier_export)


# Initialiser le logger au chargement du module
_logger_instance = LoggerApp()
