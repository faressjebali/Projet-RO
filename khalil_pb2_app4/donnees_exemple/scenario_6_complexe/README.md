# Scénario 6 : Cas Complexe avec Ruptures Inévitables

## Description
Ce scénario représente un cas réaliste et complexe où :
- **6 sites** géographiquement dispersés en Tunisie
- **4 matières premières** différentes
- **Déficit structurel** pour certaines matières → ruptures inévitables
- **Capacités limitées** sur certains arcs
- **Distances réalistes** entre villes tunisiennes

## Sites
| ID | Nom | Rôle principal |
|----|-----|----------------|
| S1 | Tunis | Hub central, forte demande |
| S2 | Sfax | Production industrielle |
| S3 | Sousse | Production + Demande |
| S4 | Bizerte | Port, approvisionnement |
| S5 | Gabès | Zone industrielle chimique |
| S6 | Kairouan | Centre de distribution |

## Matières premières
| ID | Nom | Caractéristique |
|----|-----|-----------------|
| M0 | Acier | Équilibré |
| M1 | Aluminium | Déficit 30t → ruptures |
| M2 | Cuivre | Surplus d'offre |
| M3 | Plastique | Capacités limitées |

## Équilibre Offre/Demande
| Matière | Offre totale | Demande totale | Balance |
|---------|--------------|----------------|---------|
| Acier | 250 t | 250 t | Équilibre |
| Aluminium | 120 t | 150 t | **Déficit -30t** |
| Cuivre | 180 t | 140 t | Surplus +40t |
| Plastique | 200 t | 180 t | Surplus +20t |

## Objectif pédagogique
Démontrer le comportement du modèle face à :
1. Un déficit structurel (demande > offre)
2. L'allocation optimale des ressources rares
3. Les goulots d'étranglement (capacités limitées)
4. La répartition des ruptures entre sites

## Résultats attendus
- Ruptures inévitables sur l'Aluminium (~30t)
- Stock résiduel sur Cuivre et Plastique
- Certains arcs saturés (goulots)
- Recommandations pour augmenter l'offre d'Aluminium
