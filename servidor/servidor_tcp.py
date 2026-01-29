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
from servidor.autenticacion import (
    hash_password,
    verify_password,
    registrar_usuario_seguro,
    validar_login,
)
from servidor.persistencia import (
    cargar_usuarios,
    guardar_usuarios,
    agregar_amistad,
    eliminar_amistad,
    obtener_usuario,
    usuario_existe,
    obtener_estadisticas_globales,
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
            return self._handle_login(payload, msg.request_id)

        elif tipo == MsgType.REGISTER:
            return self._handle_register(payload, msg.request_id)

        # CHANGE_PASSWORD
        elif tipo == "CHANGE_PASSWORD":
            return self._handle_change_password(payload, msg.request_id)

        # CHANGE_PASSWORD_NO_VALIDATION (para recuperación por email)
        elif tipo == "CHANGE_PASSWORD_NO_VALIDATION":
            return self._handle_change_password_no_validation(payload, msg.request_id)

        # CHECK_USER (verificar disponibilidad de usuario)
        elif tipo == "CHECK_USER":
            return self._handle_check_user(payload, msg.request_id)

        # UPDATE_PROFILE
        elif tipo == "UPDATE_PROFILE":
            return self._handle_update_profile(payload, msg.request_id)

        # GET_EMAIL
        elif tipo == "GET_EMAIL":
            return self._handle_get_email(payload, msg.request_id)

        # GET_FRIENDS_COMPLETE
        elif tipo == "GET_FRIENDS_COMPLETE":
            return self._handle_get_friends_complete(payload, msg.request_id)

        # GET_ALL_USERS
        elif tipo == "GET_ALL_USERS":
            return self._handle_get_all_users(payload, msg.request_id)

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
        Busca usuarios por nombre, apellido o usuario (query).
        Payload: {"query": "..."}
        """
        query = payload.get("query", "").strip().lower()
        if not query:
            return Response(ok=False, message="Query vacía", request_id=request_id)

        usuarios = cargar_usuarios()
        resultados = []
        
        # Buscar en nombre, apellido y usuario
        for username, datos in usuarios.items():
            nombre = datos.get("nombre", "").lower()
            apellido = datos.get("apellido", "").lower()
            usuario = username.lower()
            
            if query in nombre or query in apellido or query in usuario:
                resultados.append({
                    "usuario": username,
                    "nombre": datos.get("nombre", ""),
                    "apellido": datos.get("apellido", ""),
                    "email": datos.get("email", ""),
                    "foto": datos.get("foto", ""),
                    "amigos": datos.get("amigos", [])
                })
        
        data = {
            "usuarios": resultados
        }

        return Response(
            ok=True, message="Búsqueda completada", data=data, request_id=request_id
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
        Payload: {"usuario1": "...", "usuario2": "..."}
        """
        usuario1 = payload.get("usuario1", "").strip()
        usuario2 = payload.get("usuario2", "").strip()

        if not usuario1 or not usuario2:
            return Response(
                ok=False, message="Faltan usernames", request_id=request_id
            )

        # Verificar que ambos usuarios existan
        if not usuario_existe(usuario1):
            return Response(
                ok=False, message=f"Usuario {usuario1} no existe", request_id=request_id
            )
        if not usuario_existe(usuario2):
            return Response(
                ok=False, message=f"Usuario {usuario2} no existe", request_id=request_id
            )

        # Agregar amistad en persistencia
        exito = agregar_amistad(usuario1, usuario2)
        if not exito:
            return Response(
                ok=False, message="No se pudo agregar amistad (ya son amigos)", request_id=request_id
            )

        self._log(f"[FRIEND] Amistad agregada: {usuario1} <-> {usuario2}")
        return Response(ok=True, message="Amistad agregada", request_id=request_id)

    def _handle_remove_friend(
        self, payload: dict, request_id: Optional[str]
    ) -> Response:
        """
        Elimina una amistad.
        Payload: {"usuario1": "...", "usuario2": "..."}
        """
        usuario1 = payload.get("usuario1", "").strip()
        usuario2 = payload.get("usuario2", "").strip()

        if not usuario1 or not usuario2:
            return Response(
                ok=False, message="Faltan usernames", request_id=request_id
            )

        # Eliminar de persistencia
        exito = eliminar_amistad(usuario1, usuario2)
        if not exito:
            return Response(ok=False, message="No son amigos", request_id=request_id)

        self._log(f"[FRIEND] Amistad eliminada: {usuario1} <-> {usuario2}")
        return Response(ok=True, message="Amistad eliminada", request_id=request_id)

    def _handle_get_stats(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Calcula estadisticas globales desde persistencia.
        Payload: {} (vacio)
        """
        # Obtener estadísticas del almacenamiento persistente (usuarios.json)
        stats = obtener_estadisticas_globales()
        
        # Retornar estructura como espera el cliente
        data = {
            "estadisticas": stats
        }

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

    def _handle_login(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Autentica un usuario.
        Payload: {"usuario": "...", "password": "..."}
        """
        usuario = payload.get("usuario", "").strip()
        password = payload.get("password", "").strip()

        if not usuario or not password:
            return Response(
                ok=False, message="Usuario y password requeridos", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()
            exito, mensaje = validar_login(usuario, password, usuarios_db)

        if not exito:
            return Response(ok=False, message=mensaje, request_id=request_id)

        # Obtener datos completos del usuario
        with self._lock:
            usuarios_db = cargar_usuarios()
            if usuario in usuarios_db:
                usuario_data = usuarios_db[usuario].copy()
                usuario_data.pop("password_hash", None)
            else:
                usuario_data = {}

        return Response(
            ok=True, 
            message="Login exitoso", 
            data={"usuario_data": usuario_data}, 
            request_id=request_id
        )

    def _handle_register(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Registra un nuevo usuario.
        Payload: {"usuario": "...", "password": "...", "nombre": "...", "apellido": "...", "email": "...", "foto": "..."}
        """
        usuario = payload.get("usuario", "").strip()
        password = payload.get("password", "").strip()
        nombre = payload.get("nombre", "").strip()
        apellido = payload.get("apellido", "").strip()
        email = payload.get("email", "").strip()
        foto = payload.get("foto", "").strip()

        if not usuario or not password:
            return Response(
                ok=False, message="Usuario y password requeridos", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()

            if usuario in usuarios_db:
                return Response(
                    ok=False, message="Usuario ya existe", request_id=request_id
                )

            nuevo_usuario = registrar_usuario_seguro(
                usuario=usuario,
                password=password,
                nombre=nombre,
                apellido=apellido,
            )
            
            # Agregar email y foto
            nuevo_usuario["email"] = email
            nuevo_usuario["foto"] = foto
            
            usuarios_db[usuario] = nuevo_usuario
            guardar_usuarios(usuarios_db)

        self._log(f"[REGISTER] Nuevo usuario registrado: {usuario}")
        return Response(
            ok=True, message="Usuario registrado", data={"usuario": usuario}, request_id=request_id
        )

    def _handle_change_password(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Cambia la contraseña verificando la contraseña actual.
        Payload: {"usuario": "...", "password_actual": "...", "password_nuevo": "..."}
        """
        usuario = payload.get("usuario", "").strip()
        password_actual = payload.get("password_actual", "").strip()
        password_nuevo = payload.get("password_nuevo", "").strip()

        if not usuario or not password_actual or not password_nuevo:
            return Response(
                ok=False, message="Datos incompletos", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()

            if usuario not in usuarios_db:
                return Response(
                    ok=False, message="Usuario no existe", request_id=request_id
                )

            # Verificar password actual
            hash_actual = usuarios_db[usuario].get("password_hash", "")
            if not verify_password(password_actual, hash_actual):
                return Response(
                    ok=False, message="Contraseña actual incorrecta", request_id=request_id
                )

            # Generar nuevo hash y actualizar
            nuevo_hash = hash_password(password_nuevo)
            usuarios_db[usuario]["password_hash"] = nuevo_hash
            guardar_usuarios(usuarios_db)

        self._log(f"[PASSWORD] Contraseña cambiada: {usuario}")
        return Response(
            ok=True, message="Contraseña cambiada exitosamente", request_id=request_id
        )

    def _handle_change_password_no_validation(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Cambia la contraseña sin verificar la actual (para recuperación por email).
        Payload: {"usuario": "...", "password_nuevo": "..."}
        """
        usuario = payload.get("usuario", "").strip()
        password_nuevo = payload.get("password_nuevo", "").strip()

        if not usuario or not password_nuevo:
            return Response(
                ok=False, message="Datos incompletos", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()

            if usuario not in usuarios_db:
                return Response(
                    ok=False, message="Usuario no existe", request_id=request_id
                )

            # Generar nuevo hash y actualizar
            nuevo_hash = hash_password(password_nuevo)
            usuarios_db[usuario]["password_hash"] = nuevo_hash
            guardar_usuarios(usuarios_db)

        self._log(f"[PASSWORD] Contraseña cambiada sin validación: {usuario}")
        return Response(
            ok=True, message="Contraseña cambiada exitosamente", request_id=request_id
        )

    def _handle_check_user(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Verifica si un usuario está disponible (no existe).
        Payload: {"usuario": "..."}
        """
        usuario = payload.get("usuario", "").strip()

        if not usuario:
            return Response(
                ok=False, message="Usuario requerido", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()
            disponible = usuario not in usuarios_db

        if disponible:
            return Response(
                ok=True, message="Usuario disponible", request_id=request_id
            )
        else:
            return Response(
                ok=False, message="Usuario no disponible", request_id=request_id
            )

    def _handle_update_profile(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Actualiza los datos del perfil de un usuario.
        Payload: {"usuario": "...", "datos": {...}}
        """
        usuario = payload.get("usuario", "").strip()
        datos = payload.get("datos", {})

        if not usuario:
            return Response(
                ok=False, message="Usuario requerido", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()

            if usuario not in usuarios_db:
                return Response(
                    ok=False, message="Usuario no existe", request_id=request_id
                )

            # Actualizar campos permitidos
            for campo in ["nombre", "apellido", "email", "foto"]:
                if campo in datos:
                    usuarios_db[usuario][campo] = datos[campo]

            guardar_usuarios(usuarios_db)

        self._log(f"[PROFILE] Perfil actualizado: {usuario}")
        return Response(
            ok=True, message="Perfil actualizado exitosamente", request_id=request_id
        )

    def _handle_get_email(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Obtiene el email de un usuario.
        Payload: {"usuario": "..."}
        """
        usuario = payload.get("usuario", "").strip()

        if not usuario:
            return Response(
                ok=False, message="Usuario requerido", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()

            if usuario not in usuarios_db:
                return Response(
                    ok=False, message="Usuario no existe", request_id=request_id
                )

            email = usuarios_db[usuario].get("email", "")

        return Response(
            ok=True, data={"email": email}, request_id=request_id
        )

    def _handle_get_friends_complete(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Obtiene los datos completos de una lista de usuarios.
        Payload: {"usernames": ["user1", "user2", ...]}
        """
        usernames = payload.get("usernames", [])

        if not isinstance(usernames, list):
            return Response(
                ok=False, message="Se requiere lista de usernames", request_id=request_id
            )

        with self._lock:
            usuarios_db = cargar_usuarios()
            amigos = []

            for username in usernames:
                if username in usuarios_db:
                    usuario_data = usuarios_db[username].copy()
                    # No enviar password_hash
                    usuario_data.pop("password_hash", None)
                    amigos.append(usuario_data)

        return Response(
            ok=True, data={"amigos": amigos}, request_id=request_id
        )

    def _handle_get_all_users(self, payload: dict, request_id: Optional[str]) -> Response:
        """
        Obtiene todos los usuarios (sin passwords).
        NOTA: Evitar usar en producción, solo para compatibilidad.
        Payload: {}
        """
        with self._lock:
            usuarios_db = cargar_usuarios()
            
            # Crear copia sin password_hash
            usuarios_sin_pass = {}
            for username, data in usuarios_db.items():
                user_copy = data.copy()
                user_copy.pop("password_hash", None)
                usuarios_sin_pass[username] = user_copy

        return Response(
            ok=True, data={"usuarios": usuarios_sin_pass}, request_id=request_id
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
