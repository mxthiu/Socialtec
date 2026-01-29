# -*- coding: utf-8 -*-
"""
Test exhaustivo de:
1. Obtener estadísticas globales
2. Editar perfil
3. Guardar datos
4. Validar todo funciona
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_estadisticas_globales():
    """Test: Estadísticas globales desde el servidor"""
    print("\n" + "="*70)
    print("TEST 1: ESTADÍSTICAS GLOBALES")
    print("="*70)
    
    from servidor.persistencia import cargar_usuarios, guardar_usuarios, agregar_amistad
    from servidor.autenticacion import hash_password
    from grafo.algoritmos import calcular_estadisticas, estadisticas_como_dict
    from grafo.grafo import Grafo
    
    # Crear usuarios
    print("\n1. Creando usuarios de prueba...")
    usuarios = {
        "user_test_1": {
            "usuario": "user_test_1",
            "password_hash": hash_password("pass123"),
            "nombre": "Test",
            "apellido": "Uno",
            "email": "test1@test.com",
            "foto": "",
            "amigos": []
        },
        "user_test_2": {
            "usuario": "user_test_2",
            "password_hash": hash_password("pass123"),
            "nombre": "Test",
            "apellido": "Dos",
            "email": "test2@test.com",
            "foto": "",
            "amigos": []
        },
        "user_test_3": {
            "usuario": "user_test_3",
            "password_hash": hash_password("pass123"),
            "nombre": "Test",
            "apellido": "Tres",
            "email": "test3@test.com",
            "foto": "",
            "amigos": []
        }
    }
    guardar_usuarios(usuarios)
    print("   ✓ Usuarios creados")
    
    # Agregar amistades
    print("\n2. Agregando amistades...")
    agregar_amistad("user_test_1", "user_test_2")
    agregar_amistad("user_test_1", "user_test_3")
    agregar_amistad("user_test_2", "user_test_3")
    print("   ✓ Amistades agregadas")
    
    # Cargar usuarios y crear grafo
    print("\n3. Calculando estadísticas...")
    usuarios = cargar_usuarios()
    
    # Crear grafo
    grafo = Grafo()
    for usuario_data in usuarios.values():
        grafo.agregar_nodo(usuario_data["usuario"])
        for amigo in usuario_data.get("amigos", []):
            grafo.agregar_arista(usuario_data["usuario"], amigo)
    
    # Calcular estadísticas
    stats = calcular_estadisticas(grafo)
    stats_dict = estadisticas_como_dict(stats)
    
    print(f"   Stats raw: {stats_dict}")
    
    # Mapear para compatibilidad con GUI
    data_final = {
        "total_usuarios": stats_dict.get("cantidad_usuarios", 0),
        "total_amistades": stats_dict.get("cantidad_amistades", 0),
        "promedio_amigos": stats_dict.get("promedio_amigos", 0),
        "usuario_mas_amigos": {
            "usuario": stats_dict.get("usuario_con_mas_amigos", ""),
            "amigos": stats_dict.get("max_amigos", 0)
        } if stats_dict.get("usuario_con_mas_amigos") else None,
        "usuario_menos_amigos": {
            "usuario": stats_dict.get("usuario_con_menos_amigos", ""),
            "amigos": stats_dict.get("min_amigos", 0)
        } if stats_dict.get("usuario_con_menos_amigos") else None
    }
    
    print(f"\n   Data final: {data_final}")
    
    # Validar estructura
    assert "total_usuarios" in data_final
    assert "total_amistades" in data_final
    assert "promedio_amigos" in data_final
    assert data_final["total_usuarios"] > 0
    
    print("\n   ✓ Estadísticas calculadas correctamente")
    return True


def test_editar_perfil():
    """Test: Editar perfil y guardar"""
    print("\n" + "="*70)
    print("TEST 2: EDITAR PERFIL")
    print("="*70)
    
    from servidor.persistencia import cargar_usuarios, guardar_usuarios, obtener_usuario
    from servidor.autenticacion import hash_password
    
    # Crear usuario
    print("\n1. Crear usuario...")
    usuarios = cargar_usuarios()
    
    usuarios["profile_edit_test"] = {
        "usuario": "profile_edit_test",
        "password_hash": hash_password("pass123"),
        "nombre": "Original",
        "apellido": "Name",
        "email": "original@test.com",
        "foto": "",
        "amigos": []
    }
    guardar_usuarios(usuarios)
    print("   ✓ Usuario creado")
    
    # Obtener usuario original
    print("\n2. Obtener datos originales...")
    user = obtener_usuario("profile_edit_test")
    print(f"   Nombre original: {user['nombre']}")
    print(f"   Email original: {user['email']}")
    assert user["nombre"] == "Original"
    
    # Editar perfil
    print("\n3. Editar perfil...")
    usuarios = cargar_usuarios()
    usuarios["profile_edit_test"]["nombre"] = "Actualizado"
    usuarios["profile_edit_test"]["email"] = "updated@test.com"
    usuarios["profile_edit_test"]["apellido"] = "Apellido"
    guardar_usuarios(usuarios)
    print("   ✓ Perfil actualizado en persistencia")
    
    # Verificar cambios
    print("\n4. Verificar cambios...")
    user = obtener_usuario("profile_edit_test")
    print(f"   Nombre nuevo: {user['nombre']}")
    print(f"   Email nuevo: {user['email']}")
    assert user["nombre"] == "Actualizado"
    assert user["email"] == "updated@test.com"
    print("   ✓ Cambios guardados correctamente")
    
    return True


def test_guardar_y_cargar():
    """Test: Guardar y cargar datos completos"""
    print("\n" + "="*70)
    print("TEST 3: GUARDAR Y CARGAR DATOS")
    print("="*70)
    
    from servidor.persistencia import cargar_usuarios, guardar_usuarios
    from servidor.autenticacion import hash_password
    
    print("\n1. Crear datos complejos...")
    usuarios = {
        "save_test_1": {
            "usuario": "save_test_1",
            "password_hash": hash_password("complejPass!@#"),
            "nombre": "Nombre Acentuado: áéíóú",
            "apellido": "Apellido \"especial\"",
            "email": "test+tag@example.com",
            "foto": "C:/path/to/foto_ñoño.jpg",
            "amigos": ["save_test_2", "save_test_3"]
        },
        "save_test_2": {
            "usuario": "save_test_2",
            "password_hash": hash_password("pass456"),
            "nombre": "User 2",
            "apellido": "Test",
            "email": "test2@example.com",
            "foto": "",
            "amigos": ["save_test_1"]
        }
    }
    
    print("   ✓ Datos creados")
    
    print("\n2. Guardar a archivo...")
    exito = guardar_usuarios(usuarios)
    assert exito
    print("   ✓ Guardado exitoso")
    
    print("\n3. Cargar de archivo...")
    usuarios_cargados = cargar_usuarios()
    print(f"   ✓ Cargados {len(usuarios_cargados)} usuarios")
    
    print("\n4. Verificar integridad...")
    user1 = usuarios_cargados["save_test_1"]
    assert user1["nombre"] == "Nombre Acentuado: áéíóú"
    assert user1["email"] == "test+tag@example.com"
    assert user1["amigos"] == ["save_test_2", "save_test_3"]
    print("   ✓ Integridad verificada")
    
    return True


def test_flujo_completo():
    """Test: Flujo completo de aplicación"""
    print("\n" + "="*70)
    print("TEST 4: FLUJO COMPLETO")
    print("="*70)
    
    from servidor.persistencia import (
        cargar_usuarios, guardar_usuarios, agregar_amistad, 
        eliminar_amistad, obtener_usuario, usuario_existe
    )
    from servidor.autenticacion import hash_password, validar_login
    
    print("\n1. Registrar usuario...")
    usuarios = {}
    usuarios["flujo_user_1"] = {
        "usuario": "flujo_user_1",
        "password_hash": hash_password("FlujPass123"),
        "nombre": "Flujo",
        "apellido": "Usuario",
        "email": "flujo@test.com",
        "foto": "",
        "amigos": []
    }
    guardar_usuarios(usuarios)
    assert usuario_existe("flujo_user_1")
    print("   ✓ Usuario registrado")
    
    print("\n2. Login...")
    usuarios = cargar_usuarios()
    exito, msg = validar_login("flujo_user_1", "FlujPass123", usuarios)
    assert exito
    print(f"   ✓ Login exitoso: {msg}")
    
    print("\n3. Obtener perfil...")
    user = obtener_usuario("flujo_user_1")
    assert user is not None
    print(f"   ✓ Perfil obtenido: {user['nombre']} {user['apellido']}")
    
    print("\n4. Editar perfil...")
    usuarios = cargar_usuarios()
    usuarios["flujo_user_1"]["email"] = "newemail@test.com"
    guardar_usuarios(usuarios)
    user = obtener_usuario("flujo_user_1")
    assert user["email"] == "newemail@test.com"
    print("   ✓ Perfil actualizado")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTS EXHAUSTIVOS - ESTADÍSTICAS, EDITAR PERFIL, GUARDAR DATOS")
    print("="*70)
    
    tests = [
        ("Estadísticas Globales", test_estadisticas_globales),
        ("Editar Perfil", test_editar_perfil),
        ("Guardar y Cargar", test_guardar_y_cargar),
        ("Flujo Completo", test_flujo_completo),
    ]
    
    resultados = {}
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados[nombre] = resultado
        except Exception as e:
            print(f"\n✗ FALLO EN {nombre}: {e}")
            import traceback
            traceback.print_exc()
            resultados[nombre] = False
    
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    
    for nombre, resultado in resultados.items():
        status = "✓ PASS" if resultado else "✗ FAIL"
        print(f"[{status}] {nombre}")
    
    total_pass = sum(1 for v in resultados.values() if v)
    total_tests = len(resultados)
    
    print(f"\nTotal: {total_pass}/{total_tests} tests correctos")
    
    if total_pass == total_tests:
        print("\n✅ TODOS LOS TESTS PASARON - SISTEMA FUNCIONAL")
    else:
        print(f"\n❌ {total_tests - total_pass} tests fallaron")
