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
```bash
python scripts/run_server.py
```

### 2) Cliente
```bash
python scripts/run_client.py
```

## Estructura (alto nivel)
- `servidor/`: lógica del servidor TCP + autenticación + persistencia + GUI del servidor
- `cliente/`: cliente TCP + GUIs (login/registro/búsqueda/perfil)
- `grafo/`: estructura del grafo + algoritmos (path, estadísticas) + visualización
- `utils/`: configuración, protocolo, cifrado compartido
- `scripts/`: entrypoints para correr server/cliente
