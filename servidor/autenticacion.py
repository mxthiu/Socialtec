"""
Autenticación con Passlib - Hash y verificación de credenciales
"""

from __future__ import annotations
from typing import Dict, Tuple, Optional

from passlib.hash import argon2, bcrypt


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password no puede estar vacío")
    
    try:
        return argon2.hash(password)
    except Exception:
        return bcrypt.hash(password)


def verify_password(password: str, hash_almacenado: str) -> bool:
    try:
        if hash_almacenado.startswith("$argon2"):
            return argon2.verify(password, hash_almacenado)
        elif hash_almacenado.startswith(("$2b$", "$2a$", "$2y$")):
            return bcrypt.verify(password, hash_almacenado)
        else:
            return False
    except Exception:
        return False


def registrar_usuario_seguro(
    usuario: str,
    password: str,
    nombre: str = "",
    apellido: str = "",
    email: str = "",
    foto: str = ""
) -> Dict[str, object]:
    password_hash = hash_password(password)
    
    return {
        "usuario": usuario,
        "password_hash": password_hash,
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "foto": foto,
        "amigos": []
    }


def validar_login(
    usuario: str,
    password: str,
    usuarios_db: Dict[str, dict]
) -> Tuple[bool, str]:
    if usuario not in usuarios_db:
        return (False, "Usuario no encontrado")
    
    usuario_data = usuarios_db[usuario]
    password_hash = usuario_data.get("password_hash")
    
    if not password_hash:
        return (False, "Error: Usuario sin hash de password")
    
    if verify_password(password, password_hash):
        return (True, "Login exitoso")
    else:
        return (False, "Password incorrecto")


def cambiar_password(
    usuario: str,
    password_actual: str,
    password_nuevo: str,
    usuarios_db: Dict[str, dict]
) -> Tuple[bool, str]:
    exito, mensaje = validar_login(usuario, password_actual, usuarios_db)
    
    if not exito:
        return (False, "Password actual incorrecto")
    
    try:
        nuevo_hash = hash_password(password_nuevo)
        usuarios_db[usuario]["password_hash"] = nuevo_hash
        return (True, "Password actualizado")
    except Exception as e:
        return (False, f"Error al cambiar password: {str(e)}")
