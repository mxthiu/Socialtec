"""
Test completo de encriptación end-to-end simulando cliente-servidor.
"""

from utils.crypto import generate_dev_key, CryptoBox
from utils.protocolo import send_message_encrypted, recv_message_encrypted, Message
import json
from io import BytesIO


class MockSocket:
    """Mock de socket para testing."""
    def __init__(self):
        self.send_buffer = BytesIO()
        self.recv_buffer = BytesIO()
        
    def sendall(self, data: bytes):
        """Simula envío."""
        self.send_buffer.write(data)
        
    def recv(self, size: int) -> bytes:
        """Simula recepción."""
        return self.recv_buffer.read(size)
    
    def flip_buffers(self):
        """Copia buffer de envío a recepción (simula transmisión)."""
        self.send_buffer.seek(0)
        self.recv_buffer = BytesIO(self.send_buffer.read())
        self.recv_buffer.seek(0)


def test_login_encriptado():
    """Test: LOGIN con credenciales encriptadas."""
    print("\n" + "="*60)
    print("TEST: LOGIN CON ENCRIPTACIÓN")
    print("="*60)
    
    # Simular cliente enviando LOGIN
    credenciales = {
        "usuario": "testuser",
        "password": "MiPassword123!"
    }
    
    mock_socket = MockSocket()
    
    # Cliente: Enviar mensaje encriptado
    print("\n[CLIENTE] Enviando credenciales encriptadas...")
    print(f"  Usuario: {credenciales['usuario']}")
    print(f"  Password: {'*' * len(credenciales['password'])}")
    
    mensaje_cliente = Message(
        type="LOGIN",
        payload=credenciales
    )
    
    try:
        send_message_encrypted(mock_socket, mensaje_cliente)
        print("  ✅ Mensaje encriptado y enviado")
    except Exception as e:
        print(f"  ❌ Error al encriptar: {e}")
        return False
    
    # Simular transmisión
    mock_socket.flip_buffers()
        
    # Servidor: Recibir y desencriptar
    print("\n[SERVIDOR] Recibiendo mensaje...")
    try:
        mensaje_servidor = recv_message_encrypted(mock_socket)
        print(f"  ✅ Mensaje desencriptado correctamente")
        print(f"  Tipo: {mensaje_servidor.type}")
        print(f"  Usuario: {mensaje_servidor.payload.get('usuario')}")
        print(f"  Password recibido: {'*' * len(mensaje_servidor.payload.get('password', ''))}")
        
        # Verificar que los datos coinciden
        if mensaje_servidor.type == 'LOGIN':
            datos = mensaje_servidor.payload
            if datos.get('usuario') == credenciales['usuario'] and \
               datos.get('password') == credenciales['password']:
                print("\n  ✅ PASS: Credenciales encriptadas correctamente")
                return True
            else:
                print("\n  ❌ FAIL: Credenciales no coinciden")
                return False
        else:
            print(f"\n  ❌ FAIL: Tipo de mensaje incorrecto: {mensaje_servidor.type}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error al desencriptar: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_register_encriptado():
    """Test: REGISTER con credenciales encriptadas."""
    print("\n" + "="*60)
    print("TEST: REGISTER CON ENCRIPTACIÓN")
    print("="*60)
    
    # Simular cliente enviando REGISTER
    datos_registro = {
        "usuario": "newuser",
        "password": "SecurePass456!",
        "nombre": "Test User",
        "email": "test@example.com",
        "edad": 25,
        "foto": "default.png"
    }
    
    mock_socket = MockSocket()
    
    # Cliente: Enviar mensaje encriptado
    print("\n[CLIENTE] Enviando datos de registro encriptados...")
    print(f"  Usuario: {datos_registro['usuario']}")
    print(f"  Password: {'*' * len(datos_registro['password'])}")
    print(f"  Nombre: {datos_registro['nombre']}")
    
    mensaje_cliente = Message(
        type="REGISTER",
        payload=datos_registro
    )
    
    try:
        send_message_encrypted(mock_socket, mensaje_cliente)
        print("  ✅ Mensaje encriptado y enviado")
    except Exception as e:
        print(f"  ❌ Error al encriptar: {e}")
        return False
    
    # Simular transmisión
    mock_socket.flip_buffers()
        
    # Servidor: Recibir y desencriptar
    print("\n[SERVIDOR] Recibiendo mensaje...")
    try:
        mensaje_servidor = recv_message_encrypted(mock_socket)
        print(f"  ✅ Mensaje desencriptado correctamente")
        print(f"  Tipo: {mensaje_servidor.type}")
        print(f"  Usuario: {mensaje_servidor.payload.get('usuario')}")
        
        # Verificar que los datos coinciden
        if mensaje_servidor.type == 'REGISTER':
            datos = mensaje_servidor.payload
            if datos.get('usuario') == datos_registro['usuario'] and \
               datos.get('password') == datos_registro['password'] and \
               datos.get('nombre') == datos_registro['nombre']:
                print("\n  ✅ PASS: Datos de registro encriptados correctamente")
                return True
            else:
                print("\n  ❌ FAIL: Datos no coinciden")
                return False
        else:
            print(f"\n  ❌ FAIL: Tipo de mensaje incorrecto")
            return False
            
    except Exception as e:
        print(f"  ❌ Error al desencriptar: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "="*60)
    print("TESTS DE ENCRIPTACIÓN END-TO-END")
    print("="*60)
    
    # Verificar que la clave sea correcta
    print("\nVerificando clave de encriptación...")
    key = generate_dev_key()
    print(f"  Longitud de clave: {len(key)} bytes")
    if len(key) != 32:
        print(f"  ❌ ERROR: La clave debe tener 32 bytes")
        return
    print(f"  ✅ Clave correcta")
    
    # Ejecutar tests
    results = []
    
    results.append(("Login encriptado", test_login_encriptado()))
    results.append(("Register encriptado", test_register_encriptado()))
    
    # Resumen
    print("\n" + "="*60)
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print(f"RESULTADO: {passed}/{total} tests pasados")
    
    if passed == total:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print(f"❌ {total - passed} tests fallaron:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
