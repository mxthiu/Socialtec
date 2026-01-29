

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENV_KEY_NAME = "SOCIALTEC_SECRET_KEY"
REQUIRED_KEY_LEN = 32


class CryptoError(Exception):
    pass


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))


def load_key_from_env() -> Optional[bytes]:
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
    return b'SocialTec2026DevKey1234567890123'


@dataclass(frozen=True)
class CryptoBox:
    key: bytes

    def __post_init__(self) -> None:
        if len(self.key) != REQUIRED_KEY_LEN:
            raise CryptoError(
                f"Key length inválida: se requieren {REQUIRED_KEY_LEN} bytes."
            )

    def encrypt_bytes(self, data: bytes, aad: bytes = b"") -> Dict[str, str]:
        aes = AESGCM(self.key)
        nonce = os.urandom(12)
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


_default_box: Optional[CryptoBox] = None

def get_crypto_box() -> CryptoBox:
    global _default_box
    if _default_box is not None:
        return _default_box

    key = load_key_from_env()
    if key is None:
        key = generate_dev_key()

    _default_box = CryptoBox(key=key)
    return _default_box


def export_key_base64(key: bytes) -> str:
    if len(key) != REQUIRED_KEY_LEN:
        raise CryptoError("Key length inválida.")
    return _b64e(key)
