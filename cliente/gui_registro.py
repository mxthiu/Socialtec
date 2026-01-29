from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QApplication,
    QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath
import sys
import os

# Importar estilos
from cliente.estilos import *


class VentanaRegistro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.foto_seleccionada = None  # Path de la foto
        self.inicializar_ui()
    
    def inicializar_ui(self):
        self.setWindowTitle("SocialTec - Crear Cuenta")
        self.resize(440, 720)
        self.setMinimumSize(400, 640)
        self.setStyleSheet(ESTILO_VENTANA)
        
        # Widget central con scroll
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Scroll area para contenido largo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        scroll.setWidget(contenido)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(40, 30, 40, 30)
        layout_principal.setSpacing(20)
        contenido.setLayout(layout_principal)
        
        # Layout de la ventana
        layout_ventana = QVBoxLayout()
        layout_ventana.setContentsMargins(0, 0, 0, 0)
        widget_central.setLayout(layout_ventana)
        layout_ventana.addWidget(scroll)
        
        self.crear_header(layout_principal)
        
        self.crear_selector_foto(layout_principal)
        
        self.crear_formulario(layout_principal)
        
        self.label_mensaje = QLabel("")
        self.label_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje.setVisible(False)
        self.label_mensaje.setWordWrap(True)
        layout_principal.addWidget(self.label_mensaje)
        
        self.btn_registrar = QPushButton("Crear Cuenta")
        self.btn_registrar.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_registrar.setMinimumHeight(50)
        self.btn_registrar.clicked.connect(self.registrar_usuario)
        layout_principal.addWidget(self.btn_registrar)
        
        layout_login = QHBoxLayout()
        layout_login.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_tiene_cuenta = QLabel("¿Ya tienes cuenta?")
        label_tiene_cuenta.setStyleSheet(ESTILO_SUBTITULO)
        
        self.btn_ir_login = QPushButton("Iniciar sesión")
        self.btn_ir_login.setStyleSheet(ESTILO_BOTON_TEXTO)
        self.btn_ir_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ir_login.clicked.connect(self.ir_a_login)
        
        layout_login.addWidget(label_tiene_cuenta)
        layout_login.addWidget(self.btn_ir_login)
        layout_principal.addLayout(layout_login)
        
        layout_principal.addSpacing(20)
    
    def crear_header(self, layout):
        titulo = QLabel("Crear Cuenta")
        titulo.setStyleSheet(ESTILO_TITULO)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        subtitulo = QLabel("Únete a la comunidad SocialTec")
        subtitulo.setStyleSheet(ESTILO_SUBTITULO)
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)
        
        layout.addSpacing(10)
    
    def crear_selector_foto(self, layout):
        layout_foto = QVBoxLayout()
        layout_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Label para mostrar la foto (circular)
        self.label_foto = QLabel()
        self.label_foto.setFixedSize(120, 120)
        self.label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_foto.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORES['superficie_clara']};
                border: 3px solid {COLORES['borde']};
                border-radius: 60px;
                color: {COLORES['texto_secundario']};
                font-size: 40px;
            }}
        """)
        self.label_foto.setText("")
        
        # Botón para seleccionar foto
        btn_seleccionar = QPushButton("Seleccionar foto")
        btn_seleccionar.setStyleSheet(ESTILO_BOTON_TEXTO)
        btn_seleccionar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_seleccionar.clicked.connect(self.seleccionar_foto)
        
        layout_foto.addWidget(self.label_foto)
        layout_foto.addWidget(btn_seleccionar)
        layout.addLayout(layout_foto)
    
    def crear_formulario(self, layout):
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME)
        layout_form = QVBoxLayout()
        layout_form.setSpacing(12)
        frame.setLayout(layout_form)
        
        # Nombre
        label_nombre = QLabel("Nombre")
        label_nombre.setStyleSheet(ESTILO_LABEL)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Tu nombre")
        self.input_nombre.setStyleSheet(ESTILO_INPUT)
        self.input_nombre.setMinimumHeight(45)
        
        layout_form.addWidget(label_nombre)
        layout_form.addWidget(self.input_nombre)
        layout_form.addSpacing(5)
        
        # Apellido
        label_apellido = QLabel("Apellido")
        label_apellido.setStyleSheet(ESTILO_LABEL)
        self.input_apellido = QLineEdit()
        self.input_apellido.setPlaceholderText("Tu apellido")
        self.input_apellido.setStyleSheet(ESTILO_INPUT)
        self.input_apellido.setMinimumHeight(45)
        
        layout_form.addWidget(label_apellido)
        layout_form.addWidget(self.input_apellido)
        layout_form.addSpacing(5)
        
        # Usuario
        label_usuario = QLabel("Usuario")
        label_usuario.setStyleSheet(ESTILO_LABEL)
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Elige un nombre de usuario")
        self.input_usuario.setStyleSheet(ESTILO_INPUT)
        self.input_usuario.setMinimumHeight(45)
        self.input_usuario.textChanged.connect(self.validar_usuario_disponible)
        
        layout_form.addWidget(label_usuario)
        layout_form.addWidget(self.input_usuario)
        
        self.label_usuario_error = QLabel("")
        self.label_usuario_error.setStyleSheet(f"QLabel {{ color: {COLORES['error']}; font-size: 12px; }}")
        self.label_usuario_error.setVisible(False)
        self.label_usuario_error.setWordWrap(True)
        layout_form.addWidget(self.label_usuario_error)
        layout_form.addSpacing(5)
        
        # Email
        label_email = QLabel("Correo Electrónico")
        label_email.setStyleSheet(ESTILO_LABEL)
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("tu_email@gmail.com")
        self.input_email.setStyleSheet(ESTILO_INPUT)
        self.input_email.setMinimumHeight(45)
        
        layout_form.addWidget(label_email)
        layout_form.addWidget(self.input_email)
        layout_form.addSpacing(5)
        
        # Contraseña
        label_password = QLabel("Contraseña")
        label_password.setStyleSheet(ESTILO_LABEL)
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Mínimo 6 caracteres")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(ESTILO_INPUT)
        self.input_password.setMinimumHeight(45)
        
        layout_form.addWidget(label_password)
        layout_form.addWidget(self.input_password)
        layout_form.addSpacing(5)
        
        # Confirmar contraseña
        label_confirmar = QLabel("Confirmar Contraseña")
        label_confirmar.setStyleSheet(ESTILO_LABEL)
        self.input_confirmar = QLineEdit()
        self.input_confirmar.setPlaceholderText("Repite tu contraseña")
        self.input_confirmar.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirmar.setStyleSheet(ESTILO_INPUT)
        self.input_confirmar.setMinimumHeight(45)
        self.input_confirmar.returnPressed.connect(self.registrar_usuario)
        
        layout_form.addWidget(label_confirmar)
        layout_form.addWidget(self.input_confirmar)
        
        layout.addWidget(frame)
    
    def seleccionar_foto(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar foto de perfil",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if archivo:
            self.foto_seleccionada = archivo
            self.mostrar_foto_preview(archivo)
    
    def mostrar_foto_preview(self, ruta):
        pixmap = QPixmap(ruta)
        
        if not pixmap.isNull():
            # Redimensionar manteniendo aspecto
            pixmap = pixmap.scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Crear imagen circular
            resultado = QPixmap(120, 120)
            resultado.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(resultado)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            path.addEllipse(0, 0, 120, 120)
            painter.setClipPath(path)
            
            # Centrar la imagen
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
    
    def registrar_usuario(self):
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        usuario = self.input_usuario.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text()
        confirmar = self.input_confirmar.text()
        
        # Validaciones
        if not all([nombre, apellido, usuario, email, password, confirmar]):
            self.mostrar_mensaje("Por favor completa todos los campos", "error")
            return
        
        if len(nombre) < 2:
            self.mostrar_mensaje("El nombre debe tener al menos 2 caracteres", "error")
            return
        
        if len(apellido) < 2:
            self.mostrar_mensaje("El apellido debe tener al menos 2 caracteres", "error")
            return
        
        if len(usuario) < 3:
            self.mostrar_mensaje("El usuario debe tener al menos 3 caracteres", "error")
            return
        

        if "@" not in email or "." not in email:
            self.mostrar_mensaje("Por favor ingresa un email válido", "error")
            return
        
        if len(password) < 6:
            self.mostrar_mensaje("La contraseña debe tener al menos 6 caracteres", "error")
            return
        
        if password != confirmar:
            self.mostrar_mensaje("Las contraseñas no coinciden", "error")
            return
        
        from cliente.auth_client import registrar_usuario
        
        self.mostrar_mensaje("Creando cuenta...", "exito")
        self.btn_registrar.setEnabled(False)
        
        exito, mensaje = registrar_usuario(usuario, password, nombre, apellido, email, self.foto_seleccionada)
        
        if exito:
            QTimer.singleShot(1000, self.registro_exitoso)
        else:
            self.btn_registrar.setEnabled(True)
            self.mostrar_mensaje(mensaje, "error")
    
    def registro_exitoso(self):
        """Callback de registro exitoso"""
        self.mostrar_mensaje("¡Cuenta creada! Redirigiendo al login...", "exito")
        QTimer.singleShot(1500, self.ir_a_login)
        self.btn_registrar.setEnabled(True)
    
    def mostrar_mensaje(self, texto, tipo="error"):
        """Muestra mensaje de error o éxito"""
        self.label_mensaje.setText(texto)
        
        if tipo == "error":
            self.label_mensaje.setStyleSheet(ESTILO_ERROR)
        else:
            self.label_mensaje.setStyleSheet(ESTILO_EXITO)
        
        self.label_mensaje.setVisible(True)
        QTimer.singleShot(4000, lambda: self.label_mensaje.setVisible(False))
    
    def ir_a_login(self):
        """Vuelve a la ventana de login"""
        from cliente.gui_login import VentanaLogin
        self.ventana_login = VentanaLogin()
        self.ventana_login.show()
        self.close()
    
    def validar_usuario_disponible(self):
        """Valida en tiempo real si el usuario está disponible"""
        usuario = self.input_usuario.text().strip()
        
        if not usuario:
            self.label_usuario_error.setVisible(False)
            return
        
        if len(usuario) < 3:
            self.label_usuario_error.setText("El usuario debe tener al menos 3 caracteres")
            self.label_usuario_error.setVisible(True)
            return
        
        from cliente.auth_client import cargar_usuarios
        usuarios = cargar_usuarios()
        
        if usuario in usuarios:
            self.label_usuario_error.setText("Este usuario ya está en uso")
            self.label_usuario_error.setVisible(True)
        else:
            self.label_usuario_error.setVisible(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    
    ventana = VentanaRegistro()
    ventana.show()
    
    sys.exit(app.exec())


