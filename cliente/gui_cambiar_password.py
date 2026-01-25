from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt, QTimer

from cliente.estilos import *


class VentanaCambiarPassword(QDialog):
    """Ventana para cambiar contraseña con verificación por email"""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.codigo_enviado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        self.setWindowTitle("Cambiar Contraseña")
        self.setFixedSize(450, 550)
        self.setStyleSheet(ESTILO_VENTANA)
        self.setModal(True)
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setSpacing(20)
        self.setLayout(layout_principal)
        
        # Título
        label_titulo = QLabel("Cambiar Contraseña")
        label_titulo.setStyleSheet(ESTILO_TITULO)
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(label_titulo)
        
        # Stack para las 2 pantallas
        self.stack = QStackedWidget()
        
        # Pantalla 1: Solicitar código
        self.pantalla_solicitar = self.crear_pantalla_solicitar()
        
        # Pantalla 2: Ingresar código y nueva contraseña
        self.pantalla_codigo = self.crear_pantalla_codigo()
        
        self.stack.addWidget(self.pantalla_solicitar)
        self.stack.addWidget(self.pantalla_codigo)
        
        layout_principal.addWidget(self.stack)
        layout_principal.addStretch()
    
    def crear_pantalla_solicitar(self):
        """Primera pantalla: enviar código por email"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Descripción
        label_desc = QLabel(
            "Te enviaremos un código de verificación a tu correo electrónico."
        )
        label_desc.setStyleSheet(ESTILO_SUBTITULO)
        label_desc.setWordWrap(True)
        label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Email (mostrar, no editable)
        from cliente.datos_local import obtener_email_usuario
        email = obtener_email_usuario(self.usuario_data["usuario"])
        
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME)
        layout_frame = QVBoxLayout()
        layout_frame.setSpacing(10)
        frame.setLayout(layout_frame)
        
        label_email_titulo = QLabel("Correo Electrónico")
        label_email_titulo.setStyleSheet(ESTILO_LABEL)
        
        self.label_email = QLabel(email)
        self.label_email.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 16px;
                font-weight: bold;
                background-color: {COLORES['superficie_clara']};
                border-radius: 10px;
                padding: 14px;
            }}
        """)
        self.label_email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_frame.addWidget(label_email_titulo)
        layout_frame.addWidget(self.label_email)
        
        # Mensaje
        self.label_mensaje_1 = QLabel("")
        self.label_mensaje_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje_1.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje_1.setVisible(False)
        self.label_mensaje_1.setWordWrap(True)
        
        # Botón enviar código
        self.btn_enviar_codigo = QPushButton("Enviar Código")
        self.btn_enviar_codigo.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_enviar_codigo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_enviar_codigo.setMinimumHeight(50)
        self.btn_enviar_codigo.clicked.connect(self.enviar_codigo)
        
        # Botón cancelar
        btn_cancelar_1 = QPushButton("Cancelar")
        btn_cancelar_1.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['texto_secundario']};
                border: none;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: {COLORES['texto']};
            }}
        """)
        btn_cancelar_1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar_1.clicked.connect(self.reject)
        
        layout.addWidget(label_desc)
        layout.addWidget(frame)
        layout.addWidget(self.label_mensaje_1)
        layout.addWidget(self.btn_enviar_codigo)
        layout.addWidget(btn_cancelar_1)
        
        return widget
    
    def crear_pantalla_codigo(self):
        """Segunda pantalla: ingresar código y nueva contraseña"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        # Descripción
        label_desc = QLabel("Ingresa el código que recibiste por email y tu nueva contraseña")
        label_desc.setStyleSheet(ESTILO_SUBTITULO)
        label_desc.setWordWrap(True)
        label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Formulario
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME)
        layout_frame = QVBoxLayout()
        layout_frame.setSpacing(12)
        frame.setLayout(layout_frame)
        
        # Código
        label_codigo = QLabel("Código de Verificación")
        label_codigo.setStyleSheet(ESTILO_LABEL)
        
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ingresa el código de 6 dígitos")
        self.input_codigo.setStyleSheet(ESTILO_INPUT)
        self.input_codigo.setMinimumHeight(45)
        self.input_codigo.setMaxLength(6)
        
        layout_frame.addWidget(label_codigo)
        layout_frame.addWidget(self.input_codigo)
        layout_frame.addSpacing(10)
        
        # Nueva contraseña
        label_nueva = QLabel("Nueva Contraseña")
        label_nueva.setStyleSheet(ESTILO_LABEL)
        
        self.input_nueva = QLineEdit()
        self.input_nueva.setPlaceholderText("Mínimo 6 caracteres")
        self.input_nueva.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nueva.setStyleSheet(ESTILO_INPUT)
        self.input_nueva.setMinimumHeight(45)
        
        layout_frame.addWidget(label_nueva)
        layout_frame.addWidget(self.input_nueva)
        layout_frame.addSpacing(5)
        
        # Confirmar contraseña
        label_confirmar = QLabel("Confirmar Contraseña")
        label_confirmar.setStyleSheet(ESTILO_LABEL)
        
        self.input_confirmar = QLineEdit()
        self.input_confirmar.setPlaceholderText("Repite la contraseña")
        self.input_confirmar.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirmar.setStyleSheet(ESTILO_INPUT)
        self.input_confirmar.setMinimumHeight(45)
        
        layout_frame.addWidget(label_confirmar)
        layout_frame.addWidget(self.input_confirmar)
        
        # Mensaje
        self.label_mensaje_2 = QLabel("")
        self.label_mensaje_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje_2.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje_2.setVisible(False)
        self.label_mensaje_2.setWordWrap(True)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        btn_volver = QPushButton("← Volver")
        btn_volver.setStyleSheet(f"""
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
        btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_volver.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        self.btn_cambiar = QPushButton("Cambiar Contraseña")
        self.btn_cambiar.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_cambiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cambiar.clicked.connect(self.cambiar_password)
        
        layout_botones.addWidget(btn_volver)
        layout_botones.addWidget(self.btn_cambiar)
        
        layout.addWidget(label_desc)
        layout.addWidget(frame)
        layout.addWidget(self.label_mensaje_2)
        layout.addLayout(layout_botones)
        
        return widget
    
    def enviar_codigo(self):
        """Envía el código por email"""
        from cliente.datos_local import obtener_email_usuario
        from cliente.email_service import enviar_codigo_recuperacion
        
        email = obtener_email_usuario(self.usuario_data["usuario"])
        
        self.btn_enviar_codigo.setEnabled(False)
        self.mostrar_mensaje(1, "Enviando código...", "exito")
        
        # Enviar código
        exito, mensaje, codigo = enviar_codigo_recuperacion(
            email,
            self.usuario_data["usuario"]
        )
        
        if exito:
            self.codigo_enviado = codigo
            self.mostrar_mensaje(1, mensaje, "exito")
            QTimer.singleShot(1500, lambda: self.stack.setCurrentIndex(1))
        else:
            self.btn_enviar_codigo.setEnabled(True)
            self.mostrar_mensaje(1, mensaje, "error")
    
    def cambiar_password(self):
        """Cambia la contraseña si el código es válido"""
        codigo = self.input_codigo.text().strip()
        nueva = self.input_nueva.text()
        confirmar = self.input_confirmar.text()
        
        # Validar
        if not codigo or not nueva or not confirmar:
            self.mostrar_mensaje(2, "Completa todos los campos", "error")
            return
        
        if len(codigo) != 6:
            self.mostrar_mensaje(2, "El código debe tener 6 dígitos", "error")
            return
        
        if len(nueva) < 6:
            self.mostrar_mensaje(2, "La contraseña debe tener al menos 6 caracteres", "error")
            return
        
        if nueva != confirmar:
            self.mostrar_mensaje(2, "Las contraseñas no coinciden", "error")
            return
        
        # Verificar código
        from cliente.datos_local import obtener_email_usuario, cambiar_password
        from cliente.email_service import verificar_codigo
        
        email = obtener_email_usuario(self.usuario_data["usuario"])
        
        self.btn_cambiar.setEnabled(False)
        
        valido, mensaje_verificacion = verificar_codigo(email, codigo)
        
        if not valido:
            self.btn_cambiar.setEnabled(True)
            self.mostrar_mensaje(2, mensaje_verificacion, "error")
            return
        
        # Cambiar contraseña
        exito, mensaje = cambiar_password(self.usuario_data["usuario"], nueva)
        
        if exito:
            self.mostrar_mensaje(2, "Contraseña cambiada exitosamente", "exito")
            QTimer.singleShot(1500, self.accept)
        else:
            self.btn_cambiar.setEnabled(True)
            self.mostrar_mensaje(2, mensaje, "error")
    
    def mostrar_mensaje(self, pantalla, texto, tipo="error"):
        """Muestra mensaje en la pantalla indicada"""
        label = self.label_mensaje_1 if pantalla == 1 else self.label_mensaje_2
        
        label.setText(texto)
        
        if tipo == "error":
            label.setStyleSheet(ESTILO_ERROR)
        else:
            label.setStyleSheet(ESTILO_EXITO)
        
        label.setVisible(True)

