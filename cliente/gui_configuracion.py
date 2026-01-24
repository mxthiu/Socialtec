from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

from cliente.estilos import *


class ContenidoConfiguracion(QWidget):
    """Contenido de configuración y estadísticas"""
    
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
        
        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        scroll.setWidget(contenido)
        
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(20, 20, 20, 20)
        layout_contenido.setSpacing(20)
        contenido.setLayout(layout_contenido)
        
        # Título
        label_titulo = QLabel("Configuración")
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0;
            }}
        """)
        layout_contenido.addWidget(label_titulo)
        
        
        self.crear_seccion_estadisticas(layout_contenido)
        
        
        self.crear_seccion_cuenta(layout_contenido)
        
        
        self.crear_seccion_acciones(layout_contenido)
        
        layout_contenido.addStretch()
        layout_principal.addWidget(scroll)
    
    def crear_seccion_estadisticas(self, layout):
        """Crea la sección de estadísticas"""
        label_seccion = QLabel("Estadísticas")
        label_seccion.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0;
            }}
        """)
        layout.addWidget(label_seccion)
        
        # Frame de estadísticas
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        layout_stats = QVBoxLayout()
        layout_stats.setSpacing(15)
        frame.setLayout(layout_stats)
        
        # Stats individuales
        stats = [
            ("Total de amigos", str(len(self.usuario_data['amigos']))),
            ("Cuenta creada", "Enero 2025"),
            ("Última conexión", "Hoy"),
        ]
        
        for titulo, valor in stats:
            item = self.crear_stat_item(titulo, valor)
            layout_stats.addWidget(item)
        
        layout.addWidget(frame)
    
    def crear_stat_item(self, titulo, valor):
        """Crea un item de estadística"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        widget.setLayout(layout)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 20px;
                background: transparent;
            }}
        """)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        layout.addWidget(label_titulo)
        layout.addStretch()
        layout.addWidget(label_valor)
        
        return widget
    
    def crear_seccion_cuenta(self, layout):
        """Sección de información de cuenta"""
        label_seccion = QLabel("Cuenta")
        label_seccion.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0;
            }}
        """)
        layout.addWidget(label_seccion)
        
        # Frame
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        layout_cuenta = QVBoxLayout()
        layout_cuenta.setSpacing(10)
        frame.setLayout(layout_cuenta)
        
        # Items
        items = [
            ("Usuario", f"@{self.usuario_data['usuario']}"),
            ("Nombre", f"{self.usuario_data['nombre']} {self.usuario_data['apellido']}"),
        ]
        
        for titulo, valor in items:
            item = self.crear_info_item(titulo, valor)
            layout_cuenta.addWidget(item)
        
        layout.addWidget(frame)
    
    def crear_info_item(self, titulo, valor):
        """Crea un item de información"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        widget.setLayout(layout)
        
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 20px;
                background: transparent;
            }}
        """)
        
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)
        
        return widget
    
    def crear_seccion_acciones(self, layout):
        """Sección de acciones"""
        label_seccion = QLabel("Acciones")
        label_seccion.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                padding: 10px 0;
            }}
        """)
        layout.addWidget(label_seccion)
        
        # Botón ver estadísticas globales
        btn_stats = QPushButton("Ver Estadísticas Globales")
        btn_stats.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['primario']};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORES['primario_hover']};
            }}
        """)
        btn_stats.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_stats.clicked.connect(self.ver_estadisticas)
        
        layout.addWidget(btn_stats)
        
        # Botón editar perfil
        btn_editar = QPushButton("Editar Perfil")
        btn_editar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['superficie']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 12px;
                padding: 16px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORES['superficie_clara']};
                border-color: {COLORES['primario']};
            }}
        """)
        btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_editar.clicked.connect(self.editar_perfil)
        
        # Botón cambiar contraseña
        btn_password = QPushButton("Cambiar Contraseña")
        btn_password.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['superficie']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 12px;
                padding: 16px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORES['superficie_clara']};
                border-color: {COLORES['primario']};
            }}
        """)
        btn_password.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_password.clicked.connect(self.cambiar_password)
        
        # Botón cerrar sesión
        btn_cerrar_sesion = QPushButton("Cerrar Sesión")
        btn_cerrar_sesion.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['error']};
                border: 2px solid {COLORES['error']};
                border-radius: 12px;
                padding: 16px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['error']};
                color: white;
            }}
        """)
        btn_cerrar_sesion.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar_sesion.clicked.connect(self.cerrar_sesion)
        
        layout.addWidget(btn_editar)
        layout.addWidget(btn_password)
        layout.addSpacing(10)
        layout.addWidget(btn_cerrar_sesion)
    
    def ver_estadisticas(self):
        """Abre ventana de estadísticas globales"""
        from cliente.gui_estadisticas import VentanaEstadisticas
        dialogo = VentanaEstadisticas(self)
        dialogo.exec()
    
    def editar_perfil(self):
        """Editar perfil"""
        from cliente.gui_editar_perfil import VentanaEditarPerfil
        
        dialogo = VentanaEditarPerfil(self.usuario_data, self)
        dialogo.perfil_actualizado.connect(self.on_perfil_actualizado)
        
        if dialogo.exec():
            print("Perfil actualizado")
    
    def on_perfil_actualizado(self, datos_nuevos):
        """Callback cuando se actualiza el perfil"""
        self.usuario_data.update(datos_nuevos)
        
        if self.parent_window:
            self.parent_window.usuario_data.update(datos_nuevos)
            self.parent_window.actualizar_datos_usuario()
    
    def cambiar_password(self):
        """Cambiar contraseña"""
        from cliente.gui_cambiar_password import VentanaCambiarPassword
        
        dialogo = VentanaCambiarPassword(self.usuario_data, self)
        
        if dialogo.exec():
            print("Contraseña cambiada exitosamente")
    
    def cerrar_sesion(self):
        """Cerrar sesión"""
        if self.parent_window:
            self.parent_window.cerrar_sesion()

