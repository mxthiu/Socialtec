"""
Test de encriptación para verificar que funciona correctamente
"""
import sys
sys.path.insert(0, '.')

def test_longitud_clave():
    """Test 1: Verificar que la clave tiene 32 bytes"""
    from utils.crypto import generate_dev_key
    
    key = generate_dev_key()
    print(f"✓ Test 1: Longitud de clave")
    print(f"  Clave generada: {key}")
    print(f"  Longitud: {len(key)} bytes")
    
    assert len(key) == 32, f"ERROR: La clave debe tener 32 bytes, tiene {len(key)}"
    print(f"  ✅ PASS: Clave tiene exactamente 32 bytes\n")


def test_crypto_box():
    """Test 2: Verificar que CryptoBox funciona"""
    from utils.crypto import get_crypto_box
    
    print(f"✓ Test 2: CryptoBox initialization")
    
    try:
        box = get_crypto_box()
        print(f"  ✅ PASS: CryptoBox creado correctamente\n")
    except Exception as e:
        print(f"  ❌ FAIL: Error creando CryptoBox: {e}\n")
        raise


def test_encrypt_decrypt():
    """Test 3: Verificar encriptación y desencriptación"""
    from utils.crypto import get_crypto_box
    
    print(f"✓ Test 3: Encriptación/Desencriptación")
    
    box = get_crypto_box()
    
    # Encriptar un dict
    original = {"usuario": "testuser", "password": "testpass123"}
    print(f"  Original: {original}")
    
    encrypted = box.encrypt_dict(original)
    print(f"  Encriptado: {encrypted}")
    
    # Desencriptar
    decrypted = box.decrypt_dict(encrypted)
    print(f"  Desencriptado: {decrypted}")
    
    assert original == decrypted, "ERROR: El mensaje desencriptado no coincide con el original"
    print(f"  ✅ PASS: Encriptación/Desencriptación funciona correctamente\n")


def test_mensaje_encriptado():
    """Test 4: Verificar envío de mensaje encriptado (simulado)"""
    from utils.protocolo import Message
    from utils.crypto import get_crypto_box
    
    print(f"✓ Test 4: Mensaje encriptado")
    
    box = get_crypto_box()
    
    # Crear mensaje
    msg = Message(
        type="LOGIN",
        payload={"usuario": "testuser", "password": "testpass123"}
    )
    print(f"  Mensaje original: {msg.payload}")
    
    # Encriptar payload
    encrypted_payload = box.encrypt_dict(msg.payload)
    print(f"  Payload encriptado: {encrypted_payload}")
    
    # Desencriptar payload
    decrypted_payload = box.decrypt_dict(encrypted_payload)
    print(f"  Payload desencriptado: {decrypted_payload}")
    
    assert msg.payload == decrypted_payload, "ERROR: Payload no coincide"
    print(f"  ✅ PASS: Mensaje encriptado funciona correctamente\n")


def test_misma_clave_multiple_veces():
    """Test 5: Verificar que get_crypto_box siempre devuelve la misma clave"""
    from utils.crypto import get_crypto_box
    
    print(f"✓ Test 5: Consistencia de clave")
    
    box1 = get_crypto_box()
    box2 = get_crypto_box()
    
    # Verificar que son el mismo objeto
    assert box1 is box2, "ERROR: get_crypto_box() debe devolver el mismo objeto"
    
    # Verificar que pueden comunicarse
    test_data = {"test": "data"}
    encrypted = box1.encrypt_dict(test_data)
    decrypted = box2.decrypt_dict(encrypted)
    
    assert test_data == decrypted, "ERROR: No pueden comunicarse entre sí"
    print(f"  ✅ PASS: Misma clave se usa consistentemente\n")


def run_all_tests():
    """Ejecuta todos los tests"""
    print("=" * 60)
    print("TESTS DE ENCRIPTACIÓN AES-GCM")
    print("=" * 60 + "\n")
    
    tests = [
        test_longitud_clave,
        test_crypto_box,
        test_encrypt_decrypt,
        test_mensaje_encriptado,
        test_misma_clave_multiple_veces
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ FAIL: {test.__name__}")
            print(f"   Error: {e}\n")
    
    print("=" * 60)
    print(f"RESULTADO: {passed}/{len(tests)} tests pasados")
    if failed == 0:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print(f"❌ {failed} tests fallaron")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
