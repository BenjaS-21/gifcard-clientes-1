"""
Inspecciona el esquema de KLK_COBROHDR / KLK_COBROLINE y muestra la fila
real del cobro C006-01-00002147 para ver qué columnas guardan el monto
en USD (o la tasa) frente al monto en Bs.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from giftcards.utils import execute_query

FACTURA = 'C006-01-00002147'
CODIGO_GC = 'FSC5PGTJ'

print("=" * 70)
print(f"  COLUMNAS DE KLK_COBROHDR")
print("=" * 70)
cols_hdr = execute_query("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    FROM [KLK_CONSOLIDADO_V2].INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'KLK_COBROHDR'
    ORDER BY ORDINAL_POSITION
""")
for c in cols_hdr:
    print(f"  {c['COLUMN_NAME']:30s}  {c['DATA_TYPE']}")

print()
print("=" * 70)
print(f"  COLUMNAS DE KLK_COBROLINE")
print("=" * 70)
cols_line = execute_query("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    FROM [KLK_CONSOLIDADO_V2].INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'KLK_COBROLINE'
    ORDER BY ORDINAL_POSITION
""")
for c in cols_line:
    print(f"  {c['COLUMN_NAME']:30s}  {c['DATA_TYPE']}")

print()
print("=" * 70)
print(f"  COBRO REAL  NFactura = {FACTURA}  (la fila que se ve en pantalla)")
print("=" * 70)
hdr = execute_query("""
    SELECT TOP 1 *
    FROM [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROHDR]
    WHERE NFactura = ?
""", [FACTURA])
if hdr:
    print("\n  -- KLK_COBROHDR --")
    for k, v in hdr[0].items():
        print(f"    {k:30s} = {v}")
else:
    print("  (no se encontró la cabecera)")

lines = execute_query("""
    SELECT C2.*
    FROM [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROHDR] C1
    INNER JOIN [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROLINE] C2
      ON C2.NroCobro = C1.NroCobro AND C2.Sucursal = C1.Sucursal
    WHERE C1.NFactura = ?
""", [FACTURA])
for i, ln in enumerate(lines, 1):
    print(f"\n  -- KLK_COBROLINE línea {i} --")
    for k, v in ln.items():
        print(f"    {k:30s} = {v}")

print()
print("=" * 70)
print(f"  GIFT CARD  U_Codigo = {CODIGO_GC}")
print("=" * 70)
gc = execute_query("""
    SELECT "DocEntry","U_Codigo","U_Estado","U_MontoOriginal","U_Saldo",
           "U_FechaActivacion","U_FechaExpiracion","U_Beneficiario"
    FROM "@DM_GC_FICHA"
    WHERE "U_Codigo" = ?
""", [CODIGO_GC])
if gc:
    for k, v in gc[0].items():
        print(f"    {k:30s} = {v}")
