"""
dashboard.py — Indicadores de uso de las gift cards (panel admin y vendedores).

Con ~80 mil tarjetas no se puede consultar tarjeta por tarjeta: se traen
TODAS las fichas y TODOS los consumos de KLK en dos consultas, se guardan en
memoria unos minutos y los indicadores se calculan en Python. Así los filtros
(empresa, lote, período) responden sin volver a consultar SAP.
"""
import logging
import random
import threading
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import median

from django.conf import settings

from .models import CompanyLogo, CompanyLote
from .queries import get_dashboard_cards, get_dashboard_usos
from .utils import execute_query

logger = logging.getLogger(__name__)

CACHE_SECONDS = 10 * 60           # datos de SAP reutilizados por 10 minutos
MIN_REFRESH_SECONDS = 60          # "Actualizar" no vuelve a SAP más de una vez por minuto
SOLD_STATES = {'VENDIDA', 'ACTIVA', 'AGOTADA', 'VENCIDA', 'BLOQUEADA'}
MONTHS = 12                       # meses de las series mensuales
TOP = 15                          # filas de los rankings
LIST_LIMIT = 50                   # filas de las listas de seguimiento
SIN_USO_DIAS = 60                 # "vendida hace más de N días y sin usar"
POR_VENCER_DIAS = 30

PERIODOS = {'todo': None, 'anio': 'anio', '90d': 90, '30d': 30}

_cache = {'data': None, 'loaded_at': 0.0}
_lock = threading.Lock()


# ── Utilidades ───────────────────────────────────────────

def _key(value):
    """Clave de comparación de códigos y lotes (SQL Server ignora mayúsculas y espacios finales)."""
    return str(value or '').strip().upper()


