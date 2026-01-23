# gui_perfil_contenido.py - Contenido de la pantalla de perfil

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

from cliente.estilos import *


class ContenidoPerfil(QWidget):
    """Contenido de la pantalla de perfil (sin navegación)"""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.parent_window = parent
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura el contenido del perfil"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        # Scroll area para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        scroll.setWidget(contenido)
        
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(30, 30, 30, 30)
        layout_contenido.setSpacing(25)
        contenido.setLayout(layout_contenido)
        
        # ===== HEADER CON FOTO Y NOMBRE =====
        self.crear_header(layout_contenido)
        
        # ===== ESTADÍSTICAS =====
        self.crear_estadisticas(layout_contenido)
        
        # ===== INFORMACIÓN RÁPIDA =====
        self.crear_info_rapida(layout_contenido)
        
        layout_contenido.addStretch()
        layout_principal.addWidget(scroll)
    
    def crear_header(self, layout):
        """Header con foto y nombre"""
        layout_header = QVBoxLayout()
        layout_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_header.setSpacing(12)
        
        # Foto de perfil
        self.label_foto = QLabel()
        self.label_foto.setFixedSize(140, 140)
        self.label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.usuario_data.get("foto"):
            self.cargar_foto_circular(self.usuario_data["foto"])
        else:
            inicial = self.usuario_data["nombre"][0].upper()
            self.label_foto.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORES['primario']};
                    border: 5px solid {COLORES['superficie']};
                    border-radius: 70px;
                    color: white;
                    font-size: 56px;
                    font-weight: bold;
                }}
            """)
            self.label_foto.setText(inicial)
        
        # Nombre
        nombre_completo = f"{self.usuario_data['nombre']} {self.usuario_data['apellido']}"
        self.label_nombre = QLabel(nombre_completo)
        self.label_nombre.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 28px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        self.label_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Usuario
        self.label_usuario = QLabel(f"@{self.usuario_data['usuario']}")
        self.label_usuario.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 16px;
                background: transparent;
            }}
        """)
        self.label_usuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_header.addWidget(self.label_foto)
        layout_header.addWidget(self.label_nombre)
        layout_header.addWidget(self.label_usuario)
        
        layout.addLayout(layout_header)
    
    def crear_estadisticas(self, layout):
        """Card con estadísticas"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        layout_frame = QHBoxLayout()
        layout_frame.setSpacing(0)
        frame.setLayout(layout_frame)
        
        # Estadísticas
        stats = [
            ("", str(len(self.usuario_data['amigos'])), "Amigos"),
        ]

        for icono, numero, texto in stats:
            stat_widget, label_numero = self.crear_stat_widget(icono, numero, texto)
            if texto == "Amigos":
                self.label_amigos_stat = label_numero
            layout_frame.addWidget(stat_widget)
        
        layout.addWidget(frame)
    
    def crear_stat_widget(self, icono, numero, texto):
        """Crea un widget de estadística"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        widget.setLayout(layout)
        
        label_icono = QLabel(icono)
        label_icono.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                background: transparent;
            }}
        """)
        label_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_numero = QLabel(numero)
        label_numero.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        label_numero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_texto = QLabel(texto)
        label_texto.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 13px;
                background: transparent;
            }}
        """)
        label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label_icono)
        layout.addWidget(label_numero)
        layout.addWidget(label_texto)
        
        return widget, label_numero
    
    def crear_info_rapida(self, layout):
        """Información rápida del perfil"""
        # Título
        label_titulo = QLabel("Información")
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
        
        # Frame con info
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        layout_info = QVBoxLayout()
        layout_info.setSpacing(15)
        frame.setLayout(layout_info)
        
        # Items de información
        items = [
            ("", "Usuario", f"@{self.usuario_data['usuario']}"),
            ("", "Nombre completo", f"{self.usuario_data['nombre']} {self.usuario_data['apellido']}"),
        ]
        
        for icono, titulo, valor in items:
            item, label_valor = self.crear_item_info(icono, titulo, valor)
            if titulo == "Usuario":
                self.label_info_usuario = label_valor
            if titulo == "Nombre completo":
                self.label_info_nombre = label_valor
            layout_info.addWidget(item)
        
        layout.addWidget(frame)
    
    def crear_item_info(self, icono, titulo, valor):
        """Crea un item de información"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        # Icono
        label_icono = QLabel(icono)
        label_icono.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                background: transparent;
            }}
        """)
        
        # Texto
        layout_texto = QVBoxLayout()
        layout_texto.setSpacing(2)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 12px;
                background: transparent;
            }}
        """)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        layout_texto.addWidget(label_titulo)
        layout_texto.addWidget(label_valor)
        
        layout.addWidget(label_icono)
        layout.addLayout(layout_texto)
        layout.addStretch()
        
        return widget, label_valor
    
    def cargar_foto_circular(self, ruta):
        """Carga foto en formato circular"""
        pixmap = QPixmap(ruta)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                140, 140,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            resultado = QPixmap(140, 140)
            resultado.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(resultado)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            path.addEllipse(0, 0, 140, 140)
            painter.setClipPath(path)
            
            x = (140 - pixmap.width()) // 2
            y = (140 - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
            painter.end()
            
            self.label_foto.setPixmap(resultado)
            self.label_foto.setStyleSheet(f"""
                QLabel {{
                    border: 5px solid {COLORES['primario']};
                    border-radius: 70px;
                }}
            """)
    
    def actualizar_datos(self):
        """Actualiza los datos mostrados"""
        nombre = self.usuario_data.get("nombre", "")
        apellido = self.usuario_data.get("apellido", "")
        username = self.usuario_data.get("usuario", "")
        amigos = self.usuario_data.get("amigos", [])

        # Foto
        self.label_foto.clear()
        if self.usuario_data.get("foto"):
            self.cargar_foto_circular(self.usuario_data["foto"])
        else:
            inicial = nombre[:1].upper() or "?"
            self.label_foto.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORES['primario']};
                    border: 5px solid {COLORES['superficie']};
                    border-radius: 70px;
                    color: white;
                    font-size: 56px;
                    font-weight: bold;
                }}
            """)
            self.label_foto.setText(inicial)

        # Texto principal
        self.label_nombre.setText(f"{nombre} {apellido}".strip())
        self.label_usuario.setText(f"@{username}")

        # Info rápida
        self.label_info_usuario.setText(f"@{username}")
        self.label_info_nombre.setText(f"{nombre} {apellido}".strip())

        # Estadística de amigos
        if hasattr(self, "label_amigos_stat"):
            self.label_amigos_stat.setText(str(len(amigos)))