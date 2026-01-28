"""
Servidor TCP con soporte para multiples clientes usando threading.

Arquitectura:
  - Escucha en host/puerto configurado
  - Acepta conexiones y crea un hilo por cliente
  - Coordina acceso compartido al grafo con locks
  - Despacha operaciones segun utils.protocolo

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
from grafo.algoritmos import (
    encontrar_camino_bfs,
    calcular_estadisticas,
    estadisticas_como_dict,
)
from utils.config import SERVER_HOST, SERVER_PORT, SOCKET_BACKLOG, SOCKET_BUFFER_SIZE
from utils.protocolo import (
    Message,
    Response,
    recv_message,
    send_response,
    MsgType,
)


class ServidorTCPError(Exception):
    pass


@dataclass
class ClienteInfo:
    """Informacion de un cliente conectado."""
    conn: socket.socket
    addr: tuple[str, int]
    thread: threading.Thread
    usuario_logueado: Optional[str] = None


class ServidorTCP:
    """
    Servidor TCP que maneja multiples clientes concurrentemente.
    
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
            raise ServidorTCPError("El servidor ya esta activo.")

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
        Atiende las peticiones de un cliente hasta que se desconecta.
        """
        try:
            while self._activo:
                try:
                    # Recibir mensaje
                    msg = recv_message(conn)
                    self._log(
                        f"[RECV] Cliente #{cliente_id}: {msg.type} | payload={msg.payload}"
                    )

                    # Despachar segun tipo
                    respuesta = self._despachar_mensaje(cliente_id, msg)

                    # Enviar respuesta
                    send_response(conn, respuesta)

                except ConnectionError:
                    # Cliente desconectado
                    break
                except Exception as e:
                    self._log(f"[WARN] Error procesando mensaje de #{cliente_id}: {e}")
                    resp = Response(ok=False, message=f"Error interno: {e}")
                    try:
                        send_response(conn, resp)
                    except:
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

    # =========================
    # Despachador de mensajes
    # =========================
    def _despachar_mensaje(self, cliente_id: int, msg: Message) -> Response:
        """
        Procesa un mensaje y retorna la respuesta correspondiente.
        """
        tipo = msg.type
        payload = msg.payload

        # PING (health check)
        if tipo == MsgType.PING:
            return Response(ok=True, message="PONG", request_id=msg.request_id)

        # SEARCH_USER
        elif tipo == MsgType.SEARCH_USER:
            return self._handle_search_user(payload, msg.request_id)

        # GET_PROFILE
        elif tipo == MsgType.GET_PROFILE:
            return self._handle_get_profile(payload, msg.request_id)

        # ADD_FRIEND
        elif tipo == MsgType.ADD_FRIEND:
            return self._handle_add_friend(payload, msg.request_id)

        # REMOVE_FRIEND
        elif tipo == MsgType.REMOVE_FRIEND:
            return self._handle_remove_friend(payload, msg.request_id)

        # GET_STATS
        elif tipo == MsgType.GET_STATS:
            return self._handle_get_stats(payload, msg.request_id)

        # GET_PATH
        elif tipo == MsgType.GET_PATH:
            return self._handle_get_path(payload, msg.request_id)

        # LOGIN / REGISTER (delegado a autenticacion.py en rama 9)
        elif tipo == MsgType.LOGIN:
            return Response(
                ok=False,
                message="LOGIN no implementado aun (rama 9)",
                request_id=msg.request_id,
            )

        elif tipo == MsgType.REGISTER:
            return Response(
                ok=False,
                message="REGISTER no implementado aun (rama 9)",
                request_id=msg.request_id,
            )

        else:
            return Response(
                ok=False,
                message=f"Tipo de mensaje desconocido: {tipo}",
                request_id=msg.request_id,
            )

    # =========================
    # Handlers especificos
    # =========================
    def _handle_search_user(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Busca un usuario por username.
        Payload: {"username": "..."}
        """
        username = payload.get("username", "").strip()
        if not username:
            return Response(ok=False, message="Username vacio", request_id=request_id)

        with self._lock:
            usuario = self.grafo.buscar_usuario(username)
            if not usuario:
                return Response(
                    ok=False, message="Usuario no encontrado", request_id=request_id
                )
            
            amigos = self.grafo.obtener_amigos(username)
            data = {
                "username": username,
                "amigos": amigos,
            }

        return Response(
            ok=True, message="Usuario encontrado", data=data, request_id=request_id
        )

    def _handle_get_profile(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Obtiene perfil completo de un usuario.
        Payload: {"username": "..."}
        """
        # Mismo que search_user por ahora
        return self._handle_search_user(payload, request_id)

    def _handle_add_friend(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Agrega una amistad entre dos usuarios.
        Payload: {"user1": "...", "user2": "..."}
        """
        user1 = payload.get("user1", "").strip()
        user2 = payload.get("user2", "").strip()

        if not user1 or not user2:
            return Response(
                ok=False, message="Faltan usernames", request_id=request_id
            )

        with self._lock:
            # Verificar que ambos usuarios existan
            if not self.grafo.buscar_usuario(user1):
                return Response(
                    ok=False, message=f"Usuario {user1} no existe", request_id=request_id
                )
            if not self.grafo.buscar_usuario(user2):
                return Response(
                    ok=False, message=f"Usuario {user2} no existe", request_id=request_id
                )

            # Agregar amistad
            exito = self.grafo.agregar_amistad(user1, user2)
            if not exito:
                return Response(
                    ok=False, message="No se pudo agregar amistad", request_id=request_id
                )

        self._log(f"[FRIEND] Amistad agregada: {user1} <-> {user2}")
        return Response(ok=True, message="Amistad agregada", request_id=request_id)

    def _handle_remove_friend(
        self, payload: dict, request_id: Optional[str]
    ) -> Response:
        """
        Elimina una amistad.
        Payload: {"user1": "...", "user2": "..."}
        """
        user1 = payload.get("user1", "").strip()
        user2 = payload.get("user2", "").strip()

        if not user1 or not user2:
            return Response(
                ok=False, message="Faltan usernames", request_id=request_id
            )

        with self._lock:
            exito = self.grafo.eliminar_amistad(user1, user2)
            if not exito:
                return Response(ok=False, message="No son amigos", request_id=request_id)

        self._log(f"[FRIEND] Amistad eliminada: {user1} <-> {user2}")
        return Response(ok=True, message="Amistad eliminada", request_id=request_id)

    def _handle_get_stats(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Calcula estadisticas del grafo.
        Payload: {} (vacio)
        """
        with self._lock:
            stats = calcular_estadisticas(self.grafo)
            data = estadisticas_como_dict(stats)

        return Response(
            ok=True, message="Estadisticas calculadas", data=data, request_id=request_id
        )

    def _handle_get_path(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Encuentra camino entre dos usuarios (BFS).
        Payload: {"inicio": "...", "fin": "..."}
        """
        inicio = payload.get("inicio", "").strip()
        fin = payload.get("fin", "").strip()

        if not inicio or not fin:
            return Response(
                ok=False, message="Faltan inicio/fin", request_id=request_id
            )

        with self._lock:
            camino = encontrar_camino_bfs(self.grafo, inicio, fin)

        if camino is None:
            return Response(
                ok=False,
                message=f"No existe camino entre {inicio} y {fin}",
                request_id=request_id,
            )

        return Response(
            ok=True,
            message=f"Camino encontrado ({len(camino)} saltos)",
            data={"camino": camino},
            request_id=request_id,
        )

    # =========================
    # Utilidades
    # =========================
    def obtener_info_clientes(self) -> list[dict]:
        """
        Devuelve lista de clientes conectados (para GUI).
        """
        with self._lock:
            return [
                {
                    "id": cid,
                    "addr": f"{info.addr[0]}:{info.addr[1]}",
                    "usuario": info.usuario_logueado or "No logueado",
                }
                for cid, info in self._clientes.items()
            ]
