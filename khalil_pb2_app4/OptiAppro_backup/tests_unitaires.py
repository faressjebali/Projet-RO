"""
Tests unitaires pour le modèle d'approvisionnement
Projet RO - INSA
"""

import unittest
import numpy as np
from modele_approvisionnement import ModeleDonneesApprovisionnement, ModeleApprovisionnementPL


class TestModeleDonnees(unittest.TestCase):
    """Tests pour la classe ModeleDonneesApprovisionnement"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.donnees = ModeleDonneesApprovisionnement(n_sites=5, n_matieres=3)
        self.donnees.generer_donnees_exemple()
    
    def test_dimensions(self):
        """Vérifie que les dimensions sont correctes"""
        self.assertEqual(self.donnees.n_sites, 5)
        self.assertEqual(self.donnees.n_matieres, 3)
        self.assertEqual(self.donnees.offre.shape, (5, 3))
        self.assertEqual(self.donnees.demande.shape, (5, 3))
    
    def test_non_negativite(self):
        """Vérifie que toutes les valeurs sont non négatives"""
        self.assertTrue(np.all(self.donnees.offre >= 0))
        self.assertTrue(np.all(self.donnees.demande >= 0))
        self.assertTrue(np.all(self.donnees.cout_transport >= 0))
        self.assertTrue(np.all(self.donnees.distance >= 0))
    
    def test_validation_donnees_valides(self):
        """Vérifie la validation avec des données valides"""
        valide, erreurs = self.donnees.valider_donnees()
        self.assertTrue(valide)
        self.assertEqual(len(erreurs), 0)
    
    def test_validation_offre_negative(self):
        """Vérifie la détection d'offres négatives"""
        self.donnees.offre[0, 0] = -10
        valide, erreurs = self.donnees.valider_donnees()
        self.assertFalse(valide)
        self.assertGreater(len(erreurs), 0)
    
    def test_noms_sites(self):
        """Vérifie que les noms sont bien définis"""
        self.assertEqual(len(self.donnees.noms_sites), 5)
        self.assertIn("Site_Nord", self.donnees.noms_sites)
    
    def test_offre_totale(self):
        """Vérifie le total de l'offre"""
        offre_totale = self.donnees.offre.sum()
        self.assertEqual(offre_totale, 880.0)
    
    def test_demande_totale(self):
        """Vérifie le total de la demande"""
        demande_totale = self.donnees.demande.sum()
        self.assertEqual(demande_totale, 930.0)


