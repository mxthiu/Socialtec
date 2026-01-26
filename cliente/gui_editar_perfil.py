from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QFileDialog,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

from cliente.estilos import *


class ContenidoEditarPerfil(QWidget):
    """Pantalla para editar el perfil"""
    perfil_actualizado = pyqtSignal(dict)
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.usuario_data = usuario_data
        self.foto_nueva = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie']};
                padding: 20px;
                border-bottom: 1px solid {COLORES['borde']};
            }}
        """)
        layout_header = QVBoxLayout()
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.setSpacing(10)
        header.setLayout(layout_header)
        
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
        
        titulo = QLabel("Editar Perfil")
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        
        layout_header.addWidget(btn_volver)
        layout_header.addWidget(titulo)
        
        layout_principal.addWidget(header)
        
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {COLORES['fondo']};
            }}
            QScrollBar:vertical {{
                background: {COLORES['superficie_clara']};
                width: 10px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORES['primario']};
                border-radius: 5px;
            }}
        """)
        
        contenido = QWidget()
        layout_scroll = QVBoxLayout()
        layout_scroll.setContentsMargins(30, 30, 30, 30)
        layout_scroll.setSpacing(25)
        contenido.setLayout(layout_scroll)
        scroll.setWidget(contenido)
        
        layout_principal.addWidget(scroll)
        
        
        self.crear_selector_foto(layout_scroll)
        
        
        self.crear_formulario(layout_scroll)
        
        
        self.label_mensaje = QLabel("")
        self.label_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje.setVisible(False)
        self.label_mensaje.setWordWrap(True)
        self.label_mensaje.setMinimumHeight(40)
        layout_scroll.addWidget(self.label_mensaje)
        
        
        layout_scroll.addStretch()
        
        
        self.crear_botones(layout_principal)
    
    def crear_selector_foto(self, layout):
        """Selector de foto"""
        layout_foto = QVBoxLayout()
        layout_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Foto actual
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
                    border: 4px solid {COLORES['primario']};
                    border-radius: 70px;
                    color: white;
                    font-size: 56px;
                    font-weight: bold;
                }}
            """)
            self.label_foto.setText(inicial)
        
        # Botón cambiar foto
        btn_cambiar = QPushButton("Cambiar foto")
        btn_cambiar.setStyleSheet(ESTILO_BOTON_TEXTO)
        btn_cambiar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cambiar.setMinimumHeight(40)
        btn_cambiar.clicked.connect(self.seleccionar_foto)
        
        layout_foto.addWidget(self.label_foto)
        layout_foto.addSpacing(10)
        layout_foto.addWidget(btn_cambiar)
        layout.addLayout(layout_foto)
        layout.addSpacing(10)
    
    def crear_formulario(self, layout):
        """Formulario con campos editables"""
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME)
        layout_form = QVBoxLayout()
        layout_form.setSpacing(20)
        frame.setLayout(layout_form)
        
        
        label_nombre = QLabel("Nombre")
        label_nombre.setStyleSheet(ESTILO_LABEL)
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setText(self.usuario_data["nombre"])
        self.input_nombre.setStyleSheet(ESTILO_INPUT)
        self.input_nombre.setMinimumHeight(45)
        self.input_nombre.setPlaceholderText("Tu nombre")
        
        layout_form.addWidget(label_nombre)
        layout_form.addWidget(self.input_nombre)
        
        
        label_apellido = QLabel("Apellido")
        label_apellido.setStyleSheet(ESTILO_LABEL)
        
        self.input_apellido = QLineEdit()
        self.input_apellido.setText(self.usuario_data["apellido"])
        self.input_apellido.setStyleSheet(ESTILO_INPUT)
        self.input_apellido.setMinimumHeight(45)
        self.input_apellido.setPlaceholderText("Tu apellido")
        
        layout_form.addWidget(label_apellido)
        layout_form.addWidget(self.input_apellido)
        
        
        label_email = QLabel("Correo Electrónico")
        label_email.setStyleSheet(ESTILO_LABEL)
        
        self.input_email = QLineEdit()
        self.input_email.setText(self.usuario_data.get("email", ""))
        self.input_email.setStyleSheet(ESTILO_INPUT)
        self.input_email.setMinimumHeight(45)
        self.input_email.setPlaceholderText("tu_email@gmail.com")
        
        layout_form.addWidget(label_email)
        layout_form.addWidget(self.input_email)
        
        
        label_usuario_titulo = QLabel("Nombre de Usuario")
        label_usuario_titulo.setStyleSheet(ESTILO_LABEL)
        
        label_usuario = QLabel(f"@{self.usuario_data['usuario']}")
        label_usuario.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 15px;
                background-color: {COLORES['superficie_clara']};
                border-radius: 10px;
                padding: 13px 15px;
                font-weight: 500;
            }}
        """)
        
        layout_form.addWidget(label_usuario_titulo)
        layout_form.addWidget(label_usuario)
        
        layout.addWidget(frame)
    
    def crear_botones(self, layout):
        """Botones de acción en la parte inferior"""
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['superficie_clara']};
                border-top: 1px solid {COLORES['borde']};
                padding: 15px 30px;
            }}
        """)
        layout_botones = QHBoxLayout()
        layout_botones.setContentsMargins(0, 0, 0, 0)
        layout_botones.setSpacing(15)
        footer.setLayout(layout_botones)
        
        # Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['texto_secundario']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['superficie_clara']};
            }}
        """)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setMinimumHeight(50)
        btn_cancelar.clicked.connect(self.cancelar_con_confirmacion)
        
        # Guardar
        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setMinimumHeight(50)
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(self.btn_guardar)
        
        layout.addWidget(footer)
    
    def seleccionar_foto(self):
        """Selecciona nueva foto"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar foto de perfil",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if archivo:
            self.foto_nueva = archivo
            self.cargar_foto_circular(archivo)
    
    def cargar_foto_circular(self, ruta):
        """Carga foto en formato circular"""
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
            
            self.label_foto.setPixmap(resultado)
            self.label_foto.setStyleSheet(f"""
                QLabel {{
                    border: 3px solid {COLORES['primario']};
                    border-radius: 60px;
                }}
            """)
    
    def guardar_cambios(self):
        """Guarda los cambios del perfil"""
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        email = self.input_email.text().strip()
        
        # Validar
        if not nombre or not apellido or not email:
            self.mostrar_mensaje("Completa todos los campos", "error")
            return
        
        if len(nombre) < 2 or len(apellido) < 2:
            self.mostrar_mensaje("Nombre y apellido deben tener al menos 2 caracteres", "error")
            return
        
        # Validar formato de email
        if "@" not in email or "." not in email:
            self.mostrar_mensaje("Por favor ingresa un email válido", "error")
            return
        
        # Actualizar en datos locales
        from cliente.datos_local import actualizar_perfil
        
        self.btn_guardar.setEnabled(False)
        self.mostrar_mensaje("Guardando cambios...", "exito")
        
        foto = self.foto_nueva if self.foto_nueva else self.usuario_data.get("foto")
        exito, mensaje, datos_nuevos = actualizar_perfil(
            self.usuario_data["usuario"],
            nombre,
            apellido,
            email,
            foto
        )
        
        if exito:
            # Emitir señal con datos actualizados
            self.perfil_actualizado.emit(datos_nuevos)
            QTimer.singleShot(1000, self.volver_atras)
        else:
            self.btn_guardar.setEnabled(True)
            self.mostrar_mensaje(mensaje, "error")
    
    def cancelar_con_confirmacion(self):
        """Cancela con confirmación si hay cambios"""
        from cliente.dialogos import confirmar_cancelar_edicion
        
        nombre_actual = self.input_nombre.text().strip()
        apellido_actual = self.input_apellido.text().strip()
        email_actual = self.input_email.text().strip()
        
        hay_cambios = (
            nombre_actual != self.usuario_data.get("nombre", "") or
            apellido_actual != self.usuario_data.get("apellido", "") or
            email_actual != self.usuario_data.get("email", "") or
            self.foto_nueva is not None
        )
        
        if hay_cambios:
            if not confirmar_cancelar_edicion(self):
                return
        
        self.volver_atras()
    
    def volver_atras(self):
        """Vuelve a la pantalla anterior"""
        if self.parent_window:
            self.parent_window.volver_atras()
    
    def mostrar_mensaje(self, texto, tipo="error"):
        """Muestra mensaje"""
        self.label_mensaje.setText(texto)
        
        if tipo == "error":
            self.label_mensaje.setStyleSheet(ESTILO_ERROR)
        else:
            self.label_mensaje.setStyleSheet(ESTILO_EXITO)
        
        self.label_mensaje.setVisible(True)

