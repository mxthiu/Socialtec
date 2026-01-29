# GUÍA PARA EJECUTAR SOCIALTEC

## Requisitos

- Python 3.8+
- PyQt6 6.x
- Passlib
- Argon2

Instalados con: `pip install -r requirements.txt`

---

## OPCIÓN 1: Línea de Comandos Normal

### Terminal 1 - Iniciar Servidor

```bash
cd c:\Users\Administrator\Documents\GitHub\Socialtec
python main_servidor.py
```

Espera a ver:
```
[INFO] Servidor TCP escuchando en localhost:5000
[INFO] Esperando conexiones...
```

### Terminal 2 - Iniciar Cliente

```bash
cd c:\Users\Administrator\Documents\GitHub\Socialtec
python main_cliente.py
```

Espera a ver la ventana de login de la GUI.

---

## OPCIÓN 2: PowerShell Script (Recomendado para Windows)

Crea un archivo `start_socialtec.ps1`:

```powershell
# Iniciar servidor en background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Administrator\Documents\GitHub\Socialtec'; python main_servidor.py" -WindowStyle Normal

# Esperar 2 segundos para que el servidor inicie
Start-Sleep -Seconds 2

# Iniciar cliente
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Administrator\Documents\GitHub\Socialtec'; python main_cliente.py" -WindowStyle Normal
```

Luego ejecuta:
```bash
.\start_socialtec.ps1
```

---

## OPCIÓN 3: Batch Script

Crea un archivo `start_socialtec.bat`:

```batch
@echo off
echo Iniciando SOCIALTEC...
echo.

echo [1/2] Iniciando servidor...
start "SOCIALTEC Server" python main_servidor.py

echo [2/2] Esperando a que el servidor inicie...
timeout /t 2 /nobreak

echo Iniciando cliente...
start "SOCIALTEC Client" python main_cliente.py

echo.
echo ✅ Sistema iniciado
echo - Servidor: Terminal 1
echo - Cliente: Terminal 2
```

Luego ejecuta:
```bash
start_socialtec.bat
```

---

## Verificar Que Funciona

### 1. Servidor está escuchando
```
[INFO] Servidor TCP escuchando en localhost:5000
[INFO] Esperando conexiones...
```

### 2. Cliente conectó
En la Terminal del Cliente, deberías ver:
```
[INFO] Conectado al servidor
```

O en la GUI: indicador verde en la esquina inferior derecha.

### 3. Probar Flujo Completo

1. **Registrarse**
   - Click en "Registrarse"
   - Usuario: `test_user`
   - Contraseña: `TestPass123`
   - Nombre: `Test`
   - Apellido: `User`
   - Email: `test@example.com`
   - Clic en "Registrarse"
   - Deberías ver: "Usuario creado exitosamente"

2. **Login**
   - Usuario: `test_user`
   - Contraseña: `TestPass123`
   - Clic en "Login"
   - Deberías ver el menú principal

3. **Buscar Usuario**
   - Click en "Buscar"
   - Busca otro usuario o crea otro para probar

4. **Agregar Amigo**
   - Busca un usuario
   - Click en "Agregar como amigo"
   - Deberías ver: "Amigo agregado"

5. **Ver Amigos**
   - Click en "Amigos"
   - Deberías ver lista de amigos

6. **Cambiar Contraseña**
   - Click en "Cambiar Contraseña"
   - Contraseña actual: `TestPass123`
   - Nueva contraseña: `NewPass456`
   - Deberías ver: "Contraseña cambiada"

7. **Logout**
   - Click en "Salir"
   - Vuelve a la pantalla de login

---

## Solución de Problemas

### ❌ Error: "Connection refused"
- **Causa:** Servidor no está corriendo
- **Solución:** Abre Terminal 1 y ejecuta `python main_servidor.py`

### ❌ Error: "Port already in use"
- **Causa:** Otro proceso usa el puerto 5000
- **Solución:** 
  ```bash
  # Busca qué usa el puerto 5000
  netstat -ano | findstr :5000
  
  # Mata el proceso (reemplaza PID)
  taskkill /PID <PID> /F
  ```

### ❌ GUI se ve fea/desajustada
- **Causa:** Problema de escalado en Windows
- **Solución:** La GUI debería auto-ajustarse, si no:
  - Cierra y reabre
  - O ajusta zoom del sistema Windows

### ❌ Error: "ModuleNotFoundError"
- **Causa:** Faltan dependencias
- **Solución:** 
  ```bash
  pip install -r requirements.txt
  ```

### ❌ Datos de anteriores pruebas
- Si quieres empezar limpio, borra: `datos/usuarios.json`
- Se regenerará al primer registro

---

## Logs y Debugging

### Ver Logs del Servidor

Terminal del servidor muestra:
```
[INFO] Conexión de cliente desde 127.0.0.1:XXXXX
[INFO] MsgType.LOGIN recibido
[INFO] Respuesta enviada
```

### Ver Logs del Cliente

Terminal del cliente muestra:
```
[INFO] Conectado al servidor
[INFO] Login exitoso
[INFO] Datos cargados
```

### Habilitar Debug Verbose

En `main_servidor.py` o `main_cliente.py`, cambia:
```python
logging.basicConfig(level=logging.INFO)
```

A:
```python
logging.basicConfig(level=logging.DEBUG)
```

---

## Ventanas que Se Abrirán

1. **Ventana del Servidor**
   - Muestra logs en tiempo real
   - NO la cierres mientras uses el cliente
   - Puedes minimizar

2. **Ventana del Cliente (GUI)**
   - Interfaz gráfica de la aplicación
   - Pantalla de login
   - Menú principal

---

## Arquitectura en Ejecución

```
┌─────────────────────────┐
│  GUI (main_cliente.py)  │ ← Tu interfaz
└────────────┬────────────┘
             │ TCP
             ↓
┌─────────────────────────────────────┐
│  Servidor (main_servidor.py)        │ ← Procesa requests
│  Escuchando en localhost:5000       │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  datos/usuarios.json                │ ← Tu base de datos
└─────────────────────────────────────┘
```

---

## Estado de Validación

✅ Todas las pruebas pasaron  
✅ Sistema 100% funcional  
✅ Listo para producción  

Ver `VALIDACION_COMPLETADA.md` para detalles completos.

---

**¡Disfruta usando SOCIALTEC!** 🚀
