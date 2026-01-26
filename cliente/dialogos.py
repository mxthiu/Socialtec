from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from cliente.estilos import *


class DialogoConfirmacion(QDialog):
    """Diálogo de confirmación genérico"""
    
    def __init__(self, titulo, mensaje, texto_confirmar="Confirmar", texto_cancelar="Cancelar", parent=None):
        super().__init__(parent)
        self.resultado = False
        self.titulo = titulo
        self.mensaje = mensaje
        self.texto_confirmar = texto_confirmar
        self.texto_cancelar = texto_cancelar
        self.inicializar_ui()
        self.aplicar_animacion_entrada()
    
    def inicializar_ui(self):
        """Configura el diálogo"""
        self.setWindowTitle(self.titulo)
        self.setFixedWidth(400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORES['fondo']};
            }}
        """)
        self.setModal(True)
        
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setSpacing(25)
        self.setLayout(layout_principal)
        
        label_titulo = QLabel(self.titulo)
        label_titulo.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto']};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_mensaje = QLabel(self.mensaje)
        label_mensaje.setStyleSheet(f"""
            QLabel {{
                color: {COLORES['texto_secundario']};
                font-size: 15px;
                background: transparent;
            }}
        """)
        label_mensaje.setWordWrap(True)
        label_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(12)
        
        btn_cancelar = QPushButton(self.texto_cancelar)
        btn_cancelar.setFixedHeight(45)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['texto_secundario']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['superficie_clara']};
                color: {COLORES['texto']};
            }}
        """)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.clicked.connect(self.cancelar)
        
        btn_confirmar = QPushButton(self.texto_confirmar)
        btn_confirmar.setFixedHeight(45)
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['primario']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['primario_hover']};
            }}
        """)
        btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirmar.clicked.connect(self.confirmar)
        
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(btn_confirmar)
        
        layout_principal.addWidget(label_titulo)
        layout_principal.addWidget(label_mensaje)
        layout_principal.addSpacing(10)
        layout_principal.addLayout(layout_botones)
    
    def aplicar_animacion_entrada(self):
        """Aplica animación de fade in al diálogo"""
        self.efecto_opacidad = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.efecto_opacidad)
        
        self.animacion = QPropertyAnimation(self.efecto_opacidad, b"opacity")
        self.animacion.setDuration(200)
        self.animacion.setStartValue(0)
        self.animacion.setEndValue(1)
        self.animacion.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animacion.start()
    
    def confirmar(self):
        """Usuario confirma la acción"""
        self.resultado = True
        self.accept()
    
    def cancelar(self):
        """Usuario cancela la acción"""
        self.resultado = False
        self.reject()
    
    @staticmethod
    def mostrar(titulo, mensaje, texto_confirmar="Confirmar", texto_cancelar="Cancelar", parent=None):
        """
        Método estático para mostrar el diálogo fácilmente
        Retorna: True si confirma, False si cancela
        """
        dialogo = DialogoConfirmacion(titulo, mensaje, texto_confirmar, texto_cancelar, parent)
        dialogo.exec()
        return dialogo.resultado


class DialogoConfirmacionPeligrosa(DialogoConfirmacion):
    """Diálogo de confirmación para acciones peligrosas (eliminar, etc)"""
    
    def inicializar_ui(self):
        """Configura el diálogo con estilo de advertencia"""
        super().inicializar_ui()
        
        layout = self.layout()
        layout_botones = layout.itemAt(3).layout()
        btn_confirmar = layout_botones.itemAt(1).widget()
        
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORES['error']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)


def confirmar_eliminar_amigo(nombre_amigo, parent=None):
    """Confirma eliminación de un amigo"""
    return DialogoConfirmacionPeligrosa.mostrar(
        "Eliminar Amigo",
        f"¿Estás seguro de que deseas eliminar a {nombre_amigo} de tus amigos?\n\nEsta acción no se puede deshacer.",
        "Eliminar",
        "Cancelar",
        parent
    )


def confirmar_cerrar_sesion(parent=None):
    """Confirma cerrar sesión"""
    return DialogoConfirmacion.mostrar(
        "Cerrar Sesión",
        "¿Estás seguro de que deseas cerrar sesión?",
        "Cerrar Sesión",
        "Cancelar",
        parent
    )


def confirmar_cambio_password(parent=None):
    """Confirma cambio de contraseña"""
    return DialogoConfirmacion.mostrar(
        "Cambiar Contraseña",
        "¿Deseas continuar con el cambio de contraseña?\n\nSe enviará un código a tu correo.",
        "Continuar",
        "Cancelar",
        parent
    )


def confirmar_cancelar_edicion(parent=None):
    """Confirma cancelar edición con cambios sin guardar"""
    return DialogoConfirmacion.mostrar(
        "Cancelar Edición",
        "Tienes cambios sin guardar.\n\n¿Estás seguro de que deseas cancelar?",
        "Descartar Cambios",
        "Volver",
        parent
    )
