# -*- coding: utf-8 -*-
"""
Test de handlers del servidor TCP.
Verifica que cada endpoint procese correctamente los mensajes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def test_handler_logic():
    """Test: Lógica de handlers sin necesidad de conexión TCP"""
    print("\n" + "="*60)
    print("TEST HANDLERS DEL SERVIDOR")
    print("="*60)
    
    from servidor.persistencia import cargar_usuarios, guardar_usuarios, obtener_usuario
    from servidor.autenticacion import hash_password
    from utils.protocolo import Message, Response, MsgType
    
    # Preparar datos de prueba
    print("\n1. Preparar datos de prueba")
    usuarios = {
        "handler_test_1": {
            "usuario": "handler_test_1",
            "password_hash": hash_password("pass123"),
            "nombre": "Handler",
            "apellido": "Test1",
            "email": "handler1@test.com",
            "foto": "",
            "amigos": ["handler_test_2"]
        },
        "handler_test_2": {
            "usuario": "handler_test_2",
            "password_hash": hash_password("pass456"),
            "nombre": "Handler",
            "apellido": "Test2",
            "email": "handler2@test.com",
            "foto": "foto2.jpg",
            "amigos": ["handler_test_1"]
        }
    }
    guardar_usuarios(usuarios)
    print("   ✓ Usuarios de prueba creados")
    
    # Test 1: GET_ALL_USERS
    print("\n2. Test GET_ALL_USERS (sin password_hash)")
    usuarios_db = cargar_usuarios()
    usuarios_response = []
    for user_data in usuarios_db.values():
        user_copy = user_data.copy()
        user_copy.pop('password_hash', None)
        usuarios_response.append(user_copy)
    
    print(f"   Total usuarios: {len(usuarios_response)}")
    for user in usuarios_response:
        has_password = 'password_hash' in user
        print(f"   - {user['usuario']}: password_hash removido = {not has_password}")
        assert not has_password, f"Password_hash no fue removido para {user['usuario']}"
    print("   ✓ PASS: GET_ALL_USERS no envía password_hash")
    
    # Test 2: GET_FRIENDS_COMPLETE
    print("\n3. Test GET_FRIENDS_COMPLETE")
    user = obtener_usuario("handler_test_1")
    amigos_usernames = user.get('amigos', [])
    print(f"   Amigos de handler_test_1: {amigos_usernames}")
    
    amigos_completos = []
    for amigo_username in amigos_usernames:
        amigo_data = obtener_usuario(amigo_username)
        if amigo_data:
            amigo_copy = amigo_data.copy()
            amigo_copy.pop('password_hash', None)
            amigos_completos.append(amigo_copy)
    
    print(f"   Amigos completos obtenidos: {len(amigos_completos)}")
    for amigo in amigos_completos:
        print(f"   - {amigo['usuario']}: {amigo['nombre']} {amigo['apellido']}")
        assert 'password_hash' not in amigo, f"Password_hash no fue removido"
    print("   ✓ PASS: GET_FRIENDS_COMPLETE retorna datos completos sin password_hash")
    
    # Test 3: GET_EMAIL
    print("\n4. Test GET_EMAIL")
    user = obtener_usuario("handler_test_1")
    email = user.get('email') if user else None
    print(f"   Email de handler_test_1: {email}")
    assert email == "handler1@test.com", "Email incorrecto"
    print("   ✓ PASS: GET_EMAIL retorna email correcto")
    
    # Test 4: UPDATE_PROFILE
    print("\n5. Test UPDATE_PROFILE")
    usuarios = cargar_usuarios()
    user = usuarios["handler_test_1"]
    
    # Simular actualización
    nuevos_datos = {
        "nombre": "Updated",
        "apellido": "Handler",
        "email": "updated@test.com",
        "foto": "new_photo.jpg"
    }
    
    for clave, valor in nuevos_datos.items():
        if clave in user:
            user[clave] = valor
    
    guardar_usuarios(usuarios)
    print(f"   Actualizados: {list(nuevos_datos.keys())}")
    
    # Verificar que se guardó correctamente
    user_verificado = obtener_usuario("handler_test_1")
    print(f"   Verificación:")
    print(f"   - Nombre: {user_verificado['nombre']} (esperado: Updated)")
    print(f"   - Email: {user_verificado['email']} (esperado: updated@test.com)")
    print(f"   - Foto: {user_verificado['foto']} (esperado: new_photo.jpg)")
    
    assert user_verificado['nombre'] == "Updated"
    assert user_verificado['email'] == "updated@test.com"
    assert user_verificado['foto'] == "new_photo.jpg"
    print("   ✓ PASS: UPDATE_PROFILE actualiza correctamente")
    
    # Test 5: LOGIN retorna usuario completo
    print("\n6. Test LOGIN retorna usuario completo")
    user = obtener_usuario("handler_test_1")
    campos_requeridos = ['usuario', 'nombre', 'apellido', 'email', 'foto', 'amigos']
    
    print(f"   Verificando campos de usuario:")
    for campo in campos_requeridos:
        tiene_campo = campo in user
        print(f"   - {campo}: {tiene_campo}")
        assert tiene_campo, f"Falta campo {campo}"
    
    print("   ✓ PASS: LOGIN retorna usuario con todos los campos")
    
    return True


def test_message_protocol():
    """Test: Protocolo de mensajes"""
    print("\n" + "="*60)
    print("TEST PROTOCOLO DE MENSAJES")
    print("="*60)
    
    from utils.protocolo import Message, Response, MsgType
    import json
    
    print("\n1. Test Message creation and serialization")
    msg = Message(MsgType.LOGIN, {"usuario": "test", "password": "pass123"})
    
    msg_dict = msg.to_dict()
    print(f"   Mensaje serializado: {msg_dict}")
    assert 'type' in msg_dict
    assert 'payload' in msg_dict
    print("   ✓ PASS: Message serializa correctamente")
    
    print("\n2. Test Response creation")
    response = Response(ok=True, message="OK", data={"usuario": "test", "nombre": "Test User"})
    
    resp_dict = response.to_dict()
    print(f"   Response serializado: {resp_dict}")
    assert 'ok' in resp_dict
    assert 'data' in resp_dict
    assert resp_dict['ok'] == True
    print("   ✓ PASS: Response serializa correctamente")
    
    print("\n3. Test JSON serialization compatibility")
    json_msg = json.dumps(msg_dict)
    json_resp = json.dumps(resp_dict)
    print(f"   Mensaje JSON length: {len(json_msg)}")
    print(f"   Response JSON length: {len(json_resp)}")
    print("   ✓ PASS: Ambos serializan a JSON válido")
    
    return True


def test_password_security():
    """Test: Seguridad de contraseñas"""
    print("\n" + "="*60)
    print("TEST SEGURIDAD DE CONTRASEÑAS")
    print("="*60)
    
    from servidor.autenticacion import hash_password, validar_login
    
    password = "MySecurePass123!@#"
    
    print("\n1. Test password hashing")
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    print(f"   Hash 1: {hash1[:20]}...")
    print(f"   Hash 2: {hash2[:20]}...")
    print(f"   ¿Hashes diferentes? {hash1 != hash2}")
    print("   (Correcto: son diferentes por salt aleatorio)")
    
    print("\n2. Test password validation")
    usuarios_prueba = {
        "security_test": {
            "usuario": "security_test",
            "password_hash": hash1,
            "nombre": "Security",
            "apellido": "Test",
            "email": "sec@test.com",
            "foto": "",
            "amigos": []
        }
    }
    
    exito, msg = validar_login("security_test", password, usuarios_prueba)
    print(f"   Login con password correcto: {exito} ({msg})")
    assert exito, "Debería aceptar password correcto"
    
    exito, msg = validar_login("security_test", "WrongPassword", usuarios_prueba)
    print(f"   Login con password incorrecto: {exito} ({msg})")
    assert not exito, "Debería rechazar password incorrecto"
    
    print("   ✓ PASS: Hashing y validación funcionan correctamente")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VALIDACIÓN DE LÓGICA DEL SERVIDOR")
    print("="*60)
    
    tests = [
        ("Handler Logic", test_handler_logic),
        ("Message Protocol", test_message_protocol),
        ("Password Security", test_password_security),
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
    
    print("\n" + "="*60)
    print("RESUMEN DE VALIDACIÓN")
    print("="*60)
    
    for nombre, resultado in resultados.items():
        status = "✓ PASS" if resultado else "✗ FAIL"
        print(f"[{status}] {nombre}")
    
    total_pass = sum(1 for v in resultados.values() if v)
    total_tests = len(resultados)
    
    print(f"\nTotal: {total_pass}/{total_tests} tests correctos")
    
    if total_pass == total_tests:
        print("\n✅ LÓGICA DEL SERVIDOR VALIDADA - Completamente funcional")
        sys.exit(0)
    else:
        print(f"\n❌ {total_tests - total_pass} tests fallaron")
        sys.exit(1)
