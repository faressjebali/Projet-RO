# -*- coding: utf-8 -*-
"""
Point d'entrée de l'application
"""

import sys
from PySide6.QtWidgets import QApplication
from interface import PerfectMaintenanceApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PerfectMaintenanceApp()
    window.show()
    sys.exit(app.exec())