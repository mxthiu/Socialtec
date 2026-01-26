from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QScrollArea, QWidget, QPushButton
)
from PyQt6.QtCore import Qt

from cliente.estilos import *


class ContenidoEstadisticas(QWidget):
    """Pantalla de estadísticas globales de la red social"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        self.crear_header(layout_principal)
        
        # Scroll para contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        scroll.setWidget(contenido)
        
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(25, 20, 25, 20)
        layout_contenido.setSpacing(20)
        contenido.setLayout(layout_contenido)
        
        # Cargar estadísticas
        self.cargar_estadisticas(layout_contenido)
        
        layout_contenido.addStretch()
        layout_principal.addWidget(scroll)
    
    def crear_header(self, layout):
        """Header con título y botón volver"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-bottom: 1px solid {COLORES['borde']};
                padding: 20px;
            }}
        """)
        
        layout_frame = QVBoxLayout()
        frame.setLayout(layout_frame)
        
        btn_volver = QPushButton("← Volver")
        btn_volver.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 1px solid {COLORES['borde']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORES['primario']};
                color: white;
                border: 1px solid {COLORES['primario']};
            }}
        """)
        btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_volver.clicked.connect(self.volver_atras)
        btn_volver.setFixedWidth(110)
        
        layout_frame.addWidget(btn_volver)
        layout_frame.addSpacing(10)
        
        label_titulo = QLabel("Estadísticas Globales")
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 26px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_desc = QLabel("Análisis de la red social SocialTec")
        label_desc.setStyleSheet(ESTILO_SUBTITULO)
        
        layout_frame.addWidget(label_titulo)
        layout_frame.addWidget(label_desc)
        
        layout.addWidget(frame)
    
    def volver_atras(self):
        """Vuelve a la pantalla anterior"""
        if self.parent_window:
            self.parent_window.volver_atras()
    
    def cargar_estadisticas(self, layout):
        """Carga y muestra las estadísticas"""
        from cliente.datos_local import obtener_estadisticas_globales
        
        stats = obtener_estadisticas_globales()
        
        
        self.crear_card_principal(
            layout,
            "Total de Usuarios",
            str(stats["total_usuarios"]),
            "usuarios registrados"
        )
        
        self.crear_card_principal(
            layout,
            "Promedio de Amigos",
            str(stats["promedio_amigos"]),
            "amigos por usuario"
        )
        
        
        if stats["usuario_mas_amigos"]:
            self.crear_card_usuario(
                layout,
                "Usuario con Más Amigos",
                stats["usuario_mas_amigos"],
                COLORES['exito']
            )
        
        
        if stats["usuario_menos_amigos"]:
            self.crear_card_usuario(
                layout,
                "Usuario con Menos Amigos",
                stats["usuario_menos_amigos"],
                COLORES['texto_secundario']
            )
        
        
        if stats["todos_usuarios"]:
            self.crear_top_usuarios(layout, stats["todos_usuarios"][:5])
    
    def crear_card_principal(self, layout, titulo, valor, descripcion):
        """Card con estadística principal"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 15px;
                padding: 25px;
            }}
        """)
        
        layout_card = QVBoxLayout()
        layout_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_card.setSpacing(10)
        frame.setLayout(layout_card)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 14px;
                background: transparent;
            }}
        """)
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 48px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_desc = QLabel(descripcion)
        label_desc.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 13px;
                background: transparent;
            }}
        """)
        label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_card.addWidget(label_titulo)
        layout_card.addWidget(label_valor)
        layout_card.addWidget(label_desc)
        
        layout.addWidget(frame)
    
    def crear_card_usuario(self, layout, titulo, usuario_data, color):
        """Card con datos de un usuario específico"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-left: 5px solid {color};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        layout_card = QVBoxLayout()
        layout_card.setSpacing(8)
        frame.setLayout(layout_card)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_nombre = QLabel(usuario_data["nombre"])
        label_nombre.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_usuario = QLabel(f"@{usuario_data['usuario']}")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 14px;
                background: transparent;
            }}
        """)
        
        label_amigos = QLabel(f"{usuario_data['cantidad_amigos']} amigos")
        label_amigos.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                margin-top: 5px;
            }}
        """)
        
        layout_card.addWidget(label_titulo)
        layout_card.addWidget(label_nombre)
        layout_card.addWidget(label_usuario)
        layout_card.addWidget(label_amigos)
        
        layout.addWidget(frame)
    
    def crear_top_usuarios(self, layout, usuarios):
        """Lista de top usuarios"""
        label_titulo = QLabel("Top Usuarios por Amigos")
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0;
            }}
        """)
        layout.addWidget(label_titulo)
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout_lista = QVBoxLayout()
        layout_lista.setSpacing(10)
        frame.setLayout(layout_lista)
        
        for i, usuario in enumerate(usuarios, 1):
            item = self.crear_item_top(i, usuario)
            layout_lista.addWidget(item)
        
        layout.addWidget(frame)
    
    def crear_item_top(self, posicion, usuario_data):
        """Item de usuario en el top"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORES['superficie_clara']};
                border-radius: 8px;
            }}
        """)
        
        # Posición
        label_pos = QLabel(f"{posicion}.")
        label_pos.setFixedWidth(40)
        label_pos.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 20px;
                background: transparent;
            }}
        """)
        
        # Info usuario
        layout_info = QVBoxLayout()
        layout_info.setSpacing(2)
        
        label_nombre = QLabel(usuario_data["nombre"])
        label_nombre.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_usuario = QLabel(f"@{usuario_data['usuario']}")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 12px;
                background: transparent;
            }}
        """)
        
        layout_info.addWidget(label_nombre)
        layout_info.addWidget(label_usuario)
        
        # Cantidad amigos
        label_amigos = QLabel(str(usuario_data["cantidad_amigos"]))
        label_amigos.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['primario']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_texto = QLabel("amigos")
        label_texto.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 11px;
                background: transparent;
            }}
        """)
        
        layout_amigos = QVBoxLayout()
        layout_amigos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_amigos.setSpacing(0)
        layout_amigos.addWidget(label_amigos)
        layout_amigos.addWidget(label_texto)
        
        layout.addWidget(label_pos)
        layout.addLayout(layout_info)
        layout.addStretch()
        layout.addLayout(layout_amigos)
        
        return widget

