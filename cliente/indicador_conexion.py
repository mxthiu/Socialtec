# -*- coding: utf-8 -*-
"""
Widget que muestra el indicador de conexión con el servidor.

Componente visual para mostrar el estado de conexión en la GUI.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QColor
from cliente.connection_manager import ConnectionIndicator


class IndicadorConexion(QWidget):
    """
    Widget que muestra visualmente el estado de conexión con el servidor.

    Muestra:
    - Un círculo de color (verde = conectado, rojo = desconectado)
    - Texto del estado
    """

    def __init__(self, indicador: ConnectionIndicator, parent=None):
        super().__init__(parent)
        self.indicador = indicador
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Símbolo del estado
        self.label_simbolo = QLabel()
        self.label_simbolo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_simbolo.setFixedSize(20, 20)
        self.label_simbolo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Texto del estado
        self.label_texto = QLabel()
        self.label_texto.setFont(QFont("Arial", 9))
        self.label_texto.setMaximumWidth(150)
        self.label_texto.setWordWrap(False)

        layout.addWidget(self.label_simbolo)
        layout.addWidget(self.label_texto, 1)
        layout.addStretch()

        self.setLayout(layout)
        self.update_display()

    def update_display(self):
        """Actualiza la visualización según el estado actual"""
        connected, mensaje = self.indicador.get_status()
        color = self.indicador.get_color()
        icono = self.indicador.get_icon_text()

        # Actualizar símbolo con color
        self.label_simbolo.setText(icono)
        self.label_simbolo.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Actualizar texto
        if connected:
            self.label_texto.setText("En línea")
            self.label_texto.setStyleSheet("color: #00AA00; font-weight: bold;")
        else:
            self.label_texto.setText("Sin conexión")
            self.label_texto.setStyleSheet("color: #CC0000; font-weight: bold;")

        # Tooltip con más información
        self.setToolTip(mensaje)

    @pyqtSlot(bool, str)
    def on_connection_status_changed(self, connected: bool, mensaje: str):
        """
        Slot que se ejecuta cuando cambia el estado de conexión.

        Args:
            connected: True si conectado
            mensaje: Mensaje descriptivo
        """
        self.indicador.update(connected, mensaje)
        self.update_display()
