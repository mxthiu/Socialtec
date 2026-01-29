

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Set

try:
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError as e:
    raise ImportError(
        "Falta instalar dependencias de visualización. "
        "Ejecuta: pip install networkx matplotlib"
    ) from e

from grafo.grafo import Grafo


class VisualizacionError(Exception):
    pass


def visualizar_grafo(
    grafo: Grafo,
    ruta_salida: str = "grafo_socialtec.png",
    titulo: str = "Red Social Socialtec",
    resaltar_usuarios: Optional[Set[str]] = None,
    mostrar_etiquetas: bool = True,
    tamaño_figura: tuple[int, int] = (12, 8),
    dpi: int = 100
) -> str:
    try:
        G = nx.Graph()
        
        usuarios = grafo.usuarios()
        if not usuarios:
            raise VisualizacionError("El grafo está vacío, no hay usuarios para visualizar.")
        
        G.add_nodes_from(usuarios)
        
        for usuario in usuarios:
            amigos = grafo.amigos_de(usuario)
            for amigo in amigos:
                if usuario < amigo:
                    G.add_edge(usuario, amigo)
        
        plt.figure(figsize=tamaño_figura, dpi=dpi)
        plt.title(titulo, fontsize=16, fontweight='bold')
        plt.axis('off')
        
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        node_colors = []
        for node in G.nodes():
            if resaltar_usuarios and node in resaltar_usuarios:
                node_colors.append('#FF6B6B')  # Rojo para resaltados
            else:
                node_colors.append('#4ECDC4')  # Turquesa para normales
        
        # Dibujar nodos
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=800,
            alpha=0.9,
            edgecolors='black',
            linewidths=2
        )
        
        # Dibujar aristas
        nx.draw_networkx_edges(
            G, pos,
            width=2,
            alpha=0.5,
            edge_color='#95E1D3'
        )
        
        # Dibujar etiquetas si se solicita
        if mostrar_etiquetas:
            nx.draw_networkx_labels(
                G, pos,
                font_size=10,
                font_weight='bold',
                font_color='black'
            )
        
        # Guardar imagen
        ruta_absoluta = Path(ruta_salida).resolve()
        ruta_absoluta.parent.mkdir(parents=True, exist_ok=True)
        
        plt.tight_layout()
        plt.savefig(
            str(ruta_absoluta),
            format='png',
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none'
        )
        plt.close()
        
        return str(ruta_absoluta)
    
    except Exception as e:
        raise VisualizacionError(f"Error al visualizar grafo: {e}") from e


def visualizar_camino(
    grafo: Grafo,
    camino: list[str],
    ruta_salida: str = "camino_socialtec.png",
    titulo: Optional[str] = None
) -> str:
    """
    Visualiza el grafo completo resaltando un camino específico entre usuarios.
    
    Args:
        grafo: Instancia de Grafo
        camino: Lista de usernames que forman el camino (resultado de BFS/DFS)
        ruta_salida: Path donde guardar la imagen
        titulo: Título personalizado (si es None, se genera automático)
    
    Returns:
        str: Ruta absoluta del archivo generado
    """
    if not camino or len(camino) < 2:
        raise VisualizacionError("El camino debe tener al menos 2 usuarios.")
    
    if titulo is None:
        titulo = f"Camino: {camino[0]} → {camino[-1]}"
    
    resaltar = set(camino)
    return visualizar_grafo(
        grafo,
        ruta_salida=ruta_salida,
        titulo=titulo,
        resaltar_usuarios=resaltar
    )


def estadisticas_visuales(grafo: Grafo, ruta_salida: str = "stats_grafo.png") -> str:
    """
    Genera un gráfico con estadísticas visuales del grafo:
    - Distribución de grados (cantidad de amigos por usuario)
    
    Args:
        grafo: Instancia de Grafo
        ruta_salida: Path donde guardar la imagen
    
    Returns:
        str: Ruta absoluta del archivo generado
    """
    try:
        usuarios = grafo.usuarios()
        if not usuarios:
            raise VisualizacionError("No hay usuarios en el grafo.")
        
        # Calcular grados
        grados = [grafo.grado(u) for u in usuarios]
        
        # Crear histograma
        plt.figure(figsize=(10, 6), dpi=100)
        plt.hist(grados, bins=range(0, max(grados) + 2), 
                 color='#4ECDC4', edgecolor='black', alpha=0.7)
        plt.xlabel('Cantidad de amigos', fontsize=12, fontweight='bold')
        plt.ylabel('Cantidad de usuarios', fontsize=12, fontweight='bold')
        plt.title('Distribución de Amistades en Socialtec', 
                  fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        
        # Guardar
        ruta_absoluta = Path(ruta_salida).resolve()
        ruta_absoluta.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(str(ruta_absoluta), format='png', bbox_inches='tight')
        plt.close()
        
        return str(ruta_absoluta)
    
    except Exception as e:
        raise VisualizacionError(f"Error al generar estadísticas visuales: {e}") from e


# =========================
# Helper: Info del grafo
# =========================
def info_grafo(grafo: Grafo) -> str:
    """
    Devuelve un string con información básica del grafo para logs/GUI.
    """
    usuarios = grafo.usuarios()
    n = len(usuarios)
    m = grafo.numero_amistades()
    
    if n == 0:
        return "Grafo vacío (sin usuarios)"
    
    promedio = (2 * m) / n if n > 0 else 0
    
    return (
        f" Info del Grafo:\n"
        f"  * Usuarios: {n}\n"
        f"  * Amistades: {m}\n"
        f"  * Promedio de amigos: {promedio:.2f}"
    )
