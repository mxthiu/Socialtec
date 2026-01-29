"""
Protocolo de mensajes TCP con framing length-prefix y encriptación AES-GCM.

Define cómo se envían/reciben mensajes JSON entre cliente y servidor.
Framing: 4 bytes (big-endian) con el tamaño + payload JSON en UTF-8.

SEGURIDAD: Los payloads sensibles (usuario/password) se encriptan con AES-GCM
antes de transmitirse.

Uso:
    # Enviar mensaje con credenciales encriptadas
    msg = Message(type="LOGIN", payload={"usuario": "john", "password": "secret"})
    send_message_encrypted(sock, msg)

    # Recibir respuesta
    resp = recv_response(sock)
    if resp.ok:
        print(f"OK: {resp.message}")
"""

from __future__ import annotations

import json
import socket
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# 4 bytes para length prefix (big-endian unsigned int)
_LEN_STRUCT = struct.Struct("!I")


# =========================
# Modelo de mensaje
# =========================
@dataclass
class Message:
    """
    Mensaje estándar entre cliente y servidor.

    Campos recomendados:
      - type: tipo de operación (LOGIN, REGISTER, SEARCH_USER, ADD_FRIEND, etc.)
      - payload: datos específicos de la operación
      - request_id: opcional para correlación (debug, multi-requests)
    """
    type: str
    payload: Dict[str, Any]
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type, "payload": self.payload}
        if self.request_id is not None:
            d["request_id"] = self.request_id
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Message":
        return Message(
            type=str(d.get("type", "")),
            payload=dict(d.get("payload", {})),
            request_id=d.get("request_id"),
        )


@dataclass
class Response:
    """
    Respuesta estándar del servidor.

    - ok: True/False
    - message: texto humano (para logs/GUI)
    - data: payload de respuesta
    - request_id: para responder al request que lo originó
    """
    ok: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "ok": self.ok,
            "message": self.message,
            "data": self.data,
        }
        if self.request_id is not None:
            d["request_id"] = self.request_id
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Response":
        return Response(
            ok=bool(d.get("ok", False)),
            message=str(d.get("message", "")),
            data=dict(d.get("data", {})) if d.get("data") is not None else {},
            request_id=d.get("request_id"),
        )


# =========================
# JSON codec
# =========================
def encode_json(obj: Dict[str, Any]) -> bytes:
    """
    Serializa a JSON compacto UTF-8.
    ensure_ascii=False para permitir tildes/ñ.
    """
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def decode_json(raw: bytes) -> Dict[str, Any]:
    return json.loads(raw.decode("utf-8"))


# =========================
# Framing: length-prefix + payload
# =========================
def pack_frame(payload: bytes) -> bytes:
    """
    Frame = 4 bytes length + payload
    """
    return _LEN_STRUCT.pack(len(payload)) + payload


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Recibe exactamente n bytes o lanza ConnectionError si el socket se cierra.
    """
    chunks: list[bytes] = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("Socket cerrado mientras se recibían datos.")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def send_frame(sock: socket.socket, obj: Dict[str, Any]) -> None:
    """
    Envía un dict como JSON con framing.
    """
    payload = encode_json(obj)
    frame = pack_frame(payload)
    sock.sendall(frame)


def recv_frame(sock: socket.socket) -> Dict[str, Any]:
    """
    Recibe un frame completo y devuelve el dict.
    """
    header = recv_exact(sock, _LEN_STRUCT.size)  # 4 bytes
    (length,) = _LEN_STRUCT.unpack(header)
    payload = recv_exact(sock, length)
    return decode_json(payload)


# =========================
# Helpers para enviar/recibir Message/Response
# =========================
def send_message(sock: socket.socket, msg: Message) -> None:
    send_frame(sock, msg.to_dict())


def recv_message(sock: socket.socket) -> Message:
    d = recv_frame(sock)
    return Message.from_dict(d)


def send_response(sock: socket.socket, resp: Response) -> None:
    send_frame(sock, resp.to_dict())


def recv_response(sock: socket.socket) -> Response:
    d = recv_frame(sock)
    return Response.from_dict(d)


# =========================
# Constantes de tipos de mensaje
# =========================
class MsgType:
    PING = "PING"
    LOGIN = "LOGIN"
    REGISTER = "REGISTER"
    SEARCH_USER = "SEARCH_USER"
    GET_PROFILE = "GET_PROFILE"
    ADD_FRIEND = "ADD_FRIEND"
    REMOVE_FRIEND = "REMOVE_FRIEND"
    GET_STATS = "GET_STATS"
    GET_PATH = "GET_PATH"


# =========================
# Encriptación de mensajes sensibles
# =========================
def send_message_encrypted(sock: socket.socket, msg: Message) -> None:
    """
    Envía un mensaje encriptando el payload con AES-GCM.
    El tipo de mensaje NO se encripta (va en claro para routing).
    """
    from utils.crypto import get_crypto_box
    
    box = get_crypto_box()
    
    # Encriptar el payload
    encrypted_payload = box.encrypt_dict(msg.payload)
    
    # Crear mensaje con payload encriptado
    encrypted_msg = Message(
        type=msg.type,
        payload={"encrypted": True, "data": encrypted_payload},
        request_id=msg.request_id
    )
    
    send_message(sock, encrypted_msg)


def recv_message_encrypted(sock: socket.socket) -> Message:
    """
    Recibe un mensaje y desencripta el payload si está marcado como encrypted.
    """
    from utils.crypto import get_crypto_box
    
    msg = recv_message(sock)
    
    # Verificar si el payload está encriptado
    if msg.payload.get("encrypted"):
        box = get_crypto_box()
        encrypted_data = msg.payload.get("data", {})
        
        # Desencriptar payload
        decrypted_payload = box.decrypt_dict(encrypted_data)
        
        # Retornar mensaje con payload desencriptado
        return Message(
            type=msg.type,
            payload=decrypted_payload,
            request_id=msg.request_id
        )
    
    return msg
