# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════════════════╗
║  SYSTÈME D'OPTIMISATION PLNE - AFFECTATION DE TECHNICIENS DE MAINTENANCE  ║
║  Projet: Recherche Opérationnelle - INSAT                                 ║
║  Problème: Affectation | Modèle: PLNE(B) | Application: Maintenance       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import gurobipy as gp
from gurobipy import GRB
from PySide6.QtCore import QThread, Signal


# ═══════════════════════════════════════════════════════════════════════════
#                        MODÈLE PLNE OPTIMISÉ AVEC VARIABLES CONTINUES
# ═══════════════════════════════════════════════════════════════════════════
class OptimizedPLNEModel:
    def solve(self, capacities, specializations, n_techs, n_pannes,
              priorities, competence_matrix, skill_requirements, travel_matrix,
              time_matrix, hourly_price_matrix, complexity):
        try:
            model = gp.Model("PLNE_Maintenance")
            model.setParam('OutputFlag', 1)  # Afficher la sortie Gurobi
            model.setParam('MIPGap', 0.01)
            model.setParam('TimeLimit', 60)
            
            # ═══════════════════════════════════════════════════════════════
            # VARIABLES DE DÉCISION
            # ═══════════════════════════════════════════════════════════════
            
            # Variables binaires: affectation technicien-panne
            x = {}
            for i in range(n_techs):
                for j in range(n_pannes):
                    if specializations[i][j]:
                        x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")
            
            # Variables continues: coût variable de transport
            transport_cost = {}
            for i in range(n_techs):
                for j in range(n_pannes):
                    if specializations[i][j]:
                        transport_cost[i, j] = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
                                                            name=f"transport_{i}_{j}")
            
            # Variable continue: coût total de pénalité (relaxée)
            total_penalty = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="total_penalty")
            
            # ═══════════════════════════════════════════════════════════════
            # FONCTION OBJECTIF
            # ═══════════════════════════════════════════════════════════════
            
            objective = 0
            
            # Coût d'intervention fusionné (temps * prix horaire basé sur compétence)
            for i in range(n_techs):
                for j in range(n_pannes):
                    if (i, j) in x:
                        comp = competence_matrix[i][j]
                        temps = time_matrix[j][comp - 1]  # comp 1-5, index 0-4
                        prix_h = hourly_price_matrix[j][comp - 1]
                        intervention_cost = temps * prix_h
                        objective += intervention_cost * x[i, j]
            
            # Coût de transport variable (fonction du temps)
            for i in range(n_techs):
                for j in range(n_pannes):
                    if (i, j) in x:
                        # Liaison: transport_cost >= 0.5 * distance * x
                        model.addConstr(transport_cost[i, j] >= 0.5 * travel_matrix[i][j] * x[i, j])
                        objective += transport_cost[i, j]
            
            # Pénalités/Bonus de compétence
            for i in range(n_techs):
                for j in range(n_pannes):
                    if (i, j) in x:
                        gap = skill_requirements[j] - competence_matrix[i][j]
                        if gap > 0:
                            objective += gap * 50 * x[i, j]
                        else:
                            objective -= abs(gap) * 20 * x[i, j]
                        
                        # Pénalité supplémentaire pour complexité
                        complex_gap = complexity[j] - competence_matrix[i][j]
                        if complex_gap > 0:
                            objective += complex_gap * 20 * x[i, j]
            
            # Pénalité totale continue
            objective += total_penalty
            
            model.setObjective(objective, GRB.MINIMIZE)
            
            # ═══════════════════════════════════════════════════════════════
            # CONTRAINTES
            # ═══════════════════════════════════════════════════════════════
            
            # C1: Chaque panne doit être assignée à exactement un technicien
            for j in range(n_pannes):
                qualified = [i for i in range(n_techs) if (i, j) in x]
                if qualified:
                    model.addConstr(gp.quicksum(x[i, j] for i in qualified) == 1,
                                  name=f"C1_panne_{j}")
            
            # C2: Respect de la capacité maximale par technicien
            for i in range(n_techs):
                pannes = [j for j in range(n_pannes) if (i, j) in x]
                if pannes:
                    model.addConstr(gp.quicksum(x[i, j] for j in pannes) <= capacities[i],
                                  name=f"C2_capacite_{i}")
            
            # C3: Temps de travail maximal par technicien (40h/semaine)
            for i in range(n_techs):
                interventions = [j for j in range(n_pannes) if (i, j) in x]
                if interventions:
                    time_sum = gp.quicksum(time_matrix[j][competence_matrix[i][j] - 1] * x[i, j] for j in interventions)
                    model.addConstr(time_sum <= 40, name=f"C3_temps_max_{i}")
            
            # C4: Experts pour pannes critiques (priorité 1) et haute complexité
            for j in range(n_pannes):
                if priorities[j] == 1 and complexity[j] >= 3:
                    experts = [i for i in range(n_techs) if (i, j) in x and
                             competence_matrix[i][j] >= 4]
                    if experts:
                        model.addConstr(gp.quicksum(x[i, j] for i in experts) >= 1,
                                      name=f"C4_expert_{j}")
            
            # C5: Compétence minimale requise
            for j in range(n_pannes):
                req = skill_requirements[j]
                competent = [i for i in range(n_techs) if (i, j) in x and
                          competence_matrix[i][j] >= req]
                if competent:
                    model.addConstr(gp.quicksum(x[i, j] for i in competent) >= 1,
                                  name=f"C5_competence_{j}")
            
            # C6: Distance maximale de déplacement
            for i in range(n_techs):
                interventions = [j for j in range(n_pannes) if (i, j) in x]
                if interventions:
                    model.addConstr(
                        gp.quicksum(travel_matrix[i][j] * x[i, j] for j in interventions) <= 200,
                        name=f"C6_distance_{i}")
            
            # C8: Contrainte de pénalité continue
            penalty_sum = 0
            for i in range(n_techs):
                for j in range(n_pannes):
                    if (i, j) in x:
                        gap = max(0, skill_requirements[j] - competence_matrix[i][j])
                        penalty_sum += gap * 10 * x[i, j]
            model.addConstr(total_penalty >= penalty_sum, name="C8_penalty")
            
            # ═══════════════════════════════════════════════════════════════
            # RÉSOLUTION
            # ═══════════════════════════════════════════════════════════════
            
            print("\n" + "="*70)
            print("DÉBUT DE L'OPTIMISATION GUROBI")
            print("="*70)
            
            model.optimize()
            
            print("\n" + "="*70)
            print("FIN DE L'OPTIMISATION")
            print("="*70 + "\n")
            
            if model.status in [GRB.OPTIMAL, GRB.SUBOPTIMAL]:
                solution = {}
                stats = {
                    'total_cost': 0, 'intervention_cost': 0, 'travel_cost': 0,
                    'penalty_cost': 0, 'reward_savings': 0, 'avg_competence': 0,
                    'competence_gaps': [], 'tech_workload': {}, 'avg_time': 0,
                    'total_time': 0
                }
                
                for (i, j), var in x.items():
                    if var.X > 0.5:
                        comp = competence_matrix[i][j]
                        temps = time_matrix[j][comp - 1]
                        prix_h = hourly_price_matrix[j][comp - 1]
                        intervention_cost = temps * prix_h
                        travel_cost = transport_cost[i, j].X if (i, j) in transport_cost else 0
                        
                        gap = skill_requirements[j] - competence_matrix[i][j]
                        penalty = max(0, gap) * 50
                        reward = max(0, -gap) * 20
                        total = intervention_cost + travel_cost + penalty - reward
                        
                        solution[(i+1, j+1)] = {
                            'intervention_cost': intervention_cost,
                            'travel_distance': travel_matrix[i][j],
                            'travel_cost': travel_cost,
                            'time_hours': temps,
                            'prix_h': prix_h,
                            'penalty': penalty,
                            'reward': reward,
                            'total_cost': total,
                            'priority': priorities[j],
                            'required_skill': skill_requirements[j],
                            'tech_competence': competence_matrix[i][j],
                            'competence_gap': gap,
                            'complexity': complexity[j]
                        }
                        
                        stats['total_cost'] += total
                        stats['intervention_cost'] += intervention_cost
                        stats['travel_cost'] += travel_cost
                        stats['penalty_cost'] += penalty
                        stats['reward_savings'] += reward
                        stats['avg_competence'] += competence_matrix[i][j]
                        stats['total_time'] += temps
                        stats['competence_gaps'].append(gap)
                        
                        if (i+1) not in stats['tech_workload']:
                            stats['tech_workload'][i+1] = {
                                'count': 0, 'cost': 0, 'skill': 0, 'time': 0
                            }
                        stats['tech_workload'][i+1]['count'] += 1
                        stats['tech_workload'][i+1]['cost'] += total
                        stats['tech_workload'][i+1]['skill'] += competence_matrix[i][j]
                        stats['tech_workload'][i+1]['time'] += temps
                
                if solution:
                    stats['avg_competence'] /= len(solution)
                    stats['avg_time'] = stats['total_time'] / len(solution)
                    for tech in stats['tech_workload']:
                        count = stats['tech_workload'][tech]['count']
                        if count > 0:
                            stats['tech_workload'][tech]['skill'] /= count
                
                return stats, solution, model.Runtime
            
            return None, {}, model.Runtime
        
        except Exception as e:
            print(f"ERREUR CRITIQUE: {e}")
            import traceback
            traceback.print_exc()
            return None, {}, 0


# ═══════════════════════════════════════════════════════════════════════════
#                          THREAD OPTIMISATION
# ═══════════════════════════════════════════════════════════════════════════
class OptimizationThread(QThread):
    finished_signal = Signal(object, object, float)
    
    def __init__(self, model, params):
        super().__init__()
        self.model = model
        self.params = params
    
    def run(self):
        stats, solution, runtime = self.model.solve(**self.params)
        self.finished_signal.emit(stats, solution, runtime)