def parse_date(value):
    """Fecha de SAP/KLK como date: ISO ('2026-10-01', '2026-10-01T10:00:00') o 'dd/mm/yyyy'."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    try:
        return datetime.strptime(text[:10], '%d/%m/%Y').date()
    except ValueError:
        return None


def _num(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


# ── Carga de datos (SAP + KLK, o mock) ───────────────────

def load_base(force=False):
    """
    Fichas y consumos, desde la memoria si tienen menos de CACHE_SECONDS.
    `force` vuelve a SAP (como mucho una vez por MIN_REFRESH_SECONDS).
    """
    with _lock:
        age = time.time() - _cache['loaded_at']
        fresh = _cache['data'] is not None and age < CACHE_SECONDS
        if fresh and not (force and age >= MIN_REFRESH_SECONDS):
            return _cache['data']

        if settings.USE_MOCK_DATA:
            cards, usos = mock_dataset()
        else:
            started = time.time()
            q_cards, p_cards = get_dashboard_cards()
            q_usos, p_usos = get_dashboard_usos()
            cards = execute_query(q_cards, p_cards)
            usos = execute_query(q_usos, p_usos)
            logger.info(f"Dashboard: {len(cards)} tarjetas y {len(usos)} usos leídos en {time.time() - started:.1f}s")

        # Normalizar una sola vez: los cálculos por filtro trabajan sobre esto
        for c in cards:
            c['key'] = _key(c.get('codigo'))
            c['lote_key'] = _key(c.get('lote'))
            c['monto'] = _num(c.get('monto'))
            c['venta'] = parse_date(c.get('fecha_venta'))
            c['emision'] = parse_date(c.get('fecha_emision'))
            c['vence'] = parse_date(c.get('fecha_vencimiento'))
            c['estado'] = _key(c.get('estado'))
        for u in usos:
            u['key'] = _key(u.get('codigo'))
            u['monto'] = abs(_num(u.get('monto')))
            u['dia'] = parse_date(u.get('fecha'))
            u['sucursal'] = str(u.get('sucursal') or '').strip() or 'Sin sucursal'

        _cache['data'] = {'cards': cards, 'usos': usos, 'loaded_at': datetime.now().isoformat(timespec='seconds')}
        _cache['loaded_at'] = time.time()
        return _cache['data']


def mock_dataset():
    """Datos de prueba (USE_MOCK_DATA): ~1.200 tarjetas y sus usos de los últimos 14 meses."""
    rng = random.Random(42)
    today = date.today()
    empresas = [
        ('Corporación Andina, C.A.', 'J-400000011', 4, 0.82),
        ('Inversiones Delta, C.A.', 'J-400000022', 3, 0.64),
        ('Grupo Orinoco, S.A.', 'J-400000033', 2, 0.45),
        ('Seguros Ávila, C.A.', 'J-400000044', 2, 0.30),
        ('Distribuidora Caribe, C.A.', 'J-400000055', 1, 0.12),
    ]
    personas = ['María García', 'Carlos Rodríguez', 'Ana Martínez', 'José Pérez', 'Luisa Fernández',
                'Pedro Gómez', 'Carmen Díaz', 'Jorge Silva', 'Rosa Morales', 'Miguel Torres']
    sucursales = ['1', '2', '3', '4', '5', '6', '7', '8']
    pesos_suc = [30, 22, 15, 10, 9, 7, 4, 3]
    cards, usos, n = [], [], 0

    def nueva(estado, monto, lote, benef, cedula, venta):
        nonlocal n
        n += 1
        emision = (venta or today) - timedelta(days=rng.randint(5, 40))
        return {
            'codigo': f'MOCK{n:05d}', 'estado': estado, 'monto': monto, 'lote': lote,
            'beneficiario': benef, 'cedula': cedula,
            'fecha_emision': emision.isoformat(),
            'fecha_venta': venta.isoformat() if venta else None,
            'fecha_vencimiento': ((venta or emision) + timedelta(days=365)).isoformat(),
        }

    def usar(card, prob):
        if card['fecha_venta'] is None or rng.random() > prob:
            return
        venta = date.fromisoformat(card['fecha_venta'])
        saldo = card['monto']
        dia = venta + timedelta(days=int(rng.expovariate(1 / 25)))
        while saldo > 1 and dia <= today:
            monto = round(min(saldo, rng.choice([saldo, saldo / 2, rng.uniform(5, saldo)])), 2)
            usos.append({'codigo': card['codigo'], 'fecha': f'{dia.isoformat()}T{rng.randint(9, 20):02d}:00:00',
                         'monto': monto, 'sucursal': rng.choices(sucursales, pesos_suc)[0]})
            saldo -= monto
            if rng.random() < 0.55:
                break
            dia += timedelta(days=rng.randint(3, 45))

    for nombre, rif, n_lotes, prob in empresas:
        for i in range(n_lotes):
            venta = today - timedelta(days=rng.randint(20, 420))
            lote = f'CORP-{rif[-3:]}-{venta:%y%m}-L{i + 1}'
            monto = rng.choice([50.0, 100.0, 100.0, 200.0])
            for _ in range(rng.randint(40, 140)):
                card = nueva('VENDIDA', monto, lote, nombre, rif, venta)
                cards.append(card)
                usar(card, prob)
    for _ in range(260):  # ventas individuales en tienda
        venta = today - timedelta(days=rng.randint(0, 420))
        card = nueva('ACTIVA', rng.choice([20.0, 50.0, 100.0]), f'POS-{venta:%y%m}',
                     rng.choice(personas), f'V-{rng.randint(5_000_000, 30_000_000)}', venta)
        cards.append(card)
        usar(card, 0.7)
    for i in range(180):  # generadas sin vender
        cards.append(nueva('GENERADA', 100.0, f'STOCK-{today:%y%m}-L{i // 60 + 1}', None, None, None))

    by_code = defaultdict(float)
    for u in usos:
        by_code[u['codigo']] += u['monto']
    for c in cards:
        if c['estado'] == 'VENDIDA' and by_code[c['codigo']] >= c['monto'] - 0.01:
            c['estado'] = 'AGOTADA'
    return cards, usos


# ── Cálculo de indicadores ───────────────────────────────

def _periodo_desde(periodo, today):
    value = PERIODOS.get(periodo)
    if value is None:
        return None
    if value == 'anio':
        return date(today.year, 1, 1)
    return today - timedelta(days=value)


def _month_keys(today, count=MONTHS):
    year, month, keys = today.year, today.month, []
    for _ in range(count):
        keys.append(f'{year}-{month:02d}')
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(keys))


def build(base, company_id=None, lote=None, periodo='todo'):
    """Indicadores para el filtro elegido. `lote` filtra por coincidencia parcial."""
    today = date.today()
    desde = _periodo_desde(periodo, today)

    # Empresas compradoras por lote (Logos de Empresas)
    empresa_por_lote = {}
    for cl in CompanyLote.objects.select_related('company'):
        empresa_por_lote[_key(cl.lote)] = cl.company
    company_lotes = None
    if company_id:
        company_lotes = {k for k, c in empresa_por_lote.items() if c.id == company_id}
    lote_text = _key(lote)

    cards = []
    for c in base['cards']:
        if company_lotes is not None and c['lote_key'] not in company_lotes:
            continue
        if lote_text and lote_text not in c['lote_key']:
            continue
        if desde and not ((c['venta'] or c['emision']) and (c['venta'] or c['emision']) >= desde):
            continue
        cards.append(c)

    keys = {c['key'] for c in cards}
    usos = [u for u in base['usos'] if u['key'] in keys]

    # Actividad por tarjeta
    act = defaultdict(lambda: {'consumo': 0.0, 'usos': 0, 'primer': None, 'ultimo': None})
    for u in usos:
        a = act[u['key']]
        a['consumo'] += u['monto']
        a['usos'] += 1
        if u['dia']:
            a['primer'] = u['dia'] if not a['primer'] or u['dia'] < a['primer'] else a['primer']
            a['ultimo'] = u['dia'] if not a['ultimo'] or u['dia'] > a['ultimo'] else a['ultimo']

    def vendida(c):
        return bool(c['venta']) or c['estado'] in SOLD_STATES

    def cliente_de(c):
        """Empresa (por su lote) o, si no, el beneficiario de la tarjeta."""
        company = empresa_por_lote.get(c['lote_key'])
        if company:
            return f'E{company.id}', company.name, company.rif
        cedula = str(c.get('cedula') or '').strip()
        nombre = str(c.get('beneficiario') or '').strip()
        if not cedula and not nombre:
            return None, None, None
        return f'C{_key(cedula or nombre)}', nombre or cedula, cedula

    vendidas = [c for c in cards if vendida(c)]
    monto_vendido = sum(c['monto'] for c in vendidas)
    consumido = sum(u['monto'] for u in usos)
    con_uso = [c for c in vendidas if act[c['key']]['usos'] > 0]
    agotadas = [c for c in vendidas if c['monto'] > 0 and act[c['key']]['consumo'] >= c['monto'] - 0.01]

    def saldo(c):
        return max(c['monto'] - act[c['key']]['consumo'], 0.0)

    dias_primer_uso = [
        (act[c['key']]['primer'] - c['venta']).days
        for c in con_uso if c['venta'] and act[c['key']]['primer'] and act[c['key']]['primer'] >= c['venta']
    ]
    sin_uso_viejas = sorted(
        (c for c in vendidas if act[c['key']]['usos'] == 0 and c['venta'] and (today - c['venta']).days > SIN_USO_DIAS),
        key=lambda c: c['venta']
    )
    por_vencer = sorted(
        (c for c in vendidas if c['vence'] and today <= c['vence'] <= today + timedelta(days=POR_VENCER_DIAS) and saldo(c) > 0),
        key=lambda c: c['vence']
    )
    vencidas_con_saldo = [c for c in vendidas if c['vence'] and c['vence'] < today and saldo(c) > 0]

    kpis = {
        'generadas': len(cards),
        'vendidas': len(vendidas),
        'sin_vender': len(cards) - len(vendidas),
        'monto_vendido': round(monto_vendido, 2),
        'con_uso': len(con_uso),
        'sin_uso': len(vendidas) - len(con_uso),
        'agotadas': len(agotadas),
        'pct_uso': round(len(con_uso) / len(vendidas) * 100, 1) if vendidas else 0,
        'consumido': round(consumido, 2),
        'pct_consumido': round(consumido / monto_vendido * 100, 1) if monto_vendido else 0,
        'saldo_pendiente': round(sum(saldo(c) for c in vendidas), 2),
        'usos': len(usos),
        'ticket_promedio': round(consumido / len(usos), 2) if usos else 0,
        'dias_primer_uso': round(median(dias_primer_uso)) if dias_primer_uso else None,
        'sin_uso_viejas': len(sin_uso_viejas),
        'por_vencer': len(por_vencer),
        'por_vencer_saldo': round(sum(saldo(c) for c in por_vencer), 2),
        'vencidas_con_saldo': len(vencidas_con_saldo),
        'vencidas_saldo': round(sum(saldo(c) for c in vencidas_con_saldo), 2),
    }

    # Series mensuales (últimos 12 meses)
    meses = _month_keys(today)
    consumo_mes = {m: {'mes': m, 'monto': 0.0, 'usos': 0} for m in meses}
    for u in usos:
        m = u['dia'].strftime('%Y-%m') if u['dia'] else None
        if m in consumo_mes:
            consumo_mes[m]['monto'] += u['monto']
            consumo_mes[m]['usos'] += 1
    ventas_mes = {m: {'mes': m, 'tarjetas': 0, 'monto': 0.0} for m in meses}
    for c in vendidas:
        m = c['venta'].strftime('%Y-%m') if c['venta'] else None
        if m in ventas_mes:
            ventas_mes[m]['tarjetas'] += 1
            ventas_mes[m]['monto'] += c['monto']

    # Ranking de clientes / empresas
    clientes = {}
    for c in vendidas:
        key, nombre, ident = cliente_de(c)
        if not key:
            continue
        row = clientes.setdefault(key, {'nombre': nombre, 'identificador': ident, 'tarjetas': 0, 'con_uso': 0,
                                        'monto': 0.0, 'consumido': 0.0, 'usos': 0, 'ultimo_uso': None})
        a = act[c['key']]
        row['tarjetas'] += 1
        row['con_uso'] += 1 if a['usos'] else 0
        row['monto'] += c['monto']
        row['consumido'] += a['consumo']
        row['usos'] += a['usos']
        if a['ultimo'] and (not row['ultimo_uso'] or a['ultimo'] > row['ultimo_uso']):
            row['ultimo_uso'] = a['ultimo']

    # Ranking de lotes
    lotes = {}
    for c in cards:
        if not c['lote_key']:
            continue
        company = empresa_por_lote.get(c['lote_key'])
        row = lotes.setdefault(c['lote_key'], {'lote': str(c.get('lote')).strip(), 'empresa': company.name if company else None,
                                               'tarjetas': 0, 'vendidas': 0, 'con_uso': 0, 'monto': 0.0, 'consumido': 0.0})
        a = act[c['key']]
        row['tarjetas'] += 1
        if vendida(c):
            row['vendidas'] += 1
            row['monto'] += c['monto']
        row['con_uso'] += 1 if a['usos'] else 0
        row['consumido'] += a['consumo']

    # Dónde se usan
    sucursales = defaultdict(lambda: {'usos': 0, 'monto': 0.0})
    for u in usos:
        sucursales[u['sucursal']]['usos'] += 1
        sucursales[u['sucursal']]['monto'] += u['monto']

    # Denominaciones
    denom = defaultdict(lambda: {'vendidas': 0, 'con_uso': 0})
    for c in vendidas:
        denom[c['monto']]['vendidas'] += 1
        denom[c['monto']]['con_uso'] += 1 if act[c['key']]['usos'] else 0

    estados = defaultdict(int)
    for c in cards:
        estados[c['estado'] or 'SIN ESTADO'] += 1

    def pct(part, total):
        return round(part / total * 100, 1) if total else 0

    def finish(row):
        for k in ('monto', 'consumido'):
            if k in row:
                row[k] = round(row[k], 2)
        base_count = row.get('vendidas', row.get('tarjetas', 0))
        row['pct_uso'] = pct(row['con_uso'], base_count)
        if 'monto' in row:
            row['pct_consumido'] = pct(row['consumido'], row['monto'])
        if row.get('ultimo_uso'):
            row['ultimo_uso'] = row['ultimo_uso'].isoformat()
        return row

    def card_row(c):
        _, nombre, ident = cliente_de(c)
        return {
            'codigo': c.get('codigo'), 'cliente': nombre, 'identificador': ident, 'lote': c.get('lote'),
            'monto': c['monto'], 'saldo': round(saldo(c), 2),
            'fecha_venta': c['venta'].isoformat() if c['venta'] else None,
            'vence': c['vence'].isoformat() if c['vence'] else None,
            'dias_sin_uso': (today - c['venta']).days if c['venta'] else None,
        }

    return {
        'actualizado': base['loaded_at'],
        'kpis': kpis,
        'consumo_mensual': [{**v, 'monto': round(v['monto'], 2)} for v in consumo_mes.values()],
        'ventas_mensuales': [{**v, 'monto': round(v['monto'], 2)} for v in ventas_mes.values()],
        'clientes': [finish(r) for r in sorted(clientes.values(), key=lambda r: r['consumido'], reverse=True)[:TOP]],
        'clientes_total': len(clientes),
        'lotes': [finish(r) for r in sorted(lotes.values(), key=lambda r: r['consumido'], reverse=True)[:TOP]],
        'lotes_total': len(lotes),
        'sucursales': sorted(
            ({'sucursal': s, 'usos': v['usos'], 'monto': round(v['monto'], 2)} for s, v in sucursales.items()),
            key=lambda r: r['monto'], reverse=True
        )[:TOP],
        # Las denominaciones más vendidas (en SAP hay muchas de centavos con 1 o 2 tarjetas)
        'denominaciones': sorted(
            ({'monto': m, 'vendidas': v['vendidas'], 'con_uso': v['con_uso'], 'pct_uso': pct(v['con_uso'], v['vendidas'])}
             for m, v in denom.items()),
            key=lambda r: (-r['vendidas'], r['monto'])
        )[:TOP],
        'denominaciones_total': len(denom),
        'estados': sorted(({'estado': e, 'tarjetas': n} for e, n in estados.items()), key=lambda r: r['tarjetas'], reverse=True),
        'sin_uso_viejas': [card_row(c) for c in sin_uso_viejas[:LIST_LIMIT]],
        'por_vencer': [card_row(c) for c in por_vencer[:LIST_LIMIT]],
        'empresas': [{'id': c.id, 'nombre': c.name} for c in CompanyLogo.objects.order_by('name')],
    }
