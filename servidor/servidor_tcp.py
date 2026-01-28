"""
Servidor TCP con soporte para múltiples clientes usando threading.

Arquitectura:
  - Escucha en host/puerto configurado
  - Acepta conexiones y crea un hilo por cliente
  - Coordina acceso compartido al grafo con locks
  - Despacha operaciones según utils.protocolo

Uso:
    from servidor.servidor_tcp import ServidorTCP
    
    servidor = ServidorTCP(grafo=mi_grafo)
    servidor.iniciar()
    # ...
    servidor.detener()
"""

from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from grafo.grafo import Grafo
from utils.config import SERVER_HOST, SERVER_PORT, SOCKET_BACKLOG, SOCKET_BUFFER_SIZE
from utils.protocolo import (
    Message,
    Response,
    recv_message,
    send_response,
)


class ServidorTCPError(Exception):
    pass


@dataclass
class ClienteInfo:
    """Información de un cliente conectado."""
    conn: socket.socket
    addr: tuple[str, int]
    thread: threading.Thread
    usuario_logueado: Optional[str] = None


class ServidorTCP:
    """
    Servidor TCP que maneja múltiples clientes concurrentemente.
    
    Thread-safety:
      - self._lock protege acceso al grafo y estructura de clientes
      - Cada cliente tiene su propio thread
    """

    def __init__(
        self,
        grafo: Grafo,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
        on_log: Optional[Callable[[str], None]] = None,
    ):
        """
        Args:
            grafo: Instancia de Grafo (compartida entre threads)
            host: IP donde escuchar
            port: Puerto TCP
            on_log: Callback para logs (ej. para GUI)
        """
        self.grafo = grafo
        self.host = host
        self.port = port
        self.on_log = on_log or (lambda msg: print(f"[SERVER] {msg}"))

        self._socket: Optional[socket.socket] = None
        self._activo = False
        self._lock = threading.Lock()  # Protege grafo y clientes
        self._clientes: Dict[int, ClienteInfo] = {}  # id -> ClienteInfo
        self._contador_clientes = 0
        self._thread_aceptar: Optional[threading.Thread] = None

    def _log(self, mensaje: str) -> None:
        """Log seguro para threads."""
        if self.on_log:
            self.on_log(mensaje)

    # =========================
    # Ciclo de vida del servidor
    # =========================
    def iniciar(self) -> None:
        """
        Inicia el servidor TCP.
        Crea socket, bind, listen y lanza thread aceptador.
        """
        if self._activo:
            raise ServidorTCPError("El servidor ya está activo.")

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self.host, self.port))
            self._socket.listen(SOCKET_BACKLOG)
            self._activo = True

            self._log(f"[OK] Servidor iniciado en {self.host}:{self.port}")

            # Thread para aceptar conexiones
            self._thread_aceptar = threading.Thread(
                target=self._loop_aceptar_conexiones, daemon=True
            )
            self._thread_aceptar.start()

        except Exception as e:
            self._activo = False
            raise ServidorTCPError(f"Error al iniciar servidor: {e}") from e

    def detener(self) -> None:
        """
        Detiene el servidor y cierra todas las conexiones.
        """
        if not self._activo:
            return

        self._log("[STOP] Deteniendo servidor...")
        self._activo = False

        # Cerrar socket principal (rompe accept())
        if self._socket:
            try:
                self._socket.close()
            except:
                pass

        # Cerrar conexiones de clientes
        with self._lock:
            for cliente_id, info in list(self._clientes.items()):
                try:
                    info.conn.close()
                except:
                    pass
            self._clientes.clear()

        self._log("[OK] Servidor detenido")

    def esta_activo(self) -> bool:
        return self._activo

    # =========================
    # Loop principal: aceptar conexiones
    # =========================
    def _loop_aceptar_conexiones(self) -> None:
        """
        Loop que acepta conexiones entrantes y crea un thread por cliente.
        """
        while self._activo:
            try:
                conn, addr = self._socket.accept()
                if not self._activo:
                    conn.close()
                    break

                with self._lock:
                    self._contador_clientes += 1
                    cliente_id = self._contador_clientes

                self._log(f"[CONNECT] Cliente #{cliente_id} conectado desde {addr}")

                # Crear thread para manejar este cliente
                thread_cliente = threading.Thread(
                    target=self._manejar_cliente,
                    args=(cliente_id, conn, addr),
                    daemon=True,
                )
                thread_cliente.start()

                with self._lock:
                    self._clientes[cliente_id] = ClienteInfo(
                        conn=conn, addr=addr, thread=thread_cliente
                    )

            except OSError:
                # Socket cerrado (detener() fue llamado)
                break
            except Exception as e:
                if self._activo:
                    self._log(f"[ERROR] Error aceptando conexion: {e}")

    # =========================
    # Handler de cliente individual
    # =========================
    def _manejar_cliente(
        self, cliente_id: int, conn: socket.socket, addr: tuple[str, int]
    ) -> None:
        """
        Atiende las peticiones de un cliente en un loop hasta que se desconecta.
        Cada cliente corre en su propio thread independientemente.
        """
        try:
            while self._activo:
                try:
                    # Recibir mensaje del cliente
                    msg = recv_message(conn)
                    self._log(
                        f"[RECV] Cliente #{cliente_id}: {msg.type} | payload={msg.payload}"
                    )

                    # Placeholder: despacho real en bloques siguientes
                    respuesta = Response(
                        ok=True,
                        message=f"Tipo {msg.type} recibido (aun sin procesamiento)",
                        request_id=msg.request_id,
                    )

                    # Enviar respuesta
                    send_response(conn, respuesta)
                    self._log(f"[SEND] Cliente #{cliente_id}: respuesta enviada")

                except ConnectionError:
                    # Cliente desconectado (recv/send fallo)
                    break
                except Exception as e:
                    self._log(f"[WARN] Error procesando cliente #{cliente_id}: {e}")
                    # Intentar enviar error al cliente
                    try:
                        resp = Response(ok=False, message=f"Error interno: {e}")
                        send_response(conn, resp)
                    except:
                        pass
                    break

        finally:
            # Cleanup
            with self._lock:
                self._clientes.pop(cliente_id, None)
            try:
                conn.close()
            except:
                pass
            self._log(f"[DISCONNECT] Cliente #{cliente_id} desconectado")
