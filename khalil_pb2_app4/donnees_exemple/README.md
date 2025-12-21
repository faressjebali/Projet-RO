# Données d'exemple - OptiAppro

Ce dossier contient des jeux de données pour tester l'application d'optimisation.

## Principe fondamental

**Un site qui OFFRE une matière première ne la DEMANDE PAS** (et vice versa).
- Si Site_A offre 100t d'Acier, il n'a pas besoin d'Acier
- Si Site_A demande 50t de Plastique, il n'en produit pas

## Scénarios disponibles

| Scénario | Sites | Matières | Particularité |
|----------|-------|----------|---------------|
| `scenario_1_simple` | 3 | 2 | Équilibre parfait |
| `scenario_2_surplus` | 4 | 2 | Surplus d'offre |
| `scenario_3_capacites` | 4 | 3 | Capacités limitées |
| `scenario_4_tunisie` | 5 | 3 | Villes tunisiennes réelles |
| `scenario_5_deficit` | 4 | 2 | Demande > Offre (ruptures) |

## Format des fichiers CSV

### offre.csv
```csv
Site,Matiere1,Matiere2
Site_A,100,0
Site_B,0,80
```

### demande.csv
```csv
Site,Matiere1,Matiere2
Site_A,0,50
Site_B,60,0
```

### distances.csv
```csv
Site,Site_A,Site_B
Site_A,0,150
Site_B,150,0
```

### capacites.csv
```csv
Site,Site_A,Site_B
Site_A,0,200
Site_B,200,0
```

### couts_matiere_X.csv
```csv
Site,Site_A,Site_B
Site_A,0,3.5
Site_B,3.5,0
```

## Coûts réalistes

Les coûts de transport sont en **DT/tonne** (Dinar Tunisien).
Valeurs réalistes : **1 à 15 DT/tonne** selon :
- La distance
- Le type de matière (lourd = plus cher)
- Les conditions de route
