"""
═══════════════════════════════════════════════════════════════════════════════
VALIDATEUR DE DONNÉES AVANCÉ
OptiAppro - Optimisation de l'Approvisionnement Inter-Sites

Projet RO - INSA 2024-2025 | Enseignant: I. AJILI
═══════════════════════════════════════════════════════════════════════════════
Ce module fournit des outils de validation robustes et détaillés pour
garantir l'intégrité des données du problème d'optimisation.
"""

from typing import List, Tuple, Dict, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum

from utils.logger import obtenir_logger

logger = obtenir_logger(__name__)


class NiveauGravite(Enum):
    """Niveaux de gravité des erreurs de validation"""
    INFO = "info"
    AVERTISSEMENT = "avertissement"
    ERREUR = "erreur"
    CRITIQUE = "critique"


@dataclass
class MessageValidation:
    """Message de validation structuré"""
    niveau: NiveauGravite
    categorie: str
    message: str
    details: Optional[str] = None
    
    def __str__(self) -> str:
        symbole = {
            NiveauGravite.INFO: "ℹ️",
            NiveauGravite.AVERTISSEMENT: "⚠️",
            NiveauGravite.ERREUR: "❌",
            NiveauGravite.CRITIQUE: "🚨"
        }
        
        texte = f"{symbole[self.niveau]} [{self.categorie}] {self.message}"
        if self.details:
            texte += f"\n  └─ {self.details}"
        return texte


