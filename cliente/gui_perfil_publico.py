# gui_perfil_publico.py - Vista de perfil solo lectura para otros usuarios

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath

from cliente.estilos import COLORES, ESTILO_VENTANA


class VentanaPerfilPublico(QDialog):
    def __init__(self, usuario_actual, perfil_objetivo, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.perfil_objetivo = perfil_objetivo
        self.setWindowTitle(f"Perfil de @{perfil_objetivo.get('usuario', '')}")
        self.setFixedSize(420, 540)
        self.setStyleSheet(ESTILO_VENTANA)
        self.inicializar_ui()

    def inicializar_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)
        self.setLayout(layout)

        header = QFrame()
        header.setStyleSheet(f"QFrame {{ background-color: {COLORES['superficie']}; border-radius: 14px; }}")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(10)
        header.setLayout(header_layout)

        foto_label = QLabel()
        foto_label.setFixedSize(110, 110)
        foto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cargar_foto_circular(foto_label, self.perfil_objetivo.get("foto"))

        nombre = f"{self.perfil_objetivo.get('nombre', '')} {self.perfil_objetivo.get('apellido', '')}".strip()
        label_nombre = QLabel(nombre)
        label_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_nombre.setStyleSheet(f"color: {COLORES['texto']}; font-size: 20px; font-weight: bold;")

        label_usuario = QLabel(f"@{self.perfil_objetivo.get('usuario', '')}")
        label_usuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_usuario.setStyleSheet(f"color: {COLORES['texto_secundario']}; font-size: 14px;")

        label_email = QLabel(self.perfil_objetivo.get("email", ""))
        label_email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_email.setStyleSheet(f"color: {COLORES['texto_secundario']}; font-size: 13px;")

        header_layout.addWidget(foto_label)
        header_layout.addWidget(label_nombre)
        header_layout.addWidget(label_usuario)
        if label_email.text():
            header_layout.addWidget(label_email)

        layout.addWidget(header)

        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"QFrame {{ background-color: {COLORES['superficie']}; border-radius: 12px; }}")
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(14, 14, 14, 14)
        stats_layout.setSpacing(14)
        stats_frame.setLayout(stats_layout)

        self.label_amigos = QLabel()
        self.label_amigos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_amigos.setStyleSheet(f"color: {COLORES['texto']}; font-size: 15px; font-weight: bold;")
        self.actualizar_conteo_amigos()

        stats_layout.addWidget(self.label_amigos)
        layout.addWidget(stats_frame)

        self.btn_amigo = QPushButton()
        self.btn_amigo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_amigo.setFixedHeight(44)
        self.btn_amigo.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORES['primario']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['primario_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORES['borde']};
                color: {COLORES['texto_secundario']};
            }}
            """
        )
        self.btn_amigo.clicked.connect(self.toggle_amistad)
        layout.addWidget(self.btn_amigo)

        self.label_estado = QLabel()
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setStyleSheet(f"color: {COLORES['texto_secundario']}; font-size: 13px;")
        layout.addWidget(self.label_estado)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORES['texto']};
                border: 2px solid {COLORES['borde']};
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORES['superficie_clara']};
            }}
            """
        )
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

        self.refrescar_estado_amistad()

    def cargar_foto_circular(self, label, ruta):
        pixmap = QPixmap(ruta) if ruta else QPixmap()
        if pixmap.isNull():
            label.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {COLORES['primario']};
                    border-radius: 55px;
                    color: white;
                    font-size: 30px;
                    font-weight: bold;
                }}
                """
            )
            inicial = self.perfil_objetivo.get("nombre", "?")[:1].upper() or "?"
            label.setText(inicial)
            return

        pixmap = pixmap.scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        resultado = QPixmap(110, 110)
        resultado.fill(Qt.GlobalColor.transparent)

        painter = QPainter(resultado)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, 110, 110)
        painter.setClipPath(path)
        x = (110 - pixmap.width()) // 2
        y = (110 - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()

        label.setPixmap(resultado)

    def es_amigo(self):
        objetivo = self.perfil_objetivo.get("usuario")
        amigos = self.usuario_actual.get("amigos", [])
        amigos_usernames = [a if isinstance(a, str) else a.get("usuario") for a in amigos]
        return objetivo in amigos_usernames

    def refrescar_estado_amistad(self):
        if self.perfil_objetivo.get("usuario") == self.usuario_actual.get("usuario"):
            self.btn_amigo.setText("Es tu perfil")
            self.btn_amigo.setDisabled(True)
            self.label_estado.setText("Solo lectura")
            return

        if self.es_amigo():
            self.btn_amigo.setText("Eliminar de amigos")
            self.label_estado.setText("Ya son amigos")
        else:
            self.btn_amigo.setText("Agregar a amigos")
            self.label_estado.setText("No es tu amigo")

    def toggle_amistad(self):
        from cliente.datos_local import agregar_amigo, eliminar_amigo, cargar_usuarios, obtener_amigos_completos

        usuario_actual = self.usuario_actual.get("usuario")
        objetivo = self.perfil_objetivo.get("usuario")

        if self.es_amigo():
            exito, msg = eliminar_amigo(usuario_actual, objetivo)
        else:
            exito, msg = agregar_amigo(usuario_actual, objetivo)

        self.label_estado.setText(msg)

        if exito:
            usuarios = cargar_usuarios()
            if usuario_actual in usuarios:
                amigos_actualizados = usuarios[usuario_actual].get("amigos", [])
                self.usuario_actual["amigos"] = obtener_amigos_completos(amigos_actualizados)

            try:
                from cliente.datos_local import obtener_usuario_completo

                datos_actualizados = obtener_usuario_completo(usuario_actual)
                if datos_actualizados:
                    self.usuario_actual.update(datos_actualizados)
            except Exception:
                pass

            if objetivo in usuarios:
                amigos_objetivo = usuarios[objetivo].get("amigos", [])
                self.perfil_objetivo["amigos"] = obtener_amigos_completos(amigos_objetivo)
                self.actualizar_conteo_amigos()

            self.refrescar_estado_amistad()
            self.notificar_cambio()

    def actualizar_conteo_amigos(self):
        cantidad = len(self.perfil_objetivo.get("amigos", []))
        self.label_amigos.setText(f"{cantidad} amigos")

    def notificar_cambio(self):
        contenedor = self.parent()
        ventana_main = getattr(contenedor, "parent_window", None) if contenedor else None

        if ventana_main and hasattr(ventana_main, "actualizar_datos_usuario"):
            ventana_main.actualizar_datos_usuario()
