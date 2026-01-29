

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


class GrafoError(Exception):
    pass


@dataclass
class Usuario:
    username: str
    nombre: str = ""
    apellido: str = ""
    foto: str = ""  # ruta o identificador (opcional)

    @property
    def nombre_completo(self) -> str:
        return (f"{self.nombre} {self.apellido}").strip()


class Grafo:

    def __init__(self) -> None:
        self._adj: Dict[str, Set[str]] = {}
        self._users: Dict[str, Usuario] = {}

    def existe_usuario(self, username: str) -> bool:
        return username in self._adj

    def agregar_usuario(self, username: str, nombre: str = "", apellido: str = "", foto: str = "") -> None:
        username = username.strip()
        if not username:
            raise GrafoError("Username inválido (vacío).")
        if username not in self._adj:
            self._adj[username] = set()
        self._users[username] = Usuario(username=username, nombre=nombre, apellido=apellido, foto=foto)

    def eliminar_usuario(self, username: str) -> None:
        if username not in self._adj:
            return
        for vecino in list(self._adj[username]):
            self._adj[vecino].discard(username)
        del self._adj[username]
        self._users.pop(username, None)

    def usuarios(self) -> List[str]:
        return sorted(self._adj.keys())

    def obtener_usuario(self, username: str) -> Optional[Usuario]:
        return self._users.get(username)

    def son_amigos(self, a: str, b: str) -> bool:
        return a in self._adj and b in self._adj[a]

    def agregar_amistad(self, a: str, b: str) -> None:
        a, b = a.strip(), b.strip()
        if not a or not b:
            raise GrafoError("Usernames inválidos.")
        if a == b:
            raise GrafoError("No se puede crear amistad consigo mismo.")
        if a not in self._adj:
            self.agregar_usuario(a)
        if b not in self._adj:
            self.agregar_usuario(b)
        self._adj[a].add(b)
        self._adj[b].add(a)

    def eliminar_amistad(self, a: str, b: str) -> None:
        if a not in self._adj or b not in self._adj:
            return
        self._adj[a].discard(b)
        self._adj[b].discard(a)

    def amigos_de(self, username: str) -> List[str]:
        if username not in self._adj:
            return []
        return sorted(self._adj[username])

    def grado(self, username: str) -> int:
        if username not in self._adj:
            return 0
        return len(self._adj[username])

    def to_adj_dict(self) -> Dict[str, List[str]]:
        return {u: sorted(list(vecinos)) for u, vecinos in self._adj.items()}

    @staticmethod
    def from_usuarios_json(data: Dict[str, dict]) -> "Grafo":
        g = Grafo()
        for username, info in data.items():
            nombre = str(info.get("nombre", ""))
            apellido = str(info.get("apellido", ""))
            foto = str(info.get("foto", ""))
            g.agregar_usuario(username, nombre=nombre, apellido=apellido, foto=foto)

        for username, info in data.items():
            amigos = info.get("amigos", []) or []
            for amigo in amigos:
                g.agregar_amistad(username, str(amigo))

        return g

    def numero_usuarios(self) -> int:
        return len(self._adj)

    def numero_amistades(self) -> int:
        total = sum(len(vecinos) for vecinos in self._adj.values())
        return total // 2

    def aristas(self) -> List[Tuple[str, str]]:
        edges: List[Tuple[str, str]] = []
        for a, vecinos in self._adj.items():
            for b in vecinos:
                if a < b:
                    edges.append((a, b))
        return edges
