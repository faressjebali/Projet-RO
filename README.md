# Operations Research Project — five optimization apps

**Five real-world planning problems modeled as linear / integer programs, solved with Gurobi, each with its own desktop interface, gathered in one launcher.**

Group project for the *Operations Research* course at INSAT (2025-2026). Each team member modeled and built one problem; the launcher (`app.py`) opens them all.

| # | Problem | Model | Author |
|---|---|---|---|
| 1 | Crop planning and land allocation | LP / ILP / MILP, profit maximization under land, water, labor and budget constraints | Mehdi |
| 2 | **Multi-mode R&D project scheduling** — choosing how to run each development phase, with a **Pareto front** between duration and cost | MILP, multi-objective | **Fares Jebali** |
| 3 | Hourly staff planning in a supermarket | ILP | Idriss |
| 4 | Assigning specialized technicians to maintenance breakdowns | ILP | Rihab |
| 5 | Raw-material transfers between production sites (cost minimization) | LP | Khalil |

## My part: multi-mode R&D scheduling (`fares_pb18_app3/`)

- Each development phase can run in several modes (e.g. *normal* or *fast*: shorter but more engineers and more budget), under precedence constraints, renewable resources (machines, technicians, engineers) and a non-renewable R&D budget.
- Time-indexed MILP solved with Gurobi; the app computes the **trade-off between total duration and total cost** and displays the **Pareto front**, so the decision-maker picks a schedule instead of getting a single answer.
- When the model is infeasible, the app explains why (resources, horizon, precedences).
- PyQt6 interface: editable phases and modes, solving in a background thread, charts with Matplotlib.

## Stack

Python · Gurobi (`gurobipy`) · PyQt6 / PySide6 / Tkinter · Matplotlib

## Run it

A Gurobi license is required (free academic license on [gurobi.com](https://www.gurobi.com/academia/)).

```bash
pip install gurobipy PyQt6 matplotlib
python app.py          # launcher with the five problems
```

Some apps have their own `requirements.txt` and README in their folder.
