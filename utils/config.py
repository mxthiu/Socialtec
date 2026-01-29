

from __future__ import annotations

from pathlib import Path


SERVER_HOST: str = "127.0.0.1"
SERVER_PORT: int = 5050

SOCKET_BACKLOG: int = 10
SOCKET_BUFFER_SIZE: int = 4096
SOCKET_TIMEOUT_SECONDS: float | None = None
REPO_ROOT: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = REPO_ROOT / "datos"
LOGS_DIR: Path = REPO_ROOT / "logs"
USERS_FILE: Path = DATA_DIR / "usuarios.json"
FRIENDS_FILE: Path = DATA_DIR / "amistades.json"
APP_NAME: str = "Socialtec"
APP_VERSION: str = "0.1.0"
MAX_USERNAME_LENGTH: int = 50
MAX_PASSWORD_LENGTH: int = 128
FRIENDS_SORT_KEY: str = "full_name"

def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
