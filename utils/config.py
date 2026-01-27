"""
Configuración central del proyecto Socialtec.

Objetivo:
- Evitar valores hardcodeados (host/puerto/rutas) repartidos por el código.
- Tener un único lugar para cambiar settings sin romper imports.

Uso recomendado:
    from utils.config import SERVER_HOST, SERVER_PORT, DATA_DIR, USERS_FILE
"""

from __future__ import annotations

from pathlib import Path

# =========================
# Red (TCP)
# =========================
SERVER_HOST: str = "127.0.0.1"
SERVER_PORT: int = 5050

# Tamaños típicos para sockets (se ajustan en rama de TCP/protocolo)
SOCKET_BACKLOG: int = 10
SOCKET_BUFFER_SIZE: int = 4096

# Timeout (None = sin timeout)
SOCKET_TIMEOUT_SECONDS: float | None = None


# =========================
# Rutas del proyecto
# =========================
# Este archivo vive en: <repo_root>/utils/config.py
# Por lo tanto, repo_root = utils/.. (parent de utils)
REPO_ROOT: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = REPO_ROOT / "datos"
LOGS_DIR: Path = REPO_ROOT / "logs"  # opcional (si luego quieren logs a archivo)

# Archivos JSON sugeridos (ajusta nombres según vuestro diseño)
USERS_FILE: Path = DATA_DIR / "usuarios.json"
FRIENDS_FILE: Path = DATA_DIR / "amistades.json"  # Por si se separan relaciones


# =========================
# App / Dominio
# =========================
APP_NAME: str = "Socialtec"
APP_VERSION: str = "0.1.0"

# Si usan IDs o límites
MAX_USERNAME_LENGTH: int = 50
MAX_PASSWORD_LENGTH: int = 128

# Para ordenamiento (cliente)
FRIENDS_SORT_KEY: str = "full_name"  # ejemplo: "full_name" o "last_name_first"


# =========================
# Helpers
# =========================
def ensure_directories() -> None:
    """
    Crea directorios necesarios si no existen.
    Útil para llamar al iniciar el server.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
