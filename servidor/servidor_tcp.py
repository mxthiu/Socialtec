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
from typing import Any, Callable, Dict, List, Optional

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
        on_client_connect: Optional[Callable[[int, str], None]] = None,
        on_client_disconnect: Optional[Callable[[int], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Args:
            grafo: Instancia de Grafo (compartida entre threads)
            host: IP donde escuchar
            port: Puerto TCP
            on_log: Callback para logs (ej. para GUI)
            on_client_connect: Callback(cliente_id, addr) al conectar cliente
            on_client_disconnect: Callback(cliente_id) al desconectar cliente
            on_error: Callback(error_msg) al ocurrir error
        """
        self.grafo = grafo
        self.host = host
        self.port = port
        self.on_log = on_log or (lambda msg: print(f"[SERVER] {msg}"))
        self.on_client_connect = on_client_connect
        self.on_client_disconnect = on_client_disconnect
        self.on_error = on_error

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
    # ACCESO THREAD-SAFE AL GRAFO
    # =========================

    def _acceso_grafo_seguro(self, operacion: Callable[[], Any]) -> Any:
        """
        Wrapper thread-safe para operaciones sobre el grafo compartido.
        Uso: resultado = self._acceso_grafo_seguro(lambda: self.grafo.buscar_usuario("X"))
        
        Args:
            operacion: Función sin argumentos que accede al grafo
        
        Returns:
            Resultado de la operación
        """
        with self._lock:
            return operacion()

    def _grafo_buscar_usuario(self, username: str) -> Optional[Dict]:
        """Thread-safe: buscar usuario en el grafo."""
        with self._lock:
            return self.grafo.buscar_usuario(username)

    def _grafo_agregar_amistad(self, user1: str, user2: str) -> bool:
        """Thread-safe: agregar amistad en el grafo."""
        with self._lock:
            return self.grafo.agregar_amistad(user1, user2)

    def _grafo_eliminar_amistad(self, user1: str, user2: str) -> bool:
        """Thread-safe: eliminar amistad en el grafo."""
        with self._lock:
            return self.grafo.eliminar_amistad(user1, user2)

    def _grafo_obtener_estadisticas(self, username: str) -> Optional[Dict]:
        """Thread-safe: obtener estadisticas de un usuario."""
        with self._lock:
            # Asume que tenemos una funcion en grafo o algoritmos
            usuario = self.grafo.buscar_usuario(username)
            if not usuario:
                return None
            # Calcular estadisticas basicas
            amigos = self.grafo.obtener_amigos(username)
            return {
                "username": username,
                "num_amigos": len(amigos),
                "amigos": amigos,
            }

    def _grafo_encontrar_camino(self, origen: str, destino: str) -> Optional[List[str]]:
        """Thread-safe: encontrar camino entre dos usuarios."""
        with self._lock:
            # Importar algoritmo si es necesario
            from grafo.algoritmos import encontrar_camino_bfs
            return encontrar_camino_bfs(self.grafo, origen, destino)

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
                
                # Callback: cliente conectado
                if self.on_client_connect:
                    self.on_client_connect(cliente_id, addr[0])

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
                    msg_error = f"Error aceptando conexion: {e}"
                    self._log(f"[ERROR] {msg_error}")
                    if self.on_error:
                        self.on_error(msg_error)

    # =========================
    # DESPACHO DE MENSAJES
    # =========================
    def _despachar_mensaje(self, msg: Message, cliente_id: int) -> Response:
        """
        Despacha el mensaje recibido al handler correspondiente.
        
        Args:
            msg: Mensaje recibido del cliente
            cliente_id: ID del cliente que envió el mensaje
        
        Returns:
            Response a enviar al cliente
        """
        try:
            # PING - health check
            if msg.type == "PING":
                return self._handle_ping(msg)
            
            # Operaciones de grafo
            elif msg.type == "SEARCH_USER":
                return self._handle_search_user(msg)
            elif msg.type == "ADD_FRIEND":
                return self._handle_add_friend(msg)
            elif msg.type == "REMOVE_FRIEND":
                return self._handle_remove_friend(msg)
            elif msg.type == "GET_STATS":
                return self._handle_get_stats(msg)
            elif msg.type == "GET_PATH":
                return self._handle_get_path(msg)
            
            # Autenticacion (rama 9 - stubs por ahora)
            elif msg.type == "LOGIN":
                return Response(
                    ok=False,
                    message="LOGIN no implementado aun (rama 9 en progreso)",
                    request_id=msg.request_id,
                )
            elif msg.type == "REGISTER":
                return Response(
                    ok=False,
                    message="REGISTER no implementado aun (rama 9 en progreso)",
                    request_id=msg.request_id,
                )
            
            # Tipo desconocido
            else:
                return Response(
                    ok=False,
                    message=f"Tipo de mensaje desconocido: {msg.type}",
                    request_id=msg.request_id,
                )
        
        except Exception as e:
            self._log(f"[ERROR] Error despachando {msg.type}: {e}")
            if self.on_error:
                self.on_error(f"Error despachando {msg.type}: {e}")
            return Response(
                ok=False,
                message=f"Error procesando {msg.type}: {str(e)}",
                request_id=msg.request_id,
            )

    def _handle_ping(self, msg: Message) -> Response:
        """Handler para PING - health check."""
        return Response(
            ok=True,
            message="PONG",
            request_id=msg.request_id,
        )

    def _handle_search_user(self, msg: Message) -> Response:
        """
        Handler para SEARCH_USER.
        Payload esperado: {"username": str}
        """
        username = msg.payload.get("username")
        if not username:
            return Response(
                ok=False,
                message="Falta parametro 'username'",
                request_id=msg.request_id,
            )
        
        usuario = self._grafo_buscar_usuario(username)
        if usuario:
            return Response(
                ok=True,
                message="Usuario encontrado",
                data=usuario,
                request_id=msg.request_id,
            )
        else:
            return Response(
                ok=False,
                message=f"Usuario '{username}' no encontrado",
                request_id=msg.request_id,
            )

    def _handle_add_friend(self, msg: Message) -> Response:
        """
        Handler para ADD_FRIEND.
        Payload esperado: {"user1": str, "user2": str}
        """
        user1 = msg.payload.get("user1")
        user2 = msg.payload.get("user2")
        
        if not user1 or not user2:
            return Response(
                ok=False,
                message="Faltan parametros 'user1' o 'user2'",
                request_id=msg.request_id,
            )
        
        exito = self._grafo_agregar_amistad(user1, user2)
        if exito:
            return Response(
                ok=True,
                message=f"Amistad agregada: {user1} <-> {user2}",
                request_id=msg.request_id,
            )
        else:
            return Response(
                ok=False,
                message=f"No se pudo agregar amistad (usuarios no existen?)",
                request_id=msg.request_id,
            )

    def _handle_remove_friend(self, msg: Message) -> Response:
        """
        Handler para REMOVE_FRIEND.
        Payload esperado: {"user1": str, "user2": str}
        """
        user1 = msg.payload.get("user1")
        user2 = msg.payload.get("user2")
        
        if not user1 or not user2:
            return Response(
                ok=False,
                message="Faltan parametros 'user1' o 'user2'",
                request_id=msg.request_id,
            )
        
        exito = self._grafo_eliminar_amistad(user1, user2)
        if exito:
            return Response(
                ok=True,
                message=f"Amistad eliminada: {user1} <-> {user2}",
                request_id=msg.request_id,
            )
        else:
            return Response(
                ok=False,
                message=f"No se pudo eliminar amistad (no existe?)",
                request_id=msg.request_id,
            )

    def _handle_get_stats(self, msg: Message) -> Response:
        """
        Handler para GET_STATS.
        Payload esperado: {"username": str}
        """
        username = msg.payload.get("username")
        if not username:
            return Response(
                ok=False,
                message="Falta parametro 'username'",
                request_id=msg.request_id,
            )
        
        stats = self._grafo_obtener_estadisticas(username)
        if stats:
            return Response(
                ok=True,
                message="Estadisticas obtenidas",
                data=stats,
                request_id=msg.request_id,
            )
        else:
            return Response(
                ok=False,
                message=f"Usuario '{username}' no encontrado",
                request_id=msg.request_id,
            )

    def _handle_get_path(self, msg: Message) -> Response:
        """
        Handler para GET_PATH.
        Payload esperado: {"origen": str, "destino": str}
        """
        origen = msg.payload.get("origen")
        destino = msg.payload.get("destino")
        
        if not origen or not destino:
            return Response(
                ok=False,
                message="Faltan parametros 'origen' o 'destino'",
                request_id=msg.request_id,
            )
        
        camino = self._grafo_encontrar_camino(origen, destino)
        if camino:
            return Response(
                ok=True,
                message=f"Camino encontrado ({len(camino)} nodos)",
                data={"camino": camino},
                request_id=msg.request_id,
            )
        else:
            return Response(
                ok=False,
                message=f"No existe camino entre '{origen}' y '{destino}'",
                request_id=msg.request_id,
            )

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

                    # Despachar mensaje según tipo
                    respuesta = self._despachar_mensaje(msg, cliente_id)

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
            
            # Callback: cliente desconectado
            if self.on_client_disconnect:
                self.on_client_disconnect(cliente_id)
