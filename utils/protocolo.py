

from __future__ import annotations

import json
import socket
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

_LEN_STRUCT = struct.Struct("!I")
@dataclass
class Message:
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


def encode_json(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def decode_json(raw: bytes) -> Dict[str, Any]:
    return json.loads(raw.decode("utf-8"))


def pack_frame(payload: bytes) -> bytes:
    return _LEN_STRUCT.pack(len(payload)) + payload


def recv_exact(sock: socket.socket, n: int) -> bytes:
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
    payload = encode_json(obj)
    frame = pack_frame(payload)
    sock.sendall(frame)


def recv_frame(sock: socket.socket) -> Dict[str, Any]:
    header = recv_exact(sock, _LEN_STRUCT.size)
    (length,) = _LEN_STRUCT.unpack(header)
    payload = recv_exact(sock, length)
    return decode_json(payload)


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


def send_message_encrypted(sock: socket.socket, msg: Message) -> None:
    from utils.crypto import get_crypto_box
    
    box = get_crypto_box()
    encrypted_payload = box.encrypt_dict(msg.payload)
    encrypted_msg = Message(
        type=msg.type,
        payload={"encrypted": True, "data": encrypted_payload},
        request_id=msg.request_id
    )
    
    send_message(sock, encrypted_msg)


def recv_message_encrypted(sock: socket.socket) -> Message:
    from utils.crypto import get_crypto_box
    
    msg = recv_message(sock)
    
    if msg.payload.get("encrypted"):
        box = get_crypto_box()
        encrypted_data = msg.payload.get("data", {})
        decrypted_payload = box.decrypt_dict(encrypted_data)
        return Message(
            type=msg.type,
            payload=decrypted_payload,
            request_id=msg.request_id
        )
    
    return msg
