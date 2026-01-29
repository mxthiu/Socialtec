# -*- coding: utf-8 -*-
"""
Gestor de conexión a servidor.

Monitorea la disponibilidad del servidor TCP en segundo plano.
Emite señales PyQt cuando el estado de la conexión cambia.
"""

import socket
import threading
from typing import Callable, Optional
from PyQt6.QtCore import QThread, pyqtSignal

# Configuración del servidor
SERVER_HOST = "localhost"
SERVER_PORT = 5000
PING_INTERVAL = 5  # segundos
PING_TIMEOUT = 2  # segundos


class ConnectionManager(QThread):
    """
    Thread que monitorea la conexión con el servidor TCP.

    Señales:
        connection_status_changed: Emitida cuando cambia el estado
                                   (argumentos: bool connected, str mensaje)
    """

    connection_status_changed = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self._running = True
        self._connected = False
        self._lock = threading.Lock()
        self.daemon = True

    def run(self):
        """Inicia el monitoreo de conexión en loop"""
        while self._running:
            connected = self._check_server()

            with self._lock:
                if connected != self._connected:
                    self._connected = connected
                    status_msg = "Conectado al servidor" if connected else "Desconectado del servidor"
                    self.connection_status_changed.emit(connected, status_msg)

            # Esperar el intervalo antes de próxima verificación
            for _ in range(PING_INTERVAL):
                if not self._running:
                    break
                threading.Event().wait(1)

    def _check_server(self) -> bool:
        """
        Intenta conectarse al servidor para verificar disponibilidad.

        Returns:
            bool: True si el servidor responde, False si no
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(PING_TIMEOUT)
            sock.connect((SERVER_HOST, SERVER_PORT))
            sock.close()
            return True
        except (socket.error, socket.timeout, ConnectionRefusedError):
            return False

    def is_connected(self) -> bool:
        """
        Obtiene el estado actual de conexión.

        Returns:
            bool: True si está conectado, False si no
        """
        with self._lock:
            return self._connected

    def stop(self):
        """Detiene el monitoreo de conexión"""
        self._running = False


class ConnectionIndicator:
    """
    Indicador de conexión para mostrar en la GUI.

    Mantiene el estado actual y proporciona métodos para consultar.
    """

    def __init__(self):
        self.connected = False
        self.last_message = "Verificando conexión..."
        self._lock = threading.Lock()

    def update(self, connected: bool, mensaje: str):
        """
        Actualiza el estado de conexión.

        Args:
            connected: True si conectado, False si no
            mensaje: Mensaje descriptivo del estado
        """
        with self._lock:
            self.connected = connected
            self.last_message = mensaje

    def get_status(self) -> tuple:
        """
        Obtiene el estado actual.

        Returns:
            tuple: (bool connected, str mensaje)
        """
        with self._lock:
            return (self.connected, self.last_message)

    def get_color(self) -> str:
        """
        Obtiene el color del indicador según el estado.

        Returns:
            str: Color en formato hex (#00FF00 para conectado, #FF0000 para desconectado)
        """
        with self._lock:
            return "#00FF00" if self.connected else "#FF0000"

    def get_icon_text(self) -> str:
        """
        Obtiene el símbolo para mostrar.

        Returns:
            str: "●" para conectado, "○" para desconectado
        """
        with self._lock:
            return "●" if self.connected else "○"
