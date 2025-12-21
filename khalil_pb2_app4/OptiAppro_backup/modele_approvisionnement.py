"""
═══════════════════════════════════════════════════════════════════════════════
MODÈLE DE PROGRAMMATION LINÉAIRE
Optimisation de l'Approvisionnement Inter-Sites

INSAT - Année universitaire 2025-2026
Réalisé par: Khalil Chikhaoui
Domaine: Recherche Opérationnelle
═══════════════════════════════════════════════════════════════════════════════
Ce module implémente le modèle mathématique de programmation linéaire (PL)
pour l'optimisation des flux d'approvisionnement entre sites de production.

Solveur utilisé: Gurobi Optimizer
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np
from typing import Dict, Tuple, List
import time


class ModeleDonneesApprovisionnement:
    """
    Classe pour gérer les données du problème d'approvisionnement
    """
    
    def __init__(self, n_sites: int, n_matieres: int):
        """
        Initialise les structures de données
        
        Args:
            n_sites: Nombre de sites de production
            n_matieres: Nombre de matières premières
        """
        self.n_sites = n_sites
        self.n_matieres = n_matieres
        
        # Ensembles
        self.sites = list(range(n_sites))
        self.matieres = list(range(n_matieres))
        
        # Paramètres de base (matrices)
        self.offre = np.zeros((n_sites, n_matieres))  # O[i,m]
        self.demande = np.zeros((n_sites, n_matieres))  # D[j,m]
        self.cout_transport = np.zeros((n_sites, n_sites, n_matieres))  # c[i,j,m]
        
        # Paramètres de capacité
        self.capacite_transfert = np.full((n_sites, n_sites), float('inf'))  # Cap[i,j]
        self.capacite_expedition = np.full(n_sites, float('inf'))  # Cap_out[i]
        self.capacite_reception = np.full(n_sites, float('inf'))  # Cap_in[j]
        
        # Paramètres de coûts supplémentaires
        self.cout_stockage = np.zeros((n_sites, n_matieres))  # h[i,m]
        # Pénalité de rupture par site/matière (ancienne version, gardée pour compatibilité)
        self.penalite_rupture = np.full((n_sites, n_matieres), 1000.0)  # p[j,m]
        
        # ═══════════════════════════════════════════════════════════════
        # PÉNALITÉ DE RUPTURE UNITAIRE (PARAMÈTRE UTILISATEUR)
        # ═══════════════════════════════════════════════════════════════
        # Cette valeur est utilisée dans la fonction objectif
        # Valeur par défaut: 100 DT/tonne
        # L'utilisateur peut la modifier via l'interface
        self.penalite_rupture_unitaire = 100.0  # DT/tonne
        
        self.distance = np.zeros((n_sites, n_sites))  # d[i,j]
        self.cout_kilometrique = 0.5  # alpha (DT/tonne/km)
        
        # Paramètres de délai
        self.temps_transport = np.zeros((n_sites, n_sites))  # t[i,j]
        self.delai_max = 5.0  # T_max (jours)
        self.penalite_delai = 10.0  # beta (DT/tonne/jour)
        
        # Paramètres de priorité
        self.priorite_matiere = np.ones(n_matieres)  # q[m]
        
        # Noms pour l'affichage
        self.noms_sites = [f"Site_{i+1}" for i in range(n_sites)]
        self.noms_matieres = [f"Matière_{m+1}" for m in range(n_matieres)]
    
    def generer_donnees_exemple(self):
        """
        Génère un jeu de données réaliste pour tester le modèle
        Scénario: 5 sites, 3 matières premières
        """
        if self.n_sites == 5 and self.n_matieres == 3:
            # Noms descriptifs
            self.noms_sites = ["Site_Nord", "Site_Sud", "Site_Est", "Site_Ouest", "Site_Centre"]
            self.noms_matieres = ["Acier", "Plastique", "Aluminium"]
            
            # Offre par site et matière (tonnes)
            self.offre = np.array([
                [150, 0, 100],    # Site_Nord: excédent Acier et Aluminium
                [0, 200, 50],     # Site_Sud: excédent Plastique
                [100, 80, 0],     # Site_Est: excédent Acier et Plastique
                [50, 0, 120],     # Site_Ouest: excédent Acier et Aluminium
                [0, 100, 80]      # Site_Centre: excédent Plastique et Aluminium
            ])
            
            # Demande par site et matière (tonnes)
            self.demande = np.array([
                [0, 150, 0],      # Site_Nord: besoin Plastique
                [120, 0, 80],     # Site_Sud: besoin Acier et Aluminium
                [0, 0, 100],      # Site_Est: besoin Aluminium
                [80, 120, 0],     # Site_Ouest: besoin Acier et Plastique
                [100, 110, 170]   # Site_Centre: besoin tout
            ])
            
            # Coûts de transport (DT/tonne) par matière
            # Acier (plus lourd, plus cher)
            cout_acier = np.array([
                [0, 15, 12, 10, 8],
                [15, 0, 18, 20, 14],
                [12, 18, 0, 16, 10],
                [10, 20, 16, 0, 12],
                [8, 14, 10, 12, 0]
            ])
            
            # Plastique (intermédiaire)
            cout_plastique = np.array([
                [0, 10, 8, 7, 6],
                [10, 0, 12, 14, 10],
                [8, 12, 0, 11, 7],
                [7, 14, 11, 0, 8],
                [6, 10, 7, 8, 0]
            ])
            
            # Aluminium (léger mais cher)
            cout_aluminium = np.array([
                [0, 18, 15, 13, 10],
                [18, 0, 20, 22, 16],
                [15, 20, 0, 18, 12],
                [13, 22, 18, 0, 14],
                [10, 16, 12, 14, 0]
            ])
            
            self.cout_transport[:, :, 0] = cout_acier
            self.cout_transport[:, :, 1] = cout_plastique
            self.cout_transport[:, :, 2] = cout_aluminium
            
            # Distances entre sites (km)
            self.distance = np.array([
                [0, 450, 380, 320, 250],
                [450, 0, 520, 600, 420],
                [380, 520, 0, 480, 300],
                [320, 600, 480, 0, 350],
                [250, 420, 300, 350, 0]
            ])
            
            # Temps de transport (jours)
            self.temps_transport = self.distance / 100  # ~100 km/jour
            
            # Capacités de transfert (tonnes)
            self.capacite_transfert = np.full((5, 5), 200.0)
            np.fill_diagonal(self.capacite_transfert, 0)  # Pas d'auto-transfert
            
            # Capacités d'expédition et réception
            self.capacite_expedition = np.array([300, 280, 250, 220, 250])
            self.capacite_reception = np.array([200, 280, 150, 250, 400])
            
            # Coûts de stockage (DT/tonne)
            self.cout_stockage = np.array([
                [5, 3, 6],
                [4, 3.5, 5.5],
                [5.5, 4, 7],
                [4.5, 3, 6.5],
                [5, 3.5, 6]
            ])
            
            # Pénalités de rupture (DT/tonne)
            self.penalite_rupture = np.array([
                [100, 80, 90],
                [95, 75, 85],
                [110, 90, 95],
                [100, 85, 90],
                [105, 80, 100]
            ])
            
            # Priorités des matières (1=normale, 2=haute, 3=critique)
            self.priorite_matiere = np.array([2.0, 1.0, 2.5])  # Acier et Aluminium prioritaires
    
    def valider_donnees(self) -> Tuple[bool, List[str]]:
        """
        Vérifie la cohérence des données
        
        Returns:
            (valide, liste_erreurs)
        """
        erreurs = []
        
        # Vérifier les offres et demandes non négatives
        if np.any(self.offre < 0):
            erreurs.append("Les offres doivent être non négatives")
        if np.any(self.demande < 0):
            erreurs.append("Les demandes doivent être non négatives")
        
        # Vérifier l'équilibre global
        offre_totale = self.offre.sum()
        demande_totale = self.demande.sum()
        if offre_totale < demande_totale * 0.8:
            erreurs.append(f"Offre totale ({offre_totale:.1f}) insuffisante pour demande ({demande_totale:.1f})")
        
        # Vérifier les capacités
        if np.any(self.capacite_transfert < 0):
            erreurs.append("Les capacités de transfert doivent être non négatives")
        
        return len(erreurs) == 0, erreurs


class ModeleApprovisionnementPL:
    """
    Modèle de Programmation Linéaire pour l'optimisation de l'approvisionnement
    Utilise le solveur Gurobi
    """
    
    def __init__(self, donnees: ModeleDonneesApprovisionnement):
        """
        Initialise le modèle avec les données
        
        Args:
            donnees: Instance de ModeleDonneesApprovisionnement
        """
        self.donnees = donnees
        self.modele = None
        self.variables = {}
        self.contraintes = {}
        self.resultats = {}
        self.temps_resolution = 0
    
    def construire_modele(self):
        """
        Construit le modèle de Programmation Linéaire avec Gurobi
        """
        print("Construction du modèle de Programmation Linéaire...")
        
        d = self.donnees  # Raccourci
        
        # Créer le modèle Gurobi
        self.modele = gp.Model("Approvisionnement_Inter_Sites")
        
        # ===============================================
        # VARIABLES DE DÉCISION (continues)
        # ===============================================
        
        # x[i,j,m]: Quantité de matière m transférée de site i vers site j
        x = {}
        for i in d.sites:
            for j in d.sites:
                for m in d.matieres:
                    if i != j:  # Pas d'auto-transfert
                        x[i, j, m] = self.modele.addVar(
                            lb=0.0,
                            vtype=GRB.CONTINUOUS,
                            name=f"x_{d.noms_sites[i]}_{d.noms_sites[j]}_{d.noms_matieres[m]}"
                        )
                    else:
                        x[i, j, m] = 0  # Fixé à 0
        
        # s[i,m]: Stock résiduel de matière m au site i
        s = {}
        for i in d.sites:
            for m in d.matieres:
                s[i, m] = self.modele.addVar(
                    lb=0.0,
                    vtype=GRB.CONTINUOUS,
                    name=f"s_{d.noms_sites[i]}_{d.noms_matieres[m]}"
                )
        
        # r[j,m]: Rupture (déficit) de matière m au site j
        r = {}
        for j in d.sites:
            for m in d.matieres:
                r[j, m] = self.modele.addVar(
                    lb=0.0,
                    vtype=GRB.CONTINUOUS,
                    name=f"r_{d.noms_sites[j]}_{d.noms_matieres[m]}"
                )
        
        # y[i,j]: Flux total entre sites i et j
        y = {}
        for i in d.sites:
            for j in d.sites:
                if i != j:
                    y[i, j] = self.modele.addVar(
                        lb=0.0,
                        vtype=GRB.CONTINUOUS,
                        name=f"y_{d.noms_sites[i]}_{d.noms_sites[j]}"
                    )
        
        self.modele.update()
        
        # Stocker les variables
        self.variables['x'] = x
        self.variables['s'] = s
        self.variables['r'] = r
        self.variables['y'] = y
        
        # ===============================================
        # FONCTION OBJECTIF
        # ===============================================
        
        objectif = 0
        
        # 1. Coûts de transport direct (c[i,j,m] * x[i,j,m])
        #    Les coûts c[i,j,m] intègrent déjà la distance
        for i in d.sites:
            for j in d.sites:
                for m in d.matieres:
                    if i != j:
                        objectif += d.cout_transport[i, j, m] * x[i, j, m]
        
        # 2. Coûts de stockage (optionnel, souvent = 0)
        for i in d.sites:
            for m in d.matieres:
                objectif += d.cout_stockage[i, m] * s[i, m]
        
        # 3. Pénalités de rupture (PARAMÈTRE UTILISATEUR)
        #    Utilise penalite_rupture_unitaire défini dans les données
        #    Valeur par défaut: 100 DT/tonne
        penalite = getattr(d, 'penalite_rupture_unitaire', 100.0)
        for j in d.sites:
            for m in d.matieres:
                objectif += penalite * r[j, m]
        
        # Note: On n'ajoute PAS le coût kilométrique ni les pénalités de délai
        # car les coûts de transport intègrent déjà la distance
        
        self.modele.setObjective(objectif, GRB.MINIMIZE)
        
        # ===============================================
        # CONTRAINTES
        # ===============================================
        
        # 1. CONTRAINTE FONDAMENTALE: Un site ne peut envoyer QUE ce qu'il OFFRE
        #    (Pas de transbordement - modèle d'approvisionnement direct)
        for i in d.sites:
            for m in d.matieres:
                # Total envoyé depuis site i pour matière m <= offre du site
                total_envoye = sum(x[i, j, m] for j in d.sites if j != i)
                self.modele.addConstr(
                    total_envoye <= d.offre[i, m],
                    name=f"limite_envoi_{d.noms_sites[i]}_{d.noms_matieres[m]}"
                )
        
        # 2. Stock résiduel = Offre - Total envoyé
        for i in d.sites:
            for m in d.matieres:
                total_envoye = sum(x[i, j, m] for j in d.sites if j != i)
                self.modele.addConstr(
                    s[i, m] == d.offre[i, m] - total_envoye,
                    name=f"stock_{d.noms_sites[i]}_{d.noms_matieres[m]}"
                )
        
        # 3. Satisfaction de la demande avec rupture possible
        #    Ce qu'un site reçoit + rupture = sa demande
        for j in d.sites:
            for m in d.matieres:
                total_recu = sum(x[i, j, m] for i in d.sites if i != j)
                self.modele.addConstr(
                    total_recu + r[j, m] == d.demande[j, m],
                    name=f"demande_{d.noms_sites[j]}_{d.noms_matieres[m]}"
                )
        
        # 4. Capacité de transfert entre sites
        for i in d.sites:
            for j in d.sites:
                if i != j:
                    self.modele.addConstr(
                        sum(x[i, j, m] for m in d.matieres) <= d.capacite_transfert[i, j],
                        name=f"cap_transfert_{d.noms_sites[i]}_{d.noms_sites[j]}"
                    )
        
        # 5. Capacité d'expédition d'un site
        for i in d.sites:
            self.modele.addConstr(
                sum(x[i, j, m] for j in d.sites for m in d.matieres if i != j) <= d.capacite_expedition[i],
                name=f"cap_expedition_{d.noms_sites[i]}"
            )
        
        # 6. Capacité de réception d'un site
        for j in d.sites:
            self.modele.addConstr(
                sum(x[i, j, m] for i in d.sites for m in d.matieres if i != j) <= d.capacite_reception[j],
                name=f"cap_reception_{d.noms_sites[j]}"
            )
        
        # 7. Lien entre flux détaillé et flux total
        for i in d.sites:
            for j in d.sites:
                if i != j:
                    self.modele.addConstr(
                        y[i, j] == sum(x[i, j, m] for m in d.matieres),
                        name=f"flux_total_{d.noms_sites[i]}_{d.noms_sites[j]}"
                    )
        
        # Note: Les ruptures sont pénalisées dans la fonction objectif (1000 DT/tonne)
        # Le solveur minimisera naturellement les ruptures
        # Pas de contrainte artificielle de limitation à 20%
        
        self.modele.update()
        print(f"✓ Modèle construit: {self.modele.NumVars} variables, {self.modele.NumConstrs} contraintes")
    
    def resoudre(self, time_limit=300, verbose=True):
        """
        Résout le modèle avec Gurobi
        
        Args:
            time_limit: Temps limite en secondes
            verbose: Afficher les logs Gurobi
        """
        if self.modele is None:
            raise ValueError("Le modèle doit d'abord être construit avec construire_modele()")
        
        print("\n" + "="*70)
        print("RÉSOLUTION DU MODÈLE AVEC GUROBI")
        print("="*70)
        
        # Configuration du solveur
        self.modele.setParam('TimeLimit', time_limit)
        self.modele.setParam('OutputFlag', 1 if verbose else 0)
        self.modele.setParam('MIPGap', 0.01)  # 1% de gap acceptable
        
        # Résolution
        debut = time.time()
        self.modele.optimize()
        self.temps_resolution = time.time() - debut
        
        # Vérifier le statut
        if self.modele.Status == GRB.OPTIMAL:
            print(f"\n✓ Solution optimale trouvée en {self.temps_resolution:.2f} secondes")
            self.extraire_resultats()
            return True
        elif self.modele.Status == GRB.TIME_LIMIT:
            print(f"\n⚠ Temps limite atteint ({time_limit}s)")
            if self.modele.SolCount > 0:
                print("  Solution réalisable disponible")
                self.extraire_resultats()
                return True
            return False
        else:
            print(f"\n✗ Pas de solution trouvée (Statut: {self.modele.Status})")
            return False
    
    def extraire_resultats(self):
        """
        Extrait les résultats de la solution optimale.
        
        IMPORTANT: Les variables Gurobi ne supportent pas la comparaison directe.
        On doit d'abord vérifier si c'est une variable Gurobi avec hasattr(),
        puis accéder à la valeur avec .X
        """
        d = self.donnees
        x = self.variables['x']
        s = self.variables['s']
        r = self.variables['r']
        y = self.variables['y']
        
        # Valeur optimale
        self.resultats['valeur_optimale'] = self.modele.ObjVal
        
        # Flux optimaux x[i,j,m]
        # Note: x[i,i,m] = 0 (entier), x[i,j,m] avec i≠j = Var Gurobi
        flux = {}
        for i in d.sites:
            for j in d.sites:
                for m in d.matieres:
                    if i != j:  # Seulement les transferts entre sites différents
                        # Vérifier que c'est une variable Gurobi avant d'accéder à .X
                        if hasattr(x[i, j, m], 'X'):
                            val = x[i, j, m].X
                            if val > 0.01:  # Seuil de significativité
                                flux[i, j, m] = val
        self.resultats['flux'] = flux
        
        # Stocks résiduels
        stocks = {}
        for i in d.sites:
            for m in d.matieres:
                if hasattr(s[i, m], 'X'):
                    val = s[i, m].X
                    if val > 0.01:
                        stocks[i, m] = val
        self.resultats['stocks'] = stocks
        
        # Ruptures
        ruptures = {}
        for j in d.sites:
            for m in d.matieres:
                if hasattr(r[j, m], 'X'):
                    val = r[j, m].X
                    if val > 0.01:
                        ruptures[j, m] = val
        self.resultats['ruptures'] = ruptures
        
        # Flux totaux entre sites
        flux_totaux = {}
        for i in d.sites:
            for j in d.sites:
                if i != j:
                    if hasattr(y[i, j], 'X'):
                        val = y[i, j].X
                        if val > 0.01:
                            flux_totaux[i, j] = val
        self.resultats['flux_totaux'] = flux_totaux
        
        # Statistiques
        self.resultats['nb_transferts'] = len(flux)
        self.resultats['volume_total'] = sum(flux.values()) if flux else 0.0
        self.resultats['volume_rupture_total'] = sum(ruptures.values()) if ruptures else 0.0
        
        demande_totale = d.demande.sum()
        if demande_totale > 0:
            self.resultats['taux_satisfaction'] = 1 - (self.resultats['volume_rupture_total'] / demande_totale)
        else:
            self.resultats['taux_satisfaction'] = 1.0
        
        # Informations du modèle pour affichage scientifique
        self.resultats['nb_variables'] = self.modele.NumVars
        self.resultats['nb_contraintes'] = self.modele.NumConstrs
        self.resultats['temps_resolution'] = self.temps_resolution
        self.resultats['statut_gurobi'] = self.modele.Status
    
    def afficher_resultats(self):
        """
        Affiche un résumé des résultats
        """
        if not self.resultats:
            print("Aucun résultat disponible")
            return
        
        d = self.donnees
        r = self.resultats
        
        print("\n" + "="*70)
        print("RÉSULTATS DE L'OPTIMISATION")
        print("="*70)
        
        print(f"\n💰 COÛT TOTAL OPTIMAL: {r['valeur_optimale']:.2f} DT")
        print(f"⏱  Temps de résolution: {self.temps_resolution:.2f} secondes")
        print(f"📦 Volume total transféré: {r['volume_total']:.1f} tonnes")
        print(f"🔢 Nombre de transferts: {r['nb_transferts']}")
        print(f"✓  Taux de satisfaction: {r['taux_satisfaction']*100:.1f}%")
        
        # Flux principaux
        print(f"\n📊 FLUX PRINCIPAUX (> 10 tonnes):")
        flux_tries = sorted(r['flux'].items(), key=lambda x: x[1], reverse=True)
        for (i, j, m), quantite in flux_tries:
            if quantite > 10:
                print(f"  {d.noms_sites[i]:12} → {d.noms_sites[j]:12} | "
                      f"{d.noms_matieres[m]:12}: {quantite:7.1f} tonnes")
        
        # Ruptures
        if r['ruptures']:
            print(f"\n⚠️  RUPTURES DÉTECTÉES:")
            for (j, m), quantite in r['ruptures'].items():
                taux = (quantite / d.demande[j, m]) * 100
                print(f"  {d.noms_sites[j]:12} | {d.noms_matieres[m]:12}: "
                      f"{quantite:6.1f} tonnes ({taux:5.1f}% de la demande)")
        else:
            print("\n✓ Aucune rupture - Toutes les demandes satisfaites")
        
        # Stocks résiduels
        if r['stocks']:
            print(f"\n📦 STOCKS RÉSIDUELS:")
            for (i, m), quantite in r['stocks'].items():
                print(f"  {d.noms_sites[i]:12} | {d.noms_matieres[m]:12}: {quantite:7.1f} tonnes")


# ===============================================
# FONCTION PRINCIPALE DE TEST
# ===============================================

def exemple_resolution():
    """
    Exemple complet d'utilisation du modèle
    """
    print("="*70)
    print("SYSTÈME D'OPTIMISATION DE L'APPROVISIONNEMENT INTER-SITES")
    print("Modèle de Programmation Linéaire (PL)")
    print("="*70)
    
    # 1. Créer les données
    print("\n[1/4] Initialisation des données...")
    donnees = ModeleDonneesApprovisionnement(n_sites=5, n_matieres=3)
    donnees.generer_donnees_exemple()
    
    # 2. Valider les données
    print("\n[2/4] Validation des données...")
    valide, erreurs = donnees.valider_donnees()
    if not valide:
        print("❌ Erreurs dans les données:")
        for err in erreurs:
            print(f"  - {err}")
        return
    print("✓ Données valides")
    
    # 3. Construire et résoudre
    print("\n[3/4] Construction du modèle...")
    modele = ModeleApprovisionnementPL(donnees)
    modele.construire_modele()
    
    print("\n[4/4] Résolution...")
    succes = modele.resoudre(time_limit=300, verbose=True)
    
    if succes:
        modele.afficher_resultats()
    else:
        print("❌ Échec de la résolution")


if __name__ == "__main__":
    exemple_resolution()
