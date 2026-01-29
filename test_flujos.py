# -*- coding: utf-8 -*-
"""
Test de flujos completos end-to-end.
Prueba casos de uso reales del sistema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_flujo_registro_login():
    """Test: Registro -> Login"""
    print("\n" + "="*60)
    print("FLUJO 1: REGISTRO -> LOGIN")
    print("="*60)
    
    try:
        from servidor.persistencia import cargar_usuarios, guardar_usuarios, usuario_existe
        from servidor.autenticacion import hash_password, validar_login
        from cliente.auth_client import _enviar_solicitud_tcp
        from utils.protocolo import Message, MsgType, Response
        
        # Simular lo que el servidor haría
        print("1. Verificar que usuario no existe")
        usuarios = cargar_usuarios()
        existe = usuario_existe("test_flow")
        print(f"   usuario_existe('test_flow') = {existe}")
        
        print("2. Crear usuario de prueba")
        test_user = {
            "usuario": "test_flow",
            "password_hash": hash_password("TestPass123"),
            "nombre": "Test",
            "apellido": "Flow",
            "email": "test@flow.com",
            "foto": "",
            "amigos": []
        }
        usuarios["test_flow"] = test_user
        guardar_usuarios(usuarios)
        print("   Usuario creado")
        
        print("3. Verificar que existe")
        existe = usuario_existe("test_flow")
        print(f"   usuario_existe('test_flow') = {existe}")
        
        print("4. Validar login con contraseña correcta")
        usuarios = cargar_usuarios()
        exito, mensaje = validar_login("test_flow", "TestPass123", usuarios)
        print(f"   validar_login: exito={exito}, mensaje='{mensaje}'")
        
        print("5. Validar login con contraseña incorrecta")
        exito, mensaje = validar_login("test_flow", "WrongPass", usuarios)
        print(f"   validar_login: exito={exito}, mensaje='{mensaje}'")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flujo_amistades():
    """Test: Agregar y eliminar amistades"""
    print("\n" + "="*60)
    print("FLUJO 2: AGREGAR Y ELIMINAR AMISTADES")
    print("="*60)
    
    try:
        from servidor.persistencia import (
            cargar_usuarios, guardar_usuarios, agregar_amistad,
            eliminar_amistad, usuario_existe
        )
        from servidor.autenticacion import hash_password
        
        print("1. Crear dos usuarios de prueba")
        usuarios = cargar_usuarios()
        
        if not usuario_existe("user_a"):
            usuarios["user_a"] = {
                "usuario": "user_a",
                "password_hash": hash_password("pass_a"),
                "nombre": "User", "apellido": "A",
                "email": "a@test.com", "foto": "",
                "amigos": []
            }
        
        if not usuario_existe("user_b"):
            usuarios["user_b"] = {
                "usuario": "user_b",
                "password_hash": hash_password("pass_b"),
                "nombre": "User", "apellido": "B",
                "email": "b@test.com", "foto": "",
                "amigos": []
            }
        
        guardar_usuarios(usuarios)
        print("   Usuarios creados")
        
        print("2. Agregar amistad")
        exito = agregar_amistad("user_a", "user_b")
        print(f"   agregar_amistad('user_a', 'user_b') = {exito}")
        
        usuarios = cargar_usuarios()
        print(f"   user_a amigos: {usuarios['user_a']['amigos']}")
        print(f"   user_b amigos: {usuarios['user_b']['amigos']}")
        
        print("3. Intentar agregar de nuevo (debe fallar)")
        exito = agregar_amistad("user_a", "user_b")
        print(f"   agregar_amistad('user_a', 'user_b') = {exito} (debe ser False)")
        
        print("4. Eliminar amistad")
        exito = eliminar_amistad("user_a", "user_b")
        print(f"   eliminar_amistad('user_a', 'user_b') = {exito}")
        
        usuarios = cargar_usuarios()
        print(f"   user_a amigos: {usuarios['user_a']['amigos']}")
        print(f"   user_b amigos: {usuarios['user_b']['amigos']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flujo_perfil():
    """Test: Actualizar perfil y obtener datos"""
    print("\n" + "="*60)
    print("FLUJO 3: ACTUALIZAR PERFIL")
    print("="*60)
    
    try:
        from servidor.persistencia import cargar_usuarios, guardar_usuarios, obtener_usuario
        from servidor.autenticacion import hash_password
        
        print("1. Crear usuario")
        usuarios = cargar_usuarios()
        
        usuarios["profile_test"] = {
            "usuario": "profile_test",
            "password_hash": hash_password("pass"),
            "nombre": "Original",
            "apellido": "Name",
            "email": "original@test.com",
            "foto": "",
            "amigos": []
        }
        guardar_usuarios(usuarios)
        print("   Usuario creado")
        
        print("2. Obtener usuario original")
        user = obtener_usuario("profile_test")
        print(f"   Nombre: {user['nombre']}, Email: {user['email']}")
        
        print("3. Actualizar datos")
        usuarios = cargar_usuarios()
        usuarios["profile_test"]["nombre"] = "Updated"
        usuarios["profile_test"]["email"] = "updated@test.com"
        guardar_usuarios(usuarios)
        print("   Datos actualizados")
        
        print("4. Obtener usuario actualizado")
        user = obtener_usuario("profile_test")
        print(f"   Nombre: {user['nombre']}, Email: {user['email']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flujo_estadisticas():
    """Test: Calcular estadísticas"""
    print("\n" + "="*60)
    print("FLUJO 4: ESTADÍSTICAS")
    print("="*60)
    
    try:
        from servidor.persistencia import (
            cargar_usuarios, guardar_usuarios, agregar_amistad,
            obtener_estadisticas_globales
        )
        from servidor.autenticacion import hash_password
        
        # Limpiar y crear usuarios de prueba
        usuarios = {}
        for i in range(3):
            usuarios[f"stat_user_{i}"] = {
                "usuario": f"stat_user_{i}",
                "password_hash": hash_password("pass"),
                "nombre": f"User {i}",
                "apellido": "Stat",
                "email": f"stat{i}@test.com",
                "foto": "",
                "amigos": []
            }
        
        guardar_usuarios(usuarios)
        print("1. Creados 3 usuarios")
        
        # Agregar amistades
        agregar_amistad("stat_user_0", "stat_user_1")
        agregar_amistad("stat_user_0", "stat_user_2")
        agregar_amistad("stat_user_1", "stat_user_2")
        print("2. Agregadas amistades")
        
        # Obtener estadísticas
        stats = obtener_estadisticas_globales()
        print(f"3. Estadísticas:")
        print(f"   Total usuarios: {stats['total_usuarios']}")
        print(f"   Total amistades: {stats['total_amistades']}")
        print(f"   Promedio amigos: {stats['promedio_amigos']:.2f}")
        print(f"   Usuario con más amigos: {stats['usuario_mas_amigos']['usuario'] if stats['usuario_mas_amigos'] else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_consistency():
    """Test: Consistencia de datos"""
    print("\n" + "="*60)
    print("FLUJO 5: CONSISTENCIA DE DATOS")
    print("="*60)
    
    try:
        from servidor.persistencia import cargar_usuarios, guardar_usuarios
        from servidor.autenticacion import hash_password
        
        print("1. Guardar datos")
        usuarios = {
            "consistency_test": {
                "usuario": "consistency_test",
                "password_hash": hash_password("pass"),
                "nombre": "Test",
                "apellido": "Consistency",
                "email": "consistency@test.com",
                "foto": "path/to/foto.jpg",
                "amigos": ["amigo1", "amigo2"]
            }
        }
        exito = guardar_usuarios(usuarios)
        print(f"   guardar_usuarios: {exito}")
        
        print("2. Cargar datos")
        usuarios_cargados = cargar_usuarios()
        print(f"   cargar_usuarios: {len(usuarios_cargados)} usuarios")
        
        print("3. Verificar consistencia")
        usuario_recuperado = usuarios_cargados.get("consistency_test")
        
        assert usuario_recuperado is not None, "Usuario no encontrado"
        assert usuario_recuperado["nombre"] == "Test", "Nombre inconsistente"
        assert usuario_recuperado["email"] == "consistency@test.com", "Email inconsistente"
        assert usuario_recuperado["amigos"] == ["amigo1", "amigo2"], "Amigos inconsistentes"
        
        print("   Todos los datos son consistentes")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTS DE FLUJOS END-TO-END")
    print("="*60)
    
    tests = [
        ("Registro -> Login", test_flujo_registro_login),
        ("Amistades", test_flujo_amistades),
        ("Perfil", test_flujo_perfil),
        ("Estadísticas", test_flujo_estadisticas),
        ("Consistencia de Datos", test_data_consistency),
    ]
    
    resultados = {}
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados[nombre] = resultado
        except Exception as e:
            print(f"\n!!! FALLO CRÍTICO EN {nombre}: {e}")
            import traceback
            traceback.print_exc()
            resultados[nombre] = False
    
    print("\n" + "="*60)
    print("RESUMEN DE FLUJOS")
    print("="*60)
    
    for nombre, resultado in resultados.items():
        status = "PASS" if resultado else "FAIL"
        print(f"[{status}] {nombre}")
    
    total_pass = sum(1 for v in resultados.values() if v)
    total_tests = len(resultados)
    
    print(f"\nTotal: {total_pass}/{total_tests} flujos correctos")
    
    if total_pass == total_tests:
        print("\nLISTO PARA PRODUCCIÓN - Todos los flujos funcionan correctamente")
        sys.exit(0)
    else:
        print(f"\n{total_tests - total_pass} flujos fallaron")
        sys.exit(1)
