from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import sys

from cliente.gui_login import VentanaLogin


def main():
    app = QApplication(sys.argv)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    ventana_login = VentanaLogin()
    ventana_login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()