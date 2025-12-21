# Scénario 7 : Cas Très Complexe - Réseau National Tunisien

## Description
Scénario réaliste et complexe représentant un réseau logistique national :
- **8 sites** couvrant toute la Tunisie
- **5 matières premières** industrielles
- **Coûts réalistes** (0.5 - 4 DT/tonne selon distance)
- **Capacités variables** et contraignantes
- **Mix de surplus et déficits** selon les matières

## Sites du réseau
| ID | Ville | Région | Rôle |
|----|-------|--------|------|
| S0 | Tunis | Nord | Hub principal, forte demande |
| S1 | Sfax | Centre-Est | Zone industrielle majeure |
| S2 | Sousse | Sahel | Production textile/plastique |
| S3 | Bizerte | Nord | Port, import matières |
| S4 | Gabès | Sud | Industrie chimique |
| S5 | Kairouan | Centre | Centre logistique |
| S6 | Monastir | Sahel | Production manufacturière |
| S7 | Médenine | Sud | Zone franche |

## Matières premières
| ID | Nom | Usage | Coût moyen transport |
|----|-----|-------|---------------------|
| M0 | Acier | Construction | 1.5 DT/t |
| M1 | Plastique | Emballage | 1.0 DT/t |
| M2 | Aluminium | Automobile | 2.0 DT/t |
| M3 | Cuivre | Électrique | 2.5 DT/t |
| M4 | Ciment | BTP | 0.8 DT/t |

## Équilibre Offre/Demande
| Matière | Offre | Demande | Balance | Situation |
|---------|-------|---------|---------|-----------|
| Acier | 450t | 420t | +30t | Surplus léger |
| Plastique | 380t | 400t | -20t | **Déficit** |
| Aluminium | 300t | 300t | 0t | Équilibre parfait |
| Cuivre | 220t | 250t | -30t | **Déficit** |
| Ciment | 500t | 480t | +20t | Surplus léger |

## Caractéristiques du scénario
1. **Déficits intentionnels** sur Plastique (-20t) et Cuivre (-30t) → ruptures inévitables
2. **Capacités limitées** sur certains arcs → choix de routage
3. **Distances réelles** entre villes tunisiennes
4. **Coûts proportionnels** à la distance (≈0.01 DT/t/km)

## Objectif pédagogique
- Démontrer l'optimisation sur un réseau complexe
- Montrer comment Gurobi choisit les meilleures routes
- Illustrer la gestion des déficits et ruptures
- Comprendre l'impact des capacités sur les flux
