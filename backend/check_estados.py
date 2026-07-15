"""
Script rápido para validar los estados existentes en @DM_GC_FICHA.
"""
import os
import sys
from pathlib import Path

# Configurar Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from giftcards.utils import execute_query

# 1. Valores distintos de U_Estado con conteo
print("=" * 60)
print("  VALORES DISTINTOS DE U_Estado EN @DM_GC_FICHA")
print("=" * 60)

query = """
    SELECT 
        T0."U_Estado" AS estado,
        COUNT(*) AS cantidad
    FROM "@DM_GC_FICHA" T0
    GROUP BY T0."U_Estado"
    ORDER BY cantidad DESC
"""
results = execute_query(query)

for r in results:
    estado = r['estado'] if r['estado'] is not None else '(NULL)'
    print(f"  {estado:20s}  =>  {r['cantidad']} tarjetas")

print(f"\n  Total registros: {sum(r['cantidad'] for r in results)}")
print("=" * 60)
