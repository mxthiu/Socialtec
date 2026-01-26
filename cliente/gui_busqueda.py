from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

from cliente.estilos import *


class WidgetResultadoBusqueda(QWidget):
    """Widget para mostrar un resultado de búsqueda"""
    ver_perfil_clicked = pyqtSignal(dict)
    
    def __init__(self, usuario_data):
        super().__init__()
        self.usuario_data = usuario_data
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Crea el widget"""
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORES['superficie']};
                border-radius: 12px;
            }}
            QWidget:hover {{
                background-color: {COLORES['superficie_clara']};
            }}
        """)
        
        # Foto
        label_foto = QLabel()
        label_foto.setFixedSize(60, 60)
        label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.usuario_data.get("foto"):
            pass
        
        # Foto por defecto
        inicial = self.usuario_data["nombre"][0].upper()
        label_foto.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORES['primario']};
                border-radius: 30px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        label_foto.setText(inicial)
        
        # Información
        layout_info = QVBoxLayout()
        layout_info.setSpacing(3)
        
        nombre_completo = f"{self.usuario_data['nombre']} {self.usuario_data['apellido']}"
        label_nombre = QLabel(nombre_completo)
        label_nombre.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_usuario = QLabel(f"@{self.usuario_data['usuario']}")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 13px;
                background: transparent;
            }}
        """)
        
        layout_info.addWidget(label_nombre)
        layout_info.addWidget(label_usuario)
        
        # Botón ver perfil
        btn_ver = QPushButton("Ver")
        btn_ver.setFixedSize(70, 35)
        btn_ver.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ver.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['primario']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['primario_hover']};
            }}
        """)
        btn_ver.clicked.connect(lambda: self.ver_perfil_clicked.emit(self.usuario_data))
        
        layout.addWidget(label_foto)
        layout.addLayout(layout_info)
        layout.addStretch()
        layout.addWidget(btn_ver)


class ContenidoBusqueda(QWidget):
    """Contenido de la pantalla de búsqueda"""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.parent_window = parent
        self.resultados_widgets = []
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        # Header con barra de búsqueda
        self.crear_header(layout_principal)
        
        # Scroll para resultados
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.contenedor_resultados = QWidget()
        scroll.setWidget(self.contenedor_resultados)
        
        self.layout_resultados = QVBoxLayout()
        self.layout_resultados.setContentsMargins(20, 20, 20, 20)
        self.layout_resultados.setSpacing(12)
        self.layout_resultados.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.contenedor_resultados.setLayout(self.layout_resultados)
        
        # Mensaje inicial
        self.label_mensaje = QLabel("Busca usuarios por nombre o usuario")
        self.label_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 16px;
                padding: 60px;
                background: transparent;
            }}
        """)
        self.layout_resultados.addWidget(self.label_mensaje)
        
        layout_principal.addWidget(scroll)
    
    def crear_header(self, layout):
        """Crea el header con búsqueda"""
        frame_header = QFrame()
        frame_header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-bottom: 1px solid {COLORES['borde']};
                padding: 15px;
            }}
        """)
        
        layout_header = QVBoxLayout()
        layout_header.setSpacing(10)
        frame_header.setLayout(layout_header)
        
        # Título
        label_titulo = QLabel("Buscar Usuarios")
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        # Input de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre o usuario...")
        self.input_busqueda.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORES['fondo']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 12px;
                padding: 14px 18px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORES['primario']};
            }}
        """)
        self.input_busqueda.textChanged.connect(self.buscar_usuarios)
        self.input_busqueda.returnPressed.connect(self.buscar_usuarios)
        
        layout_header.addWidget(label_titulo)
        layout_header.addWidget(self.input_busqueda)
        
        layout.addWidget(frame_header)
    
    def buscar_usuarios(self):
        """Busca usuarios según el texto ingresado"""
        texto = self.input_busqueda.text().strip().lower()
        
        for widget in self.resultados_widgets:
            widget.deleteLater()
        self.resultados_widgets.clear()
        self.label_mensaje.hide()
        
        if not texto:
            self.label_mensaje.setText("Busca usuarios por nombre o usuario")
            self.label_mensaje.show()
            return
        
        # Buscar en datos locales
        from cliente.datos_local import buscar_usuarios as buscar
        resultados = buscar(texto)
        
        # Filtrar el usuario actual
        resultados = [u for u in resultados if u['usuario'] != self.usuario_data['usuario']]
        
        if not resultados:
            self.label_mensaje.setText(f"No se encontraron resultados para '{texto}'")
            self.label_mensaje.show()
        else:
            for usuario in resultados:
                widget = WidgetResultadoBusqueda(usuario)
                widget.ver_perfil_clicked.connect(self.ver_perfil_usuario)
                self.layout_resultados.addWidget(widget)
                self.resultados_widgets.append(widget)
    
    def ver_perfil_usuario(self, usuario_data):
        """Abre un perfil en modo lectura para otro usuario"""
        try:
            from cliente.datos_local import cargar_usuarios, obtener_amigos_completos
            from cliente.gui_perfil_publico import ContenidoPerfilPublico

            usuarios = cargar_usuarios()
            username = usuario_data["usuario"]
            if username in usuarios:
                datos = usuarios[username]
                amigos = obtener_amigos_completos(datos.get("amigos", []))
                perfil_data = {
                    "nombre": datos.get("nombre", ""),
                    "apellido": datos.get("apellido", ""),
                    "usuario": username,
                    "foto": datos.get("foto"),
                    "email": datos.get("email", ""),
                    "amigos": amigos,
                }
                contenido = ContenidoPerfilPublico(self.usuario_data, perfil_data, self.parent_window)
                self.parent_window.navegar_a_pantalla(contenido)
        except Exception:
            return

