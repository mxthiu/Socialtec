"""
Cliente de autenticación - Adaptador para servidor TCP

Este módulo actúa como intermediario entre la GUI y el servidor de autenticación.
Por ahora usa validación local con passlib, pero está preparado para migrar
a comunicación TCP con el servidor cuando esté listo.

IMPORTANTE:
===========
Todas las funciones aquí ya usan hashing seguro con Argon2 (passlib).
Los passwords NUNCA se almacenan ni transmiten en texto plano.

CUANDO EL SERVIDOR ESTÉ LISTO:
===============================
Reemplazar las implementaciones locales por llamadas TCP al servidor.
La interfaz pública (firmas de funciones) NO cambiará, solo la implementación interna.
"""

from typing import Tuple, Dict, Optional


def login_usuario(usuario: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Intenta iniciar sesión con las credenciales proporcionadas.
    
    SEGURIDAD:
    - El password se verifica contra hash Argon2 almacenado
    - NUNCA se compara password en texto plano
    - El hash se genera/verifica con passlib (servidor.autenticacion)
    
    Args:
        usuario: Nombre de usuario
        password: Contraseña en texto plano (se verificará contra hash)
        
    Returns:
        tuple: (exito: bool, datos_usuario: dict | None)
               - Si éxito: (True, {usuario, nombre, apellido, email, foto, amigos})
               - Si fallo: (False, None)
    
    TODO FUTURO:
    Cuando el servidor esté listo, reemplazar por:
        return enviar_solicitud_tcp("LOGIN", {
            "usuario": usuario,
            "password": password  # Se hasheará en tránsito o servidor
        })
    """
    # IMPLEMENTACIÓN LOCAL TEMPORAL (con passlib/argon2)
    from servidor.autenticacion import validar_login
    from cliente.datos_local import cargar_usuarios, obtener_amigos_completos
    
    usuarios_db = cargar_usuarios()
    
    # Validar con passlib (hash Argon2)
    exito, mensaje = validar_login(usuario, password, usuarios_db)
    
    if not exito:
        return (False, None)
    
    # Obtener datos completos del usuario
    datos = usuarios_db[usuario]
    amigos = obtener_amigos_completos(datos.get("amigos", []))
    
    usuario_completo = {
        "usuario": usuario,
        "nombre": datos.get("nombre", ""),
        "apellido": datos.get("apellido", ""),
        "email": datos.get("email", ""),
        "foto": datos.get("foto"),
        "amigos": amigos
    }
    
    return (True, usuario_completo)


def registrar_usuario(
    usuario: str,
    password: str,
    nombre: str,
    apellido: str,
    email: str,
    foto: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Registra un nuevo usuario en el sistema.
    
    SEGURIDAD:
    - El password se hashea con Argon2 antes de guardar
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
    
    TODO FUTURO:
    Cuando el servidor esté listo, reemplazar por:
        return enviar_solicitud_tcp("REGISTER", {
            "usuario": usuario,
            "password": password,  # Se hasheará antes/durante transmisión
            "nombre": nombre,
            ...
        })
    """
    # IMPLEMENTACIÓN LOCAL TEMPORAL (con passlib/argon2)
    from servidor.autenticacion import registrar_usuario_seguro
    from cliente.datos_local import cargar_usuarios, guardar_usuarios
    
    usuarios_db = cargar_usuarios()
    
    # Verificar que el usuario no exista
    if usuario in usuarios_db:
        return (False, "El usuario ya existe")
    
    # Crear usuario con password hasheado (Argon2)
    try:
        usuario_data = registrar_usuario_seguro(
            usuario=usuario,
            password=password,  # Se hasheará internamente
            nombre=nombre,
            apellido=apellido,
            email=email,
            foto=foto or ""
        )
        
        # Guardar en base de datos local
        usuarios_db[usuario] = usuario_data
        guardar_usuarios(usuarios_db)
        
        return (True, "Usuario registrado exitosamente")
    
    except Exception as e:
        return (False, f"Error al registrar: {str(e)}")


def cambiar_password_usuario(
    usuario: str,
    password_actual: str,
    password_nuevo: str
) -> Tuple[bool, str]:
    """
    Cambia la contraseña de un usuario.
    
    SEGURIDAD:
    - Verifica password_actual contra hash Argon2
    - Genera nuevo hash Argon2 para password_nuevo
    - Todo manejado por passlib (servidor.autenticacion)
    
    Args:
        usuario: Nombre de usuario
        password_actual: Contraseña actual (se verificará contra hash)
        password_nuevo: Nueva contraseña (se hasheará)
        
    Returns:
        tuple: (exito: bool, mensaje: str)
    
    TODO FUTURO:
    Cuando el servidor esté listo, reemplazar por:
        return enviar_solicitud_tcp("CHANGE_PASSWORD", {
            "usuario": usuario,
            "password_actual": password_actual,
            "password_nuevo": password_nuevo
        })
    """
    # IMPLEMENTACIÓN LOCAL TEMPORAL (con passlib/argon2)
    from servidor.autenticacion import cambiar_password
    from cliente.datos_local import cargar_usuarios, guardar_usuarios
    
    usuarios_db = cargar_usuarios()
    
    if usuario not in usuarios_db:
        return (False, "Usuario no encontrado")
    
    # Cambiar password (verifica actual y hashea nuevo con Argon2)
    exito, mensaje = cambiar_password(
        usuario=usuario,
        password_actual=password_actual,
        password_nuevo=password_nuevo,
        usuarios_db=usuarios_db
    )
    
    if exito:
        # Guardar cambios en base de datos local
        guardar_usuarios(usuarios_db)
    
    return (exito, mensaje)


def verificar_disponibilidad_usuario(usuario: str) -> bool:
    """
    Verifica si un nombre de usuario está disponible.
    
    Args:
        usuario: Nombre de usuario a verificar
        
    Returns:
        bool: True si está disponible, False si ya existe
    
    TODO FUTURO:
    Cuando el servidor esté listo, reemplazar por:
        return enviar_solicitud_tcp("CHECK_USER", {"usuario": usuario})
    """
    # IMPLEMENTACIÓN LOCAL TEMPORAL
    from cliente.datos_local import cargar_usuarios
    
    usuarios_db = cargar_usuarios()
    return usuario not in usuarios_db


# ==============================================
# Función auxiliar para migración futura a TCP
# ==============================================

def enviar_solicitud_tcp(comando: str, datos: Dict) -> Tuple[bool, any]:
    """
    PLACEHOLDER para comunicación TCP con servidor.
    
    Esta función será implementada cuando el servidor TCP esté listo.
    Por ahora lanza NotImplementedError.
    
    Args:
        comando: Comando a enviar ("LOGIN", "REGISTER", etc.)
        datos: Datos a enviar al servidor
        
    Returns:
        tuple: (exito: bool, respuesta: any)
    
    IMPLEMENTACIÓN FUTURA:
    ----------------------
    import socket
    import json
    from cliente.encriptacion import encriptar_datos, desencriptar_datos
    
    # Conectar al servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        
        # Encriptar y enviar
        mensaje = json.dumps({"comando": comando, "datos": datos})
        mensaje_encriptado = encriptar_datos(mensaje)
        sock.sendall(mensaje_encriptado)
        
        # Recibir y desencriptar respuesta
        respuesta_encriptada = sock.recv(4096)
        respuesta = desencriptar_datos(respuesta_encriptada)
        respuesta_dict = json.loads(respuesta)
        
        return (respuesta_dict["exito"], respuesta_dict["datos"])
    """
    raise NotImplementedError(
        "Comunicación TCP no implementada aún. "
        "Usando validación local con passlib por ahora."
    )
