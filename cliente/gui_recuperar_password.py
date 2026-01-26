from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QComboBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from cliente.estilos import *


class VentanaRecuperarPassword(QDialog):
    """Ventana para recuperar/cambiar contraseña sin autenticación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.codigo_enviado = None
        self.usuario_seleccionado = None
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz"""
        self.setWindowTitle("Recuperar Contraseña")
        self.resize(440, 700)
        self.setMinimumSize(400, 620)
        self.setStyleSheet(ESTILO_VENTANA)
        self.setModal(True)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        self.setLayout(layout_principal)
        
        
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORES['primario']};
                padding: 20px;
                border-radius: 0;
            }}
        """)
        layout_header = QVBoxLayout()
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.setSpacing(5)
        header.setLayout(layout_header)
        
        titulo = QLabel("Recuperar Contraseña")
        titulo.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        layout_scroll.setSpacing(20)
        contenido.setLayout(layout_scroll)
        scroll.setWidget(contenido)
        
        layout_principal.addWidget(scroll)
        
        
        self.pantalla_usuario = self.crear_pantalla_usuario()
        
        
        self.pantalla_codigo = self.crear_pantalla_codigo()
        
        # Agregar pantallas al scroll
        layout_scroll.addWidget(self.pantalla_usuario)
        layout_scroll.addWidget(self.pantalla_codigo)
        self.pantalla_codigo.setVisible(False)
        
        layout_scroll.addStretch()
        
        
        self.crear_botones(layout_principal)
    
    def crear_pantalla_usuario(self):
        """Primera pantalla: seleccionar usuario y enviar código"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        frame.setLayout(layout)
        
        # Descripción
        label_desc = QLabel("Selecciona tu usuario para recuperar tu contraseña")
        label_desc.setStyleSheet(ESTILO_SUBTITULO)
        label_desc.setWordWrap(True)
        label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Combo box con usuarios
        label_usuario = QLabel("Selecciona tu usuario")
        label_usuario.setStyleSheet(ESTILO_LABEL)
        
        self.combo_usuarios = QComboBox()
        self.combo_usuarios.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORES['primario']};
            }}
        """)
        self.combo_usuarios.setMinimumHeight(45)
        
        # Cargar usuarios disponibles
        self.cargar_usuarios()
        
        # Mensaje
        self.label_mensaje_1 = QLabel("")
        self.label_mensaje_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje_1.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje_1.setVisible(False)
        self.label_mensaje_1.setWordWrap(True)
        
        # Botón enviar código
        self.btn_enviar = QPushButton("Enviar Código")
        self.btn_enviar.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_enviar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_enviar.setMinimumHeight(50)
        self.btn_enviar.clicked.connect(self.enviar_codigo)
        
        layout.addWidget(label_desc)
        layout.addSpacing(10)
        layout.addWidget(label_usuario)
        layout.addWidget(self.combo_usuarios)
        layout.addWidget(self.label_mensaje_1)
        layout.addWidget(self.btn_enviar)
        
        return frame
    
    def crear_pantalla_codigo(self):
        """Segunda pantalla: ingresar código y nueva contraseña"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        frame.setLayout(layout)
        
        # Descripción
        label_desc = QLabel("Ingresa el código que recibiste y tu nueva contraseña")
        label_desc.setStyleSheet(ESTILO_SUBTITULO)
        label_desc.setWordWrap(True)
        label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Formulario
        form_frame = QFrame()
        form_frame.setStyleSheet(ESTILO_FRAME)
        layout_form = QVBoxLayout()
        layout_form.setSpacing(12)
        form_frame.setLayout(layout_form)
        
        # Código
        label_codigo = QLabel("Código de Verificación")
        label_codigo.setStyleSheet(ESTILO_LABEL)
        
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ingresa el código de 6 dígitos")
        self.input_codigo.setStyleSheet(ESTILO_INPUT)
        self.input_codigo.setMinimumHeight(45)
        self.input_codigo.setMaxLength(6)
        
        layout_form.addWidget(label_codigo)
        layout_form.addWidget(self.input_codigo)
        layout_form.addSpacing(10)
        
        # Nueva contraseña
        label_nueva = QLabel("Nueva Contraseña")
        label_nueva.setStyleSheet(ESTILO_LABEL)
        
        self.input_nueva = QLineEdit()
        self.input_nueva.setPlaceholderText("Mínimo 6 caracteres")
        self.input_nueva.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nueva.setStyleSheet(ESTILO_INPUT)
        self.input_nueva.setMinimumHeight(45)
        
        layout_form.addWidget(label_nueva)
        layout_form.addWidget(self.input_nueva)
        layout_form.addSpacing(5)
        
        # Confirmar contraseña
        label_confirmar = QLabel("Confirmar Contraseña")
        label_confirmar.setStyleSheet(ESTILO_LABEL)
        
        self.input_confirmar = QLineEdit()
        self.input_confirmar.setPlaceholderText("Repite la contraseña")
        self.input_confirmar.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirmar.setStyleSheet(ESTILO_INPUT)
        self.input_confirmar.setMinimumHeight(45)
        
        layout_form.addWidget(label_confirmar)
        layout_form.addWidget(self.input_confirmar)
        
        # Mensaje
        self.label_mensaje_2 = QLabel("")
        self.label_mensaje_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje_2.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje_2.setVisible(False)
        self.label_mensaje_2.setWordWrap(True)
        
        layout.addWidget(label_desc)
        layout.addWidget(form_frame)
        layout.addWidget(self.label_mensaje_2)
        
        return frame
    
    def crear_botones(self, layout):
        """Botones de acción"""
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
        btn_cancelar.clicked.connect(self.reject)
        
        # Cambiar contraseña / Siguiente
        self.btn_cambiar = QPushButton("Cambiar Contraseña")
        self.btn_cambiar.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_cambiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cambiar.setMinimumHeight(50)
        self.btn_cambiar.clicked.connect(self.cambiar_password)
        self.btn_cambiar.setVisible(False)
        
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(self.btn_cambiar)
        
        layout.addWidget(footer)
    
    def cargar_usuarios(self):
        """Carga la lista de usuarios disponibles"""
        from cliente.datos_local import cargar_usuarios
        
        usuarios_dict = cargar_usuarios()
        usuarios_lista = list(usuarios_dict.keys())
        
        if usuarios_lista:
            for usuario in usuarios_lista:
                nombre = usuarios_dict[usuario].get("nombre", usuario)
                apellido = usuarios_dict[usuario].get("apellido", "")
                self.combo_usuarios.addItem(f"{nombre} {apellido} (@{usuario})", usuario)
        else:
            self.combo_usuarios.addItem("No hay usuarios registrados")
    
    def enviar_codigo(self):
        """Envía el código por email"""
        self.usuario_seleccionado = self.combo_usuarios.currentData()
        
        if not self.usuario_seleccionado:
            self.mostrar_mensaje(1, "Por favor selecciona un usuario", "error")
            return
        
        from cliente.datos_local import obtener_email_usuario
        from cliente.email_service import enviar_codigo_recuperacion
        
        email = obtener_email_usuario(self.usuario_seleccionado)
        
        self.btn_enviar.setEnabled(False)
        self.mostrar_mensaje(1, "Enviando código...", "exito")
        
        # Enviar código
        exito, mensaje, codigo = enviar_codigo_recuperacion(
            email,
            self.usuario_seleccionado
        )
        
        if exito:
            self.codigo_enviado = codigo
            self.mostrar_mensaje(1, mensaje, "exito")
            QTimer.singleShot(1500, self.mostrar_pantalla_codigo)
        else:
            self.btn_enviar.setEnabled(True)
            self.mostrar_mensaje(1, mensaje, "error")
    
    def mostrar_pantalla_codigo(self):
        """Cambia a la pantalla de ingreso de código"""
        self.pantalla_usuario.setVisible(False)
        self.pantalla_codigo.setVisible(True)
        self.btn_cambiar.setVisible(True)
    
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
        
        email = obtener_email_usuario(self.usuario_seleccionado)
        
        self.btn_cambiar.setEnabled(False)
        
        valido, mensaje_verificacion = verificar_codigo(email, codigo)
        
        if not valido:
            self.btn_cambiar.setEnabled(True)
            self.mostrar_mensaje(2, mensaje_verificacion, "error")
            return
        
        # Cambiar contraseña
        exito, mensaje = cambiar_password(self.usuario_seleccionado, nueva)
        
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

