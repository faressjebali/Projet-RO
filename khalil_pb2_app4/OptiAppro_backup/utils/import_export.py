"""
═══════════════════════════════════════════════════════════════════════════════
GESTIONNAIRE D'IMPORT/EXPORT
OptiAppro - Optimisation de l'Approvisionnement Inter-Sites

INSAT - Année universitaire 2025-2026 | Réalisé par: Khalil Chikhaoui
═══════════════════════════════════════════════════════════════════════════════
Ce module gère l'import et l'export des données et résultats dans différents
formats (CSV, Excel, JSON).
"""

import csv
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from utils.logger import obtenir_logger, LoggerContextuel

logger = obtenir_logger(__name__)


class GestionnaireImportExport:
    """
    Gestionnaire centralisé pour toutes les opérations d'import/export
    
    Formats supportés:
    - CSV: Import/export des données et résultats
    - Excel: Export des résultats (si pandas disponible)
    - JSON: Sauvegarde complète des scénarios
    - TXT: Rapports textuels
    """
    
    def __init__(self):
        """Initialise le gestionnaire"""
        self.dossier_exports = Path("exports")
        self.dossier_imports = Path("imports")
        
        # Créer les dossiers si nécessaires
        self.dossier_exports.mkdir(exist_ok=True)
        self.dossier_imports.mkdir(exist_ok=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # IMPORT CSV
    # ═══════════════════════════════════════════════════════════════════════════
    
    def importer_matrice_csv(self, chemin: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Importe une matrice depuis un fichier CSV
        
        Args:
            chemin: Chemin du fichier CSV
            
        Returns:
            (matrice, message_erreur) - matrice=None si erreur
            
        Format CSV attendu:
            - Lignes commençant par # : commentaires (ignorés)
            - Première ligne de données: en-têtes (ignorés)
            - Première colonne: noms de lignes (ignorés)
            - Reste: données numériques
        """
        try:
            with LoggerContextuel(f"Import CSV: {Path(chemin).name}"):
                with open(chemin, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    lignes_brutes = list(reader)
                
                # Filtrer les lignes de commentaires et les lignes vides
                lignes = []
                for ligne in lignes_brutes:
                    # Ignorer lignes vides
                    if not ligne or len(ligne) == 0:
                        continue
                    # Ignorer lignes de commentaires (commençant par #)
                    if ligne[0].strip().startswith('#'):
                        continue
                    lignes.append(ligne)
                
                if len(lignes) < 2:
                    return None, "Fichier CSV vide ou incomplet (besoin d'au moins 2 lignes de données)"
                
                # La première ligne non-commentaire contient les en-têtes
                # Les lignes suivantes contiennent les données
                donnees = []
                for ligne in lignes[1:]:  # Skip header row
                    if len(ligne) > 1:
                        try:
                            # Ignorer la première colonne (nom de ligne) et convertir le reste
                            valeurs = []
                            for v in ligne[1:]:
                                v_clean = v.strip()
                                if v_clean == '' or v_clean == '-':
                                    valeurs.append(0.0)
                                else:
                                    valeurs.append(float(v_clean))
                            donnees.append(valeurs)
                        except ValueError as e:
                            return None, f"Valeur non numérique détectée: {e}"
                
                if not donnees:
                    return None, "Aucune donnée valide trouvée dans le fichier"
                
                matrice = np.array(donnees)
                logger.info(f"✓ Matrice importée: {matrice.shape}")
                return matrice, None
                
        except FileNotFoundError:
            return None, f"Fichier non trouvé: {chemin}"
        except Exception as e:
            logger.exception(f"Erreur lors de l'import CSV")
            return None, f"Erreur: {str(e)}"
    
    def importer_donnees_completes(self, dossier: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Importe un jeu complet de données depuis un dossier
        
        Args:
            dossier: Chemin du dossier contenant les fichiers CSV
            
        Returns:
            (dictionnaire_donnees, message_erreur)
            Le dictionnaire contient également 'n_sites' et 'n_matieres'
            
        Fichiers attendus:
            - offre.csv         : Matrice (n_sites × n_matieres) des offres
            - demande.csv       : Matrice (n_sites × n_matieres) des demandes
            - couts_matiere_0.csv, couts_matiere_1.csv, etc. : Matrices de coûts
            - distances.csv     : Matrice (n_sites × n_sites) des distances
            - capacites.csv     : Matrice (n_sites × n_sites) des capacités (optionnel)
        """
        dossier_path = Path(dossier)
        if not dossier_path.exists():
            return None, f"Dossier inexistant: {dossier}"
        
        donnees = {}
        erreurs = []
        n_sites = 0
        n_matieres = 0
        
        with LoggerContextuel(f"Import jeu de données: {dossier_path.name}"):
            # ═══════════════════════════════════════════════════════════════
            # IMPORT OFFRE (obligatoire)
            # ═══════════════════════════════════════════════════════════════
            offre, err = self.importer_matrice_csv(dossier_path / "offre.csv")
            if offre is not None:
                donnees['offre'] = offre
                n_sites = offre.shape[0]
                n_matieres = offre.shape[1] if len(offre.shape) > 1 else 1
                logger.info(f"  Offre: {offre.shape} détecté")
            else:
                erreurs.append(f"Offre: {err}")
            
            # ═══════════════════════════════════════════════════════════════
            # IMPORT DEMANDE (obligatoire)
            # ═══════════════════════════════════════════════════════════════
            demande, err = self.importer_matrice_csv(dossier_path / "demande.csv")
            if demande is not None:
                donnees['demande'] = demande
                # Vérifier la cohérence des dimensions
                if n_sites > 0 and demande.shape[0] != n_sites:
                    erreurs.append(f"Demande: incohérence de dimension ({demande.shape[0]} ≠ {n_sites} sites)")
                else:
                    logger.info(f"  Demande: {demande.shape}")
            else:
                erreurs.append(f"Demande: {err}")
            
            # ═══════════════════════════════════════════════════════════════
            # IMPORT DISTANCES (obligatoire)
            # ═══════════════════════════════════════════════════════════════
            distances, err = self.importer_matrice_csv(dossier_path / "distances.csv")
            if distances is not None:
                donnees['distance'] = distances
                logger.info(f"  Distances: {distances.shape}")
            else:
                erreurs.append(f"Distances: {err}")
            
            # ═══════════════════════════════════════════════════════════════
            # IMPORT COÛTS DE TRANSPORT (par matière)
            # ═══════════════════════════════════════════════════════════════
            couts_transport = []
            m = 0
            while True:
                fichier_cout = dossier_path / f"couts_matiere_{m}.csv"
                if not fichier_cout.exists():
                    break
                cout, err = self.importer_matrice_csv(fichier_cout)
                if cout is not None:
                    couts_transport.append(cout)
                    m += 1
                    logger.info(f"  Coûts matière {m-1}: {cout.shape}")
                else:
                    erreurs.append(f"Coûts matière {m}: {err}")
                    break
            
            if couts_transport:
                # Empiler les matrices de coûts sur l'axe 2 (n_sites × n_sites × n_matieres)
                donnees['cout_transport'] = np.stack(couts_transport, axis=2)
                # Mettre à jour n_matieres si détecté via les coûts
                if n_matieres == 0:
                    n_matieres = len(couts_transport)
            elif n_matieres > 0:
                erreurs.append("Aucun fichier de coûts trouvé (couts_matiere_0.csv, etc.)")
            
            # ═══════════════════════════════════════════════════════════════
            # IMPORT CAPACITÉS (optionnel)
            # ═══════════════════════════════════════════════════════════════
            capacites_path = dossier_path / "capacites.csv"
            if capacites_path.exists():
                capacites, err = self.importer_matrice_csv(capacites_path)
                if capacites is not None:
                    donnees['capacite_transfert'] = capacites
                    logger.info(f"  Capacités: {capacites.shape}")
                else:
                    logger.warning(f"  Capacités: {err} (optionnel)")
            else:
                # Capacités infinies par défaut
                if n_sites > 0:
                    donnees['capacite_transfert'] = np.full((n_sites, n_sites), 999.0)
                    logger.info(f"  Capacités: non trouvé, valeur par défaut (999)")
        
        # ═══════════════════════════════════════════════════════════════════
        # VALIDATION FINALE
        # ═══════════════════════════════════════════════════════════════════
        
        if erreurs:
            logger.error(f"Erreurs lors de l'import: {'; '.join(erreurs)}")
            return donnees if donnees else None, "; ".join(erreurs)
        
        if n_sites == 0 or n_matieres == 0:
            return None, "Impossible de déterminer les dimensions du problème"
        
        # Ajouter les dimensions au dictionnaire
        donnees['n_sites'] = n_sites
        donnees['n_matieres'] = n_matieres
        
        logger.info(f"✓ Import réussi: {n_sites} sites, {n_matieres} matières, {len(donnees)} matrices")
        return donnees, None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT CSV
    # ═══════════════════════════════════════════════════════════════════════════
    
    def exporter_matrice_csv(self, matrice: np.ndarray, chemin: str,
                            noms_lignes: Optional[List[str]] = None,
                            noms_colonnes: Optional[List[str]] = None) -> bool:
        """
        Exporte une matrice vers un fichier CSV
        
        Args:
            matrice: Matrice numpy à exporter
            chemin: Chemin du fichier de sortie
            noms_lignes: Noms des lignes (optionnel)
            noms_colonnes: Noms des colonnes (optionnel)
            
        Returns:
            True si succès
        """
        try:
            with LoggerContextuel(f"Export CSV: {Path(chemin).name}"):
                with open(chemin, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # En-tête
                    if noms_colonnes:
                        writer.writerow([''] + noms_colonnes)
                    
                    # Données
                    for i, ligne in enumerate(matrice):
                        if noms_lignes and i < len(noms_lignes):
                            writer.writerow([noms_lignes[i]] + ligne.tolist())
                        else:
                            writer.writerow([''] + ligne.tolist())
                
                logger.info(f"✓ Matrice exportée ({matrice.shape})")
                return True
                
        except Exception as e:
            logger.error(f"Échec de l'export CSV: {e}")
            return False
    
    def exporter_resultats_csv(self, modele, chemin: str) -> bool:
        """
        Exporte les résultats d'optimisation en CSV
        
        Args:
            modele: Instance de ModeleApprovisionnementPL
            chemin: Chemin du fichier de sortie
            
        Returns:
            True si succès
        """
        if not modele.resultats:
            logger.warning("Aucun résultat à exporter")
            return False
        
        try:
            with LoggerContextuel(f"Export résultats CSV: {Path(chemin).name}"):
                with open(chemin, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # En-tête
                    writer.writerow(['Type', 'Site Source', 'Site Destination', 
                                   'Matière', 'Quantité', 'Unité'])
                    
                    # Flux
                    for (i, j, m), quantite in modele.resultats['flux'].items():
                        writer.writerow([
                            'Flux',
                            modele.donnees.noms_sites[i],
                            modele.donnees.noms_sites[j],
                            modele.donnees.noms_matieres[m],
                            f"{quantite:.2f}",
                            'tonnes'
                        ])
                    
                    # Ruptures
                    for (j, m), quantite in modele.resultats.get('ruptures', {}).items():
                        writer.writerow([
                            'Rupture',
                            '',
                            modele.donnees.noms_sites[j],
                            modele.donnees.noms_matieres[m],
                            f"{quantite:.2f}",
                            'tonnes'
                        ])
                    
                    # Stocks
                    for (i, m), quantite in modele.resultats.get('stocks', {}).items():
                        writer.writerow([
                            'Stock résiduel',
                            modele.donnees.noms_sites[i],
                            '',
                            modele.donnees.noms_matieres[m],
                            f"{quantite:.2f}",
                            'tonnes'
                        ])
                
                logger.info("✓ Résultats exportés en CSV")
                return True
                
        except Exception as e:
            logger.error(f"Échec de l'export des résultats: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT EXCEL (si pandas disponible)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def exporter_resultats_excel(self, modele, chemin: str) -> bool:
        """
        Exporte les résultats vers un fichier Excel avec plusieurs feuilles
        
        Args:
            modele: Instance de ModeleApprovisionnementPL
            chemin: Chemin du fichier Excel
            
        Returns:
            True si succès
        """
        if not PANDAS_AVAILABLE:
            logger.warning("Pandas non disponible, export Excel impossible")
            return False
        
        if not modele.resultats:
            logger.warning("Aucun résultat à exporter")
            return False
        
        try:
            with LoggerContextuel(f"Export Excel: {Path(chemin).name}"):
                with pd.ExcelWriter(chemin, engine='openpyxl') as writer:
                    # Feuille résumé
                    resume = {
                        'Métrique': ['Coût total', 'Volume total', 'Nb transferts', 
                                    'Taux satisfaction', 'Temps résolution'],
                        'Valeur': [
                            f"{modele.resultats['valeur_optimale']:.2f} DT",
                            f"{modele.resultats['volume_total']:.1f} t",
                            modele.resultats['nb_transferts'],
                            f"{modele.resultats['taux_satisfaction']*100:.1f}%",
                            f"{modele.temps_resolution:.2f} s"
                        ]
                    }
                    pd.DataFrame(resume).to_excel(writer, sheet_name='Résumé', index=False)
                    
                    # Feuille flux
                    flux_data = []
                    for (i, j, m), quantite in modele.resultats['flux'].items():
                        flux_data.append({
                            'Site Source': modele.donnees.noms_sites[i],
                            'Site Destination': modele.donnees.noms_sites[j],
                            'Matière': modele.donnees.noms_matieres[m],
                            'Quantité (t)': round(quantite, 2)
                        })
                    
                    if flux_data:
                        pd.DataFrame(flux_data).to_excel(writer, sheet_name='Flux', index=False)
                    
                    # Feuille ruptures
                    if modele.resultats.get('ruptures'):
                        ruptures_data = []
                        for (j, m), quantite in modele.resultats['ruptures'].items():
                            ruptures_data.append({
                                'Site': modele.donnees.noms_sites[j],
                                'Matière': modele.donnees.noms_matieres[m],
                                'Rupture (t)': round(quantite, 2),
                                'Taux': f"{quantite/modele.donnees.demande[j,m]*100:.1f}%"
                            })
                        pd.DataFrame(ruptures_data).to_excel(writer, sheet_name='Ruptures', index=False)
                
                logger.info("✓ Résultats exportés en Excel")
                return True
                
        except Exception as e:
            logger.error(f"Échec de l'export Excel: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SAUVEGARDE/CHARGEMENT JSON (scénarios complets)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def sauvegarder_scenario(self, donnees, nom_scenario: str, 
                            resultats: Optional[Dict] = None) -> Optional[str]:
        """
        Sauvegarde un scénario complet (données + résultats) en JSON
        
        Args:
            donnees: Instance de ModeleDonneesApprovisionnement
            nom_scenario: Nom du scénario
            resultats: Résultats optionnels
            
        Returns:
            Chemin du fichier sauvegardé, ou None si échec
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"{nom_scenario}_{timestamp}.json"
        chemin = self.dossier_exports / nom_fichier
        
        try:
            with LoggerContextuel(f"Sauvegarde scénario: {nom_scenario}"):
                scenario = {
                    'metadata': {
                        'nom': nom_scenario,
                        'date': datetime.now().isoformat(),
                        'n_sites': donnees.n_sites,
                        'n_matieres': donnees.n_matieres
                    },
                    'donnees': {
                        'noms_sites': donnees.noms_sites,
                        'noms_matieres': donnees.noms_matieres,
                        'offre': donnees.offre.tolist(),
                        'demande': donnees.demande.tolist(),
                        'cout_transport': donnees.cout_transport.tolist(),
                        'distance': donnees.distance.tolist(),
                        'capacite_transfert': self._serialiser_capacites(donnees.capacite_transfert),
                        'capacite_expedition': self._serialiser_capacites(donnees.capacite_expedition),
                        'capacite_reception': self._serialiser_capacites(donnees.capacite_reception),
                        'cout_stockage': donnees.cout_stockage.tolist(),
                        'penalite_rupture': donnees.penalite_rupture.tolist(),
                        'temps_transport': donnees.temps_transport.tolist(),
                        'cout_kilometrique': donnees.cout_kilometrique,
                        'delai_max': donnees.delai_max,
                        'penalite_delai': donnees.penalite_delai,
                        'priorite_matiere': donnees.priorite_matiere.tolist()
                    }
                }
                
                if resultats:
                    scenario['resultats'] = {
                        'valeur_optimale': resultats.get('valeur_optimale'),
                        'temps_resolution': resultats.get('temps_resolution'),
                        'nb_transferts': resultats.get('nb_transferts'),
                        'volume_total': resultats.get('volume_total'),
                        'taux_satisfaction': resultats.get('taux_satisfaction')
                    }
                
                with open(chemin, 'w', encoding='utf-8') as f:
                    json.dump(scenario, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✓ Scénario sauvegardé: {chemin}")
                return str(chemin)
                
        except Exception as e:
            logger.error(f"Échec de la sauvegarde du scénario: {e}")
            return None
    
    def _serialiser_capacites(self, capacites):
        """Convertit les capacités (avec inf) en liste sérialisable"""
        result = []
        if capacites.ndim == 1:
            for val in capacites:
                result.append(None if val == float('inf') else float(val))
        else:
            for ligne in capacites:
                result.append([None if val == float('inf') else float(val) for val in ligne])
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT RAPPORT TEXTUEL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def generer_rapport_textuel(self, modele, chemin: str) -> bool:
        """
        Génère un rapport textuel complet des résultats
        
        Args:
            modele: Instance de ModeleApprovisionnementPL
            chemin: Chemin du fichier texte
            
        Returns:
            True si succès
        """
        if not modele.resultats:
            return False
        
        try:
            with LoggerContextuel(f"Génération rapport: {Path(chemin).name}"):
                with open(chemin, 'w', encoding='utf-8') as f:
                    f.write("═" * 80 + "\n")
                    f.write("RAPPORT D'OPTIMISATION - OptiAppro\n")
                    f.write("Optimisation de l'Approvisionnement Inter-Sites\n")
                    f.write("═" * 80 + "\n\n")
                    
                    # Métadonnées
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Problème: {modele.donnees.n_sites} sites, "
                           f"{modele.donnees.n_matieres} matières\n\n")
                    
                    # Résumé
                    r = modele.resultats
                    f.write("─" * 80 + "\n")
                    f.write("RÉSULTATS PRINCIPAUX\n")
                    f.write("─" * 80 + "\n\n")
                    f.write(f"💰 Coût total optimal: {r['valeur_optimale']:.2f} DT\n")
                    f.write(f"⏱  Temps de résolution: {modele.temps_resolution:.2f} secondes\n")
                    f.write(f"📦 Volume total transféré: {r['volume_total']:.1f} tonnes\n")
                    f.write(f"🔢 Nombre de transferts: {r['nb_transferts']}\n")
                    f.write(f"✓  Taux de satisfaction: {r['taux_satisfaction']*100:.1f}%\n\n")
                    
                    # Flux détaillés
                    f.write("─" * 80 + "\n")
                    f.write("FLUX OPTIMAUX\n")
                    f.write("─" * 80 + "\n\n")
                    
                    flux_tries = sorted(r['flux'].items(), key=lambda x: x[1], reverse=True)
                    for (i, j, m), quantite in flux_tries:
                        f.write(f"{modele.donnees.noms_sites[i]:15} → "
                               f"{modele.donnees.noms_sites[j]:15} | "
                               f"{modele.donnees.noms_matieres[m]:12}: "
                               f"{quantite:8.1f} tonnes\n")
                    
                    # Ruptures
                    if r.get('ruptures'):
                        f.write("\n" + "─" * 80 + "\n")
                        f.write("RUPTURES DÉTECTÉES\n")
                        f.write("─" * 80 + "\n\n")
                        
                        for (j, m), quantite in r['ruptures'].items():
                            taux = (quantite / modele.donnees.demande[j, m]) * 100
                            f.write(f"{modele.donnees.noms_sites[j]:15} | "
                                   f"{modele.donnees.noms_matieres[m]:12}: "
                                   f"{quantite:7.1f} tonnes ({taux:5.1f}%)\n")
                    
                    f.write("\n" + "═" * 80 + "\n")
                    f.write("FIN DU RAPPORT\n")
                    f.write("═" * 80 + "\n")
                
                logger.info("✓ Rapport textuel généré")
                return True
                
        except Exception as e:
            logger.error(f"Échec de la génération du rapport: {e}")
            return False
