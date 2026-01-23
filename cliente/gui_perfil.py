# gui_perfil.py - Pantalla de perfil del usuario en SocialTec

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QApplication,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath
import sys

# Importar estilos
from cliente.estilos import *


class WidgetAmigo(QWidget):
    """Widget personalizado para mostrar un amigo en la lista"""
    eliminar_clicked = pyqtSignal(str)  # Señal cuando se elimina
    
    def __init__(self, nombre, apellido, usuario, foto_path=None):
        super().__init__()
        self.usuario = usuario
        self.nombre_completo = f"{nombre} {apellido}"
        self.inicializar_ui(foto_path)
    
    def inicializar_ui(self, foto_path):
        """Crea el widget del amigo"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Estilo del widget
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORES['superficie_clara']};
                border-radius: 10px;
            }}
            QWidget:hover {{
                background-color: {COLORES['borde']};
            }}
        """)
        
        # Foto de perfil (circular pequeña)
        label_foto = QLabel()
        label_foto.setFixedSize(50, 50)
        label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if foto_path:
            self.cargar_foto_circular(label_foto, foto_path)
        else:
            label_foto.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORES['primario']};
                    border-radius: 25px;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                }}
            """)
            # Mostrar inicial del nombre
            inicial = self.nombre_completo[0].upper() if self.nombre_completo else "?"
            label_foto.setText(inicial)
        
        # Nombre y usuario
        layout_texto = QVBoxLayout()
        layout_texto.setSpacing(2)
        
        label_nombre = QLabel(self.nombre_completo)
        label_nombre.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        label_usuario = QLabel(f"@{self.usuario}")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 12px;
                background: transparent;
            }}
        """)
        
        layout_texto.addWidget(label_nombre)
        layout_texto.addWidget(label_usuario)
        
        # Botón eliminar
        btn_eliminar = QPushButton("X")
        btn_eliminar.setFixedSize(35, 35)
        btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eliminar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['texto_secundario']};
                border: 2px solid {COLORES['borde']};
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['error']};
                color: white;
                border-color: {COLORES['error']};
            }}
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_clicked.emit(self.usuario))
        
        # Agregar widgets al layout
        layout.addWidget(label_foto)
        layout.addLayout(layout_texto)
        layout.addStretch()
        layout.addWidget(btn_eliminar)
    
    def cargar_foto_circular(self, label, ruta):
        """Carga una foto en formato circular"""
        pixmap = QPixmap(ruta)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            resultado = QPixmap(50, 50)
            resultado.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(resultado)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            path.addEllipse(0, 0, 50, 50)
            painter.setClipPath(path)
            
            x = (50 - pixmap.width()) // 2
            y = (50 - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
            painter.end()
            
            label.setPixmap(resultado)


class VentanaPerfil(QMainWindow):
    def __init__(self, usuario_data=None):
        super().__init__()
        # Datos del usuario (simulados por ahora)
        self.usuario_data = usuario_data or {
            "nombre": "Mathias",
            "apellido": "Vargas",
            "usuario": "mathias",
            "foto": None,
            "amigos": [
                {"nombre": "Ana", "apellido": "López", "usuario": "ana_lopez", "foto": None},
                {"nombre": "Juan", "apellido": "Pérez", "usuario": "juanp", "foto": None},
                {"nombre": "María", "apellido": "García", "usuario": "mariag", "foto": None},
                {"nombre": "Carlos", "apellido": "Rodríguez", "usuario": "carlitos", "foto": None},
                {"nombre": "Laura", "apellido": "Martínez", "usuario": "laurita", "foto": None},
            ]
        }
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        self.setWindowTitle("SocialTec - Mi Perfil")
        self.setFixedSize(500, 700)
        self.setStyleSheet(ESTILO_VENTANA)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        widget_central.setLayout(layout_principal)
        
        # ===== BARRA SUPERIOR (Búsqueda) =====
        self.crear_barra_superior(layout_principal)
        
        # ===== CONTENIDO CON SCROLL =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        scroll.setWidget(contenido)
        
        layout_contenido = QVBoxLayout()
        layout_contenido.setContentsMargins(30, 20, 30, 20)
        layout_contenido.setSpacing(20)
        contenido.setLayout(layout_contenido)
        
        # ===== HEADER DE PERFIL =====
        self.crear_header_perfil(layout_contenido)
        
        # ===== ESTADÍSTICAS =====
        self.crear_estadisticas(layout_contenido)
        
        # ===== LISTA DE AMIGOS =====
        self.crear_lista_amigos(layout_contenido)
        
        # ===== BOTÓN CERRAR SESIÓN =====
        btn_cerrar_sesion = QPushButton("Cerrar Sesión")
        btn_cerrar_sesion.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['error']};
                border: 2px solid {COLORES['error']};
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['error']};
                color: white;
            }}
        """)
        btn_cerrar_sesion.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar_sesion.clicked.connect(self.cerrar_sesion)
        layout_contenido.addWidget(btn_cerrar_sesion)
        
        layout_contenido.addStretch()
        layout_principal.addWidget(scroll)
    
    def crear_barra_superior(self, layout):
        """Crea la barra de búsqueda tipo Facebook"""
        barra = QFrame()
        barra.setFixedHeight(60)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-bottom: 1px solid {COLORES['borde']};
            }}
        """)
        
        layout_barra = QHBoxLayout()
        layout_barra.setContentsMargins(15, 10, 15, 10)
        barra.setLayout(layout_barra)
        
        # Input de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar amigos...")
        self.input_busqueda.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid transparent;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORES['primario']};
                background-color: {COLORES['fondo']};
            }}
        """)
        self.input_busqueda.textChanged.connect(self.buscar_en_lista)
        
        layout_barra.addWidget(self.input_busqueda)
        layout.addWidget(barra)
    
    def crear_header_perfil(self, layout):
        """Crea el header con foto y nombre"""
        # Contenedor horizontal para centrar
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        
        # Layout vertical para la foto, nombre y usuario
        layout_header = QVBoxLayout()
        layout_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_header.setSpacing(10)
        
        # Contenedor centrado para la foto
        layout_foto_container = QVBoxLayout()
        layout_foto_container.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Foto de perfil grande
        self.label_foto_perfil = QLabel()
        self.label_foto_perfil.setFixedSize(140, 140)
        self.label_foto_perfil.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.usuario_data.get("foto"):
            self.cargar_foto_perfil(self.usuario_data["foto"])
        else:
            # Foto por defecto con inicial
            inicial = self.usuario_data["nombre"][0].upper()
            self.label_foto_perfil.setStyleSheet(f"""
                QLabel {{
                    background-color: {COLORES['primario']};
                    border: 4px solid {COLORES['borde']};
                    border-radius: 70px;
                    color: white;
                    font-size: 56px;
                    font-weight: bold;
                }}
            """)
            self.label_foto_perfil.setText(inicial)
        
        layout_foto_container.addWidget(self.label_foto_perfil)
        
        # Nombre completo
        nombre_completo = f"{self.usuario_data['nombre']} {self.usuario_data['apellido']}"
        label_nombre = QLabel(nombre_completo)
        label_nombre.setStyleSheet(ESTILO_TITULO)
        label_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Usuario
        label_usuario = QLabel(f"@{self.usuario_data['usuario']}")
        label_usuario.setStyleSheet(ESTILO_SUBTITULO)
        label_usuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_header.addLayout(layout_foto_container)
        layout_header.addWidget(label_nombre)
        layout_header.addWidget(label_usuario)
        
        layout_h.addLayout(layout_header)
        layout_h.addStretch()
        
        layout.addLayout(layout_h)
    
    def crear_estadisticas(self, layout):
        """Muestra estadísticas del usuario"""
        frame_stats = QFrame()
        frame_stats.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout_stats = QHBoxLayout()
        layout_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_stats.setLayout(layout_stats)
        
        # Cantidad de amigos
        label_amigos = QLabel(f" {len(self.usuario_data['amigos'])} amigos")
        label_amigos.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        
        layout_stats.addWidget(label_amigos)
        layout.addWidget(frame_stats)
    
    def crear_lista_amigos(self, layout):
        """Crea la lista scrolleable de amigos"""
        # Título
        label_titulo = QLabel("Mis Amigos")
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
        
        # Frame contenedor de la lista
        frame_lista = QFrame()
        frame_lista.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-radius: 12px;
                padding: 10px;
            }}
        """)
        
        self.layout_lista = QVBoxLayout()
        self.layout_lista.setSpacing(10)
        frame_lista.setLayout(self.layout_lista)
        
        # Agregar amigos a la lista
        self.widgets_amigos = []
        self.actualizar_lista_amigos()
        
        layout.addWidget(frame_lista)
    
    def actualizar_lista_amigos(self):
        """Actualiza la lista de amigos en la UI"""
        # Limpiar lista actual
        for widget in self.widgets_amigos:
            widget.deleteLater()
        self.widgets_amigos.clear()
        
        amigos_ordenados = sorted(
            self.usuario_data['amigos'],
            key=lambda x: f"{x['nombre']} {x['apellido']}"
        )
        
        # Crear widget para cada amigo
        for amigo in amigos_ordenados:
            widget_amigo = WidgetAmigo(
                amigo['nombre'],
                amigo['apellido'],
                amigo['usuario'],
                amigo.get('foto')
            )
            widget_amigo.eliminar_clicked.connect(self.eliminar_amigo)
            self.layout_lista.addWidget(widget_amigo)
            self.widgets_amigos.append(widget_amigo)
        
        # Si no hay amigos
        if not amigos_ordenados:
            label_vacio = QLabel("No tienes amigos aún.\n¡Busca usuarios y agrégalos!")
            label_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_vacio.setStyleSheet(f"""
                QLabel {{
                    color: {COLORES['texto_secundario']};
                    font-size: 14px;
                    padding: 40px;
                    background: transparent;
                }}
            """)
            self.layout_lista.addWidget(label_vacio)
            self.widgets_amigos.append(label_vacio)
    
    def buscar_en_lista(self, texto):
        """Filtra la lista de amigos en tiempo real"""
        texto = texto.lower()
        
        for widget in self.widgets_amigos:
            if isinstance(widget, WidgetAmigo):
                nombre_completo = widget.nombre_completo.lower()
                usuario = widget.usuario.lower()
                
                if texto in nombre_completo or texto in usuario:
                    widget.show()
                else:
                    widget.hide()
    
    def eliminar_amigo(self, usuario):
        """Elimina un amigo de la lista"""
        # Confirmar eliminación
        print(f"Eliminando amigo: {usuario}")
        
        # Remover de la lista
        self.usuario_data['amigos'] = [
            amigo for amigo in self.usuario_data['amigos']
            if amigo['usuario'] != usuario
        ]
        
        # Actualizar UI
        self.actualizar_lista_amigos()
    
    def cargar_foto_perfil(self, ruta):
        """Carga la foto de perfil circular"""
        pixmap = QPixmap(ruta)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            resultado = QPixmap(120, 120)
            resultado.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(resultado)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            path.addEllipse(0, 0, 120, 120)
            painter.setClipPath(path)
            
            x = (120 - pixmap.width()) // 2
            y = (120 - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
            painter.end()
            
            self.label_foto_perfil.setPixmap(resultado)
            self.label_foto_perfil.setStyleSheet(f"""
                QLabel {{
                    border: 4px solid {COLORES['primario']};
                    border-radius: 60px;
                }}
            """)
    
    def cerrar_sesion(self):
        """Cierra sesión y vuelve al login"""
        from cliente.gui_login import VentanaLogin
        self.ventana_login = VentanaLogin()
        self.ventana_login.show()
        self.close()


# ===== PRUEBAS =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    
    ventana = VentanaPerfil()
    ventana.show()
    
    sys.exit(app.exec())