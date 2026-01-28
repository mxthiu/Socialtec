"""
Entrypoint del cliente.

Objetivo de este script (rama chore/repo-structure-scripts):
- Tener un comando estable: `python scripts/run_client.py`
- Centralizar el arranque del cliente fuera de la raíz del repo
"""

from __future__ import annotations


def _try_run_real_client() -> bool:
    """
    Intenta ejecutar el cliente real si ya existe un punto de entrada estable.
    Retorna True si pudo ejecutarlo, False si todavía no existe (o no tiene la API esperada).
    """
    # Primero intenta cargar la GUI de login que ya existe
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        import sys
        from cliente.gui_login import VentanaLogin
        
        app = QApplication(sys.argv)
        fuente = QFont("Segoe UI", 10)
        app.setFont(fuente)
        ventana_login = VentanaLogin()
        ventana_login.show()
        sys.exit(app.exec())
        return True
    except Exception:
        # Si no funciona la GUI, intenta cliente_tcp
        try:
            from cliente.cliente_tcp import main as client_main  # type: ignore
            client_main()
            return True
        except Exception:
            return False


def _run_stub_client() -> None:
    print("[run_client] Cliente real aún no implementado.")
    print("[run_client] Próximo paso: definir un main() del cliente (GUI) o un launcher.")
    print("[run_client] (Stub) OK: entrypoint funcionando.")


def main() -> None:
    ran = _try_run_real_client()
    if not ran:
        _run_stub_client()


if __name__ == "__main__":
    main()
