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
    connection_status_changed = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self._running = True
        self._connected = False
        self._lock = threading.Lock()
        self.daemon = True

    def run(self):
        while self._running:
            connected = self._check_server()

            with self._lock:
                if connected != self._connected:
                    self._connected = connected
                    status_msg = "Conectado al servidor" if connected else "Desconectado del servidor"
                    self.connection_status_changed.emit(connected, status_msg)

            for _ in range(PING_INTERVAL):
                if not self._running:
                    break
                threading.Event().wait(1)

    def _check_server(self) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(PING_TIMEOUT)
            sock.connect((SERVER_HOST, SERVER_PORT))
            sock.close()
            return True
        except (socket.error, socket.timeout, ConnectionRefusedError):
            return False

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def stop(self):
        self._running = False


class ConnectionIndicator:
    
    def __init__(self):
        self.connected = False
        self.last_message = "Verificando conexión..."
        self._lock = threading.Lock()

    def update(self, connected: bool, mensaje: str):
        with self._lock:
            self.connected = connected
            self.last_message = mensaje

    def get_status(self) -> tuple:
        with self._lock:
            return (self.connected, self.last_message)

    def get_color(self) -> str:
        with self._lock:
            return "#00FF00" if self.connected else "#FF0000"

    def get_icon_text(self) -> str:
        with self._lock:
            return "●" if self.connected else "○"
