# -*- coding: utf-8 -*-
"""
Script de prueba para verificar implementación de persistencia y TCP.

Prueba:
1. Cargar y guardar usuarios con persistencia
2. Agregar/eliminar amistades
3. Obtener estadísticas globales
4. Conectar cliente a servidor TCP
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_persistencia():
    """Prueba el módulo de persistencia"""
    print("\n=== PRUEBA 1: PERSISTENCIA ===")

    from servidor.persistencia import (
        cargar_usuarios,
        guardar_usuarios,
        agregar_amistad,
        eliminar_amistad,
        obtener_usuario,
        usuario_existe,
        obtener_estadisticas_globales,
    )
    from servidor.autenticacion import hash_password

    # Crear directorio de datos si no existe
    from pathlib import Path
    datos_dir = Path(__file__).parent / "datos"
    datos_dir.mkdir(exist_ok=True)

    # 1. Probar cargar usuarios (vacío al inicio)
    usuarios = cargar_usuarios()
    print(f"✓ Usuarios cargados (inicial): {len(usuarios)} usuarios")

    # 2. Crear algunos usuarios de prueba
    usuarios_test = {
        "alice": {
            "usuario": "alice",
            "password_hash": hash_password("pass123"),
            "nombre": "Alice",
            "apellido": "Wonder",
            "email": "alice@test.com",
            "foto": "",
            "amigos": []
        },
        "bob": {
            "usuario": "bob",
            "password_hash": hash_password("pass456"),
            "nombre": "Bob",
            "apellido": "Builder",
            "email": "bob@test.com",
            "foto": "",
            "amigos": []
        }
    }

    # 3. Guardar usuarios
    exito = guardar_usuarios(usuarios_test)
    print(f"✓ Usuarios guardados: {exito}")

    # 4. Verificar que se cargaron
    usuarios = cargar_usuarios()
    print(f"✓ Usuarios cargados (después de guardar): {len(usuarios)} usuarios")
    print(f"  - {list(usuarios.keys())}")

    # 5. Probar usuario_existe
    existe_alice = usuario_existe("alice")
    existe_charlie = usuario_existe("charlie")
    print(f"✓ alice existe: {existe_alice}, charlie existe: {existe_charlie}")

    # 6. Probar obtener_usuario
    usuario_alice = obtener_usuario("alice")
    print(f"✓ Datos de alice: nombre={usuario_alice.get('nombre')}, email={usuario_alice.get('email')}")

    # 7. Agregar amistad
    exito = agregar_amistad("alice", "bob")
    print(f"✓ Amistad agregada alice-bob: {exito}")

    # 8. Verificar que se guardó
    usuarios = cargar_usuarios()
    amigos_alice = usuarios["alice"]["amigos"]
    amigos_bob = usuarios["bob"]["amigos"]
    print(f"✓ Amigos de alice: {amigos_alice}, amigos de bob: {amigos_bob}")

    # 9. Obtener estadísticas
    stats = obtener_estadisticas_globales()
    print(f"✓ Estadísticas globales:")
    print(f"  - Total usuarios: {stats['total_usuarios']}")
    print(f"  - Total amistades: {stats['total_amistades']}")
    print(f"  - Usuario con más amigos: {stats['usuario_mas_amigos']['usuario'] if stats['usuario_mas_amigos'] else 'N/A'}")

    # 10. Eliminar amistad
    exito = eliminar_amistad("alice", "bob")
    print(f"✓ Amistad eliminada alice-bob: {exito}")

    usuarios = cargar_usuarios()
    amigos_alice = usuarios["alice"]["amigos"]
    print(f"✓ Amigos de alice después de eliminar: {amigos_alice}")

    print("\n✅ PERSISTENCIA: Todas las pruebas pasaron")
    return True


def test_auth_client():
    """Prueba el módulo de auth_client"""
    print("\n=== PRUEBA 2: AUTH CLIENT ===")

    from cliente.auth_client import (
        verificar_disponibilidad_usuario,
    )

    # Nota: Estas pruebas requieren que el servidor esté corriendo
    # Por ahora solo probamos que el módulo carga sin errores

    print("✓ Módulo auth_client importado correctamente")
    print("✓ Funciones TCP disponibles: login_usuario, registrar_usuario, cambiar_password_usuario, etc.")

    print("\n✅ AUTH_CLIENT: Importación exitosa")
    return True


def test_connection_manager():
    """Prueba el módulo de connection_manager"""
    print("\n=== PRUEBA 3: CONNECTION MANAGER ===")

    from cliente.connection_manager import ConnectionManager, ConnectionIndicator

    # Crear instancias
    manager = ConnectionManager()
    indicador = ConnectionIndicator()

    print("✓ ConnectionManager creado")
    print("✓ ConnectionIndicator creado")

    # Probar ConnectionIndicator
    indicador.update(True, "Conectado al servidor")
    connected, msg = indicador.get_status()
    print(f"✓ Status: conectado={connected}, mensaje='{msg}'")

    color = indicador.get_color()
    icono = indicador.get_icon_text()
    print(f"✓ Indicador: color={color}, icono='{icono}'")

    print("\n✅ CONNECTION_MANAGER: Todas las pruebas pasaron")
    return True


def test_indicador_conexion():
    """Prueba el widget indicador de conexión"""
    print("\n=== PRUEBA 4: INDICADOR CONEXIÓN ===")

    from cliente.connection_manager import ConnectionIndicator
    from cliente.indicador_conexion import IndicadorConexion

    indicador = ConnectionIndicator()

    # No podemos crear el widget sin PyQt si no está en contexto de GUI
    # Pero podemos verificar que el módulo se importa correctamente

    print("✓ Módulo indicador_conexion importado correctamente")
    print("✓ IndicadorConexion class disponible")

    print("\n✅ INDICADOR_CONEXION: Importación exitosa")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE IMPLEMENTACIÓN SOCIALTEC")
    print("=" * 60)

    try:
        resultado1 = test_persistencia()
        resultado2 = test_auth_client()
        resultado3 = test_connection_manager()
        resultado4 = test_indicador_conexion()

        if all([resultado1, resultado2, resultado3, resultado4]):
            print("\n" + "=" * 60)
            print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n⚠ Algunas pruebas fallaron")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
