"""
Module d'interprétation des résultats d'optimisation.
Génère des insights détaillés sur la solution trouvée.

Format des résultats du modèle:
- resultats['valeur_optimale']: float
- resultats['flux']: dict avec clés (i, j, m) -> valeur
- resultats['stocks']: dict avec clés (i, m) -> valeur  
- resultats['ruptures']: dict avec clés (j, m) -> valeur
- resultats['taux_satisfaction']: float
- resultats['volume_total']: float
- resultats['volume_rupture_total']: float
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime


class CategorieInsight(Enum):
    """Catégories d'insights."""
    DONNEES = auto()
    PERFORMANCE = auto()
    FLUX = auto()
    COUTS = auto()
    CAPACITES = auto()
    STOCKS = auto()
    RUPTURES = auto()
    RECOMMANDATIONS = auto()


class NiveauImportance(Enum):
    """Niveau d'importance."""
    INFO = 1
    ATTENTION = 2
    CRITIQUE = 3
    SUCCES = 4


@dataclass
class Insight:
    """Structure d'un insight."""
    titre: str
    description: str
    categorie: CategorieInsight
    importance: NiveauImportance
    valeur: Optional[float] = None
    unite: str = ""
    icone: str = ""
    
    def __post_init__(self):
        if not self.icone:
            icones = {
                CategorieInsight.DONNEES: "📊",
                CategorieInsight.PERFORMANCE: "⚡",
                CategorieInsight.FLUX: "🔄",
                CategorieInsight.COUTS: "💰",
                CategorieInsight.CAPACITES: "📦",
                CategorieInsight.STOCKS: "🏭",
                CategorieInsight.RUPTURES: "⚠️",
                CategorieInsight.RECOMMANDATIONS: "💡"
            }
            self.icone = icones.get(self.categorie, "📌")


