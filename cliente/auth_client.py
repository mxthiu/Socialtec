"""
Cliente de autenticación - Adaptador para servidor TCP

Este módulo actúa como intermediario entre la GUI y el servidor de autenticación.
Usa comunicación TCP con el servidor para todas las operaciones de autenticación.

SEGURIDAD:
==========
- Los passwords NUNCA se almacenan ni transmiten en texto plano
- Hashing seguro con Argon2 (servidor.autenticacion)
- Encriptación AES-GCM en tránsito (utils.crypto)
- Protocolos de mensaje estandarizados (utils.protocolo)
"""

import socket
import logging
from typing import Tuple, Dict, Optional, Any

from utils.protocolo import Message, Response, MsgType, send_message, recv_response, send_message_encrypted

# Logger
logger = logging.getLogger(__name__)

# Configuración del servidor
SERVER_HOST = "localhost"
SERVER_PORT = 5000
CONNECT_TIMEOUT = 5  # segundos


def login_usuario(usuario: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Intenta iniciar sesión con las credenciales proporcionadas.

    Comunica con el servidor TCP para validar credenciales.

    SEGURIDAD:
    - El password se verifica contra hash Argon2 en el servidor
    - NUNCA se compara password en texto plano
    - El hash se genera/verifica con passlib (servidor.autenticacion)
    - Comunicación encriptada AES-GCM (utils.crypto)

    Args:
        usuario: Nombre de usuario
        password: Contraseña en texto plano

    Returns:
        tuple: (exito: bool, datos_usuario: dict | None)
               - Si éxito: (True, {usuario, nombre, apellido, email, foto, amigos})
               - Si fallo: (False, None)
    """
    try:
        # Crear mensaje de LOGIN
        msg = Message(
            type=MsgType.LOGIN,
            payload={
                "usuario": usuario,
                "password": password
            }
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            datos = respuesta.data.get("usuario_data", {})
            return (True, datos)
        else:
            logger.warning(f"Login fallido: {respuesta.message}")
            return (False, None)

    except Exception as e:
        logger.error(f"Error en login_usuario: {e}")
        return (False, None)


def registrar_usuario(
    usuario: str,
    password: str,
    nombre: str,
    apellido: str,
    email: str,
    foto: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Registra un nuevo usuario en el sistema a través del servidor TCP.

    SEGURIDAD:
    - El password se hashea con Argon2 en el servidor
    - NUNCA se almacena password en texto plano
    - El hash es generado por passlib (servidor.autenticacion)

    Args:
        usuario: Nombre de usuario único
        password: Contraseña en texto plano (se hasheará)
        nombre: Nombre real
        apellido: Apellido
        email: Email
        foto: Path opcional a foto de perfil

    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # Crear mensaje de REGISTER
        msg = Message(
            type=MsgType.REGISTER,
            payload={
                "usuario": usuario,
                "password": password,
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "foto": foto or ""
            }
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        return (respuesta.ok, respuesta.message)

    except Exception as e:
        logger.error(f"Error en registrar_usuario: {e}")
        return (False, f"Error al registrar: {str(e)}")


def cambiar_password_usuario(
    usuario: str,
    password_actual: str,
    password_nuevo: str
) -> Tuple[bool, str]:
    """
    Cambia la contraseña de un usuario a través del servidor TCP.

    SEGURIDAD:
    - Verifica password_actual contra hash Argon2 en servidor
    - Genera nuevo hash Argon2 para password_nuevo
    - Todo manejado por passlib (servidor.autenticacion)

    Args:
        usuario: Nombre de usuario
        password_actual: Contraseña actual (se verificará contra hash)
        password_nuevo: Nueva contraseña (se hasheará)

    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # Crear mensaje de CHANGE_PASSWORD
        msg = Message(
            type="CHANGE_PASSWORD",
            payload={
                "usuario": usuario,
                "password_actual": password_actual,
                "password_nuevo": password_nuevo
            }
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        return (respuesta.ok, respuesta.message)

    except Exception as e:
        logger.error(f"Error en cambiar_password_usuario: {e}")
        return (False, f"Error al cambiar contraseña: {str(e)}")


def verificar_disponibilidad_usuario(usuario: str) -> bool:
    """
    Verifica si un nombre de usuario está disponible.

    Args:
        usuario: Nombre de usuario a verificar

    Returns:
        bool: True si está disponible, False si ya existe

    """
    try:
        # Crear mensaje de CHECK_USER
        msg = Message(
            type="CHECK_USER",
            payload={"usuario": usuario}
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        return respuesta.ok

    except Exception as e:
        logger.error(f"Error en verificar_disponibilidad_usuario: {e}")
        return False


# ==============================================
# Función auxiliar para comunicación TCP
# ==============================================

def _enviar_solicitud_tcp(mensaje: Message) -> Response:
    """
    Envía un mensaje al servidor TCP y recibe la respuesta.

    SEGURIDAD:
    - Crea conexión TCP al servidor
    - Usa protocolo de framing length-prefix para mensajes
    - Encripta payloads sensibles (LOGIN, REGISTER) con AES-GCM
    - Manejo seguro de excepciones de conexión

    Args:
        mensaje: Objeto Message con type y payload

    Returns:
        Response: Respuesta del servidor con ok, message, data

    Raises:
        ConnectionError: Si no puede conectarse al servidor
        socket.timeout: Si la conexión se agota
    """
    try:
        # Crear socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONNECT_TIMEOUT)

        # Conectar al servidor
        sock.connect((SERVER_HOST, SERVER_PORT))
        logger.debug(f"Conectado a servidor {SERVER_HOST}:{SERVER_PORT}")

        # Enviar mensaje - usar encriptación para LOGIN y REGISTER
        if mensaje.type in [MsgType.LOGIN, MsgType.REGISTER]:
            send_message_encrypted(sock, mensaje)
            logger.debug(f"Mensaje encriptado enviado: {mensaje.type}")
        else:
            send_message(sock, mensaje)
            logger.debug(f"Mensaje enviado: {mensaje.type}")

        # Recibir respuesta
        respuesta = recv_response(sock)
        logger.debug(f"Respuesta recibida: {respuesta.message}")

        # Cerrar conexión
        sock.close()

        return respuesta

    except socket.timeout:
        logger.error(f"Timeout conectando a {SERVER_HOST}:{SERVER_PORT}")
        return Response(
            ok=False,
            message=f"No se pudo conectar al servidor (timeout después de {CONNECT_TIMEOUT}s)"
        )
    except ConnectionRefusedError:
        logger.error(f"Conexión rechazada por {SERVER_HOST}:{SERVER_PORT}")
        return Response(
            ok=False,
            message="No se pudo conectar al servidor (conexión rechazada)"
        )
    except ConnectionError as e:
        logger.error(f"Error de conexión: {e}")
        return Response(
            ok=False,
            message=f"Error de conexión: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado en TCP: {e}")
        return Response(
            ok=False,
            message=f"Error inesperado: {str(e)}"
        )


def cambiar_password_sin_validar(usuario: str, password_nuevo: str) -> Tuple[bool, str]:
    """
    Cambia la contraseña sin validar la contraseña actual.

    Usado para recuperación de contraseña por correo electrónico.
    Verifica primero que el usuario exista antes de cambiar.

    Args:
        usuario: Nombre de usuario
        password_nuevo: Nueva contraseña

    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # Crear mensaje con comando especial
        msg = Message(
            type="CHANGE_PASSWORD_NO_VALIDATION",
            payload={
                "usuario": usuario,
                "password_nuevo": password_nuevo
            }
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        return (respuesta.ok, respuesta.message)

    except Exception as e:
        logger.error(f"Error en cambiar_password_sin_validar: {e}")
        return (False, f"Error al cambiar contraseña: {str(e)}")


def agregar_amistad(usuario1: str, usuario2: str) -> Tuple[bool, str]:
    """
    Agrega una amistad bidireccional entre dos usuarios a través del servidor TCP.

    Args:
        usuario1: Nombre de usuario 1
        usuario2: Nombre de usuario 2

    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # Crear mensaje de ADD_FRIEND
        msg = Message(
            type=MsgType.ADD_FRIEND,
            payload={
                "usuario1": usuario1,
                "usuario2": usuario2
            }
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        return (respuesta.ok, respuesta.message)

    except Exception as e:
        logger.error(f"Error en agregar_amistad: {e}")
        return (False, f"Error al agregar amistad: {str(e)}")


def eliminar_amistad(usuario1: str, usuario2: str) -> Tuple[bool, str]:
    """
    Elimina una amistad bidireccional entre dos usuarios a través del servidor TCP.

    Args:
        usuario1: Nombre de usuario 1
        usuario2: Nombre de usuario 2

    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # Crear mensaje de REMOVE_FRIEND
        msg = Message(
            type=MsgType.REMOVE_FRIEND,
            payload={
                "usuario1": usuario1,
                "usuario2": usuario2
            }
        )

        # Enviar a servidor
        respuesta = _enviar_solicitud_tcp(msg)

        return (respuesta.ok, respuesta.message)

    except Exception as e:
        logger.error(f"Error en eliminar_amistad: {e}")
        return (False, f"Error al eliminar amistad: {str(e)}")


def buscar_usuarios(query: str) -> list:
    """
    Busca usuarios por nombre, apellido o usuario.

    Args:
        query: Texto de búsqueda

    Returns:
        list: Lista de usuarios que coinciden con la búsqueda
    """
    try:
        msg = Message(
            type=MsgType.SEARCH_USER,
            payload={"query": query}
        )

        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            return respuesta.data.get("usuarios", [])
        else:
            return []

    except Exception as e:
        logger.error(f"Error en buscar_usuarios: {e}")
        return []


def obtener_usuario_completo(usuario: str) -> Optional[Dict]:
    """
    Obtiene los datos completos de un usuario incluyendo amigos.

    Args:
        usuario: Nombre de usuario

    Returns:
        dict: Datos completos del usuario o None
    """
    try:
        msg = Message(
            type=MsgType.GET_PROFILE,
            payload={"usuario": usuario}
        )

        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            return respuesta.data.get("usuario_data", {})
        else:
            return None

    except Exception as e:
        logger.error(f"Error en obtener_usuario_completo: {e}")
        return None


def obtener_amigos_completos(lista_usernames: list) -> list:
    """
    Obtiene los datos completos de una lista de usuarios.

    Args:
        lista_usernames: Lista de nombres de usuario

    Returns:
        list: Lista de diccionarios con datos de usuarios
    """
    try:
        msg = Message(
            type="GET_FRIENDS_COMPLETE",
            payload={"usernames": lista_usernames}
        )

        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            return respuesta.data.get("amigos", [])
        else:
            return []

    except Exception as e:
        logger.error(f"Error en obtener_amigos_completos: {e}")
        return []


def actualizar_perfil(usuario: str, datos: Dict) -> Tuple[bool, str]:
    """
    Actualiza los datos del perfil de un usuario.

    Args:
        usuario: Nombre de usuario
        datos: Dict con campos a actualizar (nombre, apellido, email, foto)

    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        msg = Message(
            type="UPDATE_PROFILE",
            payload={
                "usuario": usuario,
                "datos": datos
            }
        )

        respuesta = _enviar_solicitud_tcp(msg)

        return (respuesta.ok, respuesta.message)

    except Exception as e:
        logger.error(f"Error en actualizar_perfil: {e}")
        return (False, f"Error al actualizar perfil: {str(e)}")


def obtener_estadisticas_globales() -> Optional[Dict]:
    """
    Obtiene estadísticas globales de la red social.

    Returns:
        dict: Estadísticas o None si hay error
    """
    try:
        msg = Message(
            type=MsgType.GET_STATS,
            payload={}
        )

        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            return respuesta.data.get("estadisticas", {})
        else:
            return None

    except Exception as e:
        logger.error(f"Error en obtener_estadisticas_globales: {e}")
        return None


def obtener_email_usuario(usuario: str) -> Optional[str]:
    """
    Obtiene el email de un usuario.

    Args:
        usuario: Nombre de usuario

    Returns:
        str: Email del usuario o None
    """
    try:
        msg = Message(
            type="GET_EMAIL",
            payload={"usuario": usuario}
        )

        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            return respuesta.data.get("email")
        else:
            return None

    except Exception as e:
        logger.error(f"Error en obtener_email_usuario: {e}")
        return None


def cargar_usuarios() -> Dict:
    """
    Carga todos los usuarios (para compatibilidad con código legacy).
    NOTA: En producción, esta función no debería usarse desde el cliente.

    Returns:
        dict: Diccionario de usuarios
    """
    try:
        msg = Message(
            type="GET_ALL_USERS",
            payload={}
        )

        respuesta = _enviar_solicitud_tcp(msg)

        if respuesta.ok:
            return respuesta.data.get("usuarios", {})
        else:
            return {}

    except Exception as e:
        logger.error(f"Error en cargar_usuarios: {e}")
        return {}
