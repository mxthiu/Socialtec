# gui_login.py - Pantalla de inicio de sesión para SocialTec

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys

# Importar estilos
from cliente.estilos import *


class VentanaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inicializar_ui()
    
    def inicializar_ui(self):
        """Configura la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("SocialTec - Iniciar Sesión")
        self.setFixedSize(450, 600)
        self.setStyleSheet(ESTILO_VENTANA)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(40, 40, 40, 40)
        layout_principal.setSpacing(20)
        widget_central.setLayout(layout_principal)
        
        # ===== HEADER - Título y subtítulo =====
        self.crear_header(layout_principal)
        
        # ===== FORMULARIO - Frame con campos =====
        self.crear_formulario(layout_principal)
        
        # ===== MENSAJE DE ERROR/ÉXITO =====
        self.label_mensaje = QLabel("")
        self.label_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensaje.setStyleSheet(ESTILO_ERROR)
        self.label_mensaje.setVisible(False)
        layout_principal.addWidget(self.label_mensaje)
        
        # ===== BOTÓN DE LOGIN =====
        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.setStyleSheet(ESTILO_BOTON_PRIMARIO)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setMinimumHeight(50)
        self.btn_login.clicked.connect(self.iniciar_sesion)
        layout_principal.addWidget(self.btn_login)
        
        # ===== LINK OLVIDÉ CONTRASEÑA =====
        btn_olvide = QPushButton("¿Olvidé mi contraseña?")
        btn_olvide.setStyleSheet(ESTILO_BOTON_TEXTO)
        btn_olvide.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_olvide.clicked.connect(self.recuperar_password)
        layout_principal.addWidget(btn_olvide)
        
        # ===== LINK A REGISTRO =====
        layout_registro = QHBoxLayout()
        layout_registro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_no_cuenta = QLabel("¿No tienes cuenta?")
        label_no_cuenta.setStyleSheet(ESTILO_SUBTITULO)
        
        self.btn_ir_registro = QPushButton("Crear una")
        self.btn_ir_registro.setStyleSheet(ESTILO_BOTON_TEXTO)
        self.btn_ir_registro.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ir_registro.clicked.connect(self.ir_a_registro)
        
        layout_registro.addWidget(label_no_cuenta)
        layout_registro.addWidget(self.btn_ir_registro)
        layout_principal.addLayout(layout_registro)
        
        # Espaciador al final
        layout_principal.addStretch()
    
    def crear_header(self, layout):
        """Crea el encabezado con título y subtítulo"""
        # Título
        titulo = QLabel("SocialTec")
        titulo.setStyleSheet(ESTILO_TITULO)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Conecta con tus amigos")
        subtitulo.setStyleSheet(ESTILO_SUBTITULO)
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)
        
        # Espaciador
        layout.addSpacing(20)
    
    def crear_formulario(self, layout):
        """Crea el formulario con los campos de entrada"""
        # Frame contenedor
        frame = QFrame()
        frame.setStyleSheet(ESTILO_FRAME)
        layout_form = QVBoxLayout()
        layout_form.setSpacing(15)
        frame.setLayout(layout_form)
        
        # Campo de usuario
        label_usuario = QLabel("Usuario")
        label_usuario.setStyleSheet(ESTILO_LABEL)
        
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Ingresa tu usuario")
        self.input_usuario.setStyleSheet(ESTILO_INPUT)
        self.input_usuario.setMinimumHeight(45)
        
        layout_form.addWidget(label_usuario)
        layout_form.addWidget(self.input_usuario)
        
        # Espacio entre campos
        layout_form.addSpacing(10)
        
        # Campo de contraseña
        label_password = QLabel("Contraseña")
        label_password.setStyleSheet(ESTILO_LABEL)
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Ingresa tu contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(ESTILO_INPUT)
        self.input_password.setMinimumHeight(45)
        self.input_password.returnPressed.connect(self.iniciar_sesion)  # Enter para login
        
        layout_form.addWidget(label_password)
        layout_form.addWidget(self.input_password)
        
        layout.addWidget(frame)
    
    def iniciar_sesion(self):
        """Maneja el evento de inicio de sesión"""
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()
        
        # Validación básica
        if not usuario or not password:
            self.mostrar_mensaje("Por favor completa todos los campos", tipo="error")
            return
        
        if len(usuario) < 3:
            self.mostrar_mensaje("El usuario debe tener al menos 3 caracteres", tipo="error")
            return
        
        if len(password) < 4:
            self.mostrar_mensaje("La contraseña debe tener al menos 4 caracteres", tipo="error")
            return
        
        # Validar con datos locales (MOCK)
        from cliente.datos_local import validar_login
        
        self.mostrar_mensaje("Iniciando sesión...", tipo="exito")
        self.btn_login.setEnabled(False)
        
        # Validar credenciales
        exito, datos_usuario = validar_login(usuario, password)
        
        if exito:
            # Guardar datos del usuario
            self.datos_usuario = datos_usuario
            QTimer.singleShot(800, self.login_exitoso)
        else:
            self.btn_login.setEnabled(True)
            self.mostrar_mensaje("Usuario o contraseña incorrectos", tipo="error")
    
    def login_exitoso(self):
        """Callback cuando el login es exitoso"""
        self.mostrar_mensaje("¡Login exitoso!", tipo="exito")
        # Abrir main menu con datos del usuario
        from cliente.gui_main_menu import VentanaMainMenu
        self.ventana_main = VentanaMainMenu(self.datos_usuario)
        self.ventana_main.show()
        self.close()
    
    def mostrar_mensaje(self, texto, tipo="error"):
        """Muestra un mensaje de error o éxito"""
        self.label_mensaje.setText(texto)
        
        if tipo == "error":
            self.label_mensaje.setStyleSheet(ESTILO_ERROR)
        else:
            self.label_mensaje.setStyleSheet(ESTILO_EXITO)
        
        self.label_mensaje.setVisible(True)
        
        # Ocultar mensaje después de 4 segundos
        QTimer.singleShot(4000, lambda: self.label_mensaje.setVisible(False))
    
    def ir_a_registro(self):
        """Abre la ventana de registro"""
        from cliente.gui_registro import VentanaRegistro
        self.ventana_registro = VentanaRegistro()
        self.ventana_registro.show()
        self.close()
    
    def recuperar_password(self):
        """Abre la ventana de recuperación de contraseña"""
        from cliente.gui_recuperar_password import VentanaRecuperarPassword
        self.ventana_recuperar = VentanaRecuperarPassword()
        self.ventana_recuperar.show()


# ===== PUNTO DE ENTRADA PARA PRUEBAS =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar fuente global
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)
    
    ventana = VentanaLogin()
    ventana.show()
    
    sys.exit(app.exec())