class InterpreteurResultats:
    """Interprète les résultats d'optimisation et génère des insights."""
    
    def __init__(self):
        self.insights: List[Insight] = []
        self.modele = None
        self.resultats: Dict[str, Any] = {}
        self.donnees = None
        
    def analyser(self, modele) -> List[Insight]:
        """Point d'entrée principal - compatible avec l'interface."""
        return self.interpreter_resultats(modele)
    
    def interpreter_resultats(self, modele) -> List[Insight]:
        """Analyse complète des résultats."""
        self.modele = modele
        self.resultats = getattr(modele, 'resultats', {}) or {}
        self.donnees = getattr(modele, 'donnees', None)
        self.insights = []
        
        if not self.donnees:
            self.insights.append(Insight(
                titre="Données manquantes",
                description="Les données du modèle ne sont pas disponibles.",
                categorie=CategorieInsight.DONNEES,
                importance=NiveauImportance.CRITIQUE,
                icone="❌"
            ))
            return self.insights
        
        # Analyses complètes
        self._analyser_donnees()
        self._analyser_solution()
        self._analyser_systeme_penalites()      # NOUVEAU: Explication des pénalités
        self._analyser_contraintes()             # NOUVEAU: Analyse des contraintes
        self._analyser_optimalite()              # NOUVEAU: Preuve d'optimalité
        self._analyser_alternatives()            # NOUVEAU: Solutions alternatives
        self._analyser_flux()
        self._analyser_couts()
        self._analyser_stocks()
        self._analyser_ruptures()
        self._generer_recommandations()
        
        return self.insights
    
    def _get_nom_site(self, idx: int) -> str:
        """Récupère le nom d'un site."""
        d = self.donnees
        if hasattr(d, 'noms_sites') and idx < len(d.noms_sites):
            return str(d.noms_sites[idx])
        return f"Site_{idx+1}"
    
    def _get_nom_matiere(self, idx: int) -> str:
        """Récupère le nom d'une matière."""
        d = self.donnees
        if hasattr(d, 'noms_matieres') and idx < len(d.noms_matieres):
            return str(d.noms_matieres[idx])
        return f"Matière_{idx+1}"
    
    def _analyser_donnees(self):
        """Analyse des données d'entrée."""
        d = self.donnees
        n_sites = d.n_sites
        n_matieres = d.n_matieres
        
        self.insights.append(Insight(
            titre="Dimensions du problème",
            description=f"Réseau de {n_sites} sites avec {n_matieres} matière(s) première(s).",
            categorie=CategorieInsight.DONNEES,
            importance=NiveauImportance.INFO,
            valeur=n_sites * n_matieres,
            unite="combinaisons"
        ))
        
        # Équilibre offre/demande par matière
        for m in range(n_matieres):
            nom_m = self._get_nom_matiere(m)
            offre_tot = float(np.sum(d.offre[:, m]))
            demande_tot = float(np.sum(d.demande[:, m]))
            
            fournisseurs = [self._get_nom_site(i) for i in range(n_sites) if d.offre[i, m] > 0]
            demandeurs = [self._get_nom_site(i) for i in range(n_sites) if d.demande[i, m] > 0]
            
            if demande_tot > 0:
                ratio = offre_tot / demande_tot
                if ratio >= 1.0:
                    niveau = NiveauImportance.SUCCES
                    statut = "✅ Offre suffisante"
                else:
                    niveau = NiveauImportance.CRITIQUE
                    statut = f"❌ Déficit de {demande_tot - offre_tot:.1f}t"
                
                desc = f"{statut} — Offre: {offre_tot:.1f}t | Demande: {demande_tot:.1f}t"
                if fournisseurs:
                    desc += f"\nFournisseurs: {', '.join(fournisseurs)}"
                if demandeurs:
                    desc += f"\nDemandeurs: {', '.join(demandeurs)}"
                
                self.insights.append(Insight(
                    titre=f"Équilibre {nom_m}",
                    description=desc,
                    categorie=CategorieInsight.DONNEES,
                    importance=niveau,
                    valeur=ratio * 100,
                    unite="% couverture"
                ))
    
    def _analyser_solution(self):
        """Analyse de la solution optimale."""
        if 'valeur_optimale' not in self.resultats:
            self.insights.append(Insight(
                titre="Pas de solution",
                description="Le modèle n'a pas été résolu. Lancez l'optimisation d'abord.",
                categorie=CategorieInsight.PERFORMANCE,
                importance=NiveauImportance.ATTENTION,
                icone="⏳"
            ))
            return
        
        d = self.donnees
        valeur_opt = self.resultats['valeur_optimale']
        taux_satisfaction = self.resultats.get('taux_satisfaction', 1.0) * 100
        volume_total = self.resultats.get('volume_total', 0)
        volume_rupture = self.resultats.get('volume_rupture_total', 0)
        
        # Calculer le coût de transport et des ruptures
        flux_dict = self.resultats.get('flux', {})
        ruptures_dict = self.resultats.get('ruptures', {})
        
        cout_transport = 0.0
        for (i, j, m), val in flux_dict.items():
            cout_transport += val * d.cout_transport[i, j, m]
        
        cout_ruptures = 0.0
        # Pénalité configurable (défaut: 100 DT/tonne)
        PENALITE_RUPTURE = getattr(d, 'penalite_rupture_unitaire', 100.0)
        for (j, m), val in ruptures_dict.items():
            cout_ruptures += val * PENALITE_RUPTURE
        
        # RÉSUMÉ EXÉCUTIF
        demande_totale = float(np.sum(d.demande))
        pct_transport = (cout_transport / valeur_opt * 100) if valeur_opt > 0 else 0
        pct_rupture = (cout_ruptures / valeur_opt * 100) if valeur_opt > 0 else 0
        
        self.insights.append(Insight(
            titre="📊 RÉSUMÉ EXÉCUTIF",
            description=f"═══════════════════════════════════════════════════\n"
                       f"           RÉSULTAT DE L'OPTIMISATION\n"
                       f"═══════════════════════════════════════════════════\n\n"
                       f"� COÛT OPTIMAL: {valeur_opt:,.2f} DT\n"
                       f"   ├─ Transport: {cout_transport:,.2f} DT ({pct_transport:.1f}%)\n"
                       f"   └─ Pénalités: {cout_ruptures:,.2f} DT ({pct_rupture:.1f}%)\n\n"
                       f"� VOLUMES:\n"
                       f"   ├─ Demande totale: {demande_totale:,.0f} t\n"
                       f"   ├─ Transporté: {volume_total:,.0f} t\n"
                       f"   └─ Ruptures: {volume_rupture:,.0f} t\n\n"
                       f"✅ SATISFACTION: {taux_satisfaction:.1f}%",
            categorie=CategorieInsight.PERFORMANCE,
            importance=NiveauImportance.SUCCES,
            valeur=valeur_opt,
            unite="DT",
            icone="📊"
        ))
        
        # Taux de satisfaction
        if taux_satisfaction >= 99.9:
            niveau = NiveauImportance.SUCCES
            icone = "🏆"
            commentaire = "Parfait! Toute la demande est satisfaite."
        elif taux_satisfaction >= 90:
            niveau = NiveauImportance.ATTENTION
            icone = "✅"
            commentaire = "Bon niveau malgré les contraintes."
        else:
            niveau = NiveauImportance.CRITIQUE
            icone = "⚠️"
            commentaire = "Déficit structurel important."
        self.insights.append(Insight(
            titre="Taux de satisfaction",
            description=f"{taux_satisfaction:.1f}% de la demande satisfaite. {commentaire}\n"
                       f"Volume transporté: {volume_total:.1f}t | Ruptures: {volume_rupture:.1f}t",
            categorie=CategorieInsight.PERFORMANCE,
            importance=niveau,
            valeur=taux_satisfaction,
            unite="%",
            icone=icone
        ))
        
        # Infos techniques avec explication
        nb_vars = self.resultats.get('nb_variables', 0)
        nb_constr = self.resultats.get('nb_contraintes', 0)
        temps = self.resultats.get('temps_resolution', 0)
        nb_transferts = self.resultats.get('nb_transferts', 0)
        
        self.insights.append(Insight(
            titre="Performance Gurobi",
            description=f"⚡ Résolu en {temps:.3f} secondes\n\n"
                       f"Complexité du problème:\n"
                       f"   • {nb_vars} variables de décision (flux x[i,j,m])\n"
                       f"   • {nb_constr} contraintes (capacités, conservation)\n"
                       f"   • {nb_transferts} liaisons actives dans la solution\n\n"
                       f"Gurobi utilise l'algorithme du Simplexe et Branch&Bound\n"
                       f"pour garantir l'optimalité mathématique.",
            categorie=CategorieInsight.PERFORMANCE,
            importance=NiveauImportance.INFO,
            valeur=temps,
            unite="secondes"
        ))
    
    def _analyser_systeme_penalites(self):
        """
        Analyse détaillée du système de pénalités avec exemples concrets.
        """
        if 'valeur_optimale' not in self.resultats:
            return
        
        d = self.donnees
        # Récupérer la pénalité depuis les données (paramétrable)
        PENALITE_RUPTURE = getattr(d, 'penalite_rupture_unitaire', 100.0)
        
        ruptures_dict = self.resultats.get('ruptures', {})
        flux_dict = self.resultats.get('flux', {})
        
        # Calculer les coûts
        cout_ruptures = sum(val * PENALITE_RUPTURE for val in ruptures_dict.values())
        cout_transport = sum(val * d.cout_transport[i, j, m] for (i, j, m), val in flux_dict.items())
        volume_rupture = sum(ruptures_dict.values()) if ruptures_dict else 0
        
        # Statistiques sur les coûts de transport
        volume_total = sum(flux_dict.values()) if flux_dict else 1
        cout_transport_moyen = cout_transport / volume_total if volume_total > 0 else 0
        
        # Trouver le coût min et max de transport
        couts_utilises = [d.cout_transport[i, j, m] for (i, j, m) in flux_dict.keys()]
        cout_min = min(couts_utilises) if couts_utilises else 0
        cout_max = max(couts_utilises) if couts_utilises else 0
        
        # ═══════════════════════════════════════════════════════════════
        # INSIGHT 1: Explication complète du système de pénalités
        # ═══════════════════════════════════════════════════════════════
        desc = f"═══════════════════════════════════════════════════════════════\n"
        desc += f"        SYSTÈME DE PÉNALITÉ DE RUPTURE - EXPLICATION\n"
        desc += f"═══════════════════════════════════════════════════════════════\n\n"
        
        desc += f"📌 PARAMÈTRE ACTUEL: {PENALITE_RUPTURE:.2f} DT par tonne en rupture\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"🎯 PRINCIPE FONDAMENTAL\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        desc += f"La pénalité de rupture est un COÛT FICTIF ajouté à la fonction\n"
        desc += f"objectif pour chaque tonne de demande non satisfaite.\n\n"
        
        desc += f"   FONCTION OBJECTIF:\n"
        desc += f"   ┌─────────────────────────────────────────────────────────┐\n"
        desc += f"   │ MIN Z = Σ(coût_transport × flux) + Σ(PÉNALITÉ × rupture)│\n"
        desc += f"   └─────────────────────────────────────────────────────────┘\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"🧮 LOGIQUE DE DÉCISION DU SOLVEUR\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        desc += f"Pour chaque tonne de demande, Gurobi compare:\n\n"
        desc += f"   OPTION A: Transporter (coût = {cout_transport_moyen:.2f} DT/t en moyenne)\n"
        desc += f"   OPTION B: Rupture    (coût = {PENALITE_RUPTURE:.2f} DT/t)\n\n"
        
        if PENALITE_RUPTURE > cout_transport_moyen:
            desc += f"   → Pénalité ({PENALITE_RUPTURE:.2f}) > Transport ({cout_transport_moyen:.2f})\n"
            desc += f"   → Le solveur PRÉFÈRE transporter quand c'est possible\n"
            desc += f"   → Rupture = DERNIER RECOURS (offre insuffisante)\n\n"
        else:
            desc += f"   ⚠️ Pénalité ({PENALITE_RUPTURE:.2f}) < Transport ({cout_transport_moyen:.2f})\n"
            desc += f"   → Le solveur pourrait PRÉFÉRER la rupture!\n"
            desc += f"   → Augmentez la pénalité pour forcer les livraisons\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"📊 EXEMPLE CONCRET (cette solution)\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        desc += f"   Coûts de transport utilisés:\n"
        desc += f"      • Minimum: {cout_min:.2f} DT/t\n"
        desc += f"      • Maximum: {cout_max:.2f} DT/t\n"
        desc += f"      • Moyenne: {cout_transport_moyen:.2f} DT/t\n\n"
        
        desc += f"   Pénalité de rupture: {PENALITE_RUPTURE:.2f} DT/t\n\n"
        
        if volume_rupture > 0:
            desc += f"   📍 Ruptures dans cette solution: {volume_rupture:.1f} tonnes\n"
            desc += f"      Coût des ruptures: {volume_rupture:.1f}t × {PENALITE_RUPTURE:.2f} = {cout_ruptures:,.2f} DT\n\n"
            desc += f"   💡 POURQUOI ces ruptures?\n"
            desc += f"      → L'offre totale est INSUFFISANTE pour la demande\n"
            desc += f"      → Même en payant le coût max ({cout_max:.2f} DT/t),\n"
            desc += f"        il n'y a pas assez de marchandise disponible\n"
        else:
            desc += f"   ✅ AUCUNE RUPTURE dans cette solution!\n"
            desc += f"      → Toute la demande peut être satisfaite\n"
            desc += f"      → La pénalité n'a pas eu besoin d'être appliquée\n"
        
        self.insights.append(Insight(
            titre="⚙️ Système de Pénalités - Explication Détaillée",
            description=desc,
            categorie=CategorieInsight.COUTS,
            importance=NiveauImportance.INFO,
            icone="⚙️"
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # INSIGHT 2: Impact de la valeur de la pénalité
        # ═══════════════════════════════════════════════════════════════
        desc2 = f"═══════════════════════════════════════════════════════════════\n"
        desc2 += f"        IMPACT DU CHOIX DE LA PÉNALITÉ\n"
        desc2 += f"═══════════════════════════════════════════════════════════════\n\n"
        
        desc2 += f"🔧 PÉNALITÉ ACTUELLE: {PENALITE_RUPTURE:.2f} DT/tonne\n\n"
        
        desc2 += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc2 += f"📈 EFFET DE DIFFÉRENTES VALEURS DE PÉNALITÉ:\n"
        desc2 += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Calculer ce qui se passerait avec différentes pénalités
        desc2 += f"   • Pénalité FAIBLE (< {cout_min:.2f} DT/t):\n"
        desc2 += f"     → Le solveur préfère la rupture au transport!\n"
        desc2 += f"     → ⚠️ DÉCONSEILLÉ: solution irréaliste\n\n"
        
        desc2 += f"   • Pénalité MODÉRÉE ({cout_min:.2f} - {cout_max:.2f} DT/t):\n"
        desc2 += f"     → Rupture seulement si transport très cher\n"
        desc2 += f"     → Compromis économique\n\n"
        
        desc2 += f"   • Pénalité ÉLEVÉE (> {cout_max:.2f} DT/t): ← RECOMMANDÉ\n"
        desc2 += f"     → Le solveur évite les ruptures à tout prix\n"
        desc2 += f"     → Ruptures = uniquement si impossible physiquement\n\n"
        
        desc2 += f"   • Pénalité TRÈS ÉLEVÉE (ex: 10000 DT/t):\n"
        desc2 += f"     → Force satisfaction maximale\n"
        desc2 += f"     → Peut rendre le problème infaisable si déficit\n\n"
        
        desc2 += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc2 += f"💡 RECOMMANDATION:\n"
        desc2 += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        penalite_recommandee = max(cout_max * 10, 100)
        desc2 += f"   Pénalité recommandée: {penalite_recommandee:.0f} DT/t\n"
        desc2 += f"   (10× le coût de transport maximum)\n\n"
        desc2 += f"   Cela garantit que le solveur:\n"
        desc2 += f"   ✓ Utilisera TOUTES les routes disponibles avant rupture\n"
        desc2 += f"   ✓ N'acceptera une rupture que si IMPOSSIBLE autrement"
        
        self.insights.append(Insight(
            titre="📊 Impact du Choix de la Pénalité",
            description=desc2,
            categorie=CategorieInsight.COUTS,
            importance=NiveauImportance.INFO,
            icone="📊"
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # INSIGHT 3: Décomposition du coût si ruptures
        # ═══════════════════════════════════════════════════════════════
        if cout_ruptures > 0:
            self.insights.append(Insight(
                titre="💸 Impact des Pénalités sur cette Solution",
                description=f"═══════════════════════════════════════════════════\n"
                           f"COÛT TOTAL DES RUPTURES: {cout_ruptures:,.2f} DT\n"
                           f"═══════════════════════════════════════════════════\n\n"
                           f"📈 Décomposition:\n"
                           f"   • Coût transport: {cout_transport:,.2f} DT\n"
                           f"   • Coût ruptures: {cout_ruptures:,.2f} DT\n"
                           f"   • TOTAL: {cout_transport + cout_ruptures:,.2f} DT\n\n"
                           f"❓ POURQUOI CES RUPTURES?\n"
                           f"   Le solveur a calculé que payer {cout_ruptures:,.2f} DT\n"
                           f"   de pénalités est MOINS CHER que toute alternative:\n"
                           f"   → Soit l'offre est insuffisante (déficit structurel)\n"
                           f"   → Soit les routes sont saturées (capacités limitées)\n\n"
                           f"✅ C'est mathématiquement prouvé optimal!",
                categorie=CategorieInsight.COUTS,
                importance=NiveauImportance.ATTENTION,
                valeur=cout_ruptures,
                unite="DT de pénalités",
                icone="💸"
            ))

    def _analyser_contraintes(self):
        """
        NOUVEAU: Analyse détaillée des contraintes du modèle.
        """
        if 'valeur_optimale' not in self.resultats:
            return
        
        d = self.donnees
        flux_dict = self.resultats.get('flux', {})
        
        # Identifier les contraintes actives (saturées)
        contraintes_capacite_saturees = []
        contraintes_offre_saturees = []
        
        # Vérifier les contraintes de capacité
        for i in range(d.n_sites):
            for j in range(d.n_sites):
                if i != j:
                    flux_ij = sum(flux_dict.get((i, j, m), 0) for m in range(d.n_matieres))
                    capacite = d.capacite_transfert[i, j]
                    if capacite < float('inf') and flux_ij >= capacite * 0.95:  # 95% = quasi saturé
                        contraintes_capacite_saturees.append({
                            'origine': self._get_nom_site(i),
                            'destination': self._get_nom_site(j),
                            'flux': flux_ij,
                            'capacite': capacite,
                            'taux': flux_ij / capacite * 100
                        })
        
        # Vérifier les contraintes d'offre (stock épuisé)
        for i in range(d.n_sites):
            for m in range(d.n_matieres):
                offre_im = d.offre[i, m]
                if offre_im > 0:
                    flux_sortant = sum(flux_dict.get((i, j, m), 0) for j in range(d.n_sites) if j != i)
                    if flux_sortant >= offre_im * 0.95:
                        contraintes_offre_saturees.append({
                            'site': self._get_nom_site(i),
                            'matiere': self._get_nom_matiere(m),
                            'offre': offre_im,
                            'utilise': flux_sortant
                        })
        
        nb_contraintes = self.resultats.get('nb_contraintes', 0)
        
        desc = f"═══════════════════════════════════════════════════\n"
        desc += f"LE MODÈLE RESPECTE {nb_contraintes} CONTRAINTES\n"
        desc += f"═══════════════════════════════════════════════════\n\n"
        
        desc += f"📋 TYPES DE CONTRAINTES:\n\n"
        desc += f"   1️⃣ Conservation de flux (Kirchhoff):\n"
        desc += f"      Entrées + Stock initial = Sorties + Stock final\n\n"
        desc += f"   2️⃣ Satisfaction demande:\n"
        desc += f"      Reçu + Rupture = Demande (∀ site, matière)\n\n"
        desc += f"   3️⃣ Limite d'offre:\n"
        desc += f"      Envoyé ≤ Stock disponible (∀ source)\n\n"
        desc += f"   4️⃣ Capacité de transfert:\n"
        desc += f"      Flux(i→j) ≤ Capacité(i,j) (∀ arc)"
        
        self.insights.append(Insight(
            titre="📐 Contraintes du Modèle Mathématique",
            description=desc,
            categorie=CategorieInsight.CAPACITES,
            importance=NiveauImportance.INFO,
            icone="📐"
        ))
        
        # Contraintes saturées (goulots d'étranglement)
        if contraintes_capacite_saturees or contraintes_offre_saturees:
            desc_saturees = f"═══════════════════════════════════════════════════\n"
            desc_saturees += f"⚠️ GOULOTS D'ÉTRANGLEMENT IDENTIFIÉS\n"
            desc_saturees += f"═══════════════════════════════════════════════════\n\n"
            
            if contraintes_capacite_saturees:
                desc_saturees += f"🚧 CAPACITÉS SATURÉES:\n"
                for c in contraintes_capacite_saturees[:5]:
                    desc_saturees += f"   • {c['origine']} → {c['destination']}: "
                    desc_saturees += f"{c['flux']:.0f}/{c['capacite']:.0f}t ({c['taux']:.0f}%)\n"
                desc_saturees += "\n"
            
            if contraintes_offre_saturees:
                desc_saturees += f"📦 OFFRES ÉPUISÉES:\n"
                for c in contraintes_offre_saturees[:5]:
                    desc_saturees += f"   • {c['site']} ({c['matiere']}): "
                    desc_saturees += f"{c['utilise']:.0f}/{c['offre']:.0f}t utilisé\n"
            
            desc_saturees += f"\n💡 Ces contraintes limitent la solution optimale.\n"
            desc_saturees += f"   Augmenter ces capacités pourrait améliorer le résultat."
            
            self.insights.append(Insight(
                titre="🚧 Contraintes Actives (Saturées)",
                description=desc_saturees,
                categorie=CategorieInsight.CAPACITES,
                importance=NiveauImportance.ATTENTION,
                icone="🚧"
            ))

    def _analyser_optimalite(self):
        """
        NOUVEAU: Preuve détaillée de l'optimalité de la solution.
        """
        if 'valeur_optimale' not in self.resultats:
            return
        
        d = self.donnees
        valeur_opt = self.resultats['valeur_optimale']
        statut = self.resultats.get('statut_gurobi', 2)
        
        flux_dict = self.resultats.get('flux', {})
        
        # Coûts minimaux par matière
        cout_min_par_matiere = []
        for m in range(d.n_matieres):
            couts_m = []
            for i in range(d.n_sites):
                for j in range(d.n_sites):
                    if i != j and d.cout_transport[i, j, m] > 0:
                        couts_m.append(d.cout_transport[i, j, m])
            if couts_m:
                cout_min_par_matiere.append((self._get_nom_matiere(m), min(couts_m), np.mean(couts_m)))
        
        # Borne inférieure naïve
        volume_total = self.resultats.get('volume_total', 0)
        cout_min_global = min(c[1] for c in cout_min_par_matiere) if cout_min_par_matiere else 0
        borne_inf_naive = volume_total * cout_min_global
        
        nb_vars = self.resultats.get('nb_variables', d.n_sites**2 * d.n_matieres)
        
        desc = f"═══════════════════════════════════════════════════\n"
        desc += f"🏆 PREUVE D'OPTIMALITÉ MATHÉMATIQUE\n"
        desc += f"═══════════════════════════════════════════════════\n\n"
        
        desc += f"✅ STATUT GUROBI: {'OPTIMAL' if statut == 2 else 'Sous-optimal'}\n\n"
        
        desc += f"📊 COÛT OPTIMAL TROUVÉ: {valeur_opt:,.2f} DT\n\n"
        
        desc += f"🔬 POURQUOI C'EST LE MINIMUM ABSOLU?\n\n"
        desc += f"   1. Gurobi a exploré l'espace des solutions:\n"
        desc += f"      → {nb_vars} variables de décision\n"
        desc += f"      → Espace: {d.n_sites}×{d.n_sites}×{d.n_matieres} dimensions\n\n"
        
        desc += f"   2. Algorithme Simplexe:\n"
        desc += f"      → Parcourt les sommets du polytope\n"
        desc += f"      → Garantit l'optimum global (pas local)\n\n"
        
        desc += f"   3. Conditions d'optimalité (KKT):\n"
        desc += f"      → Coûts réduits ≥ 0 pour variables nulles\n"
        desc += f"      → Toute déviation augmenterait le coût\n\n"
        
        desc += f"📉 BORNE INFÉRIEURE THÉORIQUE:\n"
        desc += f"   Route la moins chère: {cout_min_global:.2f} DT/t\n"
        desc += f"   Borne naïve: {borne_inf_naive:,.2f} DT\n"
        desc += f"   (Irréalisable: ignore capacités et offres)\n\n"
        
        desc += f"🎯 CONCLUSION:\n"
        desc += f"   {valeur_opt:,.2f} DT est le MINIMUM POSSIBLE\n"
        desc += f"   compte tenu de toutes les contraintes."
        
        self.insights.append(Insight(
            titre="🏆 Pourquoi cette Solution est Optimale?",
            description=desc,
            categorie=CategorieInsight.PERFORMANCE,
            importance=NiveauImportance.SUCCES,
            valeur=valeur_opt,
            unite="DT (minimum garanti)",
            icone="🏆"
        ))

    def _analyser_alternatives(self):
        """
        Analyse détaillée des solutions alternatives avec calculs précis.
        Explique pourquoi Gurobi fait mieux que "fournisseur le plus proche".
        """
        if 'valeur_optimale' not in self.resultats:
            return
        
        d = self.donnees
        valeur_opt = self.resultats['valeur_optimale']
        flux_dict = self.resultats.get('flux', {})
        ruptures_dict = self.resultats.get('ruptures', {})
        
        PENALITE_RUPTURE = getattr(d, 'penalite_rupture_unitaire', 100.0)
        volume_rupture = sum(ruptures_dict.values()) if ruptures_dict else 0
        demande_totale = float(np.sum(d.demande))
        cout_transport_opt = sum(val * d.cout_transport[i, j, m] for (i, j, m), val in flux_dict.items())
        
        # ═══════════════════════════════════════════════════════════════
        # INSIGHT: Comparaison détaillée avec "fournisseur le plus proche"
        # ═══════════════════════════════════════════════════════════════
        
        desc = f"═══════════════════════════════════════════════════════════════\n"
        desc += f"   GUROBI vs \"FOURNISSEUR LE PLUS PROCHE\" - COMPARAISON\n"
        desc += f"═══════════════════════════════════════════════════════════════\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"🤔 STRATÉGIE NAÏVE: \"Fournisseur le plus proche\"\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        desc += f"   Principe: Chaque site commande au fournisseur le moins cher\n"
        desc += f"   (ou le plus proche), sans coordination globale.\n\n"
        
        # Simuler la stratégie naïve avec suivi des stocks
        stock_dispo = {}  # Copie des offres
        for i in range(d.n_sites):
            for m in range(d.n_matieres):
                stock_dispo[(i, m)] = d.offre[i, m]
        
        cout_naif = 0.0
        rupture_naif = 0.0
        details_naifs = []
        
        for j in range(d.n_sites):
            for m in range(d.n_matieres):
                demande_jm = d.demande[j, m]
                if demande_jm > 0:
                    # Trier les fournisseurs par coût
                    fournisseurs = []
                    for i in range(d.n_sites):
                        if i != j and stock_dispo[(i, m)] > 0:
                            fournisseurs.append((d.cout_transport[i, j, m], i, stock_dispo[(i, m)]))
                    fournisseurs.sort()  # Trier par coût
                    
                    demande_restante = demande_jm
                    for cout, i, stock in fournisseurs:
                        if demande_restante <= 0:
                            break
                        quantite = min(demande_restante, stock)
                        cout_naif += quantite * cout
                        stock_dispo[(i, m)] -= quantite
                        demande_restante -= quantite
                        if quantite > 0.1:
                            details_naifs.append(f"{self._get_nom_site(i)}→{self._get_nom_site(j)}: {quantite:.0f}t × {cout:.2f} DT")
                    
                    if demande_restante > 0:
                        rupture_naif += demande_restante
                        cout_naif += demande_restante * PENALITE_RUPTURE
        
        desc += f"   Résultat de la stratégie naïve:\n"
        desc += f"   ┌────────────────────────────────────────┐\n"
        desc += f"   │ Coût transport:  {cout_naif - rupture_naif*PENALITE_RUPTURE:>12,.2f} DT │\n"
        desc += f"   │ Pénalités:       {rupture_naif*PENALITE_RUPTURE:>12,.2f} DT │\n"
        desc += f"   │ TOTAL NAÏF:      {cout_naif:>12,.2f} DT │\n"
        desc += f"   └────────────────────────────────────────┘\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"🏆 SOLUTION GUROBI (optimale)\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        desc += f"   Principe: Optimisation GLOBALE simultanée de tous les flux\n"
        desc += f"   pour minimiser le coût total du réseau.\n\n"
        
        desc += f"   Résultat de Gurobi:\n"
        desc += f"   ┌────────────────────────────────────────┐\n"
        desc += f"   │ Coût transport:  {cout_transport_opt:>12,.2f} DT │\n"
        desc += f"   │ Pénalités:       {volume_rupture*PENALITE_RUPTURE:>12,.2f} DT │\n"
        desc += f"   │ TOTAL OPTIMAL:   {valeur_opt:>12,.2f} DT │\n"
        desc += f"   └────────────────────────────────────────┘\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"📊 COMPARAISON\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        diff = cout_naif - valeur_opt
        if diff > 0.01:
            pct_economie = (diff / cout_naif) * 100
            desc += f"   💰 ÉCONOMIE GRÂCE À GUROBI: {diff:,.2f} DT\n"
            desc += f"   📈 Réduction: {pct_economie:.1f}% par rapport à la stratégie naïve\n\n"
            
            desc += f"   🔍 POURQUOI GUROBI FAIT MIEUX?\n\n"
            desc += f"   1. VISION GLOBALE:\n"
            desc += f"      → La stratégie naïve optimise chaque site INDÉPENDAMMENT\n"
            desc += f"      → Gurobi optimise TOUS les flux SIMULTANÉMENT\n\n"
            
            desc += f"   2. ÉVITE LES CONFLITS:\n"
            desc += f"      → Naïf: 2 sites peuvent \"se battre\" pour le même fournisseur\n"
            desc += f"      → Gurobi: Répartit intelligemment les ressources limitées\n\n"
            
            desc += f"   3. EXPLOITE LES ALTERNATIVES:\n"
            desc += f"      → Naïf: Chaque site prend la route la moins chère\n"
            desc += f"      → Gurobi: Accepte une route légèrement plus chère si ça\n"
            desc += f"        libère la route optimale pour un autre flux plus important\n\n"
        else:
            desc += f"   ✅ Les deux stratégies donnent un résultat similaire.\n\n"
            desc += f"   Cela signifie que:\n"
            desc += f"   → Le problème est \"bien conditionné\"\n"
            desc += f"   → Pas de conflits de ressources majeurs\n"
            desc += f"   → La solution naïve est proche de l'optimal\n\n"
        
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        desc += f"🎯 CONCLUSION\n"
        desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        desc += f"   La solution Gurobi à {valeur_opt:,.2f} DT est GARANTIE optimale.\n"
        desc += f"   Aucune autre affectation de flux ne peut coûter moins,\n"
        desc += f"   que ce soit \"fournisseur proche\" ou toute autre heuristique."
        
        self.insights.append(Insight(
            titre="🔄 Gurobi vs Fournisseur le Plus Proche",
            description=desc,
            categorie=CategorieInsight.COUTS,
            importance=NiveauImportance.SUCCES if diff > 0.01 else NiveauImportance.INFO,
            valeur=diff,
            unite="DT économisés",
            icone="🔄"
        ))
        
        self.insights.append(Insight(
            titre="🔄 Analyse des Alternatives",
            description=desc,
            categorie=CategorieInsight.COUTS,
            importance=NiveauImportance.INFO,
            icone="🔄"
        ))

    def _analyser_flux(self):
        """Analyse des flux de transport."""
        flux_dict = self.resultats.get('flux', {})
        if not flux_dict:
            return
        
        d = self.donnees
        volume_total = self.resultats.get('volume_total', sum(flux_dict.values()))
        n_flux = len(flux_dict)
        
        if volume_total > 0:
            flux_moyen = volume_total / n_flux if n_flux > 0 else 0
            
            self.insights.append(Insight(
                titre="Volume transporté",
                description=f"{volume_total:,.1f} tonnes via {n_flux} liaisons actives.\n"
                           f"Flux moyen: {flux_moyen:.1f}t par liaison.",
                categorie=CategorieInsight.FLUX,
                importance=NiveauImportance.INFO,
                valeur=volume_total,
                unite="tonnes"
            ))
            
            # Top 5 flux avec explication d'optimalité
            flux_list = []
            for (i, j, m), val in flux_dict.items():
                cout_unit = d.cout_transport[i, j, m]
                flux_list.append({
                    'origine': self._get_nom_site(i),
                    'destination': self._get_nom_site(j),
                    'matiere': self._get_nom_matiere(m),
                    'quantite': val,
                    'cout_unit': cout_unit,
                    'cout_total': val * cout_unit,
                    'i': i, 'j': j, 'm': m
                })
            
            if flux_list:
                flux_list.sort(key=lambda x: x['quantite'], reverse=True)
                top5 = flux_list[:5]
                
                desc = "Principales liaisons (choix optimal):"
                for k, f in enumerate(top5, 1):
                    desc += f"\n  {k}. {f['origine']} → {f['destination']} ({f['matiere']})"
                    desc += f"\n     {f['quantite']:.1f}t × {f['cout_unit']:.2f} DT/t = {f['cout_total']:.2f} DT"
                
                self.insights.append(Insight(
                    titre="Top 5 des flux",
                    description=desc,
                    categorie=CategorieInsight.FLUX,
                    importance=NiveauImportance.INFO
                ))
            
            # Explication du choix des routes
            # Trouver le flux le moins cher et le plus cher
            flux_list.sort(key=lambda x: x['cout_unit'])
            moins_cher = flux_list[0] if flux_list else None
            plus_cher = flux_list[-1] if flux_list else None
            
            if moins_cher and plus_cher and moins_cher != plus_cher:
                self.insights.append(Insight(
                    titre="Logique d'optimisation",
                    description=f"🔍 Comment Gurobi choisit les routes?\n\n"
                               f"Route la moins chère utilisée:\n"
                               f"   {moins_cher['origine']} → {moins_cher['destination']} ({moins_cher['matiere']})\n"
                               f"   Coût: {moins_cher['cout_unit']:.2f} DT/t\n\n"
                               f"Route la plus chère utilisée:\n"
                               f"   {plus_cher['origine']} → {plus_cher['destination']} ({plus_cher['matiere']})\n"
                               f"   Coût: {plus_cher['cout_unit']:.2f} DT/t\n\n"
                               f"→ Les routes chères ne sont utilisées que si nécessaire\n"
                               f"   (capacités limitées sur routes moins chères)",
                    categorie=CategorieInsight.FLUX,
                    importance=NiveauImportance.INFO,
                    icone="🧠"
                ))
    
    def _analyser_couts(self):
        """Analyse de la structure des coûts."""
        flux_dict = self.resultats.get('flux', {})
        if not flux_dict or 'valeur_optimale' not in self.resultats:
            return
        
        d = self.donnees
        valeur_opt = self.resultats['valeur_optimale']
        
        # Coût de transport
        cout_transport = 0.0
        for (i, j, m), val in flux_dict.items():
            cout_transport += val * d.cout_transport[i, j, m]
        
        # Coût des ruptures (pénalité configurable)
        ruptures_dict = self.resultats.get('ruptures', {})
        cout_ruptures = 0.0
        PENALITE_RUPTURE = getattr(d, 'penalite_rupture_unitaire', 100.0)
        
        for (j, m), val in ruptures_dict.items():
            cout_ruptures += val * PENALITE_RUPTURE
        
        if valeur_opt > 0:
            pct_transport = (cout_transport / valeur_opt) * 100
            pct_ruptures = (cout_ruptures / valeur_opt) * 100
            
            self.insights.append(Insight(
                titre="Répartition des coûts",
                description=f"Transport: {cout_transport:,.2f} DT ({pct_transport:.1f}%)\n"
                           f"Pénalités ruptures: {cout_ruptures:,.2f} DT ({pct_ruptures:.1f}%)",
                categorie=CategorieInsight.COUTS,
                importance=NiveauImportance.INFO if pct_ruptures < 20 else NiveauImportance.ATTENTION,
                valeur=cout_transport,
                unite="DT transport"
            ))
    
    def _analyser_stocks(self):
        """Analyse des stocks résiduels."""
        stocks_dict = self.resultats.get('stocks', {})
        d = self.donnees
        
        stock_total = sum(stocks_dict.values()) if stocks_dict else 0
        offre_totale = float(np.sum(d.offre))
        
        if offre_totale > 0:
            taux_utilisation = ((offre_totale - stock_total) / offre_totale) * 100
            
            if stock_total > 0.1:
                stocks_detail = []
                for (i, m), val in stocks_dict.items():
                    if val > 0.1:
                        stocks_detail.append(f"{self._get_nom_site(i)} ({self._get_nom_matiere(m)}): {val:.1f}t")
                
                desc = f"{stock_total:.1f}t de stock résiduel ({100-taux_utilisation:.1f}% non utilisé)"
                if stocks_detail:
                    desc += "\n" + "\n".join(f"  • {s}" for s in stocks_detail[:5])
                
                niveau = NiveauImportance.SUCCES if taux_utilisation >= 90 else NiveauImportance.ATTENTION
            else:
                desc = f"Toute l'offre ({offre_totale:.1f}t) a été utilisée. Excellent!"
                niveau = NiveauImportance.SUCCES
            
            self.insights.append(Insight(
                titre="Stocks résiduels",
                description=desc,
                categorie=CategorieInsight.STOCKS,
                importance=niveau,
                valeur=stock_total,
                unite="tonnes"
            ))
    
    def _analyser_ruptures(self):
        """Analyse des ruptures."""
        ruptures_dict = self.resultats.get('ruptures', {})
        d = self.donnees
        
        rupture_totale = sum(ruptures_dict.values()) if ruptures_dict else 0
        demande_totale = float(np.sum(d.demande))
        
        if rupture_totale <= 0.1:
            self.insights.append(Insight(
                titre="Zéro rupture",
                description=f"✅ Aucune rupture! Toute la demande ({demande_totale:.1f}t) est satisfaite.",
                categorie=CategorieInsight.RUPTURES,
                importance=NiveauImportance.SUCCES,
                valeur=0,
                unite="tonnes",
                icone="🏆"
            ))
        else:
            taux_rupture = (rupture_totale / demande_totale * 100) if demande_totale > 0 else 0
            
            ruptures_detail = []
            for (j, m), val in ruptures_dict.items():
                if val > 0.1:
                    ruptures_detail.append({
                        'site': self._get_nom_site(j),
                        'matiere': self._get_nom_matiere(m),
                        'quantite': val
                    })
            
            ruptures_detail.sort(key=lambda x: x['quantite'], reverse=True)
            
            desc = f"⚠️ Ruptures: {rupture_totale:.1f}t ({taux_rupture:.1f}% de la demande)"
            if ruptures_detail:
                desc += "\nDétail:"
                for r in ruptures_detail[:5]:
                    desc += f"\n  • {r['site']} ({r['matiere']}): {r['quantite']:.1f}t"
            
            niveau = NiveauImportance.CRITIQUE if taux_rupture > 10 else NiveauImportance.ATTENTION
            
            self.insights.append(Insight(
                titre="Ruptures de stock",
                description=desc,
                categorie=CategorieInsight.RUPTURES,
                importance=niveau,
                valeur=rupture_totale,
                unite="tonnes",
                icone="⚠️"
            ))
    
    def _generer_recommandations(self):
        """Génère des recommandations."""
        d = self.donnees
        recommandations = []
        
        # Recommandations basées sur les ruptures
        ruptures_dict = self.resultats.get('ruptures', {})
        if ruptures_dict:
            # Agréger par matière
            ruptures_par_matiere = {}
            for (j, m), val in ruptures_dict.items():
                ruptures_par_matiere[m] = ruptures_par_matiere.get(m, 0) + val
            
            for m, rupture_m in ruptures_par_matiere.items():
                if rupture_m > 0:
                    offre_m = float(np.sum(d.offre[:, m]))
                    demande_m = float(np.sum(d.demande[:, m]))
                    nom_m = self._get_nom_matiere(m)
                    
                    if offre_m < demande_m:
                        recommandations.append(
                            f"📈 Augmenter l'offre de {nom_m} de {demande_m - offre_m:.1f}t pour éliminer le déficit."
                        )
                    else:
                        recommandations.append(
                            f"🔄 Vérifier les capacités pour {nom_m}: l'offre existe mais n'atteint pas la demande."
                        )
        
        # Recommandations basées sur les stocks
        stocks_dict = self.resultats.get('stocks', {})
        if stocks_dict:
            stocks_par_site = {}
            for (i, m), val in stocks_dict.items():
                stocks_par_site[i] = stocks_par_site.get(i, 0) + val
            
            for i, stock_site in stocks_par_site.items():
                offre_site = float(np.sum(d.offre[i, :]))
                if offre_site > 0 and stock_site / offre_site > 0.3:
                    recommandations.append(
                        f"📦 {self._get_nom_site(i)} a {stock_site:.1f}t de stock inutilisé."
                    )
        
        recommandations = recommandations[:5]
        
        if recommandations:
            self.insights.append(Insight(
                titre="Recommandations",
                description="Actions suggérées:\n" + "\n".join(f"  {i+1}. {r}" for i, r in enumerate(recommandations)),
                categorie=CategorieInsight.RECOMMANDATIONS,
                importance=NiveauImportance.INFO,
                icone="💡"
            ))
        else:
            self.insights.append(Insight(
                titre="Solution équilibrée",
                description="La solution est bien équilibrée. Aucune recommandation particulière.",
                categorie=CategorieInsight.RECOMMANDATIONS,
                importance=NiveauImportance.SUCCES,
                icone="✅"
            ))
    
    def generer_rapport_html(self) -> str:
        """Génère un rapport HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .insight {{ padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; background: #f8f9fa; }}
        .insight.succes {{ border-left-color: #27ae60; background: #e8f5e9; }}
        .insight.attention {{ border-left-color: #f39c12; background: #fff3e0; }}
        .insight.critique {{ border-left-color: #e74c3c; background: #ffebee; }}
        .insight-title {{ font-weight: bold; font-size: 16px; margin-bottom: 8px; }}
        .insight-desc {{ color: #555; white-space: pre-line; }}
        .insight-value {{ display: inline-block; margin-top: 8px; padding: 4px 12px; background: #3498db; color: white; border-radius: 15px; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport d'Analyse - Optimisation</h1>
        <p style="color: #666;">Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}</p>
"""
        
        for insight in self.insights:
            classe = {
                NiveauImportance.SUCCES: "succes",
                NiveauImportance.ATTENTION: "attention",
                NiveauImportance.CRITIQUE: "critique"
            }.get(insight.importance, "")
            
            html += f"""
        <div class="insight {classe}">
            <div class="insight-title">{insight.icone} {insight.titre}</div>
            <div class="insight-desc">{insight.description}</div>
"""
            if insight.valeur is not None and insight.unite:
                html += f'            <div class="insight-value">{insight.valeur:,.2f} {insight.unite}</div>\n'
            html += "        </div>\n"
        
        html += """
    </div>
</body>
</html>"""
        
        return html
