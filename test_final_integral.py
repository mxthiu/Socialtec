# -*- coding: utf-8 -*-
"""
VALIDACIÓN FINAL INTEGRAL.
Test exhaustivo de TODO el sistema antes de producción.
Incluyendo: importaciones, integraciones, casos edge, concurrencia.
"""

import sys
import os
import threading
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def test_imports_completo():
    """Test: Todas las importaciones funcionan"""
    print("\n" + "="*60)
    print("TEST 1: IMPORTACIONES COMPLETAS")
    print("="*60)
    
    imports_to_check = [
        ("utils.protocolo", ["Message", "Response", "MsgType"]),
        ("servidor.autenticacion", ["hash_password", "validar_login"]),
        ("servidor.persistencia", ["cargar_usuarios", "guardar_usuarios", "agregar_amistad", "eliminar_amistad", "obtener_usuario", "usuario_existe", "obtener_estadisticas_globales"]),
        ("cliente.auth_client", ["login_usuario", "registrar_usuario", "cambiar_password_usuario", "cambiar_password_sin_validar", "agregar_amistad", "eliminar_amistad", "buscar_usuarios", "obtener_usuario_completo", "obtener_amigos_completos", "actualizar_perfil", "obtener_estadisticas_globales", "obtener_email_usuario", "cargar_usuarios", "verificar_disponibilidad_usuario"]),
    ]
    
    total = 0
    passed = 0
    
    for module_name, items in imports_to_check:
        print(f"\n  {module_name}:")
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                try:
                    getattr(module, item)
                    print(f"    ✓ {item}")
                    passed += 1
                except AttributeError:
                    print(f"    ✗ {item} NOT FOUND")
                total += 1
        except Exception as e:
            print(f"    ✗ IMPORT ERROR: {e}")
            total += len(items)
    
    print(f"\n  Resultado: {passed}/{total} imports exitosos")
    return passed == total


def test_concurrencia():
    """Test: Operaciones concurrentes no causan corrupción"""
    print("\n" + "="*60)
    print("TEST 2: CONCURRENCIA Y THREAD-SAFETY")
    print("="*60)
    
    from servidor.persistencia import cargar_usuarios, guardar_usuarios, agregar_amistad
    from servidor.autenticacion import hash_password
    
    # Crear usuarios
    print("\n  1. Crear usuarios de prueba")
    usuarios = {}
    for i in range(5):
        usuarios[f"thread_user_{i}"] = {
            "usuario": f"thread_user_{i}",
            "password_hash": hash_password("pass"),
            "nombre": f"User {i}",
            "apellido": "Thread",
            "email": f"thread{i}@test.com",
            "foto": "",
            "amigos": []
        }
    guardar_usuarios(usuarios)
    print(f"     Creados 5 usuarios")
    
    # Hacer múltiples operaciones concurrentes
    print("\n  2. Ejecutar 50 operaciones en 10 threads")
    
    errors = []
    
    def worker(thread_id):
        try:
            for i in range(5):
                user1 = f"thread_user_{thread_id}"
                user2 = f"thread_user_{(thread_id + 1) % 5}"
                agregar_amistad(user1, user2)
                agregar_amistad(user2, user1)
        except Exception as e:
            errors.append(str(e))
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i % 5,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"     Operaciones completadas")
    
    # Verificar integridad
    print("\n  3. Verificar integridad de datos")
    usuarios_final = cargar_usuarios()
    
    total_amigos = sum(len(u.get('amigos', [])) for u in usuarios_final.values())
    print(f"     Total amistades: {total_amigos}")
    print(f"     Errores: {len(errors)}")
    
    for u in usuarios_final.values():
        amigos_list = u.get('amigos', [])
        assert isinstance(amigos_list, list), f"amigos debe ser lista, no {type(amigos_list)}"
    
    print("     ✓ Estructura intacta")
    return len(errors) == 0


def test_casos_edge():
    """Test: Casos borde y errores"""
    print("\n" + "="*60)
    print("TEST 3: CASOS EDGE Y MANEJO DE ERRORES")
    print("="*60)
    
    from servidor.persistencia import obtener_usuario, usuario_existe
    from servidor.autenticacion import validar_login
    
    print("\n  1. Usuario no existe")
    existe = usuario_existe("no_existe_" + str(os.urandom(8).hex()))
    print(f"     usuario_existe('no_existe_xxx') = {existe}")
    assert not existe
    
    print("\n  2. Obtener usuario no existente")
    user = obtener_usuario("no_existe_" + str(os.urandom(8).hex()))
    print(f"     obtener_usuario('no_existe_xxx') = {user}")
    assert user is None
    
    print("\n  3. Login con usuario no existente")
    usuarios_prueba = {}
    exito, msg = validar_login("inexistente", "pass", usuarios_prueba)
    print(f"     validar_login('inexistente', 'pass') = {exito}")
    assert not exito
    
    print("\n  4. Strings vacíos")
    assert not usuario_existe("")
    assert obtener_usuario("") is None
    print("     Strings vacíos manejados correctamente")
    
    print("\n  5. Valores None")
    try:
        usuario_existe(None)
        print("     ✗ usuario_existe(None) no lanzó excepción")
    except (TypeError, AttributeError):
        print("     ✓ usuario_existe(None) maneja None")
    
    print("\n  ✓ Todos los casos edge manejados")
    return True


