#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ordonnancement multimode R&D — Frontière de Pareto
Corrections UI : suppression des "patch" blancs et fix du comportement de sélection.
Base : version fournie par l'utilisateur (harmonisation, fonctionnalités conservées).
"""

import sys
import json
import traceback
import datetime as dt   

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QFileDialog, QProgressBar,
    QMessageBox, QListWidget, QSpinBox, QFormLayout, QGroupBox,
    QAbstractItemView, QHeaderView, QDialog, QDialogButtonBox, QInputDialog
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QBrush, QColor, QFont

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ---------------------------
# Gurobi
# ---------------------------
try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except Exception:
    GUROBI_AVAILABLE = False

# ---------------------------
# Données par défaut (R&D)
# ---------------------------
DEFAULT_DATA = {
    "start_date": "2025-01-01",
    "horizon": 20,
    "resources_renewable": {
        "machines": 2,
        "techniciens": 2,
        "ingenieurs": 2
    },
    "resources_nonrenewable": {"financement_R&D": 1000},
    "logic_implies": [
        {"if": {"task": "Étude de faisabilité", "mode": "rapide"},
         "then": {"task": "Conception", "mode": "rapide"}}
    ],
    "tasks": [
        {"id": "Étude de faisabilité",
         "es": 0,  "ls": 20,
         "modes": [
             {"name": "normal", "dur": 4, "r": {"machines": 0, "techniciens": 1, "ingenieurs": 1}, "nr": {"financement_R&D": 100}, "coût": 100},
             {"name": "rapide",  "dur": 2, "r": {"machines": 0, "techniciens": 1, "ingenieurs": 2}, "nr": {"financement_R&D": 180}, "coût": 220}
         ],
         "pred": []},
        {"id": "Conception",
         "es": 0,  "ls": 20,
         "modes": [
             {"name": "normal", "dur": 3, "r": {"machines": 0, "techniciens": 1, "ingenieurs": 2}, "nr": {"financement_R&D": 200}, "coût": 150},
             {"name": "rapide",  "dur": 1, "r": {"machines": 0, "techniciens": 1, "ingenieurs": 3}, "nr": {"financement_R&D": 260}, "coût": 320}
         ],
         "pred": ["Étude de faisabilité"]},
        {"id": "Prototypage",
         "es": 0,  "ls": 20,
         "modes": [
             {"name": "normal", "dur": 5, "r": {"machines": 1, "techniciens": 2, "ingenieurs": 1}, "nr": {"financement_R&D": 150}, "coût": 120},
             {"name": "rapide",  "dur": 3, "r": {"machines": 1, "techniciens": 1, "ingenieurs": 2}, "nr": {"financement_R&D": 210}, "coût": 200}
         ],
         "pred": ["Conception"]},
        {"id": "Tests et validation",
         "es": 0,  "ls": 20,
         "modes": [
             {"name": "normal", "dur": 2, "r": {"machines": 1, "techniciens": 1, "ingenieurs": 1}, "nr": {"financement_R&D": 50}, "coût": 60},
             {"name": "rapide",  "dur": 1, "r": {"machines": 1, "techniciens": 1, "ingenieurs": 2}, "nr": {"financement_R&D": 80}, "coût": 95}
         ],
         "pred": ["Prototypage"]},
        {"id": "Industrialisation",
         "es": 0,  "ls": 20,
         "modes": [
             {"name": "normal", "dur": 3, "r": {"machines": 1, "techniciens": 1, "ingenieurs": 1}, "nr": {"financement_R&D": 100}, "coût": 80},
             {"name": "rapide",  "dur": 2, "r": {"machines": 1, "techniciens": 1, "ingenieurs": 2}, "nr": {"financement_R&D": 140}, "coût": 130}
         ],
         "pred": ["Tests et validation"]}
    ]
}

# ---------------------------
# Dialogues et worker (inchangés fonctionnellement)
# ---------------------------

class ModesEditorDialog(QDialog):
    def __init__(self, task_def, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Éditer modes – {task_def.get('id')}")
        self.resize(760, 320)
        self.task = task_def

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["name", "dur (jours)", "machines", "techniciens", "ingenieurs", "financement_R&D", "coût"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        modes = task_def.get("modes", [])
        self.table.setRowCount(len(modes))
        for r, m in enumerate(modes):
            self.table.setItem(r, 0, QTableWidgetItem(str(m.get("name", ""))))
            try:
                dur_txt = str(int(m.get("dur", 0)))
            except Exception:
                dur_txt = str(m.get("dur", ""))
            self.table.setItem(r, 1, QTableWidgetItem(dur_txt))
            self.table.setItem(r, 2, QTableWidgetItem(str(m.get("r", {}).get("machines", 0))))
            techn = m.get("r", {}).get("techniciens", None)
            ouv = m.get("r", {}).get("ouvriers", None)
            if techn is None and ouv is not None:
                techn = ouv
            self.table.setItem(r, 3, QTableWidgetItem(str(techn if techn is not None else 0)))
            self.table.setItem(r, 4, QTableWidgetItem(str(m.get("r", {}).get("ingenieurs", 0))))
            fin = m.get("nr", {}).get("financement_R&D", None)
            if fin is None:
                fin = m.get("nr", {}).get("budget", 0)
            self.table.setItem(r, 5, QTableWidgetItem(str(fin)))
            self.table.setItem(r, 6, QTableWidgetItem(str(m.get("coût", 0))))
        layout.addWidget(self.table)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.save_and_close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save_and_close(self):
        modes = []
        for r in range(self.table.rowCount()):
            name = self._text(r, 0) or f"mode{r}"
            dur = int(self._text(r, 1) or "1")
            machines = int(self._text(r, 2) or "0")
            techniciens = int(self._text(r, 3) or "0")
            ingenieurs = int(self._text(r, 4) or "0")
            financement = float(self._text(r, 5) or "0")
            coût = float(self._text(r, 6) or "0")

            modes.append({
                "name": name,
                "dur": dur,
                "r": {"machines": machines, "techniciens": techniciens, "ingenieurs": ingenieurs},
                "nr": {"financement_R&D": financement},
                "coût": coût,
            })
        self.task["modes"] = modes
        self.accept()

    def _text(self, row, col):
        item = self.table.item(row, col)
        return item.text().strip() if item else ""

class ParetoThread(QThread):
    progress = pyqtSignal(int)
    finished_success = pyqtSignal(list)
    finished_error = pyqtSignal(str)

    def __init__(self, data, n_points=10, time_limit=30, threads=2):
        super().__init__()
        self.data = data
        self.n_points = max(2, int(n_points))
        self.time_limit = time_limit
        self.threads = threads
        self._abort = False
        self.model = None

    def request_abort(self):
        self._abort = True
        try:
            if self.model is not None:
                self.model.terminate()
        except Exception:
            pass

    def run(self):
        try:
            if not GUROBI_AVAILABLE:
                raise RuntimeError("Gurobi non disponible (gurobipy introuvable).")

            tasks = self.data["tasks"]
            H = int(self.data["horizon"])
            ren_caps = self.data["resources_renewable"]
            nonren_caps = self.data["resources_nonrenewable"]

            if "budget" in nonren_caps and "financement_R&D" not in nonren_caps:
                nonren_caps["financement_R&D"] = nonren_caps.pop("budget")

            sd_txt = self.data.get("start_date", None)
            if sd_txt:
                try:
                    start_date = dt.datetime.strptime(sd_txt, "%Y-%m-%d").date()
                except Exception:
                    start_date = dt.date.today()
            else:
                start_date = dt.date.today()

            task_ids = [t["id"] for t in tasks]
            modes_per_task = {t["id"]: t["modes"] for t in tasks}

            def parse_time_field(val, default):
                if isinstance(val, str):
                    try:
                        d = dt.datetime.strptime(val, "%Y-%m-%d").date()
                        delta = (d - start_date).days
                        if delta < 0:
                            return 0
                        return int(delta)
                    except Exception:
                        try:
                            return int(float(val))
                        except Exception:
                            return int(default)
                else:
                    try:
                        return int(val)
                    except Exception:
                        return int(default)

            def build_and_optimize(weight_norm, cmin_ref, coûtmin_ref):
                m = gp.Model("multimode_time_indexed")
                m.setParam("OutputFlag", 0)
                m.setParam("TimeLimit", self.time_limit)
                m.setParam("Threads", self.threads)
                self.model = m

                x = {}
                for i in task_ids:
                    tdef = next(td for td in tasks if td["id"] == i)
                    es = parse_time_field(tdef.get("es", 0), 0)
                    ls = parse_time_field(tdef.get("ls", H), H)
                    modes = modes_per_task[i]
                    for m_idx, mode in enumerate(modes):
                        dur = int(mode["dur"])
                        for t in range(H):
                            var = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{m_idx}_{t}")
                            x[i, m_idx, t] = var
                            if t < es or (t + dur) > min(ls, H):
                                m.addConstr(var == 0, name=f"forbid_{i}_{m_idx}_{t}")

                for i in task_ids:
                    m.addConstr(
                        gp.quicksum(
                            x[i, m_idx, t]
                            for m_idx in range(len(modes_per_task[i]))
                            for t in range(H)
                        ) == 1,
                        name=f"start_once_{i}",
                    )

                for res_name, cap in ren_caps.items():
                    for tau in range(H):
                        expr = gp.LinExpr()
                        for i in task_ids:
                            modes = modes_per_task[i]
                            for m_idx, mode in enumerate(modes):
                                ri = mode.get("r", {}).get(res_name, 0)
                                if ri == 0 and res_name == "techniciens":
                                    ri = mode.get("r", {}).get("ouvriers", 0)
                                if ri == 0:
                                    continue
                                dur = int(mode["dur"])
                                tmin = max(0, tau - dur + 1)
                                tmax = tau
                                for t in range(tmin, tmax + 1):
                                    expr.addTerms(ri, x[i, m_idx, t])
                        m.addConstr(expr <= cap, name=f"res_{res_name}_time_{tau}")

                if "budget" in nonren_caps and "financement_R&D" not in nonren_caps:
                    nonren_caps["financement_R&D"] = nonren_caps.pop("budget")

                for nr_name, budget in nonren_caps.items():
                    expr = gp.quicksum(
                        (mode.get("nr", {}).get(nr_name, 0) if nr_name in mode.get("nr", {}) else mode.get("nr", {}).get("budget", 0))
                        * x[i, m_idx, t]
                        for i in task_ids
                        for m_idx, mode in enumerate(modes_per_task[i])
                        for t in range(H)
                    )
                    m.addConstr(expr <= budget, name=f"budget_{nr_name}")

                z = {}
                for i in task_ids:
                    for m_idx in range(len(modes_per_task[i])):
                        z[i, m_idx] = m.addVar(vtype=GRB.BINARY, name=f"z_{i}_{m_idx}")
                        m.addConstr(
                            z[i, m_idx] == gp.quicksum(x[i, m_idx, t] for t in range(H)),
                            name=f"link_z_{i}_{m_idx}",
                        )

                for rule in self.data.get("logic_implies", []):
                    t_if = rule["if"]["task"]
                    m_if = rule["if"]["mode"]
                    t_then = rule["then"]["task"]
                    m_then = rule["then"]["mode"]
                    if t_if in task_ids and t_then in task_ids:
                        idx_if = next((k for k, md in enumerate(modes_per_task[t_if]) if md["name"] == m_if), None)
                        idx_then = next((k for k, md in enumerate(modes_per_task[t_then]) if md["name"] == m_then), None)
                        if idx_if is not None and idx_then is not None:
                            m.addConstr(z[t_if, idx_if] <= z[t_then, idx_then], name=f"logic_{t_if}_{m_if}_imp_{t_then}_{m_then}")

                for j in task_ids:
                    preds = next(t for t in tasks if t["id"] == j).get("pred", [])
                    if not preds:
                        continue
                    for i_pred in preds:
                        s_j = gp.quicksum(t * x[j, m_idx, t] for m_idx in range(len(modes_per_task[j])) for t in range(H))
                        s_i = gp.quicksum(t * x[i_pred, m_idx, t] for m_idx in range(len(modes_per_task[i_pred])) for t in range(H))
                        rhs = gp.quicksum(int(mode["dur"]) * gp.quicksum(x[i_pred, m_idx, tt] for tt in range(H)) for m_idx, mode in enumerate(modes_per_task[i_pred]))
                        m.addConstr(s_j - s_i >= rhs, name=f"prec_{i_pred}_before_{j}")

                Cmax = m.addVar(lb=0.0, name="Cmax")
                for i in task_ids:
                    finish_expr = gp.quicksum((t + int(mode["dur"])) * x[i, m_idx, t] for m_idx, mode in enumerate(modes_per_task[i]) for t in range(H))
                    m.addConstr(Cmax >= finish_expr)

                total_coût_expr = gp.quicksum(mode.get("coût", 0.0) * x[i, m_idx, t] for i in task_ids for m_idx, mode in enumerate(modes_per_task[i]) for t in range(H))

                denom_c = cmin_ref if (cmin_ref and cmin_ref > 0.0) else 1.0
                denom_coût = coûtmin_ref if (coûtmin_ref and coûtmin_ref > 0.0) else 1.0

                obj = weight_norm * (Cmax / denom_c) + (1.0 - weight_norm) * (total_coût_expr / denom_coût)
                m.setObjective(obj, GRB.MINIMIZE)

                m.optimize()

                if self._abort:
                    raise RuntimeError("Annulé par l'utilisateur")

                if m.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT, GRB.SUBOPTIMAL):
                    if m.Status == GRB.INFEASIBLE:
                        try:
                            m.computeIIS()
                            iis_cons = []
                            for c in m.getConstrs():
                                try:
                                    if getattr(c, "IISConstr", False):
                                        name = getattr(c, "ConstrName", None) or ""
                                        iis_cons.append(name)
                                except Exception:
                                    continue
                            iis_vars = []
                            for v in m.getVars():
                                try:
                                    if getattr(v, "IISLB", 0) or getattr(v, "IISUB", 0):
                                        iis_vars.append(getattr(v, "VarName", ""))
                                except Exception:
                                    continue

                            causes = set()
                            for name in iis_cons:
                                if name.startswith("res_"):
                                    parts = name.split("_")
                                    if len(parts) >= 3:
                                        causes.add(f"ressource '{parts[1]}' (conflits temporels)")
                                    else:
                                        causes.add(name)
                                elif name.startswith("budget_"):
                                    parts = name.split("_", 1)
                                    causes.add(f"financement '{parts[1] if len(parts)>1 else parts[0]}' (budget insuffisant)")
                                elif name.startswith("prec_"):
                                    causes.add("précédence impossible (ordre/durée)")
                                elif name.startswith("forbid_"):
                                    causes.add("fenêtre temporelle / durée incompatible")
                                else:
                                    causes.add(name)

                            diag = "; ".join(sorted(causes)) if causes else ("vars: " + ", ".join(iis_vars) if iis_vars else "contraintes en conflit non identifiées")
                            suggestions = [
                                "Vérifier/augmenter les capacités (techniciens / ingénieurs / machines).",
                                "Augmenter le financement_R&D (budget non-renouvelable).",
                                "Allonger l'horizon ou réduire certaines durées / modes rapides.",
                                "Vérifier les prédécesseurs pour éviter des contraintes impossibles."
                            ]
                            msg = "Aucune solution faisable (modèle infaisable).\n\nConflits détectés : " + diag + "\n\nSuggestions :\n - " + "\n - ".join(suggestions)
                            try:
                                m.write("infeasible.ilp")
                                msg += "\n\nUn fichier IIS a été écrit : infeasible.ilp (utile pour le débogage avancé)."
                            except Exception:
                                pass
                        except Exception:
                            msg = "Aucune solution faisable (modèle infaisable). Vérifiez ressources, horizon et prédécesseurs."
                        raise RuntimeError(msg)
                    else:
                        raise RuntimeError(f"Optimisation échouée (statut={m.Status})")

                # extraction
                starts = {}
                modes_choice = {}
                durations = {}
                for i in task_ids:
                    found = False
                    for m_idx, mode in enumerate(modes_per_task[i]):
                        for t in range(H):
                            val = x[i, m_idx, t].X
                            if val > 0.5:
                                starts[i] = int(t)
                                modes_choice[i] = mode["name"]
                                durations[i] = int(mode["dur"])
                                found = True
                                break
                        if found:
                            break

                total_coût_val = 0.0
                for i in task_ids:
                    for m_idx, mode in enumerate(modes_per_task[i]):
                        used = sum(x[i, m_idx, t].X for t in range(H))
                        total_coût_val += mode.get("coût", 0.0) * used

                sol = {
                    "weight": weight_norm,
                    "objective_raw": float(m.ObjVal),
                    "Cmax": float(Cmax.X),
                    "total_coût": float(total_coût_val),
                    "starts": starts,
                    "modes_choice": modes_choice,
                    "durations": durations,
                    "status": int(m.Status),
                }
                return sol

            self.progress.emit(1)
            sol_time = build_and_optimize(1.0, cmin_ref=None, coûtmin_ref=None)
            self.progress.emit(10)
            sol_coût = build_and_optimize(0.0, cmin_ref=None, coûtmin_ref=None)
            self.progress.emit(20)

            Cmin = sol_time["Cmax"] or 1.0
            coûtMin = sol_coût["total_coût"] or 1.0
            if Cmin <= 0:
                Cmin = 1.0
            if coûtMin <= 0:
                coûtMin = 1.0

            solutions = []
            for idx in range(self.n_points):
                if self._abort:
                    break
                w = idx / (self.n_points - 1)
                sol = build_and_optimize(w, cmin_ref=Cmin, coûtmin_ref=coûtMin)
                solutions.append(sol)
                self.progress.emit(20 + int(80 * (idx + 1) / self.n_points))

            if self._abort:
                self.finished_error.emit("Calcul annulé par l'utilisateur.")
                return

            self.finished_success.emit(solutions)

        except Exception as e:
            self.finished_error.emit(str(e))

# ---------------------------
# UI principale (fixes selection / corner button / styles)
# ---------------------------

class ParetoSchedulerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ordonnancement R&D multimode — Frontière de Pareto")
        self.resize(1280, 900)

        # style global : dark theme (on précise aussi la sélection des tableaux)
        self.setStyleSheet('''
            QWidget { font-family: "Segoe UI", Roboto, Arial, sans-serif; color: #E6EEF8; background: #0b1114; font-size: 11px; }
            QGroupBox { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #0b1114, stop:1 #0f1418); border: 1px solid #1f2a30; border-radius: 8px; margin-top: 8px; padding: 8px; }
            QLabel#mainTitle { color: #7be0ff; font-size: 18px; font-weight: 800; }
            QLabel#subtitle { color: #9fb6c6; font-size: 12px; }
            QPushButton { background-color: #0ea5a4; color: #021414; padding: 8px 12px; border-radius: 8px; font-weight: 700; border: none; min-height: 30px; }
            QListWidget, QTableWidget {
                background: #071012;
                color: #e6eef8;
                border: 1px solid #123033;
                border-radius: 6px;
                alternate-background-color: #051018;
                selection-background-color: #134b53;
                selection-color: #e6eef8;
                outline: none;
            }
            QTableWidget::item { padding: 4px; }
            QTableWidget::item:selected { background: #134b53; color: #e6eef8; }
            QHeaderView::section { background: #081219; color: #9fb6c6; padding: 6px; border: 1px solid #123033; font-weight: 700; }
            QListWidget::item:selected { background: #134b53; color: #e6eef8; }
            QScrollBar:vertical { background: #071012; width: 12px; }
        ''')

        self.data = json.loads(json.dumps(DEFAULT_DATA))
        self._harmonize_old_keys(self.data)

        self.thread = None
        self.solutions = []

        self._build_ui()
        self.load_data(self.data)

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        # header
        header = QHBoxLayout()
        left = QVBoxLayout()
        lbl_title = QLabel("Ordonnancement R&D multimode — Frontière de Pareto"); lbl_title.setObjectName("mainTitle")
        lbl_sub = QLabel("Saisie structurée, calcul non bloquant et visualisation (Gurobi requis). Dates calendaires réelles affichées."); lbl_sub.setObjectName("subtitle")
        left.addWidget(lbl_title); left.addWidget(lbl_sub)
        header.addLayout(left); header.addStretch()
        self.lbl_overview = QLabel(""); self.lbl_overview.setStyleSheet("color: #9fb6c6;")
        header.addWidget(self.lbl_overview)
        main.addLayout(header)

        # top controls
        top = QHBoxLayout()
        self.btn_load = QPushButton("Charger JSON"); self.btn_save = QPushButton("Sauver JSON")
        self.btn_run = QPushButton("Résoudre")
        top.addWidget(self.btn_load); top.addWidget(self.btn_save); top.addSpacing(6)
        top.addWidget(self.btn_run); top.addStretch()
        status_layout = QVBoxLayout()
        self.lbl_status = QLabel("Prêt"); self.lbl_status.setStyleSheet("font-weight:600; color: #7ed957;")
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0); self.progress.setFixedWidth(360)
        status_layout.addWidget(self.lbl_status, alignment=Qt.AlignmentFlag.AlignRight); status_layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignRight)
        top.addLayout(status_layout)
        main.addLayout(top)

        # middle layout
        mid = QHBoxLayout(); mid.setSpacing(12)

        # left column
        left_panel = QVBoxLayout(); left_panel.setSpacing(10)
        settings_box = QGroupBox("Paramètres Pareto"); f = QFormLayout()
        self.spin_points = QSpinBox(); self.spin_points.setRange(2, 100); self.spin_points.setValue(9)
        self.spin_time_limit = QSpinBox(); self.spin_time_limit.setRange(1, 3600); self.spin_time_limit.setValue(30)
        self.spin_threads = QSpinBox(); self.spin_threads.setRange(1, 16); self.spin_threads.setValue(2)
        f.addRow("Nombre de points", self.spin_points); f.addRow("TimeLimit (s)", self.spin_time_limit); f.addRow("Threads Gurobi", self.spin_threads)
        settings_box.setLayout(f); left_panel.addWidget(settings_box)

        resources_box = QGroupBox("Ressources")
        rb_layout = QVBoxLayout()

        self.table_renew = QTableWidget(); self.table_renew.setColumnCount(2)
        self.table_renew.setHorizontalHeaderLabels(["Ressource", "Capacité"])
        self.table_renew.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_renew.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # hide vertical header to avoid empty left column showing white area
        self.table_renew.verticalHeader().setVisible(False)
        # remove corner button (prevents white square in top-left)
        try:
            self.table_renew.setCornerButtonEnabled(False)
        except Exception:
            pass
        self.table_renew.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_renew.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        rb_layout.addWidget(QLabel("Ressources renouvelables")); rb_layout.addWidget(self.table_renew)

        self.table_nonren = QTableWidget(); self.table_nonren.setColumnCount(2)
        self.table_nonren.setHorizontalHeaderLabels(["Ressource", "Financement R&D"])
        self.table_nonren.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_nonren.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_nonren.verticalHeader().setVisible(False)
        try:
            self.table_nonren.setCornerButtonEnabled(False)
        except Exception:
            pass
        self.table_nonren.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_nonren.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        rb_layout.addWidget(QLabel("Ressources non-renouvelables")); rb_layout.addWidget(self.table_nonren)

        resources_box.setLayout(rb_layout); left_panel.addWidget(resources_box)

        tasks_box = QGroupBox("Phases R&D (édition possible via JSON ou bouton Modes)")
        vtb = QVBoxLayout()
        self.table = QTableWidget()
        # ensure 3 columns for ID, Modes, Pred
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Modes", "Prédécesseurs"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True); self.table.verticalHeader().setVisible(False)
        # remove corner button to avoid small white square
        try:
            self.table.setCornerButtonEnabled(False)
        except Exception:
            pass
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.table.setWordWrap(True)
        self.table.setMinimumWidth(420); self.table.setMinimumHeight(200)
        vtb.addWidget(self.table)

        btns_h = QHBoxLayout()
        self.btn_edit_modes = QPushButton("Éditer modes de la phase sélectionnée")
        self.btn_add_phase = QPushButton("Ajouter une phase R&D")
        btns_h.addWidget(self.btn_edit_modes); btns_h.addWidget(self.btn_add_phase)
        vtb.addLayout(btns_h)
        tasks_box.setLayout(vtb); left_panel.addWidget(tasks_box, stretch=1)

        help_label = QLabel("Astuce : ajoutez des phases, éditez les modes via le bouton ou via JSON. Modifiez les capacités dans les tableaux ci-dessus.")
        help_label.setWordWrap(True); left_panel.addWidget(help_label)

        mid.addLayout(left_panel, 1)

        # right column
        right_panel = QVBoxLayout(); right_panel.setSpacing(10)
        upper = QHBoxLayout()
        vlist = QVBoxLayout(); vlist.addWidget(QLabel("Solutions Pareto"))
        self.pareto_list = QListWidget(); self.pareto_list.setMinimumWidth(280)
        # ensure selection color consistent
        self.pareto_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        vlist.addWidget(self.pareto_list); upper.addLayout(vlist, 1)

        vres = QVBoxLayout(); vres.addWidget(QLabel("Détails solution sélectionnée"))
        self.lbl_obj = QLabel("Objectif (raw): -"); self.lbl_cmax = QLabel("Cmax: -"); self.lbl_coût = QLabel("Coût total: -")
        sum_layout = QHBoxLayout(); sum_layout.addWidget(self.lbl_obj); sum_layout.addWidget(self.lbl_cmax); sum_layout.addWidget(self.lbl_coût)
        vres.addLayout(sum_layout)

        self.result_table = QTableWidget(); self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Phase", "Mode", "Début (date)", "Durée (jours)"])
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.verticalHeader().setVisible(False)
        try:
            self.result_table.setCornerButtonEnabled(False)
        except Exception:
            pass
        vres.addWidget(self.result_table)

        vres.addWidget(QLabel("Variables de décision (x)"))
        self.vars_table = QTableWidget(); self.vars_table.setColumnCount(4)
        self.vars_table.setHorizontalHeaderLabels(["Phase", "Mode idx", "Start t (jours)", "Valeur"])
        self.vars_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vars_table.verticalHeader().setVisible(False)
        try:
            self.vars_table.setCornerButtonEnabled(False)
        except Exception:
            pass
        vres.addWidget(self.vars_table)

        upper.addLayout(vres, 2); right_panel.addLayout(upper, 2)

        self.fig_pareto, self.ax_pareto = plt.subplots(figsize=(7, 4), dpi=100)
        self.fig_pareto.patch.set_facecolor("#0b1114"); self.ax_pareto.set_facecolor("#0b1114")
        self.canvas_pareto = FigureCanvas(self.fig_pareto); self.canvas_pareto.setMinimumHeight(280); right_panel.addWidget(self.canvas_pareto, 1)

        self.fig_gantt, self.ax_gantt = plt.subplots(figsize=(8, 3.4), dpi=100)
        self.fig_gantt.patch.set_facecolor("#0b1114"); self.ax_gantt.set_facecolor("#0b1114")
        self.canvas_gantt = FigureCanvas(self.fig_gantt); right_panel.addWidget(self.canvas_gantt, 2)

        mid.addLayout(right_panel, 2)
        main.addLayout(mid, 10)

        footer = QHBoxLayout(); self.lbl_footer = QLabel("Prêt • Utilisez 'Charger JSON' pour ouvrir une instance personnalisée"); footer.addWidget(self.lbl_footer); footer.addStretch(); main.addLayout(footer)

        # signals
        self.btn_load.clicked.connect(self.load_json)
        self.btn_save.clicked.connect(self.save_json)
        self.btn_run.clicked.connect(self.on_run)
        self.btn_edit_modes.clicked.connect(self.on_edit_modes)
        self.btn_add_phase.clicked.connect(self.on_add_phase)
        self.pareto_list.currentRowChanged.connect(self.on_select_solution)

    # ---------- utilitaires ----------
    def _harmonize_old_keys(self, data):
        nonren = data.get("resources_nonrenewable", {})
        if "budget" in nonren and "financement_R&D" not in nonren:
            nonren["financement_R&D"] = nonren.pop("budget")
        data["resources_nonrenewable"] = nonren

        ren = data.get("resources_renewable", {})
        if "ouvriers" in ren and "techniciens" not in ren and "ingenieurs" not in ren:
            ren["techniciens"] = ren.pop("ouvriers")
        data["resources_renewable"] = ren

        for t in data.get("tasks", []):
            for m in t.get("modes", []):
                if "cost" in m and "coût" not in m:
                    m["coût"] = m.pop("cost")
                nr = m.get("nr", {})
                if "budget" in nr and "financement_R&D" not in nr:
                    nr["financement_R&D"] = nr.pop("budget")
                r = m.get("r", {})
                if "ouvriers" in r and "techniciens" not in r:
                    r["techniciens"] = r.pop("ouvriers")
                m["nr"] = nr
                m["r"] = r

    def _apply_item_colors(self, item):
        if item:
            item.setBackground(QBrush(QColor("#071012")))
            item.setForeground(QBrush(QColor("#e6eef8")))

    def _normalize_mode_durations(self):
        for tt in self.data.get("tasks", []):
            for mm in tt.get("modes", []):
                try:
                    mm["dur"] = int(mm.get("dur", 0))
                except Exception:
                    try:
                        mm["dur"] = int(float(mm.get("dur", 0)))
                    except Exception:
                        mm["dur"] = 0
                if "coût" not in mm and "cost" in mm:
                    mm["coût"] = mm.get("cost")
                nr = mm.get("nr", {})
                if "financement_R&D" not in nr and "budget" in nr:
                    nr["financement_R&D"] = nr.pop("budget")
                mm["nr"] = nr
                r = mm.get("r", {})
                if "techniciens" not in r and "ouvriers" in r:
                    r["techniciens"] = r.pop("ouvriers")
                mm["r"] = r

    def _silent_fix_durations(self):
        changed = False
        for t in self.data.get("tasks", []):
            for m in t.get("modes", []):
                dur = m.get("dur")
                try:
                    if not isinstance(dur, int):
                        m["dur"] = int(dur); changed = True
                except Exception:
                    try:
                        m["dur"] = int(float(dur)); changed = True
                    except Exception:
                        m["dur"] = 0; changed = True
        if changed:
            self.load_data(self.data)

    # ---------- load / save ----------
    def load_data(self, data):
        self.data = json.loads(json.dumps(data))
        self._harmonize_old_keys(self.data)
        self._normalize_mode_durations()

        tasks = self.data.get("tasks", [])
        self.table.setRowCount(len(tasks))
        for r, t in enumerate(tasks):
            id_item = QTableWidgetItem(t.get("id", ""))
            modes_str = "; ".join(f"{m['name']}:{int(m['dur'])},{m.get('coût', 0)}" for m in t.get("modes", []))
            modes_item = QTableWidgetItem(modes_str)
            preds_item = QTableWidgetItem(",".join(t.get("pred", [])))
            self._apply_item_colors(id_item); self._apply_item_colors(modes_item); self._apply_item_colors(preds_item)
            self.table.setItem(r, 0, id_item); self.table.setItem(r, 1, modes_item); self.table.setItem(r, 2, preds_item)

        ren = self.data.get("resources_renewable", {})
        if "techniciens" not in ren and "ouvriers" in ren:
            ren["techniciens"] = ren.pop("ouvriers")
        if "ingenieurs" not in ren:
            ren["ingenieurs"] = ren.get("ingenieurs", 0)
        self.table_renew.setRowCount(len(ren))
        for r, (k, v) in enumerate(ren.items()):
            it0 = QTableWidgetItem(str(k)); it1 = QTableWidgetItem(str(v))
            self._apply_item_colors(it0); self._apply_item_colors(it1)
            self.table_renew.setItem(r, 0, it0); self.table_renew.setItem(r, 1, it1)

        nonren = self.data.get("resources_nonrenewable", {})
        self.table_nonren.setRowCount(len(nonren))
        for r, (k, v) in enumerate(nonren.items()):
            it0 = QTableWidgetItem(str(k)); it1 = QTableWidgetItem(str(v))
            self._apply_item_colors(it0); self._apply_item_colors(it1)
            self.table_nonren.setItem(r, 0, it0); self.table_nonren.setItem(r, 1, it1)

        sd = self.data.get("start_date", "N/A"); horizon = self.data.get("horizon", "")
        self.lbl_overview.setText(f"Phases: {len(tasks)}  •  Horizon: {horizon} jours  •  Start date: {sd}")
        self._silent_fix_durations()

    def read_table_to_data(self):
        rows = self.table.rowCount()
        for r in range(rows):
            id_item = self.table.item(r, 0)
            preds_item = self.table.item(r, 2)
            if id_item:
                tid = id_item.text().strip()
                for t in self.data.get("tasks", []):
                    if t.get("id") == tid:
                        if preds_item:
                            t["pred"] = [p.strip() for p in preds_item.text().split(",") if p.strip()]
                        break

        ren = {}
        for r in range(self.table_renew.rowCount()):
            key_item = self.table_renew.item(r, 0); val_item = self.table_renew.item(r, 1)
            if key_item and val_item:
                txt = val_item.text().strip()
                try:
                    ren[key_item.text().strip()] = float(txt) if "." in txt else int(txt)
                except Exception:
                    ren[key_item.text().strip()] = txt
        if "techniciens" not in ren and "ouvriers" in ren:
            ren["techniciens"] = ren.pop("ouvriers")
        if "ingenieurs" not in ren:
            ren["ingenieurs"] = ren.get("ingenieurs", 0)

        nonren = {}
        for r in range(self.table_nonren.rowCount()):
            key_item = self.table_nonren.item(r, 0); val_item = self.table_nonren.item(r, 1)
            if key_item and val_item:
                txt = val_item.text().strip()
                try:
                    nonren[key_item.text().strip()] = float(txt) if "." in txt else int(txt)
                except Exception:
                    nonren[key_item.text().strip()] = txt
        if "budget" in nonren and "financement_R&D" not in nonren:
            nonren["financement_R&D"] = nonren.pop("budget")

        self.data["resources_renewable"] = ren
        self.data["resources_nonrenewable"] = nonren

    def load_json(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Ouvrir JSON", "", "JSON Files (*.json)")
        if not fname:
            return
        try:
            with open(fname, "r") as f:
                data = json.load(f)
            self._harmonize_old_keys(data)
            self.load_data(data)
            QMessageBox.information(self, "OK", "Fichier chargé")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def save_json(self):
        self.read_table_to_data()
        self._normalize_mode_durations()
        fname, _ = QFileDialog.getSaveFileName(self, "Sauver JSON", "", "JSON Files (*.json)")
        if not fname:
            return
        try:
            with open(fname, "w") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "OK", "Fichier sauvé")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # ---------- actions ----------
    def on_edit_modes(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez d'abord une phase dans le tableau.")
            return
        tid_item = self.table.item(row, 0)
        if not tid_item:
            return
        tid = tid_item.text().strip()
        for t in self.data.get("tasks", []):
            if t.get("id") == tid:
                dlg = ModesEditorDialog(t, parent=self)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    modes_str = "; ".join(f"{m['name']}:{int(m['dur'])},{m.get('coût',0)}" for m in t.get("modes", []))
                    modes_item = QTableWidgetItem(modes_str)
                    self._apply_item_colors(modes_item)
                    self.table.setItem(row, 1, modes_item)
                break

    def on_add_phase(self):
        name, ok = QInputDialog.getText(self, "Nouvelle phase R&D", "Nom de la phase :")
        if not ok or not name.strip():
            return
        name = name.strip()
        horizon = int(self.data.get("horizon", 20))
        new_task = {
            "id": name,
            "es": 0,
            "ls": horizon,
            "modes": [
                {"name": "normal", "dur": 3,
                 "r": {"machines": 0, "techniciens": 1, "ingenieurs": 1},
                 "nr": {"financement_R&D": 100},
                 "coût": 100}
            ],
            "pred": []
        }
        self.data.setdefault("tasks", []).append(new_task)
        self._harmonize_old_keys(self.data)
        self.load_data(self.data)

    def on_run(self):
        if not GUROBI_AVAILABLE:
            QMessageBox.critical(self, "Gurobi absent", "Gurobi (gurobipy) n'est pas disponible dans cet environnement.")
            return

        self.read_table_to_data()
        n_points = self.spin_points.value()
        tlimit = self.spin_time_limit.value()
        threads = self.spin_threads.value()

        self.btn_run.setEnabled(False)
        self.lbl_status.setText("Calcul Pareto en cours.")
        self.progress.setValue(0)
        self.pareto_list.clear()
        self.result_table.setRowCount(0)
        self.vars_table.setRowCount(0)
        self.ax_pareto.clear(); self.canvas_pareto.draw()
        self.ax_gantt.clear(); self.canvas_gantt.draw()

        self.thread = ParetoThread(self.data, n_points=n_points, time_limit=tlimit, threads=threads)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished_success.connect(self.on_pareto_done)
        self.thread.finished_error.connect(self.on_pareto_error)
        self.thread.start()

    

    def on_pareto_done(self, solutions):
        self.lbl_status.setText("Terminé")
        self.btn_run.setEnabled(True)
        self.solutions = solutions

        cmaxs = [s.get("Cmax", 0) for s in solutions]
        coûts = [s.get("total_coût", 0) for s in solutions]
        self.ax_pareto.clear()
        self.ax_pareto.set_facecolor("#0b1114")
        self.ax_pareto.grid(True, linestyle="--", alpha=0.28, color="#0f2a2a")
        palette = ["#7be0ff", "#ffb07b", "#7ed957", "#d291ff", "#ff6b6b", "#ffd166", "#61dafb", "#9ad3bc"]
        colors = [palette[i % len(palette)] for i in range(len(solutions))]
        self.ax_pareto.scatter(cmaxs, coûts, s=110, c=colors, edgecolors="#071012", linewidths=0.9, zorder=3)
        self.pareto_list.clear()
        for i, s in enumerate(solutions):
            self.pareto_list.addItem(f"#{i} w={s['weight']:.2f}  Cmax={s.get('Cmax',0):.1f}  coût={s.get('total_coût',0):.1f}")
            self.ax_pareto.annotate(str(i), (cmaxs[i], coûts[i]), textcoords="offset points", xytext=(8, 6), fontsize=9, color="#071012",
                                    bbox=dict(boxstyle="round,pad=0.25", fc=colors[i], ec="#ffffff22", lw=0.6), zorder=4)

        self.ax_pareto.set_xlabel("Cmax (temps en jours)", color="#cfeefc")
        self.ax_pareto.set_ylabel("Coût total", color="#cfeefc")
        self.ax_pareto.set_title("Frontière de Pareto (échantillonnage)", pad=14, fontsize=13, color="#9fe9ff")
        for spine in self.ax_pareto.spines.values():
            spine.set_color("#123033")
        self.ax_pareto.tick_params(colors="#9fb6c6")
        self.fig_pareto.tight_layout(pad=1.0)
        self.canvas_pareto.draw()
        self.progress.setValue(100)
        if solutions:
            self.pareto_list.setCurrentRow(len(solutions)//2)

    def on_pareto_error(self, msg):
        self.lbl_status.setText("Erreur")
        QMessageBox.critical(self, "Erreur solveur", msg)
        self.btn_run.setEnabled(True)
        self.progress.setValue(0)

    def on_select_solution(self, idx):
        if idx < 0 or idx >= len(self.solutions):
            return
        s = self.solutions[idx]
        starts = s.get("starts", {}); modes = s.get("modes_choice", {}); dur = s.get("durations", {})

        self.lbl_obj.setText(f"Objectif (raw): {s.get('objective_raw', '-'):.4f}")
        self.lbl_cmax.setText(f"Cmax: {s.get('Cmax', '-')}")
        self.lbl_coût.setText(f"Coût total: {s.get('total_coût', '-')}")

        rows = len(starts)
        self.result_table.setRowCount(rows)
        sd_txt = self.data.get("start_date", None)
        try:
            start_date = dt.datetime.strptime(sd_txt, "%Y-%m-%d").date() if sd_txt else dt.date.today()
        except Exception:
            start_date = dt.date.today()

        for r, tid in enumerate(sorted(starts.keys(), key=lambda x: starts[x])):
            self.result_table.setItem(r, 0, QTableWidgetItem(tid))
            self.result_table.setItem(r, 1, QTableWidgetItem(modes.get(tid, "")))
            st = int(starts[tid]); date_str = (start_date + dt.timedelta(days=st)).isoformat()
            self.result_table.setItem(r, 2, QTableWidgetItem(date_str))
            dval = dur.get(tid, "")
            display_d = "" if dval == "" else str(int(dval)) if isinstance(dval, (int, float)) else str(dval)
            self.result_table.setItem(r, 3, QTableWidgetItem(display_d))

        self.vars_table.setRowCount(0)
        row = 0
        for tid, st in sorted(starts.items(), key=lambda x: x[1]):
            mode_name = modes.get(tid, ""); m_idx = 0
            for tdef in self.data.get("tasks", []):
                if tdef.get("id") == tid:
                    for ii, mm in enumerate(tdef.get("modes", [])):
                        if mm.get("name") == mode_name:
                            m_idx = ii; break
            self.vars_table.insertRow(row)
            self.vars_table.setItem(row, 0, QTableWidgetItem(tid))
            self.vars_table.setItem(row, 1, QTableWidgetItem(str(m_idx)))
            self.vars_table.setItem(row, 2, QTableWidgetItem(str(st)))
            self.vars_table.setItem(row, 3, QTableWidgetItem("1"))
            row += 1

        # Gantt chart
        from matplotlib.patches import Patch
        self.ax_gantt.clear(); self.ax_gantt.set_facecolor("#0b1114")
        y = 0; yticks = []; ylabels = []
        sd_num = mdates.date2num(start_date)
        dates_bar_left = []; dates_bar_width = []
        mode_order = []
        for tid, _ in sorted(starts.items(), key=lambda x: x[1]):
            mode_name = modes.get(tid, "")
            if mode_name not in mode_order:
                mode_order.append(mode_name)
        palette = ["#7be0ff", "#ffb07b", "#7ed957", "#d291ff", "#ff6b6b", "#ffd166", "#61dafb", "#9ad3bc"]
        color_map = {m: palette[i % len(palette)] for i, m in enumerate(mode_order)}

        for tid, st in sorted(starts.items(), key=lambda x: x[1]):
            length = dur.get(tid, 0)
            try:
                length = int(length)
            except Exception:
                length = 0
            left_date = start_date + dt.timedelta(days=int(st)); left_num = mdates.date2num(left_date)
            mode_name = modes.get(tid, ""); color = color_map.get(mode_name, palette[0])
            self.ax_gantt.barh(y, length, left=left_num, height=0.6, color=color, edgecolor="#081219", linewidth=0.8, zorder=3)
            txt_x = left_num + max(0.5, length) / 2
            self.ax_gantt.text(txt_x, y, mode_name or "", va="center", ha="center", fontsize=9, color="#071012",
                               bbox=dict(boxstyle="round,pad=0.2", fc="#e6eef8", ec="#ffffff11", alpha=0.95), zorder=4)
            yticks.append(y); ylabels.append(tid); y += 1

        self.ax_gantt.set_yticks(yticks); self.ax_gantt.set_yticklabels(ylabels, color="#e6eef8"); self.ax_gantt.set_xlabel("Date", color="#cfeefc")
        self.ax_gantt.xaxis_date(); self.ax_gantt.xaxis.set_major_locator(mdates.AutoDateLocator()); self.ax_gantt.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        if yticks:
            lefts = [mdates.date2num(start_date + dt.timedelta(days=int(st))) for st in starts.values()]
            widths = [int(dur.get(tid, 0)) for tid in starts.keys()]
            if lefts and widths:
                left_min = min(lefts); right_max = max([l + w for l, w in zip(lefts, widths)])
                self.ax_gantt.set_xlim(left_min - 0.5, right_max + 0.5)
        self.ax_gantt.set_title(f"Gantt (Cmax={s.get('Cmax','-')}, coût={s.get('total_coût','-')})", color="#9fe9ff")
        for spine in self.ax_gantt.spines.values():
            spine.set_color("#123033")
        if mode_order:
            legend_patches = [Patch(facecolor=color_map[m], edgecolor="#081219", label=m) for m in mode_order]
            self.ax_gantt.legend(handles=legend_patches, bbox_to_anchor=(1.02, 1.0), loc='upper left', frameon=False, fontsize=9)
        self.fig_gantt.autofmt_xdate(rotation=30); self.fig_gantt.tight_layout(pad=1.0); self.canvas_gantt.draw()

# ---------------------------
def main():
    app = QApplication(sys.argv)
    try:
        app.setFont(QFont("Segoe UI", 10))
    except Exception:
        pass
    gui = ParetoSchedulerGUI(); gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
