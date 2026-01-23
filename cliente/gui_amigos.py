# gui_amigos.py - Pantalla de lista de amigos

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

from cliente.estilos import *


class WidgetAmigoLista(QWidget):
    """Widget para mostrar un amigo en la lista"""
    eliminar_clicked = pyqtSignal(str)
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
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Foto
        label_foto = QLabel()
        label_foto.setFixedSize(55, 55)
        label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        inicial = self.usuario_data["nombre"][0].upper()
        label_foto.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORES['primario']};
                border-radius: 27px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }}
        """)
        label_foto.setText(inicial)
        
        # Info
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
        
        # Botón eliminar
        btn_eliminar = QPushButton("X")
        btn_eliminar.setFixedSize(38, 38)
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eliminar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['texto_secundario']};
                border: 2px solid {COLORES['borde']};
                border-radius: 19px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['error']};
                color: white;
                border-color: {COLORES['error']};
            }}
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_clicked.emit(self.usuario_data['usuario']))
        
        layout.addWidget(label_foto)
        layout.addLayout(layout_info)
        layout.addStretch()
        layout.addWidget(btn_eliminar)
    
    def mousePressEvent(self, event):
        """Click para ver perfil"""
        self.ver_perfil_clicked.emit(self.usuario_data)


class ContenidoAmigos(QWidget):
    """Contenido de la pantalla de amigos"""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.parent_window = parent
        self.widgets_amigos = []
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        # Header
        self.crear_header(layout_principal)
        
        # Scroll para amigos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.contenedor_amigos = QWidget()
        scroll.setWidget(self.contenedor_amigos)
        
        self.layout_amigos = QVBoxLayout()
        self.layout_amigos.setContentsMargins(20, 20, 20, 20)
        self.layout_amigos.setSpacing(12)
        self.contenedor_amigos.setLayout(self.layout_amigos)
        
        # Cargar amigos
        self.actualizar_lista_amigos()
        
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
        layout_header.setSpacing(10)
        frame_header.setLayout(layout_header)
        
        # Título con contador
        self.label_titulo = QLabel()
        self.label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        # Búsqueda rápida
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar amigos...")
        self.input_filtro.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORES['fondo']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORES['primario']};
            }}
        """)
        self.input_filtro.textChanged.connect(self.filtrar_amigos)
        
        layout_header.addWidget(self.label_titulo)
        layout_header.addWidget(self.input_filtro)
        
        layout.addWidget(frame_header)
    
    def actualizar_lista_amigos(self):
        """Actualiza la lista de amigos"""
        # Limpiar layout completo (incluye stretches previas)
        while self.layout_amigos.count():
            item = self.layout_amigos.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.widgets_amigos.clear()
        
        amigos_ordenados = sorted(
            self.usuario_data['amigos'],
            key=lambda x: f"{x['nombre']} {x['apellido']}"
        )

        # Actualizar contador en header
        self.label_titulo.setText(f"Mis Amigos ({len(amigos_ordenados)})")
        
        if not amigos_ordenados:
            label_vacio = QLabel("No tienes amigos aún.\nVe a Buscar para agregar amigos.")
            label_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_vacio.setStyleSheet(f"""
                QLabel {{
                    color: {COLORES['texto_secundario']};
                    font-size: 16px;
                    padding: 80px 20px;
                    background: transparent;
                }}
            """)
            self.layout_amigos.addWidget(label_vacio)
            self.widgets_amigos.append(label_vacio)
        else:
            for amigo in amigos_ordenados:
                widget = WidgetAmigoLista(amigo)
                widget.eliminar_clicked.connect(self.eliminar_amigo)
                widget.ver_perfil_clicked.connect(self.ver_perfil)
                self.layout_amigos.addWidget(widget)
                self.widgets_amigos.append(widget)
        
        self.layout_amigos.addStretch()
    
    def filtrar_amigos(self):
        """Filtra la lista en tiempo real"""
        texto = self.input_filtro.text().lower()
        
        for widget in self.widgets_amigos:
            if isinstance(widget, WidgetAmigoLista):
                nombre = f"{widget.usuario_data['nombre']} {widget.usuario_data['apellido']}".lower()
                usuario = widget.usuario_data['usuario'].lower()
                
                if texto in nombre or texto in usuario:
                    widget.show()
                else:
                    widget.hide()
    
    def eliminar_amigo(self, usuario):
        """Elimina un amigo"""
        try:
            from cliente.datos_local import eliminar_amigo, cargar_usuarios, obtener_amigos_completos

            usuario_actual = self.usuario_data.get("usuario")
            exito, _ = eliminar_amigo(usuario_actual, usuario)
            if not exito:
                return

            usuarios = cargar_usuarios()
            if usuario_actual in usuarios:
                amigos_actualizados = usuarios[usuario_actual].get("amigos", [])
                self.usuario_data['amigos'] = obtener_amigos_completos(amigos_actualizados)

            self.actualizar_lista_amigos()

            # Actualizar otras pantallas
            if self.parent_window:
                self.parent_window.actualizar_datos_usuario()
        except Exception:
            return
    
    def ver_perfil(self, usuario_data):
        """Ver perfil de un amigo en modo lectura"""
        try:
            from cliente.datos_local import cargar_usuarios, obtener_amigos_completos
            from cliente.gui_perfil_publico import VentanaPerfilPublico
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
                self.ventana_perfil = VentanaPerfilPublico(self.usuario_data, perfil_data, self)
                self.ventana_perfil.show()
        except Exception:
            return
    
    def actualizar_datos(self):
        """Recarga los datos"""
        try:
            from cliente.datos_local import cargar_usuarios, obtener_amigos_completos

            username = self.usuario_data.get("usuario")
            usuarios = cargar_usuarios()
            if username in usuarios:
                amigos_actualizados = usuarios[username].get("amigos", [])
                self.usuario_data['amigos'] = obtener_amigos_completos(amigos_actualizados)
        except Exception:
            pass

        self.actualizar_lista_amigos()