class TestModeleOptimisation(unittest.TestCase):
    """Tests pour la classe ModeleApprovisionnementPL"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.donnees = ModeleDonneesApprovisionnement(n_sites=5, n_matieres=3)
        self.donnees.generer_donnees_exemple()
        self.modele = ModeleApprovisionnementPL(self.donnees)
    
    def test_construction_modele(self):
        """Vérifie que le modèle se construit sans erreur"""
        self.modele.construire_modele()
        self.assertIsNotNone(self.modele.modele)
        self.assertGreater(self.modele.modele.NumVars, 0)
        self.assertGreater(self.modele.modele.NumConstrs, 0)
    
    def test_resolution(self):
        """Vérifie que la résolution fonctionne"""
        self.modele.construire_modele()
        succes = self.modele.resoudre(time_limit=60, verbose=False)
        self.assertTrue(succes)
        self.assertIsNotNone(self.modele.resultats)
    
    def test_valeur_optimale_positive(self):
        """Vérifie que le coût optimal est positif"""
        self.modele.construire_modele()
        self.modele.resoudre(time_limit=60, verbose=False)
        self.assertGreater(self.modele.resultats['valeur_optimale'], 0)
    
    def test_flux_non_negatifs(self):
        """Vérifie que tous les flux sont non négatifs"""
        self.modele.construire_modele()
        self.modele.resoudre(time_limit=60, verbose=False)
        for quantite in self.modele.resultats['flux'].values():
            self.assertGreaterEqual(quantite, 0)
    
    def test_conservation_flux(self):
        """Vérifie la conservation des flux pour chaque site et matière"""
        self.modele.construire_modele()
        self.modele.resoudre(time_limit=60, verbose=False)
        
        d = self.donnees
        flux = self.modele.resultats['flux']
        stocks = self.modele.resultats.get('stocks', {})
        
        for i in d.sites:
            for m in d.matieres:
                # Entrées: offre + réceptions
                entrees = d.offre[i, m]
                for k in d.sites:
                    if k != i and (k, i, m) in flux:
                        entrees += flux[k, i, m]
                
                # Sorties: expéditions + stock
                sorties = stocks.get((i, m), 0)
                for j in d.sites:
                    if j != i and (i, j, m) in flux:
                        sorties += flux[i, j, m]
                
                # Conservation (avec tolérance numérique)
                self.assertAlmostEqual(entrees, sorties, places=1,
                    msg=f"Conservation violée pour site {i}, matière {m}")
    
    def test_satisfaction_demande(self):
        """Vérifie que demande = réceptions + rupture"""
        self.modele.construire_modele()
        self.modele.resoudre(time_limit=60, verbose=False)
        
        d = self.donnees
        flux = self.modele.resultats['flux']
        ruptures = self.modele.resultats.get('ruptures', {})
        
        for j in d.sites:
            for m in d.matieres:
                # Réceptions
                receptions = 0
                for i in d.sites:
                    if i != j and (i, j, m) in flux:
                        receptions += flux[i, j, m]
                
                # Rupture
                rupture = ruptures.get((j, m), 0)
                
                # Demande satisfaite
                total = receptions + rupture
                self.assertAlmostEqual(total, d.demande[j, m], places=1,
                    msg=f"Demande non satisfaite pour site {j}, matière {m}")
    
    def test_limite_rupture(self):
        """Vérifie que les ruptures ne dépassent pas 20% de la demande"""
        self.modele.construire_modele()
        self.modele.resoudre(time_limit=60, verbose=False)
        
        d = self.donnees
        ruptures = self.modele.resultats.get('ruptures', {})
        
        for (j, m), rupture in ruptures.items():
            demande = d.demande[j, m]
            if demande > 0:
                taux_rupture = rupture / demande
                self.assertLessEqual(taux_rupture, 0.21,  # 20% + marge
                    msg=f"Rupture excessive pour site {j}, matière {m}: {taux_rupture*100:.1f}%")
    
    def test_taux_satisfaction(self):
        """Vérifie que le taux de satisfaction est calculé correctement"""
        self.modele.construire_modele()
        self.modele.resoudre(time_limit=60, verbose=False)
        
        taux = self.modele.resultats['taux_satisfaction']
        self.assertGreater(taux, 0.9)  # Au moins 90%
        self.assertLessEqual(taux, 1.0)


class TestCasLimites(unittest.TestCase):
    """Tests de cas limites et cas d'erreur"""
    
    def test_offre_insuffisante(self):
        """Teste le cas où l'offre est très insuffisante"""
        donnees = ModeleDonneesApprovisionnement(n_sites=3, n_matieres=2)
        donnees.offre = np.array([[10, 20], [15, 10], [5, 15]])
        donnees.demande = np.array([[50, 60], [40, 30], [20, 25]])
        
        # Distances et coûts minimaux
        donnees.distance = np.array([[0, 100, 150], [100, 0, 120], [150, 120, 0]])
        donnees.cout_transport = np.ones((3, 3, 2)) * 10
        
        modele = ModeleApprovisionnementPL(donnees)
        modele.construire_modele()
        succes = modele.resoudre(time_limit=60, verbose=False)
        
        # Doit trouver une solution avec ruptures
        self.assertTrue(succes)
        self.assertGreater(len(modele.resultats['ruptures']), 0)
    
    def test_capacites_tres_limitees(self):
        """Teste avec des capacités très restrictives"""
        donnees = ModeleDonneesApprovisionnement(n_sites=3, n_matieres=2)
        donnees.generer_donnees_exemple()
        
        # Réduire fortement les capacités
        donnees.capacite_transfert = np.full((3, 3), 10.0)
        np.fill_diagonal(donnees.capacite_transfert, 0)
        
        modele = ModeleApprovisionnementPL(donnees)
        modele.construire_modele()
        succes = modele.resoudre(time_limit=60, verbose=False)
        
        # Doit trouver une solution (avec ruptures probables)
        self.assertTrue(succes)
    
    def test_petit_probleme(self):
        """Teste un problème minimal (2 sites, 1 matière)"""
        donnees = ModeleDonneesApprovisionnement(n_sites=2, n_matieres=1)
        donnees.offre = np.array([[100], [0]])
        donnees.demande = np.array([[0], [80]])
        donnees.distance = np.array([[0, 100], [100, 0]])
        donnees.cout_transport = np.array([[[0, 10], [10, 0]]])
        
        modele = ModeleApprovisionnementPL(donnees)
        modele.construire_modele()
        succes = modele.resoudre(time_limit=60, verbose=False)
        
        self.assertTrue(succes)
        # Doit transférer 80t de site 0 vers site 1
        self.assertAlmostEqual(modele.resultats['flux'].get((0, 1, 0), 0), 80.0, places=1)


