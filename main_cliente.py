# main_cliente.py - Punto de entrada del cliente SocialTec

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import sys

# Importar la ventana de login
from cliente.gui_login import VentanaLogin


def main():
    """Función principal del cliente"""
    app = QApplication(sys.argv)
    
    # Configurar fuente global para toda la aplicación
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    
    # Crear y mostrar la ventana de login
    ventana_login = VentanaLogin()
    ventana_login.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()