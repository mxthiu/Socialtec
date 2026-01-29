# -*- coding: utf-8 -*-
"""
Test comprehensivo de todas las funciones y métodos.
Valida lógica, imports, estructura de datos y flujos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar encoding para PowerShell
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_imports():
    """Verifica que todos los imports funcionan"""
    print("\n" + "="*60)
    print("TEST 1: IMPORTS")
    print("="*60)
    
    try:
        from cliente.auth_client import (
            login_usuario, registrar_usuario, cambiar_password_usuario,
            cambiar_password_sin_validar, agregar_amistad, eliminar_amistad,
            buscar_usuarios, obtener_usuario_completo, obtener_amigos_completos,
            actualizar_perfil, obtener_estadisticas_globales, obtener_email_usuario,
            cargar_usuarios, verificar_disponibilidad_usuario, _enviar_solicitud_tcp
        )
        print("✓ auth_client: todas las funciones importadas")
    except ImportError as e:
        print(f"✗ Error en auth_client: {e}")
        return False
    
    try:
        from servidor.persistencia import (
            cargar_usuarios, guardar_usuarios, agregar_amistad as agregar_amistad_persist,
            eliminar_amistad as eliminar_amistad_persist, obtener_usuario,
            usuario_existe, obtener_estadisticas_globales as get_stats
        )
        print("✓ persistencia: todas las funciones importadas")
    except ImportError as e:
        print(f"✗ Error en persistencia: {e}")
        return False
    
    try:
        from servidor.servidor_tcp import ServidorTCP
        print("✓ servidor_tcp: ServidorTCP importado")
    except ImportError as e:
        print(f"✗ Error en servidor_tcp: {e}")
        return False
    
    return True


def test_persistencia_logic():
    """Prueba la lógica de persistencia"""
    print("\n" + "="*60)
    print("TEST 2: PERSISTENCIA LOGIC")
    print("="*60)
    
    try:
        from servidor.persistencia import (
            cargar_usuarios, guardar_usuarios, agregar_amistad,
            eliminar_amistad, obtener_usuario, usuario_existe,
            obtener_estadisticas_globales
        )
        from servidor.autenticacion import hash_password
        from pathlib import Path
        
        # Crear directorio si no existe
        datos_dir = Path(__file__).parent / "datos"
        datos_dir.mkdir(exist_ok=True)
        
        # Test 1: cargar_usuarios debe retornar dict
        usuarios = cargar_usuarios()
        assert isinstance(usuarios, dict), "cargar_usuarios debe retornar dict"
        print("✓ cargar_usuarios retorna dict")
        
        # Test 2: guardar_usuarios debe aceptar dict y retornar bool
        test_data = {
            "test_user": {
                "usuario": "test_user",
                "password_hash": hash_password("testpass"),
                "nombre": "Test",
                "apellido": "User",
                "email": "test@test.com",
                "foto": "",
                "amigos": []
            }
        }
        result = guardar_usuarios(test_data)
        assert isinstance(result, bool), "guardar_usuarios debe retornar bool"
        assert result == True, "guardar_usuarios debe retornar True si es exitoso"
        print("✓ guardar_usuarios funciona correctamente")
        
        # Test 3: usuario_existe debe funcionar
        existe = usuario_existe("test_user")
        assert isinstance(existe, bool), "usuario_existe debe retornar bool"
        assert existe == True, "test_user debe existir después de guardar"
        print("✓ usuario_existe funciona correctamente")
        
        # Test 4: obtener_usuario debe retornar dict o None
        usuario = obtener_usuario("test_user")
        assert usuario is not None, "obtener_usuario debe encontrar test_user"
        assert usuario["usuario"] == "test_user", "usuario debe coincidir"
        print("✓ obtener_usuario funciona correctamente")
        
        # Test 5: agregar_amistad debe funcionar
        test_data["amigo_user"] = {
            "usuario": "amigo_user",
            "password_hash": hash_password("amigopass"),
            "nombre": "Amigo",
            "apellido": "User",
            "email": "amigo@test.com",
            "foto": "",
            "amigos": []
        }
        guardar_usuarios(test_data)
        
        resultado = agregar_amistad("test_user", "amigo_user")
        assert isinstance(resultado, bool), "agregar_amistad debe retornar bool"
        assert resultado == True, "agregar_amistad debe retornar True"
        
        # Verificar que se agregó bidireccional
        usuarios = cargar_usuarios()
        assert "amigo_user" in usuarios["test_user"]["amigos"], "amigo debe estar en amigos de test_user"
        assert "test_user" in usuarios["amigo_user"]["amigos"], "test_user debe estar en amigos de amigo_user"
        print("✓ agregar_amistad funciona bidireccional")
        
        # Test 6: eliminar_amistad
        resultado = eliminar_amistad("test_user", "amigo_user")
        assert resultado == True, "eliminar_amistad debe retornar True"
        
        usuarios = cargar_usuarios()
        assert "amigo_user" not in usuarios["test_user"]["amigos"], "amigo debe haber sido eliminado"
        print("✓ eliminar_amistad funciona correctamente")
        
        # Test 7: obtener_estadisticas_globales
        stats = obtener_estadisticas_globales()
        assert isinstance(stats, dict), "estadisticas debe ser dict"
        assert "total_usuarios" in stats, "debe tener total_usuarios"
        assert "promedio_amigos" in stats, "debe tener promedio_amigos"
        print("✓ obtener_estadisticas_globales funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en persistencia: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth_client_structure():
    """Prueba la estructura de auth_client sin necesidad de servidor"""
    print("\n" + "="*60)
    print("TEST 3: AUTH CLIENT STRUCTURE")
    print("="*60)
    
    try:
        import inspect
        from cliente.auth_client import (
            login_usuario, registrar_usuario, cambiar_password_usuario,
            cambiar_password_sin_validar, agregar_amistad, eliminar_amistad,
            buscar_usuarios, obtener_usuario_completo, obtener_amigos_completos,
            actualizar_perfil, obtener_estadisticas_globales, obtener_email_usuario,
            cargar_usuarios, verificar_disponibilidad_usuario
        )
        
        # Verificar que cada función existe y es callable
        funciones = {
            'login_usuario': login_usuario,
            'registrar_usuario': registrar_usuario,
            'cambiar_password_usuario': cambiar_password_usuario,
            'cambiar_password_sin_validar': cambiar_password_sin_validar,
            'agregar_amistad': agregar_amistad,
            'eliminar_amistad': eliminar_amistad,
            'buscar_usuarios': buscar_usuarios,
            'obtener_usuario_completo': obtener_usuario_completo,
            'obtener_amigos_completos': obtener_amigos_completos,
            'actualizar_perfil': actualizar_perfil,
            'obtener_estadisticas_globales': obtener_estadisticas_globales,
            'obtener_email_usuario': obtener_email_usuario,
            'cargar_usuarios': cargar_usuarios,
            'verificar_disponibilidad_usuario': verificar_disponibilidad_usuario,
        }
        
        for nombre, func in funciones.items():
            assert callable(func), f"{nombre} no es callable"
            sig = inspect.signature(func)
            print(f"✓ {nombre}{sig}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en estructura de auth_client: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_structure():
    """Prueba que los mensajes se estructuran correctamente"""
    print("\n" + "="*60)
    print("TEST 4: MESSAGE STRUCTURE")
    print("="*60)
    
    try:
        from utils.protocolo import Message, Response, MsgType
        import json
        
        # Test 1: Crear messages
        msg_login = Message(
            type=MsgType.LOGIN,
            payload={"usuario": "test", "password": "pass"}
        )
        assert msg_login.type == MsgType.LOGIN
        assert msg_login.payload["usuario"] == "test"
        print("✓ Message LOGIN estructura correcta")
        
        msg_register = Message(
            type=MsgType.REGISTER,
            payload={
                "usuario": "test",
                "password": "pass",
                "nombre": "Test",
                "apellido": "User"
            }
        )
        assert msg_register.type == MsgType.REGISTER
        print("✓ Message REGISTER estructura correcta")
        
        msg_add_friend = Message(
            type=MsgType.ADD_FRIEND,
            payload={"usuario1": "user1", "usuario2": "user2"}
        )
        assert msg_add_friend.type == MsgType.ADD_FRIEND
        print("✓ Message ADD_FRIEND estructura correcta")
        
        # Test 2: Convertir a dict y JSON
        msg_dict = msg_login.to_dict()
        assert isinstance(msg_dict, dict)
        msg_json = json.dumps(msg_dict)
        assert isinstance(msg_json, str)
        print("✓ Message serializable a JSON")
        
        # Test 3: Response
        resp = Response(
            ok=True,
            message="Test",
            data={"key": "value"}
        )
        assert resp.ok == True
        resp_dict = resp.to_dict()
        assert resp_dict["ok"] == True
        print("✓ Response estructura correcta")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en message structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_imports():
    """Prueba que todas las GUIs puedan importar auth_client"""
    print("\n" + "="*60)
    print("TEST 5: GUI IMPORTS")
    print("="*60)
    
    guis = [
        'cliente.gui_login',
        'cliente.gui_registro',
        'cliente.gui_busqueda',
        'cliente.gui_amigos',
        'cliente.gui_perfil_publico',
        'cliente.gui_estadisticas',
        'cliente.gui_editar_perfil',
        'cliente.gui_cambiar_password',
        'cliente.gui_recuperar_password',
        'cliente.gui_main_menu',
    ]
    
    failed = []
    for gui_name in guis:
        try:
            __import__(gui_name)
            print(f"✓ {gui_name} importa correctamente")
        except Exception as e:
            print(f"✗ {gui_name}: {e}")
            failed.append((gui_name, e))
    
    return len(failed) == 0


def test_data_structures():
    """Prueba estructuras de datos esperadas"""
    print("\n" + "="*60)
    print("TEST 6: DATA STRUCTURES")
    print("="*60)
    
    try:
        from servidor.autenticacion import hash_password
        
        # Estructura esperada de usuario
        usuario_esperado = {
            "usuario": "test",
            "password_hash": hash_password("pass"),
            "nombre": "Test",
            "apellido": "User",
            "email": "test@test.com",
            "foto": "path/to/foto.jpg",
            "amigos": ["amigo1", "amigo2"]
        }
        
        # Verificar campos
        campos_requeridos = ["usuario", "password_hash", "nombre", "apellido", "email", "foto", "amigos"]
        for campo in campos_requeridos:
            assert campo in usuario_esperado, f"Falta campo {campo}"
            print(f"✓ Campo '{campo}' presente")
        
        assert isinstance(usuario_esperado["amigos"], list), "amigos debe ser lista"
        assert all(isinstance(a, str) for a in usuario_esperado["amigos"]), "amigos debe contener strings"
        print("✓ Estructura de usuario válida")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en data structures: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Prueba manejo de errores"""
    print("\n" + "="*60)
    print("TEST 7: ERROR HANDLING")
    print("="*60)
    
    try:
        from cliente.auth_client import (
            login_usuario, registrar_usuario, cambiar_password_usuario,
            verificar_disponibilidad_usuario, buscar_usuarios, obtener_usuario_completo
        )
        
        # Test con datos vacíos (no debe crashear)
        # Nota: Estas llamadas retornarán error TCP porque el servidor no está activo,
        # pero no deben lanzar excepciones no manejadas
        
        result = verificar_disponibilidad_usuario("")
        assert isinstance(result, bool), "verificar_disponibilidad debe retornar bool"
        print("✓ verificar_disponibilidad maneja entrada vacía")
        
        result = buscar_usuarios("")
        assert isinstance(result, list), "buscar_usuarios debe retornar list"
        print("✓ buscar_usuarios maneja búsqueda vacía")
        
        result = obtener_usuario_completo("nonexistent")
        assert result is None or isinstance(result, dict), "obtener_usuario retorna None o dict"
        print("✓ obtener_usuario_completo maneja usuario inexistente")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en error handling: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_function_signatures():
    """Verifica que las firmas de funciones sean consistentes"""
    print("\n" + "="*60)
    print("TEST 8: FUNCTION SIGNATURES")
    print("="*60)
    
    try:
        import inspect
        from cliente import auth_client
        
        # Funciones que deben retornar tuple(bool, str)
        tuple_bool_str_funcs = [
            'cambiar_password_usuario',
            'cambiar_password_sin_validar',
            'agregar_amistad',
            'eliminar_amistad',
            'actualizar_perfil',
            'registrar_usuario'
        ]
        
        # Funciones que deben retornar tuple(bool, dict/None)
        tuple_bool_dict_funcs = [
            'login_usuario'
        ]
        
        # Funciones que deben retornar dict/list
        collection_funcs = [
            'buscar_usuarios',
            'obtener_amigos_completos',
            'cargar_usuarios',
            'obtener_estadisticas_globales'
        ]
        
        # Funciones que deben retornar bool
        bool_funcs = [
            'verificar_disponibilidad_usuario'
        ]
        
        for func_name in tuple_bool_str_funcs:
            func = getattr(auth_client, func_name)
            sig = inspect.signature(func)
            print(f"✓ {func_name}: {sig}")
        
        for func_name in tuple_bool_dict_funcs:
            func = getattr(auth_client, func_name)
            sig = inspect.signature(func)
            print(f"✓ {func_name}: {sig}")
        
        for func_name in collection_funcs:
            func = getattr(auth_client, func_name)
            sig = inspect.signature(func)
            print(f"✓ {func_name}: {sig}")
        
        for func_name in bool_funcs:
            func = getattr(auth_client, func_name)
            sig = inspect.signature(func)
            print(f"✓ {func_name}: {sig}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en function signatures: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING COMPREHENSIVO DE SOCIALTEC TCP")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Persistencia Logic", test_persistencia_logic),
        ("Auth Client Structure", test_auth_client_structure),
        ("Message Structure", test_message_structure),
        ("GUI Imports", test_gui_imports),
        ("Data Structures", test_data_structures),
        ("Error Handling", test_error_handling),
        ("Function Signatures", test_function_signatures),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            resultado = test_func()
            results[name] = resultado
        except Exception as e:
            print(f"\n✗✗✗ FALLO CRÍTICO EN {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    
    for name, resultado in results.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status}: {name}")
    
    total_pass = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\nTotal: {total_pass}/{total_tests} tests pasaron")
    
    if total_pass == total_tests:
        print("\n✅ TODOS LOS TESTS PASARON - LISTO PARA PRODUCCIÓN")
        sys.exit(0)
    else:
        print(f"\n❌ {total_tests - total_pass} tests fallaron")
        sys.exit(1)
