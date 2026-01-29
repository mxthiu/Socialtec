# -*- coding: utf-8 -*-
"""
Persistencia basada en archivos JSON.

Capa de acceso a datos que maneja la comunicación con archivos JSON.
El servidor accede a los datos solo a través de este módulo.
"""

import json
import os
import threading
from pathlib import Path
from typing import Dict, Optional, List

# Ruta del archivo de usuarios
ARCHIVO_USUARIOS = Path(__file__).parent.parent / "datos" / "usuarios.json"

# Lock para evitar condiciones de carrera en acceso concurrente
_lock = threading.Lock()


def _asegurar_directorio():
    """Crea el directorio de datos si no existe"""
    ARCHIVO_USUARIOS.parent.mkdir(parents=True, exist_ok=True)


def _asegurar_archivo():
    """Crea el archivo de usuarios si no existe"""
    _asegurar_directorio()
    if not ARCHIVO_USUARIOS.exists():
        ARCHIVO_USUARIOS.write_text(json.dumps({}), encoding='utf-8')


def cargar_usuarios() -> Dict:
    """
    Carga todos los usuarios desde datos/usuarios.json.

    Returns:
        dict: Diccionario con estructura:
              {
                "username": {
                  "usuario": "username",
                  "password_hash": "hash_argon2",
                  "nombre": "Nombre",
                  "apellido": "Apellido",
                  "email": "email@example.com",
                  "foto": "ruta/foto.jpg",
                  "amigos": ["amigo1", "amigo2", ...]
                },
                ...
              }
    """
    with _lock:
        _asegurar_archivo()
        try:
            contenido = ARCHIVO_USUARIOS.read_text(encoding='utf-8')
            if not contenido.strip():
                return {}
            return json.loads(contenido)
        except (json.JSONDecodeError, IOError):
            return {}


def guardar_usuarios(usuarios_dict: Dict) -> bool:
    """
    Guarda el diccionario de usuarios en datos/usuarios.json.

    Args:
        usuarios_dict: Diccionario de usuarios a guardar

    Returns:
        bool: True si se guardó exitosamente, False si hubo error
    """
    with _lock:
        try:
            _asegurar_directorio()
            # Guardar en archivo temporal primero
            archivo_temp = ARCHIVO_USUARIOS.with_suffix('.tmp')
            archivo_temp.write_text(json.dumps(usuarios_dict, indent=2, ensure_ascii=False), encoding='utf-8')
            # Reemplazar archivo original
            archivo_temp.replace(ARCHIVO_USUARIOS)
            return True
        except Exception as e:
            return False


def agregar_amistad(usuario1: str, usuario2: str) -> bool:
    """
    Agrega una amistad bidireccional entre usuario1 y usuario2.

    Args:
        usuario1: Nombre de usuario 1
        usuario2: Nombre de usuario 2

    Returns:
        bool: True si se agregó, False si ya eran amigos o no existen
    """
    usuarios = cargar_usuarios()

    # Validar que ambos usuarios existen
    if usuario1 not in usuarios or usuario2 not in usuarios:
        return False

    # Validar que no son amigos ya
    if usuario2 in usuarios[usuario1].get("amigos", []):
        return False

    # Agregar la amistad bidireccional
    if "amigos" not in usuarios[usuario1]:
        usuarios[usuario1]["amigos"] = []
    if "amigos" not in usuarios[usuario2]:
        usuarios[usuario2]["amigos"] = []

    usuarios[usuario1]["amigos"].append(usuario2)
    usuarios[usuario2]["amigos"].append(usuario1)

    return guardar_usuarios(usuarios)


def eliminar_amistad(usuario1: str, usuario2: str) -> bool:
    """
    Elimina una amistad bidireccional entre usuario1 y usuario2.

    Args:
        usuario1: Nombre de usuario 1
        usuario2: Nombre de usuario 2

    Returns:
        bool: True si se eliminó, False si no eran amigos
    """
    usuarios = cargar_usuarios()

    # Validar que ambos usuarios existen
    if usuario1 not in usuarios or usuario2 not in usuarios:
        return False

    # Validar que son amigos
    if usuario2 not in usuarios[usuario1].get("amigos", []):
        return False

    # Eliminar la amistad bidireccional
    usuarios[usuario1]["amigos"].remove(usuario2)
    usuarios[usuario2]["amigos"].remove(usuario1)

    return guardar_usuarios(usuarios)


def obtener_usuario(username: str) -> Optional[Dict]:
    """
    Obtiene los datos de un usuario específico.

    Args:
        username: Nombre de usuario a buscar

    Returns:
        dict: Datos del usuario o None si no existe
    """
    usuarios = cargar_usuarios()
    return usuarios.get(username)


def usuario_existe(username: str) -> bool:
    """
    Verifica si un usuario existe.

    Args:
        username: Nombre de usuario a verificar

    Returns:
        bool: True si existe, False si no
    """
    usuarios = cargar_usuarios()
    return username in usuarios


def obtener_estadisticas_globales() -> Dict:
    """
    Calcula estadísticas globales de la red social.

    Returns:
        dict: Diccionario con:
              {
                "total_usuarios": int,
                "promedio_amigos": float,
                "usuario_mas_amigos": {"usuario": "...", "nombre": "...", "amigos": [...], ...},
                "usuario_menos_amigos": {"usuario": "...", "nombre": "...", "amigos": [...], ...},
                "total_amistades": int
              }
    """
    usuarios = cargar_usuarios()

    if not usuarios:
        return {
            "total_usuarios": 0,
            "promedio_amigos": 0,
            "usuario_mas_amigos": None,
            "usuario_menos_amigos": None,
            "total_amistades": 0
        }

    total_usuarios = len(usuarios)
    total_amistades = 0
    usuario_mas = None
    usuario_menos = None
    max_amigos = -1
    min_amigos = float('inf')

    for usuario, datos in usuarios.items():
        cantidad_amigos = len(datos.get("amigos", []))
        total_amistades += cantidad_amigos

        if cantidad_amigos > max_amigos:
            max_amigos = cantidad_amigos
            usuario_mas = {
                "usuario": usuario,
                "nombre": datos.get("nombre", ""),
                "apellido": datos.get("apellido", ""),
                "amigos": datos.get("amigos", []),
                "email": datos.get("email", "")
            }

        if cantidad_amigos < min_amigos:
            min_amigos = cantidad_amigos
            usuario_menos = {
                "usuario": usuario,
                "nombre": datos.get("nombre", ""),
                "apellido": datos.get("apellido", ""),
                "amigos": datos.get("amigos", []),
                "email": datos.get("email", "")
            }

    # Cada amistad se cuenta dos veces (bidireccional), así que dividimos por 2
    total_amistades = total_amistades // 2

    promedio_amigos = total_amistades / total_usuarios if total_usuarios > 0 else 0

    return {
        "total_usuarios": total_usuarios,
        "promedio_amigos": promedio_amigos,
        "usuario_mas_amigos": usuario_mas,
        "usuario_menos_amigos": usuario_menos,
        "total_amistades": total_amistades
    }

