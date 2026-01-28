from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QTextEdit, QStatusBar, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

from cliente.estilos import *


class VentanaServidor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.puerto = 5000
        self.servidor_activo = False
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz del servidor"""
        self.setWindowTitle("Servidor SocialTec")
        self.resize(900, 700)
        self.setMinimumSize(800, 600)
        self.setStyleSheet(ESTILO_VENTANA)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)
        widget_central.setLayout(layout_principal)
        
        # Título
        titulo = QLabel("Servidor SocialTec")
        titulo.setStyleSheet(ESTILO_TITULO)
        layout_principal.addWidget(titulo)
        
        # Subtítulo con información del puerto
        subtitulo = QLabel(f"Escuchando en puerto {self.puerto} (TCP)")
        subtitulo.setStyleSheet(ESTILO_SUBTITULO)
        layout_principal.addWidget(subtitulo)
        
        # Separador
        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet(f"background-color: {COLORES['borde']};")
        layout_principal.addWidget(separador)
        
        # Panel de controles
        layout_controles = QHBoxLayout()
        layout_controles.setSpacing(10)
        
        # Botón prender servidor
        self.boton_prender = QPushButton("Prender Server")
        self.boton_prender.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.boton_prender.clicked.connect(self.prender_servidor)
        layout_controles.addWidget(self.boton_prender)
        
        # Botón apagar servidor
        self.boton_apagar = QPushButton("Apagar Server")
        self.boton_apagar.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.boton_apagar.clicked.connect(self.apagar_servidor)
        self.boton_apagar.setEnabled(False)
        layout_controles.addWidget(self.boton_apagar)
        
        # Botón cargar grafo
        self.boton_cargar_grafo = QPushButton("Cargar Grafo")
        self.boton_cargar_grafo.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.boton_cargar_grafo.clicked.connect(self.cargar_grafo)
        self.boton_cargar_grafo.setEnabled(False)
        layout_controles.addWidget(self.boton_cargar_grafo)
        
        layout_principal.addLayout(layout_controles)
        
        # Área del grafo
        label_grafo = QLabel("Visualización del Grafo")
        label_grafo.setStyleSheet(ESTILO_LABEL)
        label_grafo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout_principal.addWidget(label_grafo)
        
        frame_grafo = QFrame()
        frame_grafo.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie_clara']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
            }}
        """)
        frame_grafo.setMinimumHeight(400)
        layout_frame_grafo = QVBoxLayout()
        layout_frame_grafo.setContentsMargins(0, 0, 0, 0)
        frame_grafo.setLayout(layout_frame_grafo)
        
        # Área de visualización del grafo (placeholder)
        self.area_grafo = QTextEdit()
        self.area_grafo.setReadOnly(True)
        self.area_grafo.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Courier New';
            }}
            QTextEdit:focus {{
                border: 2px solid {COLORES['primario']};
            }}
        """)
        self.area_grafo.setText("Grafo vacío - Presiona 'Cargar Grafo' para visualizar\n")
        layout_frame_grafo.addWidget(self.area_grafo)
        
        layout_principal.addWidget(frame_grafo)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORES['superficie']};
                color: {COLORES['texto']};
                border-top: 1px solid {COLORES['borde']};
            }}
        """)
        self.estado_label = QLabel("Estado: Servidor apagado")
        self.estado_label.setStyleSheet(ESTILO_LABEL)
        self.status_bar.addWidget(self.estado_label)
    
    def prender_servidor(self):
        """Enciende el servidor"""
        # Aquí se implementará la lógica del servidor TCP
        pass
    
    def apagar_servidor(self):
        """Apaga el servidor"""
        # Aquí se implementará la lógica para apagar el servidor TCP
        pass
    
    def cargar_grafo(self):
        """Carga y visualiza el grafo"""
        # Aquí se implementará la lógica para cargar y visualizar el grafo
        pass


def main():
    app = QApplication(sys.argv)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    ventana = VentanaServidor()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()