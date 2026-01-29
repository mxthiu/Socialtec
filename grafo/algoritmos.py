

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from grafo.grafo import Grafo


class AlgoritmosGrafoError(Exception):
    pass


@dataclass(frozen=True)
class EstadisticasGrafo:
    usuario_con_mas_amigos: Optional[str]
    max_amigos: int
    usuario_con_menos_amigos: Optional[str]
    min_amigos: int
    promedio_amigos: float
    cantidad_usuarios: int
    cantidad_amistades: int


def encontrar_camino_bfs(grafo: Grafo, inicio: str, fin: str) -> Optional[List[str]]:
    inicio = inicio.strip()
    fin = fin.strip()
    if not inicio or not fin:
        raise AlgoritmosGrafoError("Inicio/fin inválidos.")
    if not grafo.existe_usuario(inicio) or not grafo.existe_usuario(fin):
        return None
    if inicio == fin:
        return [inicio]

    cola = deque([inicio])
    visitado = {inicio}
    padre: Dict[str, Optional[str]] = {inicio: None}

    while cola:
        actual = cola.popleft()
        for vecino in grafo.amigos_de(actual):
            if vecino in visitado:
                continue
            visitado.add(vecino)
            padre[vecino] = actual
            if vecino == fin:
                return _reconstruir_camino(padre, fin)
            cola.append(vecino)

    return None


def _reconstruir_camino(padre: Dict[str, Optional[str]], fin: str) -> List[str]:
    camino: List[str] = []
    cur: Optional[str] = fin
    while cur is not None:
        camino.append(cur)
        cur = padre.get(cur)
    camino.reverse()
    return camino


def encontrar_camino_dfs(grafo: Grafo, inicio: str, fin: str) -> Optional[List[str]]:
    inicio = inicio.strip()
    fin = fin.strip()
    if not grafo.existe_usuario(inicio) or not grafo.existe_usuario(fin):
        return None
    if inicio == fin:
        return [inicio]

    visitado = set()
    padre: Dict[str, Optional[str]] = {inicio: None}

    def dfs(u: str) -> bool:
        visitado.add(u)
        for v in grafo.amigos_de(u):
            if v in visitado:
                continue
            padre[v] = u
            if v == fin:
                return True
            if dfs(v):
                return True
        return False

    ok = dfs(inicio)
    if not ok:
        return None
    return _reconstruir_camino(padre, fin)


def calcular_estadisticas(grafo: Grafo) -> EstadisticasGrafo:
    usuarios = grafo.usuarios()
    n = len(usuarios)

    if n == 0:
        return EstadisticasGrafo(
            usuario_con_mas_amigos=None,
            max_amigos=0,
            usuario_con_menos_amigos=None,
            min_amigos=0,
            promedio_amigos=0.0,
            cantidad_usuarios=0,
            cantidad_amistades=0,
        )

    max_u = usuarios[0]
    min_u = usuarios[0]
    max_deg = grafo.grado(max_u)
    min_deg = grafo.grado(min_u)

    suma_grados = 0
    for u in usuarios:
        deg = grafo.grado(u)
        suma_grados += deg
        if deg > max_deg:
            max_deg = deg
            max_u = u
        if deg < min_deg:
            min_deg = deg
            min_u = u

    promedio = suma_grados / n
    amistades = grafo.numero_amistades()

    return EstadisticasGrafo(
        usuario_con_mas_amigos=max_u,
        max_amigos=max_deg,
        usuario_con_menos_amigos=min_u,
        min_amigos=min_deg,
        promedio_amigos=promedio,
        cantidad_usuarios=n,
        cantidad_amistades=amistades,
    )


def estadisticas_como_dict(stats: EstadisticasGrafo) -> Dict[str, object]:
    """
    Helper para enviar por red/GUI fácilmente.
    """
    return {
        "usuario_con_mas_amigos": stats.usuario_con_mas_amigos,
        "max_amigos": stats.max_amigos,
        "usuario_con_menos_amigos": stats.usuario_con_menos_amigos,
        "min_amigos": stats.min_amigos,
        "promedio_amigos": stats.promedio_amigos,
        "cantidad_usuarios": stats.cantidad_usuarios,
        "cantidad_amistades": stats.cantidad_amistades,
    }
