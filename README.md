# Socialtec (Proyecto IV)

Red social basada en grafos con arquitectura cliente/servidor usando sockets TCP.

## Requisitos
- Python 3.10+ (recomendado)
- Instalar dependencias:
  ```bash
  pip install -r requirements.txt
  ```

## Ejecutar

### 1) Servidor

python -c "import sys; sys.path.insert(0, '.'); from servidor.gui_servidor import main; main()"

### 2) Cliente

python -c "import sys; sys.path.insert(0, '.'); from cliente.gui_login import VentanaLogin; from PyQt6.QtWidgets import QApplication; app = QApplication(sys.argv); ventana = VentanaLogin(); ventana.show(); sys.exit(app.exec())"

## Estructura (alto nivel)
- `servidor/`: lógica del servidor TCP + autenticación + persistencia + GUI del servidor
- `cliente/`: cliente TCP + GUIs (login/registro/búsqueda/perfil)
- `grafo/`: estructura del grafo + algoritmos (path, estadísticas) + visualización
- `utils/`: configuración, protocolo, cifrado compartido
- `scripts/`: entrypoints para correr server/cliente
