from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QTextEdit, QStatusBar, QApplication,
    QTabWidget, QScrollArea, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap
import sys
import threading
import time
from pathlib import Path

from cliente.estilos import *
from servidor.servidor_tcp import ServidorTCP
from grafo.grafo import Grafo
from grafo.visualizacion import visualizar_grafo
from grafo.algoritmos import encontrar_camino_bfs, calcular_estadisticas


class ServidorThread(QThread):
    log_signal = pyqtSignal(str)
    
    def __init__(self, servidor: ServidorTCP):
        super().__init__()
        self.servidor = servidor
        # Conectar el callback del servidor a la señal
        self.servidor.on_log = lambda msg: self.log_signal.emit(msg)
    
    def run(self):
        self.servidor.iniciar()


class VentanaServidor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.puerto = 5000
        self.servidor_activo = False
        self.servidor_tcp: ServidorTCP = None
        self.servidor_thread: ServidorThread = None
        self.grafo = Grafo()
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz del servidor"""
        self.setWindowTitle("Servidor SocialTec")
        self.resize(1100, 800)
        self.setMinimumSize(1000, 700)
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
        
        # Botón actualizar visualización
        self.boton_actualizar_grafo = QPushButton("Actualizar Visualización")
        self.boton_actualizar_grafo.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.boton_actualizar_grafo.clicked.connect(self.actualizar_visualizacion_grafo)
        self.boton_actualizar_grafo.setEnabled(False)
        layout_controles.addWidget(self.boton_actualizar_grafo)
        
        layout_principal.addLayout(layout_controles)
        
        # Crear TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget {{
                background-color: {COLORES['fondo']};
            }}
            QTabBar::tab {{
                background-color: {COLORES['superficie']};
                color: {COLORES['texto']};
                padding: 10px 20px;
                border-bottom: 2px solid {COLORES['borde']};
            }}
            QTabBar::tab:selected {{
                background-color: {COLORES['primario']};
                color: white;
                border-bottom: 2px solid {COLORES['primario']};
            }}
        """)
        layout_principal.addWidget(self.tab_widget)
        
        # Pestaña de Logs
        self.area_logs = QTextEdit()
        self.area_logs.setReadOnly(True)
        self.area_logs.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Courier New';
            }}
        """)
        self.area_logs.setText("Servidor apagado - Presiona 'Prender Server' para iniciar\n")
        self.tab_widget.addTab(self.area_logs, "Logs")
        
        # Pestaña de Visualización del Grafo
        self.scroll_grafo = QScrollArea()
        self.scroll_grafo.setWidgetResizable(True)
        self.scroll_grafo.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORES['fondo']};
                border: none;
            }}
        """)
        
        self.label_imagen_grafo = QLabel()
        self.label_imagen_grafo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagen_grafo.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORES['fondo']};
                padding: 20px;
            }}
        """)
        self.label_imagen_grafo.setText("Grafo vacío - No hay usuarios registrados aún")
        self.scroll_grafo.setWidget(self.label_imagen_grafo)
        self.tab_widget.addTab(self.scroll_grafo, "Visualización Grafo")
        
        # Pestaña de búsqueda de caminos
        self._crear_tab_buscar_camino()
        
        # Pestaña de estadísticas
        self._crear_tab_estadisticas()
        
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
        
        # Timer para actualizar visualización cada 5 segundos
        self.timer_actualizacion = QTimer()
        self.timer_actualizacion.timeout.connect(self.actualizar_visualizacion_grafo_auto)
        self.timer_actualizacion.setInterval(5000)  # 5 segundos
    
    def prender_servidor(self):
        """Enciende el servidor TCP"""
        if self.servidor_activo:
            self.log("Servidor ya está activo")
            return
        
        try:
            self.servidor_tcp = ServidorTCP(
                grafo=self.grafo,
                host="localhost",
                port=self.puerto,
                on_log=lambda msg: None  # Se reemplaza en el thread
            )
            
            self.servidor_thread = ServidorThread(self.servidor_tcp)
            self.servidor_thread.log_signal.connect(self.log)
            self.servidor_thread.start()
            
            self.servidor_activo = True
            self.boton_prender.setEnabled(False)
            self.boton_apagar.setEnabled(True)
            self.boton_actualizar_grafo.setEnabled(True)
            self.estado_label.setText(f"Estado: Servidor activo (puerto {self.puerto})")
            self.timer_actualizacion.start()
            self.log(f"✓ Servidor iniciado en puerto {self.puerto}")
        except Exception as e:
            self.log(f"✗ Error al iniciar servidor: {e}")
    
    def apagar_servidor(self):
        """Apaga el servidor TCP"""
        if not self.servidor_activo:
            return
        
        try:
            if self.servidor_tcp:
                self.servidor_tcp.detener()
            
            self.timer_actualizacion.stop()
            self.servidor_activo = False
            self.boton_prender.setEnabled(True)
            self.boton_apagar.setEnabled(False)
            self.boton_actualizar_grafo.setEnabled(False)
            self.estado_label.setText("Estado: Servidor apagado")
            self.log("✓ Servidor detenido")
        except Exception as e:
            self.log(f"✗ Error al detener servidor: {e}")
    
    def actualizar_visualizacion_grafo(self):
        """Actualiza la visualización del grafo manualmente"""
        self.actualizar_visualizacion_grafo_auto()
    
    def actualizar_visualizacion_grafo_auto(self):
        """Genera y actualiza la visualización del grafo"""
        try:
            # Cargar usuarios desde persistencia
            from servidor.persistencia import cargar_usuarios
            usuarios = cargar_usuarios()
            
            if not usuarios:
                self.label_imagen_grafo.setText("Grafo vacío - No hay usuarios registrados aún")
                return
            
            # Limpiar el grafo
            self.grafo._adj.clear()
            self.grafo._users.clear()
            
            # Agregar usuarios (nodos)
            for username, datos in usuarios.items():
                self.grafo.agregar_usuario(
                    username,
                    nombre=datos.get("nombre", ""),
                    apellido=datos.get("apellido", ""),
                    foto=datos.get("foto", "")
                )
            
            # Agregar amistades (aristas)
            for usuario, datos in usuarios.items():
                amigos = datos.get("amigos", [])
                for amigo in amigos:
                    if amigo in usuarios and self.grafo.existe_usuario(amigo):
                        try:
                            self.grafo.agregar_amistad(usuario, amigo)
                        except:
                            pass  # Evitar errores si ya existe la amistad
            
            # Generar visualización
            ruta_temp = Path("datos/grafo_temp.png")
            ruta_temp.parent.mkdir(parents=True, exist_ok=True)
            
            visualizar_grafo(
                self.grafo,
                ruta_salida=str(ruta_temp),
                titulo=f"Red Social SocialTec ({len(usuarios)} usuarios)",
                mostrar_etiquetas=True
            )
            
            # Mostrar la imagen
            if ruta_temp.exists():
                pixmap = QPixmap(str(ruta_temp))
                # Escalar a un tamaño razonable
                pixmap = pixmap.scaledToWidth(900, Qt.TransformationMode.SmoothTransformation)
                self.label_imagen_grafo.setPixmap(pixmap)
                self.log(f"✓ Visualización actualizada ({len(usuarios)} usuarios)")
            
        except Exception as e:
            self.label_imagen_grafo.setText(f"Error al generar visualización: {str(e)}")
            self.log(f"✗ Error al actualizar grafo: {e}")
    
    def log(self, mensaje: str):
        """Agrega mensaje al área de logs"""
        texto_actual = self.area_logs.toPlainText()
        self.area_logs.setText(texto_actual + mensaje + "\n")
        
        # Scroll al final
        scrollbar = self.area_logs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _crear_tab_buscar_camino(self):
        """Crea la pestaña para buscar caminos de amistad"""
        widget_camino = QWidget()
        layout_camino = QVBoxLayout()
        layout_camino.setContentsMargins(20, 20, 20, 20)
        layout_camino.setSpacing(15)
        
        # Título
        titulo_camino = QLabel("Buscar Camino de Amistad")
        titulo_camino.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORES['texto']};
        """)
        layout_camino.addWidget(titulo_camino)
        
        # Descripción
        desc = QLabel("Busca si existe un path de amistad entre dos usuarios")
        desc.setStyleSheet(f"color: {COLORES['texto_secundario']}; font-size: 12px;")
        layout_camino.addWidget(desc)
        
        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORES['borde']};")
        layout_camino.addWidget(sep)
        
        # Layout de entrada
        layout_entrada = QHBoxLayout()
        layout_entrada.setSpacing(10)
        
        # Usuario inicial
        layout_entrada.addWidget(QLabel("Desde:"))
        self.input_usuario_inicio = QLineEdit()
        self.input_usuario_inicio.setPlaceholderText("Ej: alice")
        self.input_usuario_inicio.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORES['primario']};
            }}
        """)
        layout_entrada.addWidget(self.input_usuario_inicio)
        
        # Usuario final
        layout_entrada.addWidget(QLabel("Hasta:"))
        self.input_usuario_fin = QLineEdit()
        self.input_usuario_fin.setPlaceholderText("Ej: david")
        self.input_usuario_fin.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORES['primario']};
            }}
        """)
        layout_entrada.addWidget(self.input_usuario_fin)
        
        # Botón buscar
        self.boton_buscar_camino = QPushButton("Buscar")
        self.boton_buscar_camino.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.boton_buscar_camino.clicked.connect(self.buscar_camino)
        self.boton_buscar_camino.setFixedWidth(100)
        layout_entrada.addWidget(self.boton_buscar_camino)
        
        layout_entrada.addStretch()
        layout_camino.addLayout(layout_entrada)
        
        # Área de resultado
        self.area_resultado_camino = QTextEdit()
        self.area_resultado_camino.setReadOnly(True)
        self.area_resultado_camino.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
                font-family: 'Courier New';
                line-height: 1.6;
            }}
        """)
        self.area_resultado_camino.setText("Ingresa dos usuarios y presiona 'Buscar' para encontrar si existe un camino de amistad entre ellos.")
        layout_camino.addWidget(self.area_resultado_camino)
        
        widget_camino.setLayout(layout_camino)
        self.tab_widget.addTab(widget_camino, "Buscar Camino")
    
    def buscar_camino(self):
        """Busca un camino entre dos usuarios"""
        inicio = self.input_usuario_inicio.text().strip()
        fin = self.input_usuario_fin.text().strip()
        
        if not inicio or not fin:
            self.area_resultado_camino.setText("ERROR: Debes ingresar ambos usuarios")
            return
        
        if inicio == fin:
            self.area_resultado_camino.setText(f"ADVERTENCIA: Los usuarios son los mismos ({inicio})")
            return
        
        try:
            # Buscar camino
            camino = encontrar_camino_bfs(self.grafo, inicio, fin)
            
            if camino:
                # Camino encontrado
                saltos = len(camino) - 1
                resultado = f"""CAMINO ENCONTRADO