class TestPerformance(unittest.TestCase):
    """Tests de performance"""
    
    def test_temps_resolution_5_sites(self):
        """Vérifie que la résolution est rapide pour 5 sites"""
        donnees = ModeleDonneesApprovisionnement(n_sites=5, n_matieres=3)
        donnees.generer_donnees_exemple()
        
        modele = ModeleApprovisionnementPL(donnees)
        modele.construire_modele()
        modele.resoudre(time_limit=60, verbose=False)
        
        # Doit être résolu en moins de 5 secondes
        self.assertLess(modele.temps_resolution, 5.0)
    
    def test_scalabilite_10_sites(self):
        """Teste avec 10 sites"""
        donnees = ModeleDonneesApprovisionnement(n_sites=10, n_matieres=3)
        # Données aléatoires
        np.random.seed(42)
        donnees.offre = np.random.rand(10, 3) * 100
        donnees.demande = np.random.rand(10, 3) * 100
        donnees.distance = np.random.rand(10, 10) * 500
        donnees.cout_transport = np.random.rand(10, 10, 3) * 20
        
        modele = ModeleApprovisionnementPL(donnees)
        modele.construire_modele()
        succes = modele.resoudre(time_limit=60, verbose=False)
        
        self.assertTrue(succes)
        # Doit être résolu en moins de 30 secondes
        self.assertLess(modele.temps_resolution, 30.0)


def suite_tests_rapides():
    """Suite de tests rapides pour vérification de base"""
    suite = unittest.TestSuite()
    suite.addTest(TestModeleDonnees('test_dimensions'))
    suite.addTest(TestModeleDonnees('test_non_negativite'))
    suite.addTest(TestModeleOptimisation('test_construction_modele'))
    suite.addTest(TestModeleOptimisation('test_resolution'))
    return suite


def suite_tests_complets():
    """Suite de tests complète"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestModeleDonnees))
    suite.addTests(loader.loadTestsFromTestCase(TestModeleOptimisation))
    suite.addTests(loader.loadTestsFromTestCase(TestCasLimites))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    return suite


if __name__ == '__main__':
    print("="*70)
    print("TESTS UNITAIRES - Optimisation Approvisionnement")
    print("="*70)
    
    # Choisir la suite de tests
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--rapide':
        print("\n[Mode RAPIDE - Tests essentiels uniquement]\n")
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite_tests_rapides())
    else:
        print("\n[Mode COMPLET - Tous les tests]\n")
        unittest.main(verbosity=2)
