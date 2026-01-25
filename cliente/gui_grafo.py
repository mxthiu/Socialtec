from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

from cliente.estilos import *


class ContenidoGrafo(QWidget):
    """Contenido de la pantalla de visualización del grafo"""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.parent_window = parent
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        # Header
        self.crear_header(layout_principal)
        
        # Scroll para contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        scroll.setWidget(contenido)
        
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(20, 20, 20, 20)
        layout_contenido.setSpacing(20)
        contenido.setLayout(layout_contenido)
        
        # Área donde se mostrará el grafo
        self.crear_area_grafo(layout_contenido)
        
        # Controles
        self.crear_controles(layout_contenido)
        
        layout_contenido.addStretch()
        layout_principal.addWidget(scroll)
    
    def crear_header(self, layout):
        """Crea el header"""
        frame_header = QFrame()
        frame_header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-bottom: 1px solid {COLORES['borde']};
                padding: 15px;
            }}
        """)
        
        layout_header = QVBoxLayout()
        layout_header.setSpacing(5)
        frame_header.setLayout(layout_header)
        
        # Título
        label_titulo = QLabel("Visualización del Grafo")
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        # Descripción
        label_desc = QLabel("Red de conexiones entre usuarios de SocialTec")
        label_desc.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 14px;
                background: transparent;
            }}
        """)
        
        layout_header.addWidget(label_titulo)
        layout_header.addWidget(label_desc)
        
        layout.addWidget(frame_header)
    
    def crear_area_grafo(self, layout):
        """Crea el área donde se dibujará el grafo"""
        # Frame contenedor del grafo
        self.frame_grafo = QFrame()
        self.frame_grafo.setMinimumHeight(400)
        self.frame_grafo.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 15px;
                border: 2px dashed {COLORES['borde']};
            }}
        """)
        
        # Layout del frame
        layout_grafo = QVBoxLayout()
        layout_grafo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_grafo.setLayout(layout_grafo)
        
        # Mensaje placeholder (mientras no hay grafo)
        self.label_placeholder = QLabel(
            "El grafo se mostrará aquí\n\n"
            "Implementación pendiente del servidor"
        )
        self.label_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_placeholder.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 16px;
                background: transparent;
                padding: 60px;
            }}
        """)
        layout_grafo.addWidget(self.label_placeholder)
        
        # agregar el canvas de matplotlib/networkx
        # self.canvas_grafo = FigureCanvasQTAgg(figura)
        # layout_grafo.addWidget(self.canvas_grafo)
        
        layout.addWidget(self.frame_grafo)
    
    def crear_controles(self, layout):
        """Crea botones de control del grafo"""
        # Título de sección
        label_controles = QLabel("Controles")
        label_controles.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0;
            }}
        """)
        layout.addWidget(label_controles)
        
        # Frame de botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout_botones = QVBoxLayout()
        layout_botones.setSpacing(10)
        frame_botones.setLayout(layout_botones)
        
        # Botón actualizar grafo
        btn_actualizar = QPushButton("Actualizar Grafo")
        btn_actualizar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['primario']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORES['primario_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto_secundario']};
            }}
        """)
        btn_actualizar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_actualizar.clicked.connect(self.actualizar_grafo)
        btn_actualizar.setEnabled(False)  # Deshabilitado hasta que haya implementación
        
        # Botón buscar camino
        btn_buscar_camino = QPushButton("Buscar Camino entre Usuarios")
        btn_buscar_camino.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORES['borde']};
                border-color: {COLORES['primario']};
            }}
            QPushButton:disabled {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto_secundario']};
                border-color: {COLORES['borde']};
            }}
        """)
        btn_buscar_camino.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_buscar_camino.clicked.connect(self.buscar_camino)
        btn_buscar_camino.setEnabled(False)  # Deshabilitado hasta que haya implementación
        
        # Botón ver estadísticas del grafo
        btn_estadisticas = QPushButton("Ver Estadísticas del Grafo")
        btn_estadisticas.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORES['borde']};
                border-color: {COLORES['primario']};
            }}
        """)
        btn_estadisticas.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_estadisticas.clicked.connect(self.ver_estadisticas_grafo)
        
        layout_botones.addWidget(btn_actualizar)
        layout_botones.addWidget(btn_buscar_camino)
        layout_botones.addWidget(btn_estadisticas)
        
        # Información adicional
        label_info = QLabel(
            "Nota: La actualización en tiempo real y búsqueda de caminos\n"
            "se habilitarán cuando el servidor esté implementado."
        )
        label_info.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 12px;
                background: transparent;
                padding: 10px;
            }}
        """)
        label_info.setWordWrap(True)
        layout_botones.addWidget(label_info)
        
        layout.addWidget(frame_botones)
    
    def actualizar_grafo(self):
        """Actualiza la visualización del grafo"""
        
        # 1. Pedir datos al servidor
        # 2. Redibujar el grafo con NetworkX
        print("Actualizar grafo - Implementación pendiente")
    
    def buscar_camino(self):
        """Abre diálogo para buscar camino entre dos usuarios"""
        
        # 1. Mostrar diálogo con 2 campos (usuario origen y destino)
        # 2. Pedir al servidor que calcule el camino (BFS/DFS)
        # 3. Mostrar el resultado visualmente en el grafo
        print("Buscar camino - Implementación pendiente")
    
    def ver_estadisticas_grafo(self):
        """Muestra estadísticas del grafo (abre ventana de estadísticas globales)"""
        from cliente.gui_estadisticas import VentanaEstadisticas
        dialogo = VentanaEstadisticas(self)
        dialogo.exec()
    
    def actualizar_datos(self):
        """Recarga los datos cuando se actualiza desde otra pantalla"""
        pass