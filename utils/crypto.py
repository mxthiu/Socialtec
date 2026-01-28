"""
Cifrado AES-GCM para proteger credenciales y payloads en tránsito (cliente -> servidor).

NO reemplaza Passlib (que hashea passwords en almacenamiento). Este módulo cifra
datos en tránsito.

Uso:
    # Generar clave (una sola vez)
    import os, base64
    key = base64.b64encode(os.urandom(32)).decode()
    # Exportar como: export SOCIALTEC_SECRET_KEY="<key>"
    
    # Usar
    from utils.crypto import get_crypto_box
    box = get_crypto_box()
    
    encrypted_pkg = box.encrypt_dict({"usuario": "john", "password": "secret"})
    decrypted = box.decrypt_dict(encrypted_pkg)
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# =========================
# Config de clave
# =========================
ENV_KEY_NAME = "SOCIALTEC_SECRET_KEY"
# Longitud recomendada para AES-256: 32 bytes (base64 -> 44 chars aprox)
REQUIRED_KEY_LEN = 32


class CryptoError(Exception):
    pass


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))


def load_key_from_env() -> Optional[bytes]:
    """
    Carga la clave desde variable de entorno SOCIALTEC_SECRET_KEY (base64).
    Devuelve bytes o None si no existe.
    """
    raw = os.getenv(ENV_KEY_NAME)
    if not raw:
        return None
    try:
        key = _b64d(raw)
    except Exception as e:
        raise CryptoError(f"Clave inválida en {ENV_KEY_NAME} (base64).") from e
    if len(key) != REQUIRED_KEY_LEN:
        raise CryptoError(
            f"Clave inválida: se esperaban {REQUIRED_KEY_LEN} bytes, got {len(key)}."
        )
    return key


def generate_dev_key() -> bytes:
    """
    Genera una clave aleatoria (solo dev). NO versionar claves reales.
    """
    return os.urandom(REQUIRED_KEY_LEN)


@dataclass(frozen=True)
class CryptoBox:
    """
    Caja criptográfica AES-GCM para cifrar/descifrar payloads.
    """
    key: bytes

    def __post_init__(self) -> None:
        if len(self.key) != REQUIRED_KEY_LEN:
            raise CryptoError(
                f"Key length inválida: se requieren {REQUIRED_KEY_LEN} bytes."
            )

    def encrypt_bytes(self, data: bytes, aad: bytes = b"") -> Dict[str, str]:
        """
        Retorna un paquete serializable:
          {
            "alg": "AESGCM",
            "nonce": "<b64>",
            "ciphertext": "<b64>"
          }
        """
        aes = AESGCM(self.key)
        nonce = os.urandom(12)  # 96-bit nonce recomendado para GCM
        ct = aes.encrypt(nonce, data, aad)
        return {
            "alg": "AESGCM",
            "nonce": _b64e(nonce),
            "ciphertext": _b64e(ct),
        }

    def decrypt_bytes(self, package: Dict[str, str], aad: bytes = b"") -> bytes:
        if package.get("alg") != "AESGCM":
            raise CryptoError("Algoritmo no soportado.")
        try:
            nonce = _b64d(package["nonce"])
            ct = _b64d(package["ciphertext"])
        except Exception as e:
            raise CryptoError("Paquete inválido (base64).") from e

        aes = AESGCM(self.key)
        try:
            return aes.decrypt(nonce, ct, aad)
        except Exception as e:
            raise CryptoError("No se pudo descifrar (clave/AAD incorrecta o datos corruptos).") from e

    def encrypt_dict(self, obj: Dict[str, Any], aad: bytes = b"") -> Dict[str, str]:
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return self.encrypt_bytes(raw, aad=aad)

    def decrypt_dict(self, package: Dict[str, str], aad: bytes = b"") -> Dict[str, Any]:
        raw = self.decrypt_bytes(package, aad=aad)
        return json.loads(raw.decode("utf-8"))


# =========================
# Helpers globales
# =========================
_default_box: Optional[CryptoBox] = None


def get_crypto_box() -> CryptoBox:
    """
    Devuelve una CryptoBox global.
    Prioridad:
      1) SOCIALTEC_SECRET_KEY (base64) en entorno
      2) clave dev generada al vuelo (solo para pruebas locales)
    """
    global _default_box
    if _default_box is not None:
        return _default_box

    key = load_key_from_env()
    if key is None:
        # Fallback dev: útil para correr sin configurar nada,
        # pero cliente y server deben compartir clave para que funcione.
        key = generate_dev_key()

    _default_box = CryptoBox(key=key)
    return _default_box


def export_key_base64(key: bytes) -> str:
    """
    Convierte clave bytes -> base64 para setearla en variable de entorno.
    """
    if len(key) != REQUIRED_KEY_LEN:
        raise CryptoError("Key length inválida.")
    return _b64e(key)
