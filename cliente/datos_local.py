import json
import os
from passlib.hash import argon2

ARCHIVO_USUARIOS = "datos/usuarios_local.json"


def inicializar_archivo():
    """Crea el archivo de usuarios si no existe"""
    os.makedirs("datos", exist_ok=True)
    
    if not os.path.exists(ARCHIVO_USUARIOS):
        usuarios = {
            "mathias": {
                "nombre": "Mathias",
                "apellido": "Vargas",
                "usuario": "mathias",
                "password_hash": argon2.hash("1234"),  # Contraseña: 1234
                "email": "praraora@gmail.com",
                "foto": None,
                "amigos": ["ana_lopez", "juanp"]
            },
            "ana_lopez": {
                "nombre": "Ana",
                "apellido": "López",
                "usuario": "ana_lopez",
                "password_hash": argon2.hash("1234"),
                "email": "ana.lopez@example.com",
                "foto": None,
                "amigos": ["mathias"]
            },
            "juanp": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "usuario": "juanp",
                "password_hash": argon2.hash("1234"),
                "email": "juan.perez@example.com",
                "foto": None,
                "amigos": ["mathias"]
            }
        }
        
        guardar_usuarios(usuarios)


def cargar_usuarios():
    """Carga los usuarios del archivo"""
    inicializar_archivo()
    
    try:
        with open(ARCHIVO_USUARIOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def guardar_usuarios(usuarios):
    """Guarda los usuarios en el archivo"""
    with open(ARCHIVO_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)


def validar_login(usuario, password):
    """
    Valida las credenciales de login
    Retorna: (bool, dict) - (éxito, datos_usuario o None)
    """
    usuarios = cargar_usuarios()
    
    if usuario not in usuarios:
        return False, None
    
    user_data = usuarios[usuario]
    
    try:
        if argon2.verify(password, user_data['password_hash']):
            datos_usuario = {
                "nombre": user_data["nombre"],
                "apellido": user_data["apellido"],
                "usuario": user_data["usuario"],
                "email": user_data.get("email", f"{usuario}@socialtec.com"),
                "foto": user_data.get("foto"),
                "amigos": obtener_amigos_completos(user_data["amigos"])
            }
            return True, datos_usuario
    except:
        pass
    
    return False, None


def registrar_usuario(nombre, apellido, usuario, password, email, foto_path=None):
    """
    Registra un nuevo usuario
    Retorna: (bool, str) - (éxito, mensaje)
    """
    usuarios = cargar_usuarios()
    
    if usuario in usuarios:
        return False, "El usuario ya existe"
    
    # Verificar si el email ya está en uso
    for user_data in usuarios.values():
        if user_data.get("email") == email:
            return False, "El email ya está en uso"
    
    usuarios[usuario] = {
        "nombre": nombre,
        "apellido": apellido,
        "usuario": usuario,
        "password_hash": argon2.hash(password),
        "email": email,
        "foto": foto_path,
        "amigos": []
    }
    
    guardar_usuarios(usuarios)
    return True, "Usuario registrado exitosamente"


def obtener_amigos_completos(lista_usuarios):
    """
    Convierte una lista de usuarios en lista de datos completos
    """
    usuarios = cargar_usuarios()
    amigos = []
    
    for username in lista_usuarios:
        if username in usuarios:
            user = usuarios[username]
            amigos.append({
                "nombre": user["nombre"],
                "apellido": user["apellido"],
                "usuario": user["usuario"],
                "foto": user.get("foto")
            })
    
    return amigos


    def obtener_usuario_completo(usuario):
        """
        Retorna los datos completos de un usuario con la lista de amigos expandida
        """
        usuarios = cargar_usuarios()
        if usuario not in usuarios:
            return None

        user = usuarios[usuario]
        return {
            "nombre": user.get("nombre", ""),
            "apellido": user.get("apellido", ""),
            "usuario": user.get("usuario", usuario),
            "email": user.get("email", f"{usuario}@socialtec.com"),
            "foto": user.get("foto"),
            "amigos": obtener_amigos_completos(user.get("amigos", [])),
        }


def buscar_usuarios(query):
    """
    Busca usuarios por nombre, apellido o usuario
    Retorna: lista de usuarios que coinciden
    """
    usuarios = cargar_usuarios()
    resultados = []
    query = query.lower()
    
    for username, data in usuarios.items():
        nombre_completo = f"{data['nombre']} {data['apellido']}".lower()
        
        if (query in nombre_completo or 
            query in data['usuario'].lower()):
            resultados.append({
                "nombre": data["nombre"],
                "apellido": data["apellido"],
                "usuario": data["usuario"],
                "foto": data.get("foto")
            })
    
    return resultados


def agregar_amigo(usuario_actual, usuario_amigo):
    """
    Agrega una relación de amistad (bidireccional)
    Retorna: (bool, str) - (éxito, mensaje)
    """
    usuarios = cargar_usuarios()
    
    if usuario_actual not in usuarios or usuario_amigo not in usuarios:
        return False, "Usuario no encontrado"
    
    if usuario_amigo not in usuarios[usuario_actual]["amigos"]:
        usuarios[usuario_actual]["amigos"].append(usuario_amigo)
    
    if usuario_actual not in usuarios[usuario_amigo]["amigos"]:
        usuarios[usuario_amigo]["amigos"].append(usuario_actual)
    
    guardar_usuarios(usuarios)
    return True, "Amigo agregado exitosamente"


def eliminar_amigo(usuario_actual, usuario_amigo):
    """
    Elimina una relación de amistad (bidireccional)
    Retorna: (bool, str) - (éxito, mensaje)
    """
    usuarios = cargar_usuarios()
    
    if usuario_actual not in usuarios:
        return False, "Usuario no encontrado"
    
    if usuario_amigo in usuarios[usuario_actual]["amigos"]:
        usuarios[usuario_actual]["amigos"].remove(usuario_amigo)
    
    if usuario_actual in usuarios[usuario_amigo]["amigos"]:
        usuarios[usuario_amigo]["amigos"].remove(usuario_actual)
    
    guardar_usuarios(usuarios)
    return True, "Amigo eliminado"


def obtener_estadisticas_globales():
    """
    Calcula estadísticas globales de la red social
    Retorna: dict con estadísticas
    """
    usuarios = cargar_usuarios()
    
    if not usuarios:
        return {
            "usuario_mas_amigos": None,
            "usuario_menos_amigos": None,
            "promedio_amigos": 0,
            "total_usuarios": 0
        }
    
    # Calcular cantidad de amigos por usuario
    stats_usuarios = []
    for username, data in usuarios.items():
        stats_usuarios.append({
            "usuario": username,
            "nombre": f"{data['nombre']} {data['apellido']}",
            "cantidad_amigos": len(data['amigos'])
        })
    
    # Ordenar por cantidad de amigos
    stats_usuarios.sort(key=lambda x: x['cantidad_amigos'], reverse=True)
    
    # Usuario con más amigos
    mas_amigos = stats_usuarios[0] if stats_usuarios else None
    
    # Usuario con menos amigos
    menos_amigos = stats_usuarios[-1] if stats_usuarios else None
    
    # Promedio
    total_amigos = sum(u['cantidad_amigos'] for u in stats_usuarios)
    promedio = total_amigos / len(stats_usuarios) if stats_usuarios else 0
    
    return {
        "usuario_mas_amigos": mas_amigos,
        "usuario_menos_amigos": menos_amigos,
        "promedio_amigos": round(promedio, 2),
        "total_usuarios": len(usuarios),
        "todos_usuarios": stats_usuarios  # Lista completa ordenada
    }


def actualizar_perfil(usuario, nombre=None, apellido=None, email=None, foto=None):
    """
    Actualiza los datos del perfil de un usuario
    Retorna: (bool, str, dict) - (éxito, mensaje, datos_actualizados)
    """
    usuarios = cargar_usuarios()
    
    if usuario not in usuarios:
        return False, "Usuario no encontrado", None
    
    if email:
        for username, user_data in usuarios.items():
            if username != usuario and user_data.get("email") == email:
                return False, "El email ya está en uso", None
    
    if nombre:
        usuarios[usuario]['nombre'] = nombre
    if apellido:
        usuarios[usuario]['apellido'] = apellido
    if email:
        usuarios[usuario]['email'] = email
    if foto is not None:  # Puede ser None o una ruta
        usuarios[usuario]['foto'] = foto
    
    guardar_usuarios(usuarios)
    
    user_data = usuarios[usuario]
    datos_actualizados = {
        "nombre": user_data["nombre"],
        "apellido": user_data["apellido"],
        "usuario": user_data["usuario"],
        "email": user_data.get("email", f"{usuario}@socialtec.com"),
        "foto": user_data.get("foto"),
        "amigos": obtener_amigos_completos(user_data["amigos"])
    }
    
    return True, "Perfil actualizado exitosamente", datos_actualizados


def cambiar_password(usuario, password_nueva):
    """
    Cambia la contraseña de un usuario
    Retorna: (bool, str) - (éxito, mensaje)
    """
    usuarios = cargar_usuarios()
    
    if usuario not in usuarios:
        return False, "Usuario no encontrado"
    
    # Actualizar password
    usuarios[usuario]['password_hash'] = argon2.hash(password_nueva)
    
    guardar_usuarios(usuarios)
    return True, "Contraseña actualizada exitosamente"


def obtener_email_usuario(usuario):
    """
    Retorna el email real del usuario desde la base de datos
    """
    usuarios = cargar_usuarios()
    
    if usuario not in usuarios:
        return f"{usuario}@socialtec.com"
    
    return usuarios[usuario].get("email", f"{usuario}@socialtec.com")


# Inicializar al importar
inicializar_archivo()

