# -*- coding: utf-8 -*-
"""
Interface graphique complète
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import random
from datetime import datetime
import csv
import os

from solver import OptimizedPLNEModel, OptimizationThread

plt.rcParams['font.size'] = 11


# ═══════════════════════════════════════════════════════════════════════════
#                     INTERFACE GRAPHIQUE AVEC VALIDATION
# ═══════════════════════════════════════════════════════════════════════════
class PerfectMaintenanceApp(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.model = OptimizedPLNEModel()
        self.solution_data = None
        
        self.setWindowTitle("🏭 Système d'Optimisation - Affectation Techniciens Maintenance | INSAT")
        self.resize(1400, 900)
        
        self.setup_ui()
        self.generate_data()
        self.apply_styles()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header = QLabel("🏭 OPTIMISATION - AFFECTATION TECHNICIENS MAINTENANCE")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a237e, stop:0.5 #3f51b5, stop:1 #5c6bc0);
            color: white; padding: 20px; border-radius: 10px;
        """)
        layout.addWidget(header)
        
        config_group = QGroupBox("⚙️ Configuration")
        config_layout = QHBoxLayout()
        
        config_layout.addWidget(QLabel("👷 Techniciens:"))
        self.tech_spin = QSpinBox()
        self.tech_spin.setRange(1, 100)
        self.tech_spin.setValue(6)
        self.tech_spin.valueChanged.connect(self.update_tables)
        config_layout.addWidget(self.tech_spin)
        
        config_layout.addWidget(QLabel("🔧 Pannes:"))
        self.panne_spin = QSpinBox()
        self.panne_spin.setRange(1, 100)
        self.panne_spin.setValue(8)
        self.panne_spin.valueChanged.connect(self.update_tables)
        config_layout.addWidget(self.panne_spin)
        
        config_layout.addStretch()
        
        self.gen_btn = QPushButton("📊 Générer")
        self.gen_btn.clicked.connect(self.generate_data)
        config_layout.addWidget(self.gen_btn)
        
        self.solve_btn = QPushButton("🚀 OPTIMISER")
        self.solve_btn.clicked.connect(self.solve)
        config_layout.addWidget(self.solve_btn)
        
        self.export_btn = QPushButton("💾 Exporter CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        self.export_btn.setEnabled(False)
        config_layout.addWidget(self.export_btn)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        self.status = QLabel("✅ Prêt")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("background: #d4edda; padding: 8px; border-radius: 6px; font-weight: bold;")
        layout.addWidget(self.status)
        
        self.tabs = QTabWidget()
        
        self.setup_comp_tab()
        self.setup_params_tab()
        self.setup_time_price_tab()
        self.setup_detailed_results_tab()
        self.setup_graphs_tab()
        
        layout.addWidget(self.tabs)
    
    def validate_cell_input(self, table, row, col, min_val, max_val, field_name):
        """Valide l'entrée d'une cellule et colore en rouge si erreur"""
        item = table.item(row, col)
        if item and item.text().strip():
            try:
                value = float(item.text())
                if value < min_val or value > max_val:
                    item.setBackground(QColor(255, 200, 200))
                    QMessageBox.warning(
                        self,
                        "❌ Valeur Invalide",
                        f"<b>{field_name}</b> doit être entre <b>{min_val}</b> et <b>{max_val}</b>.<br><br>"
                        f"Valeur entrée: <b>{value}</b><br>"
                        f"Position: Ligne {row+1}, Colonne {col+1}"
                    )
                    return False
                else:
                    item.setBackground(QColor(255, 255, 255))
                    return True
            except ValueError:
                item.setBackground(QColor(255, 200, 200))
                QMessageBox.warning(
                    self,
                    "❌ Format Invalide",
                    f"Veuillez entrer un nombre valide pour <b>{field_name}</b>.<br><br>"
                    f"Position: Ligne {row+1}, Colonne {col+1}"
                )
                return False
        return True
    
    def setup_comp_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        cap_group = QGroupBox("📊 Capacités (1-10)")
        cap_layout = QVBoxLayout()
        self.capacity_table = QTableWidget()
        self.capacity_table.setRowCount(1)
        self.capacity_table.setVerticalHeaderLabels(["Max"])
        self.capacity_table.setMaximumHeight(400)
        self.capacity_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.capacity_table, r, c, 1, 10, "Capacité")
        )
        cap_layout.addWidget(self.capacity_table)
        cap_group.setLayout(cap_layout)
        layout.addWidget(cap_group, 1)
        
        comp_group = QGroupBox("🎯 Matrice Compétences (1-5)")
        comp_layout = QVBoxLayout()
        comp_layout.addWidget(QLabel("<small>⭐ 1:Débutant → ⭐⭐⭐⭐⭐ 5:Spécialiste | Vide = Non qualifié</small>"))
        self.comp_table = QTableWidget()
        self.comp_table.setMaximumHeight(350)
        self.comp_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.comp_table, r, c, 1, 5, "Compétence")
        )
        comp_layout.addWidget(self.comp_table)
        comp_group.setLayout(comp_layout)
        layout.addWidget(comp_group)
        
        req_group = QGroupBox("📋 Exigences (1-5)")
        req_layout = QVBoxLayout()
        self.req_table = QTableWidget(1, 8)
        self.req_table.setMaximumHeight(100)
        self.req_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.req_table, r, c, 1, 5, "Exigence")
        )
        req_layout.addWidget(self.req_table)
        req_group.setLayout(req_layout)
        layout.addWidget(req_group)
        
        self.tabs.addTab(tab, "🎯 Compétences")
    
    def setup_params_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        prio_group = QGroupBox("🚨 Priorités")
        prio_layout = QVBoxLayout()
        prio_layout.addWidget(QLabel("<small>1:🔴 Critique | 2:🟡 Moyen | 3:🟢 Faible</small>"))
        self.prio_table = QTableWidget(0, 1)
        self.prio_table.setHorizontalHeaderLabels(["Priorité"])
        self.prio_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.prio_table, r, c, 1, 3, "Priorité")
        )
        prio_layout.addWidget(self.prio_table)
        prio_group.setLayout(prio_layout)
        layout.addWidget(prio_group)
        
        complex_group = QGroupBox("🧠 Complexité")
        complex_layout = QVBoxLayout()
        complex_layout.addWidget(QLabel("<small>1:Simple → 5:Très Complexe</small>"))
        self.complex_table = QTableWidget(0, 1)
        self.complex_table.setHorizontalHeaderLabels(["Complexité"])
        self.complex_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.complex_table, r, c, 1, 5, "Complexité")
        )
        complex_layout.addWidget(self.complex_table)
        complex_group.setLayout(complex_layout)
        layout.addWidget(complex_group)
        
        dist_group = QGroupBox("📍 Distances (5-200 km)")
        dist_layout = QVBoxLayout()
        self.dist_table = QTableWidget()
        self.dist_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.dist_table, r, c, 5, 200, "Distance")
        )
        dist_layout.addWidget(self.dist_table)
        dist_group.setLayout(dist_layout)
        layout.addWidget(dist_group)
        
        self.tabs.addTab(tab, "⚙️ Paramètres")
    
    def setup_time_price_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        time_group = QGroupBox("⏱️ Temps par Niveau")
        time_layout = QVBoxLayout()
        time_layout.addWidget(QLabel("<small>Temps pour chaque panne par niveau de compétence</small>"))
        self.time_table = QTableWidget()
        self.time_table.setMaximumHeight(400)
        self.time_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.time_table, r, c, 0.5, 40, "Temps")
        )
        time_layout.addWidget(self.time_table)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        price_group = QGroupBox("💰 Prix Horaire par Niveau (20-50 €/h)")
        price_layout = QVBoxLayout()
        price_layout.addWidget(QLabel("<small>Prix horaire pour chaque panne par niveau de compétence</small>"))
        self.price_table = QTableWidget()
        self.price_table.setMaximumHeight(400)
        self.price_table.cellChanged.connect(
            lambda r, c: self.validate_cell_input(self.price_table, r, c, 20, 50, "Prix Horaire")
        )
        price_layout.addWidget(self.price_table)
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        self.tabs.addTab(tab, "⏱️💰 Temps & Prix")
    
    def setup_detailed_results_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        self.tabs.addTab(tab, "📊 Résultats")
    
    def setup_graphs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = plt.Figure(figsize=(16, 20), facecolor='white', dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(1600, 2000)
        
        graph_layout.addWidget(self.canvas)
        scroll_area.setWidget(graph_widget)
        
        layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab, "📈 Visualisation")
    
    def update_tables(self):
        n_techs = self.tech_spin.value()
        n_pannes = self.panne_spin.value()
        
        for table in [self.comp_table, self.dist_table]:
            table.setRowCount(n_techs)
            table.setColumnCount(n_pannes)
            table.setVerticalHeaderLabels([f"T{i+1}" for i in range(n_techs)])
            table.setHorizontalHeaderLabels([f"P{j+1}" for j in range(n_pannes)])
        
        self.capacity_table.setRowCount(1)
        self.capacity_table.setColumnCount(n_techs)
        self.capacity_table.setHorizontalHeaderLabels([f"T{i+1}" for i in range(n_techs)])
        self.capacity_table.setVerticalHeaderLabels(["Max"])
        
        self.req_table.setColumnCount(n_pannes)
        self.req_table.setHorizontalHeaderLabels([f"P{j+1}" for j in range(n_pannes)])
        
        for table in [self.prio_table, self.complex_table]:
            table.setRowCount(n_pannes)
            table.setColumnCount(1)
            table.setVerticalHeaderLabels([f"P{j+1}" for j in range(n_pannes)])
        
        self.prio_table.setHorizontalHeaderLabels(["Priorité"])
        self.complex_table.setHorizontalHeaderLabels(["Complexité"])
        
        for table in [self.time_table, self.price_table]:
            table.setRowCount(n_pannes)
            table.setColumnCount(5)
            table.setVerticalHeaderLabels([f"P{j+1}" for j in range(n_pannes)])
            table.setHorizontalHeaderLabels([f"Niv {k+1}" for k in range(5)])
    
    def check_capacities(self, silent=False):
        n_techs = self.tech_spin.value()
        n_pannes = self.panne_spin.value()
        
        errors = []
        warnings = []
        
        for i in range(n_techs):
            qualified_count = 0
            for j in range(n_pannes):
                item = self.comp_table.item(i, j)
                if item and item.text().strip():
                    qualified_count += 1
            
            cap_item = self.capacity_table.item(0, i)
            if cap_item and cap_item.text().strip():
                try:
                    capacity = int(cap_item.text())
                    if qualified_count > capacity:
                        errors.append(f"Technicien T{i+1}: {qualified_count} qualifications pour capacité {capacity}")
                    elif qualified_count == 0:
                        warnings.append(f"Technicien T{i+1}: Aucune qualification")
                except ValueError:
                    errors.append(f"Capacité T{i+1}: valeur invalide")
            else:
                errors.append(f"Capacité T{i+1}: non spécifiée")
        
        if errors and not silent:
            error_msg = "<h3>❌ Problèmes de Capacité:</h3><ul>"
            for err in errors:
                error_msg += f"<li>{err}</li>"
            error_msg += "</ul>"
            if warnings:
                error_msg += "<h4>⚠️ Avertissements:</h4><ul>"
                for warn in warnings:
                    error_msg += f"<li>{warn}</li>"
                error_msg += "</ul>"
            QMessageBox.warning(self, "Problèmes de Capacité", error_msg)
            return False
        
        if warnings and not silent:
            warning_msg = "<h4>⚠️ Avertissements:</h4><ul>"
            for warn in warnings:
                warning_msg += f"<li>{warn}</li>"
            warning_msg += "</ul>"
            QMessageBox.warning(self, "Avertissements", warning_msg)
        
        return len(errors) == 0
    
    def check_capacities_silent(self):
        n_techs = self.tech_spin.value()
        n_pannes = self.panne_spin.value()
        
        ok = True
        for i in range(n_techs):
            qualified_count = 0
            for j in range(n_pannes):
                item = self.comp_table.item(i, j)
                if item and item.text().strip():
                    qualified_count += 1
            
            cap_item = self.capacity_table.item(0, i)
            if cap_item and cap_item.text().strip():
                try:
                    capacity = int(cap_item.text())
                    if qualified_count > capacity:
                        ok = False
                        print(f"ATTENTION: Technicien T{i+1}: {qualified_count} qualifications pour capacité {capacity}")
                except:
                    pass
        return ok
    
    def generate_data(self):
        for table in [self.capacity_table, self.comp_table,
                      self.req_table, self.prio_table, self.dist_table,
                      self.time_table, self.price_table, self.complex_table]:
            table.blockSignals(True)
        
        self.update_tables()
        n_techs = self.tech_spin.value()
        n_pannes = self.panne_spin.value()
        
        capacities = []
        for i in range(n_techs):
            cap = random.choices([2, 3, 4], weights=[30, 50, 20])[0]
            capacities.append(cap)
            self.capacity_table.setItem(0, i, QTableWidgetItem(str(cap)))
        
        qualified_per_panne = [0] * n_pannes
        
        for i in range(n_techs):
            capacity = capacities[i]
            min_qualified = max(1, capacity - 1)
            max_qualified = capacity
            num_qualified = random.randint(min_qualified, max_qualified)
            
            qualified_pannes = []
            
            for j in range(n_pannes):
                if qualified_per_panne[j] == 0 and len(qualified_pannes) < num_qualified:
                    qualified_pannes.append(j)
                    qualified_per_panne[j] += 1
            
            remaining_slots = num_qualified - len(qualified_pannes)
            if remaining_slots > 0:
                other_pannes = [j for j in range(n_pannes) if j not in qualified_pannes]
                if len(other_pannes) > 0:
                    additional = random.sample(other_pannes, min(remaining_slots, len(other_pannes)))
                    qualified_pannes.extend(additional)
                    for panne in additional:
                        qualified_per_panne[panne] += 1
            
            while len(qualified_pannes) < num_qualified:
                all_pannes = list(range(n_pannes))
                random.shuffle(all_pannes)
                for panne in all_pannes:
                    if panne not in qualified_pannes:
                        qualified_pannes.append(panne)
                        qualified_per_panne[panne] += 1
                        break
            
            for j in range(n_pannes):
                if j in qualified_pannes:
                    comp = random.choices([2, 3, 4, 5], weights=[10, 40, 40, 10])[0]
                    self.comp_table.setItem(i, j, QTableWidgetItem(str(comp)))
                else:
                    self.comp_table.setItem(i, j, QTableWidgetItem(""))
                
                dist = random.randint(10, 80)
                self.dist_table.setItem(i, j, QTableWidgetItem(str(dist)))
        
        for j in range(n_pannes):
            if qualified_per_panne[j] == 0:
                for i in range(n_techs):
                    current_qualified = 0
                    for k in range(n_pannes):
                        item = self.comp_table.item(i, k)
                        if item and item.text().strip():
                            current_qualified += 1
                    
                    if current_qualified < capacities[i]:
                        comp = random.choices([2, 3, 4], weights=[20, 60, 20])[0]
                        self.comp_table.setItem(i, j, QTableWidgetItem(str(comp)))
                        qualified_per_panne[j] += 1
                        break
        
        for j in range(n_pannes):
            req = random.choices([2, 3, 4], weights=[30, 50, 20])[0]
            self.req_table.setItem(0, j, QTableWidgetItem(str(req)))
            
            complex_level = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 30, 25, 15])[0]
            self.complex_table.setItem(j, 0, QTableWidgetItem(str(complex_level)))
            
            r = random.random()
            prio = 1 if r < 0.15 else 2 if r < 0.4 else 3
            self.prio_table.setItem(j, 0, QTableWidgetItem(str(prio)))
        
        for j in range(n_pannes):
            for level in range(5):
                temps_ranges = [(6,8), (5,7), (4,6), (3,5), (2,4)]
                temps = random.uniform(*temps_ranges[level])
                self.time_table.setItem(j, level, QTableWidgetItem(f"{temps:.1f}"))
                
                price_ranges = [(20,30), (25,35), (30,40), (35,45), (40,50)]
                prix_h = random.uniform(*price_ranges[level])
                self.price_table.setItem(j, level, QTableWidgetItem(f"{prix_h:.1f}"))
        
        for table in [self.capacity_table, self.comp_table,
                      self.req_table, self.prio_table, self.dist_table,
                      self.time_table, self.price_table, self.complex_table]:
            table.blockSignals(False)
        
        self.check_capacities_silent()
        
        self.status.setText("✅ Données générées avec qualification cohérente")
    
    def validate_all_inputs(self):
        n_techs = self.tech_spin.value()
        n_pannes = self.panne_spin.value()
        
        errors = []
        
        for i in range(n_techs):
            item = self.capacity_table.item(0, i)
            if not item or not item.text().strip():
                errors.append(f"Capacité T{i+1}: manquante")
            else:
                try:
                    val = int(item.text())
                    if val < 1 or val > 10:
                        errors.append(f"Capacité T{i+1}: {val} (doit être 1-10)")
                except:
                    errors.append(f"Capacité T{i+1}: format invalide")
        
        for i in range(n_techs):
            for j in range(n_pannes):
                item = self.comp_table.item(i, j)
                if item and item.text().strip():
                    try:
                        val = int(item.text())
                        if val < 1 or val > 5:
                            errors.append(f"Compétence T{i+1}-P{j+1}: {val} (doit être 1-5 ou vide)")
                    except:
                        errors.append(f"Compétence T{i+1}-P{j+1}: format invalide")
        
        for j in range(n_pannes):
            item = self.req_table.item(0, j)
            if not item or not item.text().strip():
                errors.append(f"Exigence P{j+1}: manquante")
            else:
                try:
                    val = int(item.text())
                    if val < 1 or val > 5:
                        errors.append(f"Exigence P{j+1}: {val} (doit être 1-5)")
                except:
                    errors.append(f"Exigence P{j+1}: format invalide")
        
        for j in range(n_pannes):
            item = self.complex_table.item(j, 0)
            if not item or not item.text().strip():
                errors.append(f"Complexité P{j+1}: manquante")
            else:
                try:
                    val = int(item.text())
                    if val < 1 or val > 5:
                        errors.append(f"Complexité P{j+1}: {val} (doit être 1-5)")
                except:
                    errors.append(f"Complexité P{j+1}: format invalide")
        
        for j in range(n_pannes):
            item = self.prio_table.item(j, 0)
            if not item or not item.text().strip():
                errors.append(f"Priorité P{j+1}: manquante")
            else:
                try:
                    val = int(item.text())
                    if val < 1 or val > 3:
                        errors.append(f"Priorité P{j+1}: {val} (doit être 1-3)")
                except:
                    errors.append(f"Priorité P{j+1}: format invalide")
        
        for i in range(n_techs):
            for j in range(n_pannes):
                item = self.dist_table.item(i, j)
                if not item or not item.text().strip():
                    errors.append(f"Distance T{i+1}-P{j+1}: manquante")
                else:
                    try:
                        val = float(item.text())
                        if val < 5 or val > 200:
                            errors.append(f"Distance T{i+1}-P{j+1}: {val} (doit être 5-200)")
                    except:
                        errors.append(f"Distance T{i+1}-P{j+1}: format invalide")
        
        for j in range(n_pannes):
            for level in range(5):
                item = self.time_table.item(j, level)
                if not item or not item.text().strip():
                    errors.append(f"Temps P{j+1}-Niv{level+1}: manquant")
                else:
                    try:
                        val = float(item.text())
                        if val < 0.5 or val > 40:
                            errors.append(f"Temps P{j+1}-Niv{level+1}: {val} (doit être 0.5-40)")
                    except:
                        errors.append(f"Temps P{j+1}-Niv{level+1}: format invalide")
        
        for j in range(n_pannes):
            for level in range(5):
                item = self.price_table.item(j, level)
                if not item or not item.text().strip():
                    errors.append(f"Prix H P{j+1}-Niv{level+1}: manquant")
                else:
                    try:
                        val = float(item.text())
                        if val < 20 or val > 50:
                            errors.append(f"Prix H P{j+1}-Niv{level+1}: {val} (doit être 20-50)")
                    except:
                        errors.append(f"Prix H P{j+1}-Niv{level+1}: format invalide")
        
        if not self.check_capacities():
            errors.append("Problèmes de cohérence entre capacités et qualifications")
        
        if errors:
            error_msg = "<h3>❌ Erreurs de Validation Détectées:</h3><ul>"
            for err in errors[:20]:
                error_msg += f"<li>{err}</li>"
            if len(errors) > 20:
                error_msg += f"<li><b>... et {len(errors)-20} autres erreurs</b></li>"
            error_msg += "</ul>"
            
            QMessageBox.critical(self, "Validation Échouée", error_msg)
            return False
        
        return True
    
    def solve(self):
        if not self.validate_all_inputs():
            self.status.setText("❌ Validation échouée - Corrigez les erreurs")
            return
        
        try:
            n_techs = self.tech_spin.value()
            n_pannes = self.panne_spin.value()
            
            specs = []
            comp_matrix = []
            for i in range(n_techs):
                row_s = []
                row_comp = []
                for j in range(n_pannes):
                    item = self.comp_table.item(i, j)
                    if item and item.text().strip():
                        comp = int(item.text())
                        row_s.append(True)
                        row_comp.append(comp)
                    else:
                        row_s.append(False)
                        row_comp.append(0)
                specs.append(row_s)
                comp_matrix.append(row_comp)
            
            capacities = [int(self.capacity_table.item(0, i).text()) for i in range(n_techs)]
            skill_req = [int(self.req_table.item(0, j).text()) for j in range(n_pannes)]
            complexity = [int(self.complex_table.item(j, 0).text()) for j in range(n_pannes)]
            priorities = [int(self.prio_table.item(j, 0).text()) for j in range(n_pannes)]
            
            travel = []
            for i in range(n_techs):
                row = [float(self.dist_table.item(i, j).text()) for j in range(n_pannes)]
                travel.append(row)
            
            time_matrix = []
            for j in range(n_pannes):
                row = [float(self.time_table.item(j, level).text()) for level in range(5)]
                time_matrix.append(row)
            
            hourly_price_matrix = []
            for j in range(n_pannes):
                row = [float(self.price_table.item(j, level).text()) for level in range(5)]
                hourly_price_matrix.append(row)
            
            params = {
                'capacities': capacities, 'specializations': specs,
                'n_techs': n_techs, 'n_pannes': n_pannes, 'priorities': priorities,
                'competence_matrix': comp_matrix, 'skill_requirements': skill_req,
                'travel_matrix': travel, 'time_matrix': time_matrix,
                'hourly_price_matrix': hourly_price_matrix, 'complexity': complexity
            }
            
            self.solve_btn.setEnabled(False)
            self.status.setText("🔄 Optimisation en cours...")
            
            self.thread = OptimizationThread(self.model, params)
            self.thread.finished_signal.connect(self.on_finished)
            self.thread.start()
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du lancement: {str(e)}")
            self.solve_btn.setEnabled(True)
    
    def on_finished(self, stats, solution, runtime):
        self.solve_btn.setEnabled(True)
        
        if not stats or not solution:
            self.status.setText("❌ Pas de solution")
            QMessageBox.warning(self, "Aucune Solution",
                              "Le modèle n'a pas trouvé de solution réalisable.\n"
                              "Vérifiez les contraintes de capacité et de compétence.")
            return
        
        self.solution_data = (stats, solution, runtime)
        self.status.setText(f"✅ {stats['total_cost']:.0f}€ en {runtime:.2f}s")
        self.export_btn.setEnabled(True)
        
        self.display_results(stats, solution, runtime)
        self.tabs.setCurrentIndex(3)
    
    def export_to_csv(self):
        if not self.solution_data:
            QMessageBox.warning(self, "Aucune Donnée", "Lancez d'abord l'optimisation.")
            return
        
        stats, solution, runtime = self.solution_data
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter les Résultats",
            f"resultats_optimisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "Fichiers CSV (*.csv)")
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                
                writer.writerow(['=== RÉSULTATS OPTIMISATION ==='])
                writer.writerow([f'Date: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
                writer.writerow([f'Temps d\'exécution: {runtime:.3f}s'])
                writer.writerow([])
                
                writer.writerow(['STATISTIQUES GLOBALES'])
                writer.writerow(['Métrique', 'Valeur'])
                writer.writerow(['Coût Total', f'{stats["total_cost"]:.2f} €'])
                writer.writerow(['Coût Interventions (Temps * Prix H)', f'{stats["intervention_cost"]:.2f} €'])
                writer.writerow(['Coût Transport', f'{stats["travel_cost"]:.2f} €'])
                writer.writerow(['Pénalités', f'{stats["penalty_cost"]:.2f} €'])
                writer.writerow(['Économies', f'{stats["reward_savings"]:.2f} €'])
                writer.writerow(['Compétence Moyenne', f'{stats["avg_competence"]:.2f}/5'])
                writer.writerow(['Temps Moyen', f'{stats["avg_time"]:.2f}h'])
                writer.writerow(['Temps Total', f'{stats["total_time"]:.2f}h'])
                writer.writerow([])
                
                writer.writerow(['AFFECTATIONS DÉTAILLÉES'])
                writer.writerow(['Technicien', 'Panne', 'Coût Intervention (€)',
                               'Distance (km)', 'Coût Transport (€)', 'Temps (h)',
                               'Prix H (€/h)', 'Exigence', 'Compétence',
                               'Écart', 'Priorité', 'Complexité', 'Pénalité (€)',
                               'Bonus (€)', 'Coût Total (€)'])
                
                for (tech, panne), d in sorted(solution.items()):
                    writer.writerow([
                        f'T{tech}',
                        f'P{panne}',
                        f'{d["intervention_cost"]:.2f}',
                        f'{d["travel_distance"]:.1f}',
                        f'{d["travel_cost"]:.2f}',
                        f'{d["time_hours"]:.2f}',
                        f'{d["prix_h"]:.2f}',
                        d['required_skill'],
                        d['tech_competence'],
                        d['competence_gap'],
                        d['priority'],
                        d['complexity'],
                        f'{d["penalty"]:.2f}',
                        f'{d["reward"]:.2f}',
                        f'{d["total_cost"]:.2f}'
                    ])
                
                writer.writerow([])
                
                writer.writerow(['CHARGE PAR TECHNICIEN'])
                writer.writerow(['Technicien', 'Nb Interventions', 'Coût Total (€)',
                               'Compétence Moy', 'Temps Total (h)'])
                
                for tech in sorted(stats['tech_workload'].keys()):
                    w = stats['tech_workload'][tech]
                    writer.writerow([
                        f'T{tech}',
                        w['count'],
                        f'{w["cost"]:.2f}',
                        f'{w["skill"]:.2f}',
                        f'{w["time"]:.2f}'
                    ])
            
            QMessageBox.information(self, "✅ Exportation Réussie",
                                  f"Résultats exportés vers:\n{filename}")
            self.status.setText(f"✅ Exporté: {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'Export", f"Impossible d'exporter:\n{str(e)}")
    
    def display_results(self, stats, solution, runtime):
        perfect = sum(1 for d in solution.values() if d['competence_gap'] == 0)
        over = sum(1 for d in solution.values() if d['competence_gap'] < 0)
        under = sum(1 for d in solution.values() if d['competence_gap'] > 0)
        
        html = f"""
        <html>
        <head>
        <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: white; 
            margin: 10px; 
            color: black;
        }}
        .header {{
            background: #1a237e;
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
            border: 3px solid #3949ab;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: white;
            font-weight: bold;
        }}
        .header .cost {{
            font-size: 48px;
            font-weight: bold;
            margin: 20px 0;
            color: white;
            background: #3949ab;
            display: inline-block;
            padding: 10px 30px;
            border-radius: 10px;
        }}
        .header .subtitle {{
            font-size: 18px;
            color: #bbdefb;
            font-weight: 500;
            margin-top: 10px;
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 15px; 
            margin: 20px 0; 
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 6px solid #007bff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border: 1px solid #ddd;
        }}
        .stat-value {{ 
            font-size: 32px; 
            font-weight: bold; 
            color: #1a237e;
            margin: 5px 0; 
        }}
        .stat-label {{ 
            font-size: 14px; 
            color: #555;
            margin-top: 5px; 
        }}
        .section-title {{
            color: #1a237e;
            font-size: 22px;
            font-weight: bold;
            margin: 25px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #3949ab;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0; 
            background: white;
            border: 2px solid #3949ab;
        }}
        th {{
            background: #1a237e;
            color: white;
            padding: 16px;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
            border: 2px solid #0d1b5e;
        }}
        td {{ 
            padding: 14px; 
            text-align: center; 
            border: 2px solid #b3c6ff;
            font-size: 13px;
            color: black;
            background: white;
            font-weight: 500;
        }}
        tr:nth-child(even) {{ 
            background: #f8f9fa; 
        }}
        tr:hover {{ 
            background: #e3f2fd; 
        }}
        .badge {{ 
            padding: 6px 14px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: bold; 
            display: inline-block;
            border: 2px solid;
            min-width: 80px;
        }}
        .badge-red {{ 
            background: #ffebee; 
            color: #c62828; 
            border-color: #c62828; 
        }}
        .badge-orange {{ 
            background: #fff3e0; 
            color: #ef6c00; 
            border-color: #ef6c00;
        }}
        .badge-green {{ 
            background: #e8f5e9; 
            color: #2e7d32; 
            border-color: #2e7d32;
        }}
        .badge-blue {{ 
            background: #e3f2fd; 
            color: #1565c0; 
            border-color: #1565c0;
        }}
        .analysis-grid {{ 
            display: grid; 
            grid-template-columns: repeat(3, 1fr); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .analysis-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border: 2px solid #e0e0e0;
        }}
        .analysis-value {{ 
            font-size: 44px; 
            font-weight: bold; 
            margin: 15px 0; 
        }}
        .analysis-label {{ 
            font-size: 16px; 
            color: #555; 
            font-weight: 600;
        }}
        .priority-critical {{ 
            color: #d32f2f; 
            font-weight: bold;
        }}
        .priority-medium {{ 
            color: #f57c00; 
            font-weight: bold;
        }}
        .priority-low {{ 
            color: #388e3c; 
            font-weight: bold;
        }}
        .stars {{ 
            color: #FF8C00;
            font-size: 16px;
            padding: 5px 10px;
            border: 2px solid #b3c6ff;
            border-radius: 8px;
            background: #f8f9fa;
            display: inline-block;
            min-width: 60px;
        }}
        .cell-border {{
            border: 2px solid #b3c6ff !important;
        }}
        .distance-cell {{
            border: 2px solid #b3c6ff;
            padding: 12px;
            font-weight: bold;
        }}
        .complexity-cell {{
            border: 2px solid #b3c6ff;
            padding: 12px;
            font-weight: bold;
            background: #f8f9fa;
        }}
        .cost-cell {{
            border: 2px solid #b3c6ff;
            padding: 12px;
            font-weight: bold;
            color: #1a237e;
        }}
        .total-cell {{
            border: 2px solid #3949ab;
            padding: 12px;
            font-weight: bold;
            color: #1a237e;
            background: #e3f2fd;
        }}
        </style>
        </head>
        <body>
        
        <div class='header'>
            <h1>🎯 OPTIMISATION PLNE RÉUSSIE</h1>
            <div class='cost'>{stats['total_cost']:.2f} €</div>
            <div class='subtitle'>{len(solution)} interventions | {runtime:.3f}s | Compétence moy: {stats['avg_competence']:.2f}/5</div>
        </div>
        
        <div class='stats-grid'>
            <div class='stat-card'>
                <div class='stat-value'>{stats['intervention_cost']:.0f}€</div>
                <div class='stat-label'>💼 Coût Interventions (Temps * Prix H)</div>
            </div>
            <div class='stat-card' style='border-left-color: #f57c00;'>
                <div class='stat-value' style='color: #f57c00;'>{stats['travel_cost']:.0f}€</div>
                <div class='stat-label'>🚗 Coût Transport</div>
            </div>
            <div class='stat-card' style='border-left-color: #d32f2f;'>
                <div class='stat-value' style='color: #d32f2f;'>{stats['penalty_cost']:.0f}€</div>
                <div class='stat-label'>⚠️ Pénalités</div>
            </div>
            <div class='stat-card' style='border-left-color: #388e3c;'>
                <div class='stat-value' style='color: #388e3c;'>{stats['reward_savings']:.0f}€</div>
                <div class='stat-label'>💰 Économies</div>
            </div>
        </div>
        
        <div class='section-title'>📊 ANALYSE DES COMPÉTENCES</div>
        <div class='analysis-grid'>
            <div class='analysis-card' style='border-color: #1976d2;'>
                <div class='analysis-value' style='color: #1976d2;'>{perfect}</div>
                <div class='analysis-label'>🎯 Adéquation Parfaite</div>
                <div style='font-size: 12px; color: #666; margin-top: 5px;'>Compétence = Exigence</div>
            </div>
            <div class='analysis-card' style='border-color: #388e3c;'>
                <div class='analysis-value' style='color: #388e3c;'>{over}</div>
                <div class='analysis-label'>✅ Sur-qualifiés</div>
                <div style='font-size: 12px; color: #666; margin-top: 5px;'>Bonus appliqués</div>
            </div>
            <div class='analysis-card' style='border-color: #f57c00;'>
                <div class='analysis-value' style='color: #f57c00;'>{under}</div>
                <div class='analysis-label'>⚠️ Sous-qualifiés</div>
                <div style='font-size: 12px; color: #666; margin-top: 5px;'>Pénalités appliquées</div>
            </div>
        </div>
        
        <div class='section-title'>📋 AFFECTATIONS DÉTAILLÉES</div>
        <table>
            <tr>
                <th>Technicien</th>
                <th>Panne</th>
                <th>Coût (€)</th>
                <th>Distance (km)</th>
                <th>Exigence</th>
                <th>Compétence</th>
                <th>Écart</th>
                <th>Complexité</th>
                <th>Total (€)</th>
            </tr>
        """
        
        for (tech, panne), d in sorted(solution.items()):
            if d['competence_gap'] == 0:
                gap_badge = 'badge-blue'
                gap_text = '0 (Parfait)'
            elif d['competence_gap'] < 0:
                gap_badge = 'badge-green'
                gap_text = f"{d['competence_gap']:+d}"
            else:
                gap_badge = 'badge-red'
                gap_text = f"{d['competence_gap']:+d}"
            
            if d['priority'] == 1:
                priority_class = 'priority-critical'
            elif d['priority'] == 2:
                priority_class = 'priority-medium'
            else:
                priority_class = 'priority-low'
            
            html += f"""
            <tr>
                <td style='font-weight: bold;' class='{priority_class}'>👷 Tech {tech}</td>
                <td style='font-weight: bold;'>🔧 Panne {panne}</td>
                <td class='cost-cell'>{d['intervention_cost']:.0f}€</td>
                <td class='distance-cell'>{d['travel_distance']} km</td>
                <td><span class='stars'>{'★' * d['required_skill']}</span></td>
                <td><span class='stars'>{'★' * d['tech_competence']}</span></td>
                <td><span class='badge {gap_badge}'>{gap_text}</span></td>
                <td class='complexity-cell'>{d['complexity']}/5</td>
                <td class='total-cell'>{d['total_cost']:.0f}€</td>
            </tr>
            """
        
        html += """
        </table>
        </body>
        </html>
        """
        
        self.results_text.setHtml(html)
        self.create_graphs(stats, solution, runtime)
        
    def create_graphs(self, stats, solution, runtime):
        self.figure.clear()
        
        gs = self.figure.add_gridspec(5, 2, hspace=0.5, wspace=0.4,
                                     left=0.08, right=0.95, top=0.94, bottom=0.04)
        
        ax1 = self.figure.add_subplot(gs[0, :])
        n_techs = max(tech for tech, _ in solution.keys())
        n_pannes = max(panne for _, panne in solution.keys())
        
        data = np.zeros((n_techs, n_pannes))
        for (tech, panne), d in solution.items():
            data[tech-1, panne-1] = d['tech_competence']
        
        im = ax1.imshow(data, cmap='RdYlGn', vmin=1, vmax=5, aspect='auto')
        ax1.set_title('Matrice Affectations', fontsize=16, fontweight='bold', pad=12)
        ax1.set_xlabel('Pannes')
        ax1.set_ylabel('Techniciens')
        ax1.set_xticks(np.arange(n_pannes))
        ax1.set_xticklabels([str(i+1) for i in range(n_pannes)])
        ax1.set_yticks(np.arange(n_techs))
        ax1.set_yticklabels([str(i+1) for i in range(n_techs)])
        self.figure.colorbar(im, ax=ax1, label='Compétence')
        
        ax2 = self.figure.add_subplot(gs[1, 0])
        times = [d['time_hours'] for d in solution.values()]
        ax2.hist(times, bins=10, color='#1976d2', edgecolor='black', alpha=0.7)
        ax2.axvline(stats['avg_time'], color='red', linestyle='--', linewidth=2,
                   label=f'Moyenne: {stats["avg_time"]:.1f}h')
        ax2.set_title('Distribution Temps d\'Intervention', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Temps (heures)')
        ax2.set_ylabel('Fréquence')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        ax3 = self.figure.add_subplot(gs[1, 1])
        techs = sorted(stats['tech_workload'].keys())
        times_tech = [stats['tech_workload'][t]['time'] for t in techs]
        bars = ax3.bar(range(len(techs)), times_tech, color='#ff9800',
                      edgecolor='black', linewidth=2)
        ax3.axhline(40, color='red', linestyle='--', linewidth=2, label='Limite 40h')
        ax3.set_title('Temps Total par Technicien', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Heures')
        ax3.set_xticks(range(len(techs)))
        ax3.set_xticklabels([f'T{t}' for t in techs])
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        ax4 = self.figure.add_subplot(gs[2, :])
        categories = ['Intervention (Temps*Prix H)', 'Transport', 'Pénalités', 'Économies']
        values = [stats['intervention_cost'], stats['travel_cost'],
                 stats['penalty_cost'], stats['reward_savings']]
        colors_bars = ['#3498db', '#f39c12', '#e74c3c', '#27ae60']
        
        bars = ax4.barh(categories, values, color=colors_bars, edgecolor='black', linewidth=2)
        ax4.set_title('Décomposition des Coûts', fontsize=16, fontweight='bold')
        ax4.set_xlabel('Coût (€)')
        ax4.grid(axis='x', alpha=0.3)
        
        for bar, val in zip(bars, values):
            ax4.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.0f}€', va='center', fontsize=12, fontweight='bold')
        
        ax5 = self.figure.add_subplot(gs[3, 0])
        perfect = sum(1 for d in solution.values() if d['competence_gap'] == 0)
        over = sum(1 for d in solution.values() if d['competence_gap'] < 0)
        under = sum(1 for d in solution.values() if d['competence_gap'] > 0)
        
        labels = ['Parfaites', 'Sur-qualifiés', 'Sous-qualifiés']
        sizes = [perfect, over, under]
        colors = ['#27ae60', '#f39c12', '#e74c3c']
        
        wedges, texts, autotexts = ax5.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 12})
        ax5.set_title('Adéquations Compétences', fontsize=14, fontweight='bold')
        
        ax6 = self.figure.add_subplot(gs[3, 1])
        competences = [d['tech_competence'] for d in solution.values()]
        times_scatter = [d['time_hours'] for d in solution.values()]
        colors_scatter = [d['total_cost'] for d in solution.values()]
        
        scatter = ax6.scatter(competences, times_scatter, c=colors_scatter,
                            s=200, cmap='viridis', edgecolor='black', linewidth=1.5, alpha=0.7)
        ax6.set_title('Temps vs Compétence', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Compétence')
        ax6.set_ylabel('Temps (h)')
        ax6.grid(alpha=0.3)
        self.figure.colorbar(scatter, ax=ax6, label='Coût (€)')
        
        ax7 = self.figure.add_subplot(gs[4, :])
        ax7.axis('off')
        
        summary = f"""
RÉSUMÉ OPTIMISATION
═══════════════════════════════════════════════════════════════
COÛTS:  Total: {stats['total_cost']:.2f}€ | Interventions: {stats['intervention_cost']:.2f}€
Transport: {stats['travel_cost']:.2f}€ | Pénalités: {stats['penalty_cost']:.2f}€
TEMPS:  Total: {stats['total_time']:.1f}h | Moyen: {stats['avg_time']:.1f}h | Max Tech: {max(times_tech):.1f}h
COMPÉTENCES:  Moyenne: {stats['avg_competence']:.2f}/5 | Parfaites: {perfect} | Sur-qualifiés: {over} | Sous-qualifiés: {under}
PERFORMANCE:  Temps d'exécution: {runtime:.3f}s | Interventions: {len(solution)}
        """
        
        ax7.text(0.05, 0.95, summary, fontsize=11, verticalalignment='top',
                fontfamily='monospace', color='#333',
                bbox=dict(boxstyle='round,pad=1', facecolor='#f0f4f8',
                         edgecolor='#333', linewidth=2, alpha=0.95))
        
        self.figure.suptitle('VISUALISATION DES RÉSULTATS',
                     fontsize=19, fontweight='bold', 
                     x=0.45,
                     y=0.99,
                     bbox=dict(boxstyle='round,pad=0.8', facecolor='#48d1cc',
                              edgecolor='black', linewidth=3),
                     color='white')
        
        self.canvas.draw()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QGroupBox {
                font-weight: bold; border: 2px solid #ccc;
                border-radius: 8px; margin-top: 10px; padding-top: 10px;
                background: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
            QPushButton {
                background: #2196f3; color: white; border: none;
                padding: 10px 20px; border-radius: 6px;
                font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background: #1976d2; }
            QPushButton:pressed { background: #0d47a1; }
            QPushButton:disabled { background: #ccc; }
            QTableWidget {
                background: white; gridline-color: #ddd;
                border: 2px solid #ccc; border-radius: 6px;
            }
            QHeaderView::section {
                background: #37474f; color: white; padding: 8px;
                border: none; font-weight: bold;
            }
            QTextEdit {
                background: white; border: 2px solid #ccc;
                border-radius: 6px; padding: 10px;
                color: #333;
            }
        """)