class ValidateurDonnees:
    """
    Validateur complet pour les données du problème d'approvisionnement
    
    Vérifie:
    - La cohérence dimensionnelle
    - Les contraintes de non-négativité
    - L'équilibre offre-demande
    - La cohérence des capacités
    - Les valeurs aberrantes
    """
    
    def __init__(self):
        """Initialise le validateur"""
        self.messages: List[MessageValidation] = []
        self.erreurs_critiques = 0
        self.erreurs = 0
        self.avertissements = 0
    
    def reinitialiser(self):
        """Réinitialise l'état du validateur"""
        self.messages.clear()
        self.erreurs_critiques = 0
        self.erreurs = 0
        self.avertissements = 0
    
    def ajouter_message(self, niveau: NiveauGravite, categorie: str, 
                       message: str, details: Optional[str] = None):
        """Ajoute un message de validation"""
        msg = MessageValidation(niveau, categorie, message, details)
        self.messages.append(msg)
        
        if niveau == NiveauGravite.CRITIQUE:
            self.erreurs_critiques += 1
        elif niveau == NiveauGravite.ERREUR:
            self.erreurs += 1
        elif niveau == NiveauGravite.AVERTISSEMENT:
            self.avertissements += 1
        
        logger.log(
            logging.CRITICAL if niveau == NiveauGravite.CRITIQUE else
            logging.ERROR if niveau == NiveauGravite.ERREUR else
            logging.WARNING if niveau == NiveauGravite.AVERTISSEMENT else
            logging.INFO,
            str(msg)
        )
    
    def est_valide(self) -> bool:
        """Retourne True si aucune erreur critique ou erreur"""
        return self.erreurs_critiques == 0 and self.erreurs == 0
    
    def obtenir_resume(self) -> str:
        """Génère un résumé de la validation"""
        if self.est_valide():
            return f"✓ Validation réussie ({self.avertissements} avertissement(s))"
        else:
            return (f"✗ Validation échouée - "
                   f"{self.erreurs_critiques} critique(s), "
                   f"{self.erreurs} erreur(s), "
                   f"{self.avertissements} avertissement(s)")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATIONS DIMENSIONNELLES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def valider_dimensions(self, donnees) -> bool:
        """Valide la cohérence des dimensions"""
        n, m = donnees.n_sites, donnees.n_matieres
        
        # Vérifier les tailles minimales
        if n < 2:
            self.ajouter_message(
                NiveauGravite.CRITIQUE, "Dimensions",
                f"Nombre de sites insuffisant: {n} (minimum: 2)"
            )
        
        if m < 1:
            self.ajouter_message(
                NiveauGravite.CRITIQUE, "Dimensions",
                f"Nombre de matières insuffisant: {m} (minimum: 1)"
            )
        
        # Vérifier la cohérence des matrices
        verifications = [
            ("offre", donnees.offre.shape, (n, m)),
            ("demande", donnees.demande.shape, (n, m)),
            ("cout_transport", donnees.cout_transport.shape, (n, n, m)),
            ("distance", donnees.distance.shape, (n, n)),
            ("capacite_transfert", donnees.capacite_transfert.shape, (n, n)),
            ("cout_stockage", donnees.cout_stockage.shape, (n, m)),
            ("penalite_rupture", donnees.penalite_rupture.shape, (n, m)),
            ("temps_transport", donnees.temps_transport.shape, (n, n)),
        ]
        
        for nom, forme_reelle, forme_attendue in verifications:
            if forme_reelle != forme_attendue:
                self.ajouter_message(
                    NiveauGravite.CRITIQUE, "Dimensions",
                    f"Dimension incorrecte pour {nom}",
                    f"Attendu: {forme_attendue}, obtenu: {forme_reelle}"
                )
        
        return self.est_valide()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATIONS DE POSITIVITÉ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def valider_non_negativite(self, donnees) -> bool:
        """Vérifie que toutes les valeurs sont non négatives"""
        
        verifications = [
            ("offre", donnees.offre),
            ("demande", donnees.demande),
            ("cout_transport", donnees.cout_transport),
            ("distance", donnees.distance),
            ("cout_stockage", donnees.cout_stockage),
            ("penalite_rupture", donnees.penalite_rupture),
            ("temps_transport", donnees.temps_transport),
        ]
        
        for nom, matrice in verifications:
            negatifs = np.where(matrice < 0)
            if len(negatifs[0]) > 0:
                nb_negatifs = len(negatifs[0])
                valeur_min = matrice.min()
                self.ajouter_message(
                    NiveauGravite.ERREUR, "Non-négativité",
                    f"Valeurs négatives détectées dans {nom}",
                    f"{nb_negatifs} valeur(s) négative(s), min = {valeur_min:.2f}"
                )
        
        # Capacités (peuvent être infinies mais pas négatives)
        cap_neg = np.where((donnees.capacite_transfert < 0) & 
                          (donnees.capacite_transfert != float('inf')))
        if len(cap_neg[0]) > 0:
            self.ajouter_message(
                NiveauGravite.ERREUR, "Non-négativité",
                "Capacités de transfert négatives détectées"
            )
        
        return self.est_valide()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATIONS D'ÉQUILIBRE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def valider_equilibre_offre_demande(self, donnees) -> bool:
        """Vérifie l'équilibre global et par matière"""
        
        # Équilibre global
        offre_totale = donnees.offre.sum()
        demande_totale = donnees.demande.sum()
        desequilibre = offre_totale - demande_totale
        taux_desequilibre = abs(desequilibre) / max(demande_totale, 1) * 100
        
        if desequilibre < -1e-6:  # Offre insuffisante
            self.ajouter_message(
                NiveauGravite.AVERTISSEMENT, "Équilibre",
                f"Offre totale insuffisante pour la demande",
                f"Déficit: {-desequilibre:.1f} tonnes ({taux_desequilibre:.1f}%)"
            )
        elif desequilibre > demande_totale * 0.5:  # Excès important
            self.ajouter_message(
                NiveauGravite.INFO, "Équilibre",
                f"Excédent d'offre important",
                f"Surplus: {desequilibre:.1f} tonnes ({taux_desequilibre:.1f}%)"
            )
        
        # Équilibre par matière
        for m in range(donnees.n_matieres):
            offre_m = donnees.offre[:, m].sum()
            demande_m = donnees.demande[:, m].sum()
            deseq_m = offre_m - demande_m
            
            if demande_m > 0:
                taux_m = abs(deseq_m) / demande_m * 100
                
                if deseq_m < -1e-6 and taux_m > 20:
                    self.ajouter_message(
                        NiveauGravite.AVERTISSEMENT, "Équilibre",
                        f"Matière '{donnees.noms_matieres[m]}': offre insuffisante",
                        f"Déficit: {-deseq_m:.1f}t ({taux_m:.1f}%)"
                    )
        
        return self.est_valide()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATIONS DE COHÉRENCE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def valider_coherence_capacites(self, donnees) -> bool:
        """Vérifie la cohérence des capacités"""
        
        # Capacités de transfert vs capacités d'expédition/réception
        for i in range(donnees.n_sites):
            cap_exp = donnees.capacite_expedition[i]
            cap_sortie_totale = 0
            
            for j in range(donnees.n_sites):
                if i != j:
                    cap_ij = donnees.capacite_transfert[i, j]
                    if cap_ij != float('inf'):
                        cap_sortie_totale += cap_ij
            
            if cap_exp != float('inf') and cap_sortie_totale > cap_exp * 1.5:
                self.ajouter_message(
                    NiveauGravite.AVERTISSEMENT, "Cohérence",
                    f"Site '{donnees.noms_sites[i]}': capacités de transfert "
                    f"supérieures à la capacité d'expédition",
                    f"Exp: {cap_exp:.0f}t, Transferts cumulés: {cap_sortie_totale:.0f}t"
                )
        
        # Vérifier la diagonale (pas d'auto-transfert)
        for i in range(donnees.n_sites):
            if donnees.capacite_transfert[i, i] != 0:
                self.ajouter_message(
                    NiveauGravite.ERREUR, "Cohérence",
                    f"Capacité d'auto-transfert non nulle pour '{donnees.noms_sites[i]}'"
                )
        
        return self.est_valide()
    
    def valider_coherence_distances(self, donnees) -> bool:
        """Vérifie la cohérence des distances"""
        
        # Symétrie
        if not np.allclose(donnees.distance, donnees.distance.T, atol=1e-6):
            self.ajouter_message(
                NiveauGravite.AVERTISSEMENT, "Cohérence",
                "Matrice des distances non symétrique"
            )
        
        # Diagonale nulle
        if not np.allclose(np.diag(donnees.distance), 0, atol=1e-6):
            self.ajouter_message(
                NiveauGravite.ERREUR, "Cohérence",
                "Distances non nulles sur la diagonale (auto-distance)"
            )
        
        # Inégalité triangulaire (échantillon)
        violations = 0
        for i in range(min(5, donnees.n_sites)):
            for j in range(min(5, donnees.n_sites)):
                for k in range(min(5, donnees.n_sites)):
                    if i != j and j != k and i != k:
                        d_ij = donnees.distance[i, j]
                        d_jk = donnees.distance[j, k]
                        d_ik = donnees.distance[i, k]
                        
                        if d_ik > d_ij + d_jk + 1:  # Tolérance
                            violations += 1
        
        if violations > 0:
            self.ajouter_message(
                NiveauGravite.AVERTISSEMENT, "Cohérence",
                f"Inégalité triangulaire violée ({violations} cas détectés)"
            )
        
        return self.est_valide()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATION COMPLÈTE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def valider_tout(self, donnees) -> Tuple[bool, List[MessageValidation]]:
        """
        Effectue une validation complète des données
        
        Args:
            donnees: Instance de ModeleDonneesApprovisionnement
            
        Returns:
            (valide, liste_messages)
        """
        self.reinitialiser()
        
        logger.info("🔍 Début de la validation complète des données...")
        
        # Validations
        self.valider_dimensions(donnees)
        self.valider_non_negativite(donnees)
        self.valider_equilibre_offre_demande(donnees)
        self.valider_coherence_capacites(donnees)
        self.valider_coherence_distances(donnees)
        
        # Statistiques
        logger.info(self.obtenir_resume())
        
        return self.est_valide(), self.messages.copy()
    
    def generer_rapport_html(self) -> str:
        """Génère un rapport de validation en HTML"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .critique { color: #c0392b; font-weight: bold; }
                .erreur { color: #e74c3c; }
                .avertissement { color: #f39c12; }
                .info { color: #3498db; }
                .message { margin: 10px 0; padding: 10px; border-left: 4px solid; }
            </style>
        </head>
        <body>
            <h1>Rapport de Validation</h1>
            <p><strong>{}</strong></p>
        """.format(self.obtenir_resume())
        
        for msg in self.messages:
            classe = msg.niveau.value
            html += f'<div class="message {classe}">{msg}</div>'
        
        html += "</body></html>"
        return html


import logging
