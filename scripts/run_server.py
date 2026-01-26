"""
Entrypoint del servidor.

Objetivo de este script (rama chore/repo-structure-scripts):
- Tener un comando estable: `python scripts/run_server.py`
- Evitar que el código "main" quede en la raíz del repo
"""

from __future__ import annotations


def _try_run_real_server() -> bool:
    """
    Intenta ejecutar el servidor real si ya fue implementado, (obviamente todavía no), en servidor/servidor_tcp.py.
    Retorna True si pudo ejecutarlo, False si todavía no existe (o no tiene la API esperada).
    """
    try:
        # Opción A (recomendada): servidor/servidor_tcp.py expone main()
        from servidor.servidor_tcp import main as server_main  # type: ignore
        server_main()
        return True
    except Exception:
        # Opción B: servidor/servidor_tcp.py expone start_server()
        try:
            from servidor.servidor_tcp import start_server  # type: ignore
            start_server()
            return True
        except Exception:
            return False


def _run_stub_server() -> None:
    """
    Stub temporal para que el script funcione aunque el servidor real
    no esté implementado todavía.
    """
    print("[run_server] Servidor real aún no implementado.")
    print("[run_server] Próximo paso: crear servidor/servidor_tcp.py con main() o start_server().")
    print("[run_server] (Stub) OK: entrypoint funcionando.")


def main() -> None:
    ran = _try_run_real_server()
    if not ran:
        _run_stub_server()


if __name__ == "__main__":
    main()
