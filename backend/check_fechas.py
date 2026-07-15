"""Check date formats returned by SAP."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django; django.setup()
from giftcards.utils import execute_query

query = """
    SELECT TOP 5
        T0."DocEntry" AS id,
        T0."U_Codigo" AS codigo,
        T0."U_Estado" AS estado,
        T0."U_Beneficiario" AS beneficiario,
        T0."U_CedulaBenef" AS cedula,
        T0."U_FechaGeneracion" AS fecha_generacion,
        T0."U_FechaVenta" AS fecha_venta,
        T0."U_FechaExpiracion" AS fecha_expiracion,
        T0."U_FechaActivacion" AS fecha_activacion
    FROM "@DM_GC_FICHA" T0
    WHERE T0."U_Estado" = 'VENDIDA'
"""
results = execute_query(query)

for r in results:
    print(f"ID={r['id']} | Codigo={r['codigo']} | Estado={r['estado']}")
    print(f"  Beneficiario: {r['beneficiario']}")
    print(f"  Cedula:       {r['cedula']}")
    print(f"  FechaGen:     {repr(r['fecha_generacion'])}")
    print(f"  FechaVenta:   {repr(r['fecha_venta'])}")
    print(f"  FechaExpir:   {repr(r['fecha_expiracion'])}")
    print(f"  FechaActiv:   {repr(r['fecha_activacion'])}")
    print()
