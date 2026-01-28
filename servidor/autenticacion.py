"""
Autenticación con Passlib (hash y verificación de credenciales).

Este módulo implementa el hashing seguro de passwords con Argon2 (preferido) o bcrypt.
Se usa en el servidor para:
  - Registrar nuevos usuarios (hashear password antes de guardar)
  - Login (verificar password recibido contra hash almacenado)

INSTRUCCIONES PARA IMPLEMENTAR:
================================

1. Importa passlib:
   from passlib.hash import argon2, bcrypt
   
2. Implementa hash_password(password: str) -> str:
   - Usa argon2.hash(password) como método principal
   - Si falla, usa bcrypt.hash(password) como fallback
   - Retorna el hash como string
   
3. Implementa verify_password(password: str, hash_almacenado: str) -> bool:
   - Usa argon2.verify(password, hash_almacenado)
   - Si el hash es de bcrypt (empieza con $2b$ o $2a$), usa bcrypt.verify()
   - Retorna True si coincide, False si no
   
4. Implementa registrar_usuario_seguro(usuario: str, password: str, email: str, ...) -> dict:
   - Hashea el password con hash_password()
   - Crea dict con los datos del usuario (usuario, password_hash, email, etc.)
   - Retorna el dict listo para guardar en datos/usuarios.json
   
5. Implementa validar_login(usuario: str, password: str, usuarios_db: dict) -> tuple[bool, str]:
   - Busca el usuario en usuarios_db
   - Si no existe, retorna (False, "Usuario no encontrado")
   - Si existe, verifica el password con verify_password()
   - Retorna (True, "Login exitoso") o (False, "Password incorrecto")

TESTING:
========
Crea un script test_autenticacion.py:

    from servidor.autenticacion import hash_password, verify_password
    
    # Test 1: Hash y verificación básica
    password = "miPassword123"
    hash_generado = hash_password(password)
    print(f"Hash: {hash_generado[:50]}...")
    
    # Test 2: Verificar correcto
    assert verify_password(password, hash_generado) == True
    print("OK: Password correcto verificado")
    
    # Test 3: Verificar incorrecto
    assert verify_password("passwordMalo", hash_generado) == False
    print("OK: Password incorrecto rechazado")
    
    print("Todos los tests pasaron")

NOTAS:
======
- Argon2 es más seguro que bcrypt (ganador Password Hashing Competition 2015)
- Los hashes de Argon2 empiezan con $argon2...
- Los hashes de bcrypt empiezan con $2b$ o $2a$
- NUNCA guardes passwords en texto plano
- El hash es unidireccional (no se puede "desencriptar")
"""

from __future__ import annotations
from typing import Dict, Tuple, Optional

# TODO: Importar passlib
# from passlib.hash import argon2, bcrypt


# =========================
# Funciones principales
# =========================

def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando Argon2.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña (formato Argon2 o bcrypt)
        
    Ejemplo:
        >>> hash_pwd = hash_password("miPassword123")
        >>> print(hash_pwd[:20])
        $argon2id$v=19$m=...
    """
    # TODO: Implementar
    # 1. Validar que password no esté vacío
    # 2. Intentar usar argon2.hash(password)
    # 3. Si falla, usar bcrypt.hash(password)
    # 4. Retornar el hash
    raise NotImplementedError("hash_password no implementado aún")


def verify_password(password: str, hash_almacenado: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        password: Contraseña en texto plano a verificar
        hash_almacenado: Hash almacenado en la base de datos
        
    Returns:
        bool: True si coincide, False si no
        
    Ejemplo:
        >>> hash_pwd = hash_password("test123")
        >>> verify_password("test123", hash_pwd)
        True
        >>> verify_password("wrong", hash_pwd)
        False
    """
    # TODO: Implementar
    # 1. Detectar si el hash es Argon2 o bcrypt (ver prefijo)
    # 2. Usar argon2.verify() o bcrypt.verify() según corresponda
    # 3. Retornar True/False
    # 4. Si hay error (hash inválido), retornar False
    raise NotImplementedError("verify_password no implementado aún")


def registrar_usuario_seguro(
    usuario: str,
    password: str,
    nombre: str = "",
    apellido: str = "",
    email: str = "",
    foto: str = ""
) -> Dict[str, object]:
    """
    Crea un dict de usuario con password hasheado, listo para guardar.
    
    Args:
        usuario: Nombre de usuario (único)
        password: Contraseña en texto plano
        nombre: Nombre real
        apellido: Apellido
        email: Email
        foto: Path a foto de perfil
        
    Returns:
        dict: Usuario con password_hash (sin password plano)
        
    Ejemplo:
        >>> user = registrar_usuario_seguro("john", "secret123", "John", "Doe")
        >>> "password_hash" in user
        True
        >>> "password" in user  # No debe existir
        False
    """
    # TODO: Implementar
    # 1. Hashear el password con hash_password()
    # 2. Crear dict: {"usuario": ..., "password_hash": ..., "nombre": ..., etc.}
    # 3. Agregar campo "amigos": [] (lista vacía inicial)
    # 4. NO incluir el password en texto plano
    # 5. Retornar el dict
    raise NotImplementedError("registrar_usuario_seguro no implementado aún")


def validar_login(
    usuario: str,
    password: str,
    usuarios_db: Dict[str, dict]
) -> Tuple[bool, str]:
    """
    Valida credenciales de login contra la base de datos.
    
    Args:
        usuario: Username a verificar
        password: Password en texto plano
        usuarios_db: Dict de usuarios {username: {password_hash, ...}}
        
    Returns:
        tuple: (éxito: bool, mensaje: str)
        
    Ejemplos:
        >>> db = {"john": {"password_hash": "$argon2..."}}
        >>> validar_login("john", "correctPass", db)
        (True, "Login exitoso")
        >>> validar_login("john", "wrongPass", db)
        (False, "Password incorrecto")
        >>> validar_login("noexiste", "any", db)
        (False, "Usuario no encontrado")
    """
    # TODO: Implementar
    # 1. Buscar usuario en usuarios_db
    # 2. Si no existe, retornar (False, "Usuario no encontrado")
    # 3. Obtener password_hash del usuario
    # 4. Verificar con verify_password(password, password_hash)
    # 5. Si coincide, retornar (True, "Login exitoso")
    # 6. Si no coincide, retornar (False, "Password incorrecto")
    raise NotImplementedError("validar_login no implementado aún")


# =========================
# Helpers opcionales
# =========================

def cambiar_password(
    usuario: str,
    password_actual: str,
    password_nuevo: str,
    usuarios_db: Dict[str, dict]
) -> Tuple[bool, str]:
    """
    Cambia el password de un usuario (opcional, para rama futura).
    
    Args:
        usuario: Username
        password_actual: Password actual (para verificar)
        password_nuevo: Nuevo password a establecer
        usuarios_db: Base de datos de usuarios
        
    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    # TODO OPCIONAL: Implementar si hay tiempo
    # 1. Validar que el password_actual es correcto con validar_login()
    # 2. Hashear password_nuevo
    # 3. Actualizar password_hash en usuarios_db[usuario]
    # 4. Retornar (True, "Password actualizado")
    raise NotImplementedError("cambiar_password no implementado aún (opcional)")
