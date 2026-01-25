# estilos.py - Estilos visuales para SocialTec

COLORES = {
    "primario": "#2563EB",      # Azul principal
    "primario_hover": "#1D4ED8", # Azul hover
    "fondo": "#0F172A",         # Fondo oscuro
    "superficie": "#1E293B",    # Cards/frames
    "superficie_clara": "#334155", # Superficie más clara
    "texto": "#F1F5F9",         # Texto claro
    "texto_secundario": "#94A3B8", # Texto gris
    "error": "#EF4444",         # Rojo para errores
    "exito": "#10B981",         # Verde para éxito
    "borde": "#475569"          # Bordes
}

# Estilo para toda la ventana principal
ESTILO_VENTANA = f"""
    QMainWindow {{
        background-color: {COLORES['fondo']};
    }}
"""

# Estilo para frames/contenedores
ESTILO_FRAME = f"""
    QFrame {{
        background-color: {COLORES['superficie']};
        border-radius: 15px;
        padding: 20px;
    }}
"""

# Estilo para labels/etiquetas
ESTILO_LABEL = f"""
    QLabel {{
        color: {COLORES['texto']};
        font-size: 14px;
        background: transparent;
        border: none;
    }}
"""

ESTILO_TITULO = f"""
    QLabel {{
        color: {COLORES['texto']};
        font-size: 32px;
        font-weight: bold;
        background: transparent;
        border: none;
    }}
"""

ESTILO_SUBTITULO = f"""
    QLabel {{
        color: {COLORES['texto_secundario']};
        font-size: 14px;
        background: transparent;
        border: none;
    }}
"""

# Estilo para inputs/campos de texto
ESTILO_INPUT = f"""
    QLineEdit {{
        background-color: {COLORES['superficie_clara']};
        color: {COLORES['texto']};
        border: 2px solid {COLORES['borde']};
        border-radius: 10px;
        padding: 12px 15px;
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORES['primario']};
        background-color: {COLORES['superficie']};
    }}
    QLineEdit::placeholder {{
        color: {COLORES['texto_secundario']};
    }}
"""

# Estilo para botones principales
ESTILO_BOTON_PRIMARIO = f"""
    QPushButton {{
        background-color: {COLORES['primario']};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px;
        font-size: 15px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORES['primario_hover']};
    }}
    QPushButton:pressed {{
        background-color: #1E40AF;
    }}
    QPushButton:disabled {{
        background-color: {COLORES['superficie_clara']};
        color: {COLORES['texto_secundario']};
    }}
"""

# Estilo para botones secundarios (texto)
ESTILO_BOTON_TEXTO = f"""
    QPushButton {{
        background-color: transparent;
        color: {COLORES['primario']};
        border: none;
        padding: 10px;
        font-size: 13px;
        text-decoration: underline;
    }}
    QPushButton:hover {{
        color: {COLORES['primario_hover']};
    }}
"""

# Estilo para mensajes de error
ESTILO_ERROR = f"""
    QLabel {{
        color: {COLORES['error']};
        font-size: 13px;
        background: transparent;
        border: none;
        padding: 5px;
    }}
"""

# Estilo para mensajes de éxito
ESTILO_EXITO = f"""
    QLabel {{
        color: {COLORES['exito']};
        font-size: 13px;
        background: transparent;
        border: none;
        padding: 5px;
    }}
"""

