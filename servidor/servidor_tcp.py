"""
Servidor TCP con soporte para multiples clientes usando hilos.

TODO:
- Escuchar en host/puerto desde utils.config.
- Aceptar conexiones y crear un hilo por cliente.
- Coordinar acceso a estado compartido (usuarios, grafo) con locks.
- Despachar acciones segun utils.protocolo.
"""
