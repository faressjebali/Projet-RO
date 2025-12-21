import sys
import subprocess
import threading
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QVBoxLayout, QLabel
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

# shared theme helper
from theme import apply_dark_theme


class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        # Window metadata
        self.setWindowTitle("Projet de Recherche Opérationnelle")
        self.setGeometry(300, 200, 600, 400)

        # apply shared theme
        try:
            apply_dark_theme(self)
        except Exception:
            pass

        # ----- Titre -----
        titre = QLabel("Projet de Recherche Opérationnelle")
        titre.setObjectName("mainTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        titre.setFont(title_font)
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # description under title
        description = QLabel(
            "Cette application permet d'accéder aux différentes\n"
            "applications développées pour les problèmes étudiés."
        )
        description.setObjectName("subtitle")
        description.setWordWrap(True)

        # ----- Boutons -----
        btn_p1 = QPushButton("Problème 1 - Planification des cultures et allocation des terres.")
        btn_p2 = QPushButton("Problème 2 - Ordonnancement des phases de développement de produits.")
        btn_p3 = QPushButton("Problème 3 – Planification du personnel en magasin par heure de la journée.")
        btn_p4 = QPushButton("Problème 4 - Maintenance: Affecter des techniciens spécialisés aux pannes.")
        btn_opti = QPushButton("Problème 5 - Approvisionnement: Transfert de matières premières entre sites de production")

        btn_p1.clicked.connect(lambda: self.launch_app("mehdi_pb1_app4/gui.py"))
        btn_p2.clicked.connect(lambda: self.launch_app("fares_pb18_app3/ihm_fares.py"))
        btn_p3.clicked.connect(lambda: self.launch_app("idriss_pb19_app3/ihm_supermarche.py"))
        btn_p4.clicked.connect(lambda: self.launch_app("rihab_pb3_app4/main.py"))
        btn_opti.clicked.connect(lambda: self.launch_app("khalil_pb2_app4/interface_approvisionnement.py"))

        # ----- Layout -----
        layout = QVBoxLayout()
        layout.addWidget(titre)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addWidget(btn_p1)
        layout.addWidget(btn_p2)
        layout.addWidget(btn_p3)
        layout.addWidget(btn_p4)
        layout.addWidget(btn_opti)

        self.setLayout(layout)

        # store running child process (if any)
        self._child_proc = None

    def launch_app(self, path, cwd=None):
        """Launch a child Python process. If cwd is provided, the process is started from that directory.

        This is important for apps (like OptiAppro) that import local modules by filename.
        """
        try:
            # Use the same Python executable as the launcher to keep environments consistent
            cmd = [sys.executable, path]
            if cwd:
                # Ensure cwd exists; if relative, make it relative to script location
                subprocess.Popen(cmd, cwd=os.path.abspath(cwd))
            else:
                subprocess.Popen(cmd)
        except Exception as e:
            print(f"Erreur lors du lancement : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
