"""
Ejecuta el query real de get_giftcard_transactions_by_code para FSC5PGTJ
y muestra qué devuelve. Si aquí sale en USD pero en la UI sale en Bs,
el problema es caché del backend (reinicia Django) o del frontend.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from giftcards.queries import get_giftcard_transactions_by_code
from giftcards.utils import execute_query

CODIGO = 'FSC5PGTJ'

query, params = get_giftcard_transactions_by_code(CODIGO)
rows = execute_query(query, params)

print(f"Movimientos para {CODIGO}: {len(rows)} filas")
print("=" * 70)
for r in rows:
    print(f"  origen   : {r.get('origen')}")
    print(f"  fecha    : {r.get('fecha')}")
    print(f"  tipo     : {r.get('tipo')}")
    print(f"  monto    : {r.get('monto')}     <-- DEBE ESTAR EN USD")
    print(f"  ref      : {r.get('referencia')}")
    print(f"  saldo_ant: {r.get('saldo_anterior')}")
    print(f"  saldo_pos: {r.get('saldo_posterior')}")
    print("-" * 70)