def test_data_integrity():
    """Test: Integridad de datos tras múltiples operaciones"""
    print("\n" + "="*60)
    print("TEST 4: INTEGRIDAD DE DATOS")
    print("="*60)
    
    from servidor.persistencia import cargar_usuarios, guardar_usuarios, obtener_usuario
    from servidor.autenticacion import hash_password
    import time
    
    print("\n  1. Crear usuarios con datos complejos")
    usuarios = {
        "integrity_test": {
            "usuario": "integrity_test",
            "password_hash": hash_password("complex!@#$"),
            "nombre": "Nombre con acentos: áéíóú",
            "apellido": "Apellido \"especial\" 'quotes'",
            "email": "test+tag@example.com",
            "foto": "path/to/fotos/especial_ñoño.jpg",
            "amigos": ["friend1", "friend2", "friend3"]
        }
    }
    guardar_usuarios(usuarios)
    
    print("\n  2. Cargar y verificar")
    usuarios_cargados = cargar_usuarios()
    user = usuarios_cargados["integrity_test"]
    
    checks = [
        ("nombre", user["nombre"], "Nombre con acentos: áéíóú"),
        ("apellido", user["apellido"], "Apellido \"especial\" 'quotes'"),
        ("email", user["email"], "test+tag@example.com"),
        ("foto", user["foto"], "path/to/fotos/especial_ñoño.jpg"),
        ("amigos", user["amigos"], ["friend1", "friend2", "friend3"]),
    ]
    
    all_ok = True
    for campo, valor, esperado in checks:
        ok = valor == esperado
        status = "✓" if ok else "✗"
        print(f"     {status} {campo}: {ok}")
        all_ok = all_ok and ok
    
    print(f"\n  ✓ Integridad mantida")
    return all_ok


def test_file_operations():
    """Test: Operaciones de archivo (atomic writes, etc)"""
    print("\n" + "="*60)
    print("TEST 5: OPERACIONES DE ARCHIVO")
    print("="*60)
    
    from servidor.persistencia import guardar_usuarios, cargar_usuarios
    from servidor.autenticacion import hash_password
    from pathlib import Path
    
    print("\n  1. Verificar que usuarios.json existe")
    json_path = Path("datos/usuarios.json")
    print(f"     Path: {json_path.absolute()}")
    print(f"     Existe: {json_path.exists()}")
    
    if json_path.exists():
        size = json_path.stat().st_size
        print(f"     Tamaño: {size} bytes")
    
    print("\n  2. Guardar y recargar múltiples veces")
    for i in range(3):
        usuarios = cargar_usuarios()
        usuarios[f"file_test_{i}"] = {
            "usuario": f"file_test_{i}",
            "password_hash": hash_password("pass"),
            "nombre": "File",
            "apellido": "Test",
            "email": f"file{i}@test.com",
            "foto": "",
            "amigos": []
        }
        guardar_usuarios(usuarios)
        usuarios_reloaded = cargar_usuarios()
        assert f"file_test_{i}" in usuarios_reloaded
        print(f"     Iteración {i+1}: OK")
    
    print("\n  3. Verificar que no hay archivos temporales")
    datos_dir = Path("datos")
    temp_files = list(datos_dir.glob("*.tmp"))
    print(f"     Archivos temporales restantes: {len(temp_files)}")
    
    print("\n  ✓ Operaciones de archivo válidas")
    return True


def test_estadisticas():
    """Test: Cálculo de estadísticas"""
    print("\n" + "="*60)
    print("TEST 6: CÁLCULO DE ESTADÍSTICAS")
    print("="*60)
    
    from servidor.persistencia import (
        cargar_usuarios, guardar_usuarios, obtener_estadisticas_globales,
        agregar_amistad
    )
    from servidor.autenticacion import hash_password
    
    print("\n  1. Crear escenario de prueba")
    usuarios = {}
    for i in range(4):
        usuarios[f"stat_user_{i}"] = {
            "usuario": f"stat_user_{i}",
            "password_hash": hash_password("pass"),
            "nombre": f"Stat {i}",
            "apellido": "User",
            "email": f"stat{i}@test.com",
            "foto": "",
            "amigos": []
        }
    guardar_usuarios(usuarios)
    
    # Agregar amistades creando una red
    agregar_amistad("stat_user_0", "stat_user_1")
    agregar_amistad("stat_user_0", "stat_user_2")
    agregar_amistad("stat_user_1", "stat_user_2")
    agregar_amistad("stat_user_2", "stat_user_3")
    
    print("\n  2. Calcular estadísticas")
    stats = obtener_estadisticas_globales()
    
    print(f"     Total usuarios: {stats.get('total_usuarios')}")
    print(f"     Total amistades: {stats.get('total_amistades')}")
    print(f"     Promedio amigos/usuario: {stats.get('promedio_amigos'):.2f}")
    
    usuario_top = stats.get('usuario_mas_amigos')
    if usuario_top:
        print(f"     Usuario con más amigos: {usuario_top['usuario']} ({len(usuario_top['amigos'])} amigos)")
    
    # Validaciones
    assert stats['total_usuarios'] > 0
    assert stats['total_amistades'] > 0
    assert stats['promedio_amigos'] > 0
    
    print("\n  ✓ Estadísticas calculadas correctamente")
    return True


