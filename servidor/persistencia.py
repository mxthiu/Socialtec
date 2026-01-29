# -*- coding: utf-8 -*-

import json
import os
import threading
from pathlib import Path
from typing import Dict, Optional, List

ARCHIVO_USUARIOS = Path(__file__).parent.parent / "datos" / "usuarios.json"
_lock = threading.Lock()


def _asegurar_directorio():
    ARCHIVO_USUARIOS.parent.mkdir(parents=True, exist_ok=True)


def _asegurar_archivo():
    _asegurar_directorio()
    if not ARCHIVO_USUARIOS.exists():
        ARCHIVO_USUARIOS.write_text(json.dumps({}), encoding='utf-8')


def cargar_usuarios() -> Dict:
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
    with _lock:
        try:
            _asegurar_directorio()
            archivo_temp = ARCHIVO_USUARIOS.with_suffix('.tmp')
            archivo_temp.write_text(json.dumps(usuarios_dict, indent=2, ensure_ascii=False), encoding='utf-8')
            archivo_temp.replace(ARCHIVO_USUARIOS)
            return True
        except Exception as e:
            return False


def agregar_amistad(usuario1: str, usuario2: str) -> bool:
    usuarios = cargar_usuarios()

    if usuario1 not in usuarios or usuario2 not in usuarios:
        return False

    if usuario2 in usuarios[usuario1].get("amigos", []):
        return False

    if "amigos" not in usuarios[usuario1]:
        usuarios[usuario1]["amigos"] = []
    if "amigos" not in usuarios[usuario2]:
        usuarios[usuario2]["amigos"] = []

    usuarios[usuario1]["amigos"].append(usuario2)
    usuarios[usuario2]["amigos"].append(usuario1)

    return guardar_usuarios(usuarios)


def eliminar_amistad(usuario1: str, usuario2: str) -> bool:
    usuarios = cargar_usuarios()

    if usuario1 not in usuarios or usuario2 not in usuarios:
        return False

    if usuario2 not in usuarios[usuario1].get("amigos", []):
        return False

    usuarios[usuario1]["amigos"].remove(usuario2)
    usuarios[usuario2]["amigos"].remove(usuario1)

    return guardar_usuarios(usuarios)


def obtener_usuario(username: str) -> Optional[Dict]:
    usuarios = cargar_usuarios()
    return usuarios.get(username)


def usuario_existe(username: str) -> bool:
    usuarios = cargar_usuarios()
    return username in usuarios


def obtener_estadisticas_globales() -> Dict:
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