Desde: {inicio}
Hasta: {fin}
Saltos: {saltos}
Camino: {' → '.join(camino)}

Detalle del camino:
"""
                for i, usuario in enumerate(camino, 1):
                    if i == 1:
                        resultado += f"\n  {i}. {usuario} (inicio)"
                    elif i == len(camino):
                        resultado += f"\n  {i}. {usuario} (fin)"
                    else:
                        resultado += f"\n  {i}. {usuario} (amigo intermedio)"
                
                self.area_resultado_camino.setText(resultado)
                self.log(f"Camino encontrado: {inicio} -> {fin} ({saltos} saltos)")
            else:
                # No existe camino
                resultado = f"""NO EXISTE CAMINO

Desde: {inicio}
Hasta: {fin}

No se encontró un camino de amistad entre estos usuarios.
Esto significa que no están conectados a través de amigos comunes.
"""
                self.area_resultado_camino.setText(resultado)
                self.log(f"No existe camino entre {inicio} y {fin}")
        
        except Exception as e:
            self.area_resultado_camino.setText(f"ERROR: {str(e)}")
            self.log(f"Error al buscar camino: {str(e)}")
    
    def _crear_tab_estadisticas(self):
        """Crea la pestaña para mostrar estadísticas del grafo"""
        widget_stats = QWidget()
        layout_stats = QVBoxLayout()
        layout_stats.setContentsMargins(20, 20, 20, 20)
        layout_stats.setSpacing(15)
        
        # Título
        titulo_stats = QLabel("Estadísticas del Grafo")
        titulo_stats.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORES['texto']};
        """)
        layout_stats.addWidget(titulo_stats)
        
        # Descripción
        desc = QLabel("Estadísticas globales de la red social")
        desc.setStyleSheet(f"color: {COLORES['texto_secundario']}; font-size: 12px;")
        layout_stats.addWidget(desc)
        
        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORES['borde']};")
        layout_stats.addWidget(sep)
        
        # Botón actualizar estadísticas
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(10)
        
        self.boton_actualizar_stats = QPushButton("Actualizar Estadísticas")
        self.boton_actualizar_stats.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.boton_actualizar_stats.clicked.connect(self.actualizar_estadisticas)
        layout_botones.addWidget(self.boton_actualizar_stats)
        
        layout_botones.addStretch()
        layout_stats.addLayout(layout_botones)
        
        # Área de estadísticas
        self.area_estadisticas = QTextEdit()
        self.area_estadisticas.setReadOnly(True)
        self.area_estadisticas.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
                font-family: 'Courier New';
                line-height: 1.8;
            }}
        """)
        self.area_estadisticas.setText("Presiona 'Actualizar Estadísticas' para calcular las métricas del grafo.")
        layout_stats.addWidget(self.area_estadisticas)
        
        widget_stats.setLayout(layout_stats)
        self.tab_widget.addTab(widget_stats, "Estadísticas")
    
    def actualizar_estadisticas(self):
        """Calcula y muestra las estadísticas del grafo"""
        try:
            stats = calcular_estadisticas(self.grafo)
            
            resultado = f"""
ESTADÍSTICAS DEL GRAFO
{'='*50}

USUARIOS:
  Total de usuarios: {stats.cantidad_usuarios}
  Total de amistades: {stats.cantidad_amistades}

USUARIO CON MÁS AMIGOS:
  Usuario: {stats.usuario_con_mas_amigos if stats.usuario_con_mas_amigos else 'N/A'}
  Cantidad de amigos: {stats.max_amigos}

USUARIO CON MENOS AMIGOS:
  Usuario: {stats.usuario_con_menos_amigos if stats.usuario_con_menos_amigos else 'N/A'}
  Cantidad de amigos: {stats.min_amigos}

PROMEDIO:
  Promedio de amigos por usuario: {stats.promedio_amigos:.2f}

{'='*50}
"""
            self.area_estadisticas.setText(resultado)
            self.log(f"Estadísticas actualizadas: {stats.cantidad_usuarios} usuarios, promedio {stats.promedio_amigos:.2f} amigos")
        
        except Exception as e:
            self.area_estadisticas.setText(f"ERROR: {str(e)}")
            self.log(f"Error al calcular estadísticas: {str(e)}")


def main():
    app = QApplication(sys.argv)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    ventana = VentanaServidor()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
