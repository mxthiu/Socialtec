from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

# Importar estilos y pantallas
from cliente.estilos import *
from cliente.gui_perfil_contenido import ContenidoPerfil
from cliente.gui_busqueda import ContenidoBusqueda
from cliente.gui_amigos import ContenidoAmigos
from cliente.gui_grafo import ContenidoGrafo
from cliente.gui_configuracion import ContenidoConfiguracion


class BotonNavegacion(QPushButton):
    """Botón personalizado para la barra de navegación"""
    
    def __init__(self, icono, texto):
        super().__init__()
        self.icono = icono
        self.texto_label = texto
        self.activo = False
        self.setText(texto)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.actualizar_estilo()
    
    def actualizar_estilo(self):
        """Actualiza el estilo según si está activo o no"""
        if self.activo:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORES['primario']};
                    border: none;
                    padding: 10px;
                    font-size: 15px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORES['texto_secundario']};
                    border: none;
                    padding: 10px;
                    font-size: 15px;
                }}
                QPushButton:hover {{
                    color: {COLORES['texto']};
                }}
            """)
    
    def set_activo(self, activo):
        """Marca el botón como activo o inactivo"""
        self.activo = activo
        self.actualizar_estilo()


class VentanaMainMenu(QMainWindow):
    def __init__(self, usuario_data=None):
        super().__init__()
        # Datos del usuario (pasados desde login)
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
        
        self.botones_nav = []
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz principal"""
        self.setWindowTitle("SocialTec")
        self.setFixedSize(500, 750)
        self.setStyleSheet(ESTILO_VENTANA)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        widget_central.setLayout(layout_principal)
        
        
        self.stack_pantallas = QStackedWidget()
        

        self.pantalla_perfil = ContenidoPerfil(self.usuario_data, self)
        self.pantalla_busqueda = ContenidoBusqueda(self.usuario_data, self)
        self.pantalla_amigos = ContenidoAmigos(self.usuario_data, self)
        self.pantalla_grafo = ContenidoGrafo(self.usuario_data, self)
        self.pantalla_config = ContenidoConfiguracion(self.usuario_data, self)
        
        # Agregar pantallas al stack
        self.stack_pantallas.addWidget(self.pantalla_perfil)      # índice 0
        self.stack_pantallas.addWidget(self.pantalla_busqueda)    # índice 1
        self.stack_pantallas.addWidget(self.pantalla_amigos)      # índice 2
        self.stack_pantallas.addWidget(self.pantalla_grafo)       # índice 3
        self.stack_pantallas.addWidget(self.pantalla_config)      # índice 4
        
        layout_principal.addWidget(self.stack_pantallas)
        
        
        self.crear_barra_navegacion(layout_principal)
        
        # Iniciar en perfil
        self.cambiar_pantalla(0)
    
    def crear_barra_navegacion(self, layout):
        """Crea la barra de navegación inferior"""
        barra = QFrame()
        barra.setFixedHeight(70)
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                border-top: 1px solid {COLORES['borde']};
            }}
        """)
        
        layout_barra = QHBoxLayout()
        layout_barra.setContentsMargins(0, 0, 0, 0)
        layout_barra.setSpacing(0)
        barra.setLayout(layout_barra)
        
        # Botones de navegación
        botones_info = [
            ("", "Perfil", 0),
            ("", "Buscar", 1),
            ("", "Amigos", 2),
            ("", "Grafo", 3),
            ("", "Config", 4),
        ]
        
        for icono, texto, indice in botones_info:
            boton = BotonNavegacion(icono, texto)
            boton.clicked.connect(lambda checked, idx=indice: self.cambiar_pantalla(idx))
            layout_barra.addWidget(boton)
            self.botones_nav.append(boton)
        
        layout.addWidget(barra)
    
    def cambiar_pantalla(self, indice):
        """Cambia la pantalla mostrada y actualiza botones"""
        self.stack_pantallas.setCurrentIndex(indice)
        
        # Actualizar estado de botones
        for i, boton in enumerate(self.botones_nav):
            boton.set_activo(i == indice)
    
    def actualizar_datos_usuario(self):
        """Actualiza los datos en todas las pantallas cuando cambian"""
        try:
            from cliente.datos_local import obtener_usuario_completo

            datos_actualizados = obtener_usuario_completo(self.usuario_data.get("usuario"))
            if datos_actualizados:
                self.usuario_data.update(datos_actualizados)
        except Exception:
            pass

        self.pantalla_perfil.actualizar_datos()
        self.pantalla_amigos.actualizar_datos()
        self.pantalla_grafo.actualizar_datos()
    
    def cerrar_sesion(self):
        """Cierra sesión y vuelve al login"""
        from cliente.gui_login import VentanaLogin
        self.ventana_login = VentanaLogin()
        self.ventana_login.show()
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    
    ventana = VentanaMainMenu()
    ventana.show()
    
    sys.exit(app.exec())

