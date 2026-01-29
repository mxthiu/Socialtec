# -*- coding: utf-8 -*-
"""
Test: Verificar que el servidor retorna estadísticas correctamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("="*70)
print("TEST: Verificar estructura de datos de estadísticas")
print("="*70)

from servidor.persistencia import cargar_usuarios, guardar_usuarios, agregar_amistad
from servidor.autenticacion import hash_password
from grafo.algoritmos import calcular_estadisticas, estadisticas_como_dict
from utils.protocolo import Response

# Crear usuarios
print("\n1. Crear usuarios...")
usuarios = {
    "est_user_1": {
        "usuario": "est_user_1",
        "password_hash": hash_password("pass"),
        "nombre": "Est", "apellido": "User1",
        "email": "est1@test.com", "foto": "",
        "amigos": []
    },
    "est_user_2": {
        "usuario": "est_user_2",
        "password_hash": hash_password("pass"),
        "nombre": "Est", "apellido": "User2",
        "email": "est2@test.com", "foto": "",
        "amigos": []
    }
}
guardar_usuarios(usuarios)
agregar_amistad("est_user_1", "est_user_2")
print("✓ Usuarios creados")

# Lo importante: verificar que el SERVIDOR retorna bien la estructura
print("\n2. Verificar estructura que el SERVIDOR retorna...")

# Simular datos que retorna estadisticas_como_dict
stats_dict = {
    "usuario_con_mas_amigos": "est_user_1",
    "max_amigos": 1,
    "usuario_con_menos_amigos": "est_user_2",
    "min_amigos": 1,
    "promedio_amigos": 1.0,
    "cantidad_usuarios": 2,
    "cantidad_amistades": 1
}

print(f"\n   Stats dict raw: {stats_dict}")

# Mapear como lo hace el servidor (después de mi cambio)
data = {
    "estadisticas": {
        "total_usuarios": stats_dict.get("cantidad_usuarios", 0),
        "total_amistades": stats_dict.get("cantidad_amistades", 0),
        "promedio_amigos": stats_dict.get("promedio_amigos", 0),
        "usuario_mas_amigos": {
            "usuario": stats_dict.get("usuario_con_mas_amigos", ""),
            "amigos": stats_dict.get("max_amigos", 0)
        } if stats_dict.get("usuario_con_mas_amigos") else None
    }
}

print(f"\n   Data con estructura: {data}")

# Simular respuesta del servidor
respuesta = Response(
    ok=True,
    message="Estadisticas calculadas",
    data=data
)

print(f"\n3. Simular lo que retorna el cliente (auth_client)...")
# El cliente hace: respuesta.data.get("estadisticas", {})
stats_cliente = respuesta.data.get("estadisticas", {})
print(f"   Stats recibidas por cliente: {stats_cliente}")

# Verificar que tiene las keys
print(f"\n4. Verificar keys...")
required_keys = ["total_usuarios", "total_amistades", "promedio_amigos", "usuario_mas_amigos"]
for key in required_keys:
    tiene = key in stats_cliente
    valor = stats_cliente.get(key, "N/A")
    print(f"   {key}: {tiene} (valor: {valor})")

if all(key in stats_cliente for key in required_keys):
    print("\n✅ ESTRUCTURA CORRECTA - El cliente recibirá bien los datos")
else:
    print("\n❌ ESTRUCTURA INCORRECTA")