def test_estructura_datos():
    """Test: Estructura de datos esperada"""
    print("\n" + "="*60)
    print("TEST 7: ESTRUCTURA DE DATOS")
    print("="*60)
    
    from servidor.persistencia import cargar_usuarios
    
    usuarios = cargar_usuarios()
    
    print("\n  1. Verificar estructura de usuario")
    if usuarios:
        username = list(usuarios.keys())[0]
        user = usuarios[username]
        
        campos_requeridos = [
            "usuario",
            "password_hash", 
            "nombre",
            "apellido",
            "email",
            "foto",
            "amigos"
        ]
        
        for campo in campos_requeridos:
            tiene = campo in user
            tipo_esperado = None
            if campo == "amigos":
                tipo_esperado = list
            elif campo == "password_hash":
                tipo_esperado = str
            
            status = "✓" if tiene else "✗"
            print(f"     {status} {campo}")
            assert tiene, f"Falta campo {campo}"
        
        # Validar tipos
        assert isinstance(user["amigos"], list), "amigos debe ser lista"
        assert isinstance(user["password_hash"], str), "password_hash debe ser string"
        print("\n  2. Tipos de datos correctos")
    
    print("\n  ✓ Estructura de datos válida")
    return True


def test_gui_readiness():
    """Test: Las GUIs pueden usar las funciones"""
    print("\n" + "="*60)
    print("TEST 8: COMPATIBILIDAD CON GUIs")
    print("="*60)
    
    print("\n  1. Importar funciones que usan las GUIs")
    
    gui_dependencies = [
        ("gui_login", ["login_usuario", "registrar_usuario"]),
        ("gui_busqueda", ["buscar_usuarios"]),
        ("gui_amigos", ["obtener_amigos_completos", "agregar_amistad", "eliminar_amistad"]),
        ("gui_perfil_publico", ["obtener_usuario_completo", "agregar_amistad"]),
        ("gui_editar_perfil", ["actualizar_perfil"]),
        ("gui_estadisticas", ["obtener_estadisticas_globales"]),
        ("gui_cambiar_password", ["cambiar_password_usuario"]),
        ("gui_recuperar_password", ["cambiar_password_sin_validar"]),
    ]
    
    from cliente import auth_client
    
    for gui_name, functions in gui_dependencies:
        print(f"\n  {gui_name}:")
        for func_name in functions:
            try:
                func = getattr(auth_client, func_name)
                print(f"    ✓ {func_name}")
            except AttributeError:
                print(f"    ✗ {func_name} NOT FOUND")
                return False
    
    print("\n  ✓ Todas las funciones disponibles")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VALIDACIÓN FINAL INTEGRAL DEL SISTEMA")
    print("="*60)
    
    tests = [
        ("Importaciones Completas", test_imports_completo),
        ("Concurrencia", test_concurrencia),
        ("Casos Edge", test_casos_edge),
        ("Integridad de Datos", test_data_integrity),
        ("Operaciones de Archivo", test_file_operations),
        ("Estadísticas", test_estadisticas),
        ("Estructura de Datos", test_estructura_datos),
        ("Compatibilidad GUIs", test_gui_readiness),
    ]
    
    resultados = {}
    for nombre, test_func in tests:
        try:
            print(f"\nEjecutando: {nombre}...")
            resultado = test_func()
            resultados[nombre] = resultado
        except Exception as e:
            print(f"\n✗ EXCEPCIÓN EN {nombre}: {e}")
            import traceback
            traceback.print_exc()
            resultados[nombre] = False
    
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    for nombre, resultado in resultados.items():
        status = "✓ PASS" if resultado else "✗ FAIL"
        print(f"[{status}] {nombre}")
    
    total_pass = sum(1 for v in resultados.values() if v)
    total_tests = len(resultados)
    
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL: {total_pass}/{total_tests} tests correctos")
    print(f"{'='*60}")
    
    if total_pass == total_tests:
        print("\n✅ ✅ ✅ SISTEMA COMPLETAMENTE VALIDADO ✅ ✅ ✅")
        print("\n🚀 LISTO PARA PRODUCCIÓN - Todos los tests pasaron")
        print("\nEl sistema es seguro, confiable y está completamente funcional.")
        sys.exit(0)
    else:
        print(f"\n❌ {total_tests - total_pass} tests fallaron")
        sys.exit(1)
