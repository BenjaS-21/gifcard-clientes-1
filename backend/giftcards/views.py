"""
views.py — API Views para el portal de Gift Cards Damasco.

Endpoints conectados a SAP (SQL Server) vía pyodbc.
Si USE_MOCK_DATA=true en .env, usa datos de ejemplo.
"""

import hmac
import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from django.conf import settings

from .queries import (
    get_all_clients,
    get_client_detail,
    get_all_giftcards,
    get_client_giftcards,
    get_giftcard_detail,
    get_giftcard_by_number,
    get_giftcard_transactions,
    get_giftcard_transactions_by_code,
    get_dashboard_stats,
    get_recent_transactions,
    get_top_clients,
    get_lotes,
    activate_giftcard,
)
from .auth import (
    get_admin_token,
    get_client_cedula,
    make_caja_token,
    make_client_token,
    require_admin_token,
    require_caja,
)
from .models import AdminToken, CardTemplate, CompanyLogo, CompanyLote
from .utils import execute_query, execute_query_single, execute_query_paginated, execute_update


DEBIT_TYPES = {'USO', 'REDENCION', 'USO-PENDIENTE', 'CONSUMO'}


def adjust_saldo_with_pending(giftcard, transactions):
    """
    Calcula el saldo real de la gift card como:
        saldo_inicial - suma(débitos confirmados SAP + pendientes KLK)

    Esto es más robusto que `U_Saldo - pendientes` porque cubre casos
    donde SAP tiene U_Saldo inconsistente (p.ej. 0 sin movimiento que
    lo justifique en @DM_GC_TRX).
    """
    if not transactions:
        return giftcard
    debitos = sum(
        abs(float(tx.get('monto', 0) or 0))
        for tx in transactions
        if (tx.get('tipo', '') or '').upper() in DEBIT_TYPES
    )
    saldo_inicial = float(giftcard.get('saldo_inicial', 0) or 0)
    saldo_real = max(saldo_inicial - debitos, 0)
    return {**giftcard, 'saldo': saldo_real}


def normalize_lote(lote):
    """Normaliza un código de lote para compararlo (sin espacios, mayúsculas)."""
    return str(lote if lote is not None else '').strip().upper()


def normalize_id(value):
    """Normaliza una cédula o RIF para compararlos (sin guiones ni espacios, mayúsculas)."""
    return re.sub(r'[^0-9A-Z]', '', str(value or '').upper())


def find_company_by_rif(identificador):
    """Empresa compradora cuyo RIF coincide con el identificador, o None."""
    key = normalize_id(identificador)
    if not key:
        return None
    for company in CompanyLogo.objects.exclude(rif='').prefetch_related('lotes'):
        if normalize_id(company.rif) == key:
            return company
    return None


def add_card_activity(gc, transactions, owner_cedula):
    """
    Agrega datos de actividad a la gift card para los KPI del cliente:
    cantidad de usos, fecha del último uso y si ya fue entregada
    (está a nombre de alguien distinto a quien consulta).
    """
    debitos = [tx for tx in transactions if (tx.get('tipo', '') or '').upper() in DEBIT_TYPES]
    gc['num_usos'] = len(debitos)
    gc['ultimo_uso'] = max((str(tx['fecha']) for tx in debitos if tx.get('fecha')), default=None)
    gc['entregada'] = normalize_id(gc.get('cliente_cedula')) != normalize_id(owner_cedula)
    return gc


def card_belongs_to(giftcard, cedula):
    """
    True si la tarjeta es del cliente: está a su nombre o, si la cédula es el
    RIF de una empresa compradora, pertenece a uno de sus lotes.
    """
    if normalize_id(giftcard.get('cliente_cedula')) == normalize_id(cedula):
        return True
    company = find_company_by_rif(cedula)
    if not company:
        return False
    return normalize_lote(giftcard.get('lote')) in {normalize_lote(cl.lote) for cl in company.lotes.all()}


def client_auth_required():
    return Response(
        {'error': 'Tu sesión venció. Inicia sesión de nuevo.', 'code': 'client_auth'},
        status=status.HTTP_401_UNAUTHORIZED
    )


def card_not_found():
    return Response({'error': 'Gift Card no encontrada'}, status=status.HTTP_404_NOT_FOUND)


def attach_company_logos(request, giftcards):
    """
    Agrega 'empresa_logo' a cada gift card según la empresa dueña de su lote.
    Queda en None si el lote no pertenece a ninguna empresa con logo.
    """
    by_lote = {
        normalize_lote(cl.lote): cl.company
        for cl in CompanyLote.objects.select_related('company')
    }
    for gc in giftcards:
        company = by_lote.get(normalize_lote(gc.get('lote')))
        gc['empresa_logo'] = {
            'empresa': company.name,
            'url': request.build_absolute_uri(company.logo.url),
            'x': company.pos_x,
            'y': company.pos_y,
            'width': company.width,
        } if company and company.logo else None
    return giftcards


# ============================================================
# Datos mock para desarrollo (cuando USE_MOCK_DATA=true)
# ============================================================
MOCK_CLIENTS = [
    {"id": 1, "nombre": "María García López", "cedula": "V-12345678", "email": "maria@email.com", "telefono": "0414-1234567", "direccion": "Caracas, Venezuela", "fecha_registro": "2024-01-15", "total_giftcards": 3, "saldo_total": 450.00},
    {"id": 2, "nombre": "Carlos Rodríguez", "cedula": "V-23456789", "email": "carlos@email.com", "telefono": "0424-2345678", "direccion": "Valencia, Venezuela", "fecha_registro": "2024-02-20", "total_giftcards": 1, "saldo_total": 150.00},
    {"id": 3, "nombre": "Ana Martínez", "cedula": "V-34567890", "email": "ana@email.com", "telefono": "0412-3456789", "direccion": "Maracaibo, Venezuela", "fecha_registro": "2024-03-10", "total_giftcards": 2, "saldo_total": 300.00},
]

MOCK_GIFTCARDS = [
    {"id": 1, "numero_tarjeta": "DAM-2024-0001", "saldo": 150.00, "saldo_inicial": 200.00, "estado": "activa", "fecha_emision": "2024-01-15", "cliente_id": 1, "cliente_nombre": "María García López", "cliente_cedula": "V-12345678", "lote": "LOTE-001"},
    {"id": 2, "numero_tarjeta": "DAM-2024-0002", "saldo": 200.00, "saldo_inicial": 200.00, "estado": "activa", "fecha_emision": "2024-01-20", "cliente_id": 1, "cliente_nombre": "María García López", "cliente_cedula": "V-12345678", "lote": "LOTE-002"},
    {"id": 3, "numero_tarjeta": "DAM-2024-0003", "saldo": 0.00, "saldo_inicial": 100.00, "estado": "agotada", "fecha_emision": "2024-03-10", "cliente_id": 3, "cliente_nombre": "Ana Martínez", "cliente_cedula": "V-34567890", "lote": "LOTE-002"},
]

MOCK_TRANSACTIONS = [
    {"id": 1, "fecha": "2024-12-20 14:30:00", "tipo": "compra", "monto": -25.00, "descripcion": "Compra en tienda Damasco", "referencia": "TXN-001", "saldo_anterior": 175.00, "saldo_posterior": 150.00, "giftcard_id": 1, "numero_tarjeta": "DAM-2024-0001", "cliente_nombre": "María García López"},
]

USE_MOCK = settings.USE_MOCK_DATA


class DashboardStatsView(APIView):
    """GET /api/dashboard/stats/ — Estadísticas generales (admin)"""

    @require_admin_token
    def get(self, request):
        if USE_MOCK:
            active = sum(1 for gc in MOCK_GIFTCARDS if gc['estado'] == 'activa')
            return Response({
                'total_giftcards': len(MOCK_GIFTCARDS),
                'saldo_total': sum(gc['saldo'] for gc in MOCK_GIFTCARDS),
                'emision_total': sum(gc['saldo_inicial'] for gc in MOCK_GIFTCARDS),
                'activas': active, 'vencidas': 0, 'agotadas': 1, 'bloqueadas': 0,
                'total_clientes': len(MOCK_CLIENTS),
                'recent_transactions': MOCK_TRANSACTIONS[:5],
                'top_clients': MOCK_CLIENTS[:5],
            })

        try:
            query, params = get_dashboard_stats()
            stats = execute_query_single(query, params) or {}

            query_tx, params_tx = get_recent_transactions()
            recent = execute_query(query_tx, params_tx)

            query_top, params_top = get_top_clients()
            top = execute_query(query_top, params_top)

            # Contar clientes únicos
            client_count_q = """
                SELECT COUNT(DISTINCT T0."U_CedulaBenef") AS total
                FROM "@DM_GC_FICHA" T0
                WHERE T0."U_CedulaBenef" IS NOT NULL AND T0."U_CedulaBenef" != ''
            """
            client_count = execute_query_single(client_count_q) or {}

            data = {
                **stats,
                'total_clientes': client_count.get('total', 0),
                'recent_transactions': recent,
                'top_clients': top,
            }
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClientListView(APIView):
    """GET /api/clients/ — Lista de clientes (admin)"""

    @require_admin_token
    def get(self, request):
        search = request.query_params.get('search', None)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        if USE_MOCK:
            results = MOCK_CLIENTS
            if search:
                sl = search.lower()
                results = [c for c in results if sl in c['nombre'].lower() or sl in c['cedula'].lower()]
            total = len(results)
            start = (page - 1) * page_size
            return Response({
                'results': results[start:start + page_size],
                'page': page, 'page_size': page_size,
                'total': total, 'total_pages': (total + page_size - 1) // page_size,
            })

        try:
            query, params = get_all_clients(search)
            data = execute_query_paginated(query, params, page, page_size)
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo clientes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClientDetailView(APIView):
    """GET /api/clients/<cedula>/ — Detalle de un cliente por cédula (admin)"""

    @require_admin_token
    def get(self, request, client_id):
        if USE_MOCK:
            client = next((c for c in MOCK_CLIENTS if c['id'] == client_id or c['cedula'] == str(client_id)), None)
            if not client:
                return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            client_cards = [dict(gc) for gc in MOCK_GIFTCARDS if gc.get('cliente_cedula') == client.get('cedula')]
            attach_company_logos(request, client_cards)
            return Response({**client, 'giftcards': client_cards})

        try:
            # client_id puede ser cédula (string) o DocEntry
            cedula = str(client_id)
            query, params = get_client_detail(cedula)
            client = execute_query_single(query, params)

            if not client:
                return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

            query_gc, params_gc = get_client_giftcards(cedula)
            giftcards = execute_query(query_gc, params_gc)

            # Para cada gift card, cargar transacciones SAP+KLK y ajustar saldo
            for gc in giftcards:
                try:
                    q_tx, p_tx = get_giftcard_transactions_by_code(gc['numero_tarjeta'])
                    txns = execute_query(q_tx, p_tx)
                except Exception:
                    txns = []
                adjusted = adjust_saldo_with_pending(gc, txns)
                gc['saldo'] = adjusted['saldo']
                gc['transactions'] = txns

            # Recalcular saldo total del cliente con los saldos ajustados
            client['saldo_total'] = sum(float(gc.get('saldo', 0)) for gc in giftcards)

            attach_company_logos(request, giftcards)
            return Response({**client, 'giftcards': giftcards})
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo cliente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GiftCardListView(APIView):
    """
    GET /api/giftcards/ — Lista de gift cards.
    El cliente solo recibe las suyas (la cédula sale de su token);
    el admin puede listar todas o filtrar por cédula.
    """

    def get(self, request):
        search = request.query_params.get('search', None)
        card_status = request.query_params.get('status', None)
        cedula = request.query_params.get('cedula', None)
        if not get_admin_token(request):
            cedula = get_client_cedula(request)
            if not cedula:
                return client_auth_required()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        if USE_MOCK:
            results = MOCK_GIFTCARDS
            if cedula:
                company = find_company_by_rif(cedula)
                company_lotes = {normalize_lote(cl.lote) for cl in company.lotes.all()} if company else set()
                results = [
                    gc for gc in results
                    if gc.get('cliente_cedula', '').lower() == cedula.lower()
                    or normalize_lote(gc.get('lote')) in company_lotes
                ]
            if search:
                sl = search.lower()
                results = [gc for gc in results if sl in gc['numero_tarjeta'].lower() or sl in gc['cliente_nombre'].lower()]
            if card_status:
                results = [gc for gc in results if gc['estado'] == card_status]
            total = len(results)
            start = (page - 1) * page_size
            page_results = [dict(gc) for gc in results[start:start + page_size]]
            if cedula:
                for gc in page_results:
                    add_card_activity(gc, [t for t in MOCK_TRANSACTIONS if t['giftcard_id'] == gc['id']], cedula)
            attach_company_logos(request, page_results)
            return Response({
                'results': page_results,
                'page': page, 'page_size': page_size,
                'total': total, 'total_pages': (total + page_size - 1) // page_size,
            })

        try:
            # Si viene cédula, buscar gift cards del cliente.
            # Si es el RIF de una empresa compradora, incluye todas las
            # tarjetas de sus lotes (también las ya entregadas a empleados).
            if cedula:
                company = find_company_by_rif(cedula)
                company_lotes = [cl.lote for cl in company.lotes.all()] if company else None
                query, params = get_client_giftcards(cedula, company_lotes)
                data = execute_query_paginated(query, params, page, page_size)
                # Ajustar saldo de cada GC con transacciones pendientes de KLK
                for gc in data.get('results', []):
                    try:
                        q_tx, p_tx = get_giftcard_transactions_by_code(gc['numero_tarjeta'])
                        txns = execute_query(q_tx, p_tx)
                    except Exception:
                        txns = []
                    adjusted = adjust_saldo_with_pending(gc, txns)
                    gc['saldo'] = adjusted['saldo']
                    add_card_activity(gc, txns, cedula)
                attach_company_logos(request, data.get('results', []))
                return Response(data)

            query, params = get_all_giftcards(search, card_status)
            data = execute_query_paginated(query, params, page, page_size)
            attach_company_logos(request, data.get('results', []))
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo gift cards: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GiftCardDetailView(APIView):
    """GET /api/giftcards/<id>/ — Detalle de una gift card (del cliente o admin)"""

    def get(self, request, giftcard_id):
        is_admin = bool(get_admin_token(request))
        cedula = get_client_cedula(request)
        if not is_admin and not cedula:
            return client_auth_required()

        if USE_MOCK:
            gc = next((g for g in MOCK_GIFTCARDS if g['id'] == giftcard_id), None)
            if not gc or (not is_admin and not card_belongs_to(gc, cedula)):
                return card_not_found()
            txns = [t for t in MOCK_TRANSACTIONS if t['giftcard_id'] == giftcard_id]
            gc = attach_company_logos(request, [dict(gc)])[0]
            return Response({**gc, 'transactions': txns})

        try:
            query, params = get_giftcard_detail(giftcard_id)
            giftcard = execute_query_single(query, params)

            if not giftcard or (not is_admin and not card_belongs_to(giftcard, cedula)):
                return card_not_found()

            # Obtener transacciones SAP + KLK usando el código de tarjeta
            try:
                query_tx, params_tx = get_giftcard_transactions_by_code(giftcard['numero_tarjeta'])
                transactions = execute_query(query_tx, params_tx)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error obteniendo transacciones para GC {giftcard_id}: {e}")
                transactions = []

            # Ajustar saldo con transacciones pendientes de KLK
            giftcard = adjust_saldo_with_pending(giftcard, transactions)
            attach_company_logos(request, [giftcard])
            return Response({**giftcard, 'transactions': transactions})
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo gift card: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GiftCardTransactionsView(APIView):
    """GET /api/giftcards/<id>/transactions/ — Movimientos de una gift card (del cliente o admin)"""

    def get(self, request, giftcard_id):
        is_admin = bool(get_admin_token(request))
        cedula = get_client_cedula(request)
        if not is_admin and not cedula:
            return client_auth_required()

        if USE_MOCK:
            gc = next((g for g in MOCK_GIFTCARDS if g['id'] == giftcard_id), None)
            if not gc or (not is_admin and not card_belongs_to(gc, cedula)):
                return card_not_found()
            txns = [t for t in MOCK_TRANSACTIONS if t['giftcard_id'] == giftcard_id]
            return Response({'results': txns})

        try:
            # Obtener el código de la tarjeta para incluir transacciones KLK
            query_gc, params_gc = get_giftcard_detail(giftcard_id)
            giftcard = execute_query_single(query_gc, params_gc)
            if not giftcard or (not is_admin and not card_belongs_to(giftcard, cedula)):
                return card_not_found()
            query, params = get_giftcard_transactions_by_code(giftcard['numero_tarjeta'])
            transactions = execute_query(query, params)
            return Response({'results': transactions})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error obteniendo transacciones para GC {giftcard_id}: {e}")
            return Response({'results': [], 'error': str(e)})


class GiftCardLookupView(APIView):
    """GET /api/giftcards/lookup/?numero=XXX — Buscar gift card por número (caja)"""

    @require_caja
    def get(self, request):
        numero = request.query_params.get('numero', '').strip()

        if not numero:
            return Response(
                {'error': 'El número de tarjeta es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if USE_MOCK:
            gc = next(
                (g for g in MOCK_GIFTCARDS if g['numero_tarjeta'].lower() == numero.lower()),
                None
            )
            if not gc:
                return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            txns = [t for t in MOCK_TRANSACTIONS if t['giftcard_id'] == gc['id']]
            client = next((c for c in MOCK_CLIENTS if c.get('cedula') == gc.get('cliente_cedula')), None)
            gc = attach_company_logos(request, [dict(gc)])[0]
            return Response({
                **gc, 'transactions': txns,
                'cliente_email': client.get('email', '') if client else '',
                'cliente_telefono': client.get('telefono', '') if client else '',
            })

        try:
            query, params = get_giftcard_by_number(numero)
            giftcard = execute_query_single(query, params)

            if not giftcard:
                return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)

            # Transacciones SAP + KLK usando código de tarjeta
            try:
                query_tx, params_tx = get_giftcard_transactions_by_code(numero)
                transactions = execute_query(query_tx, params_tx)
            except Exception:
                transactions = []

            # Ajustar saldo con transacciones pendientes de KLK
            giftcard = adjust_saldo_with_pending(giftcard, transactions)
            attach_company_logos(request, [giftcard])
            return Response({**giftcard, 'transactions': transactions})
        except Exception as e:
            return Response(
                {'error': f'Error buscando tarjeta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActivateGiftCardView(APIView):
    """POST /api/giftcards/activate/ — Activar gift card (nombre + cédula) (caja)"""

    @require_caja
    def post(self, request):
        codigo = (request.data.get('codigo') or '').strip()
        nombre = (request.data.get('nombre') or '').strip()
        cedula = (request.data.get('cedula') or '').strip()

        if not codigo:
            return Response(
                {'error': 'El código de tarjeta es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not nombre:
            return Response(
                {'error': 'El nombre del beneficiario es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not cedula:
            return Response(
                {'error': 'La cédula del beneficiario es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if USE_MOCK:
            return Response({'message': 'Tarjeta activada (mock)', 'estado': 'ACTIVA'})

        try:
            # Buscar la tarjeta por código para obtener DocEntry
            query_find, params_find = get_giftcard_by_number(codigo)
            giftcard = execute_query_single(query_find, params_find)

            if not giftcard:
                return Response(
                    {'error': 'Tarjeta no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Verificar que no esté ya activa
            estado_actual = (giftcard.get('estado') or '').strip().upper()
            if estado_actual == 'ACTIVA':
                return Response(
                    {'error': 'Esta tarjeta ya se encuentra activa'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            doc_entry = giftcard['id']

            query_update, params_update = activate_giftcard(doc_entry, nombre, cedula)
            rows = execute_update(query_update, params_update)

            if rows == 0:
                return Response(
                    {'error': 'No se pudo activar la tarjeta. Verifique el estado actual.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'message': f'Tarjeta {codigo} activada exitosamente',
                'estado': 'ACTIVA',
                'beneficiario': nombre,
                'cedula': cedula,
            })
        except Exception as e:
            return Response(
                {'error': f'Error activando tarjeta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def client_login_response(client):
    """Respuesta de login de cliente con su token de sesión."""
    return Response({'tipo': 'cliente', 'cliente': client, 'token': make_client_token(client['cedula'])})


class AuthLoginView(APIView):
    """POST /api/auth/login/ — Login por cédula o número de tarjeta"""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        identificador = (request.data.get('identificador') or '').strip()

        if not identificador:
            return Response(
                {'error': 'Ingresa tu cédula o número de tarjeta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if USE_MOCK:
            if identificador.upper().startswith('DAM-'):
                gc = next(
                    (g for g in MOCK_GIFTCARDS if g['numero_tarjeta'].lower() == identificador.lower()),
                    None
                )
                if not gc:
                    return Response({'error': 'Tarjeta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
                return Response({'tipo': 'tarjeta', 'numero_tarjeta': gc['numero_tarjeta']})

            client = next(
                (c for c in MOCK_CLIENTS if c['cedula'].lower() == identificador.lower()),
                None
            )
            if not client:
                company = find_company_by_rif(identificador)
                if company:
                    return client_login_response({'cedula': identificador, 'nombre': company.name})
                return Response({'error': 'Cédula no registrada'}, status=status.HTTP_404_NOT_FOUND)
            return client_login_response(client)

        try:
            # Detectar si es un número de tarjeta o cédula
            # Buscar primero como tarjeta
            query_gc, params_gc = get_giftcard_by_number(identificador)
            giftcard = execute_query_single(query_gc, params_gc)

            if giftcard:
                return Response({
                    'tipo': 'tarjeta',
                    'numero_tarjeta': giftcard['numero_tarjeta']
                })

            # Buscar como cédula
            query_cl, params_cl = get_client_detail(identificador)
            client = execute_query_single(query_cl, params_cl)

            if client:
                return client_login_response(client)

            # Empresa compradora que ya entregó todas sus tarjetas
            company = find_company_by_rif(identificador)
            if company:
                return client_login_response({'cedula': identificador, 'nombre': company.name})

            return Response(
                {'error': 'No se encontró tarjeta ni cliente con ese identificador'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al verificar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CajaLoginView(APIView):
    """POST /api/caja/login/ — Valida el PIN de caja y devuelve un token de sesión."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        pin = str(request.data.get('pin') or '')
        if not settings.CAJA_PIN:
            return Response(
                {'error': 'El PIN de caja no está configurado en el servidor (CAJA_PIN).'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if not pin or not hmac.compare_digest(pin.encode(), settings.CAJA_PIN.encode()):
            return Response({'error': 'PIN incorrecto'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'token': make_caja_token()})


class AuthLogoutView(APIView):
    """POST /api/auth/logout/ — Cerrar sesión"""

    def post(self, request):
        return Response({'message': 'Sesión cerrada exitosamente'})


class AuthCheckView(APIView):
    """GET /api/auth/check/ — Verificar sesión activa"""

    def get(self, request):
        return Response({'authenticated': False})


# ============================================================
# ADMIN — Panel de Templates de Gift Card
# ============================================================
from django.contrib.auth import authenticate


class AdminLoginView(APIView):
    """POST /api/admin/login/ — Login con credenciales Django, devuelve token."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'Usuario y contraseña requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_staff:
            return Response(
                {'error': 'No tienes permisos de administrador'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Desactivar tokens anteriores de este usuario
        AdminToken.objects.filter(label=username, is_active=True).update(is_active=False)

        # Crear nuevo token
        admin_token = AdminToken.objects.create(label=username)

        return Response({
            'token': str(admin_token.token),
            'user': username,
            'message': 'Autenticación exitosa'
        })


class ActiveCardTemplateView(APIView):
    """GET /api/card-templates/active/ — Devuelve la URL de la imagen activa (público)."""

    def get(self, request):
        try:
            template = CardTemplate.objects.get(is_active=True)
            image_url = request.build_absolute_uri(template.image.url) if template.image else None
            return Response({
                'id': template.id,
                'name': template.name,
                'image_url': image_url,
                'html_code': template.html_code or None,
                'type': 'html' if template.html_code else 'image',
                'active': True
            })
        except CardTemplate.DoesNotExist:
            return Response({
                'active': False,
                'image_url': None,
                'html_code': None,
                'message': 'No hay template activo, usar imagen por defecto'
            })


class CardTemplateListView(APIView):
    """
    GET  /api/admin/templates/ — Lista todos los templates
    POST /api/admin/templates/ — Subir nuevo template (multipart)
    """

    @require_admin_token
    def get(self, request):
        templates = CardTemplate.objects.all()
        data = []
        for t in templates:
            data.append({
                'id': t.id,
                'name': t.name,
                'image_url': request.build_absolute_uri(t.image.url) if t.image else None,
                'html_code': t.html_code or None,
                'type': 'html' if t.html_code else 'image',
                'is_active': t.is_active,
                'created_at': t.created_at.isoformat(),
            })
        return Response(data)

    @require_admin_token
    def post(self, request):
        name = request.data.get('name', '').strip()
        image = request.FILES.get('image')

        if not name:
            return Response({'error': 'El nombre es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not image:
            return Response({'error': 'La imagen es requerida'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que sea imagen
        allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
        if image.content_type not in allowed:
            return Response(
                {'error': f'Tipo de archivo no permitido: {image.content_type}. Use JPG, PNG, WebP o SVG.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        template = CardTemplate.objects.create(name=name, image=image)

        return Response({
            'id': template.id,
            'name': template.name,
            'image_url': request.build_absolute_uri(template.image.url),
            'is_active': template.is_active,
            'created_at': template.created_at.isoformat(),
            'message': 'Template creado exitosamente'
        }, status=status.HTTP_201_CREATED)


class CardTemplateActivateView(APIView):
    """POST /api/admin/templates/<id>/activate/ — Activar un template."""

    @require_admin_token
    def post(self, request, template_id):
        try:
            template = CardTemplate.objects.get(pk=template_id)
        except CardTemplate.DoesNotExist:
            return Response({'error': 'Template no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        template.activate()

        return Response({
            'id': template.id,
            'name': template.name,
            'is_active': True,
            'message': f'Template "{template.name}" activado'
        })


class CardTemplateDeleteView(APIView):
    """DELETE /api/admin/templates/<id>/ — Eliminar template."""

    @require_admin_token
    def delete(self, request, template_id):
        try:
            template = CardTemplate.objects.get(pk=template_id)
        except CardTemplate.DoesNotExist:
            return Response({'error': 'Template no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if template.is_active:
            return Response(
                {'error': 'No puedes eliminar el template activo. Activa otro primero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borrar archivo de disco
        if template.image:
            template.image.delete(save=False)

        template.delete()
        return Response({'message': 'Template eliminado'})


class SaveDesignView(APIView):
    """POST /api/admin/designs/ — Guardar diseño HTML/CSS generado por IA."""

    @require_admin_token
    def post(self, request):
        name = request.data.get('name', '').strip()
        html_code = request.data.get('html_code', '').strip()

        if not name:
            return Response({'error': 'El nombre es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not html_code:
            return Response({'error': 'El código HTML es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        template = CardTemplate.objects.create(name=name, html_code=html_code)

        return Response({
            'id': template.id,
            'name': template.name,
            'html_code': template.html_code,
            'is_active': template.is_active,
            'created_at': template.created_at.isoformat(),
            'message': 'Diseño guardado exitosamente'
        }, status=status.HTTP_201_CREATED)


# ============================================================
# ADMIN — Logos de empresas compradoras (por lote)
# ============================================================
import json
import logging
from django.db import transaction

LOGO_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
LOGO_MAX_BYTES = 5 * 1024 * 1024


def _company_to_dict(request, company):
    return {
        'id': company.id,
        'name': company.name,
        'rif': company.rif,
        'logo_url': request.build_absolute_uri(company.logo.url) if company.logo else None,
        'pos_x': company.pos_x,
        'pos_y': company.pos_y,
        'width': company.width,
        'lotes': [cl.lote for cl in company.lotes.all()],
        'created_at': company.created_at.isoformat(),
    }


def _parse_lotes(raw):
    """Acepta una lista, un JSON de lista o texto separado por comas / saltos de línea."""
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            raw = parsed if isinstance(parsed, list) else re.split(r'[,;\n]', raw)
        except ValueError:
            raw = re.split(r'[,;\n]', raw)
    lotes, seen = [], set()
    for item in raw or []:
        lote = str(item).strip()
        key = normalize_lote(lote)
        if key and key not in seen:
            seen.add(key)
            lotes.append(lote)
    return lotes


def _parse_percent(value, default, low, high):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number != number:  # NaN
        return default
    return max(low, min(high, number))


def _validate_logo_file(logo):
    """Devuelve un mensaje de error si el archivo no es un logo válido."""
    if logo.content_type not in LOGO_CONTENT_TYPES:
        return f'Tipo de archivo no permitido: {logo.content_type}. Use PNG, JPG, WebP o SVG.'
    if logo.size > LOGO_MAX_BYTES:
        return 'El logo no puede pesar más de 5 MB.'
    return None


def _delete_logo_file(storage, name):
    """Borra el archivo del logo; si está en uso (Windows) lo deja huérfano en disco."""
    try:
        storage.delete(name)
    except OSError as e:
        logging.getLogger(__name__).warning(f"No se pudo borrar el logo {name}: {e}")


def _lotes_conflict(lotes, exclude_company=None):
    """Devuelve un mensaje de error si algún lote ya pertenece a otra empresa."""
    wanted = {normalize_lote(lote) for lote in lotes}
    taken = CompanyLote.objects.select_related('company')
    if exclude_company is not None:
        taken = taken.exclude(company=exclude_company)
    for cl in taken:
        if normalize_lote(cl.lote) in wanted:
            return f'El lote "{cl.lote}" ya está asignado a {cl.company.name}.'
    return None


class CompanyLogoListView(APIView):
    """
    GET  /api/admin/companies/ — Lista de empresas con su logo y lotes
    POST /api/admin/companies/ — Crear empresa con logo (multipart)
    """

    @require_admin_token
    def get(self, request):
        companies = CompanyLogo.objects.prefetch_related('lotes')
        return Response([_company_to_dict(request, c) for c in companies])

    @require_admin_token
    def post(self, request):
        name = (request.data.get('name') or '').strip()
        logo = request.FILES.get('logo')
        lotes = _parse_lotes(request.data.get('lotes'))

        if not name:
            return Response({'error': 'El nombre de la empresa es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        if not logo:
            return Response({'error': 'El logo es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        error = _validate_logo_file(logo) or _lotes_conflict(lotes)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            company = CompanyLogo.objects.create(
                name=name,
                rif=(request.data.get('rif') or '').strip(),
                logo=logo,
                pos_x=_parse_percent(request.data.get('pos_x'), 50, 0, 100),
                pos_y=_parse_percent(request.data.get('pos_y'), 50, 0, 100),
                width=_parse_percent(request.data.get('width'), 25, 5, 100),
            )
            CompanyLote.objects.bulk_create([CompanyLote(company=company, lote=lote) for lote in lotes])

        return Response(_company_to_dict(request, company), status=status.HTTP_201_CREATED)


class CompanyLogoDetailView(APIView):
    """
    PATCH  /api/admin/companies/<id>/ — Actualizar nombre, logo, lotes, posición o tamaño
    DELETE /api/admin/companies/<id>/ — Eliminar empresa y su logo
    """

    @require_admin_token
    def patch(self, request, company_id):
        try:
            company = CompanyLogo.objects.get(pk=company_id)
        except CompanyLogo.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        logo = request.FILES.get('logo')
        lotes = _parse_lotes(request.data.get('lotes')) if 'lotes' in request.data else None

        if 'name' in request.data and not (request.data.get('name') or '').strip():
            return Response({'error': 'El nombre de la empresa es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        error = (logo and _validate_logo_file(logo)) or (lotes is not None and _lotes_conflict(lotes, company))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        old_logo_name = company.logo.name if logo and company.logo else None
        storage = company.logo.storage

        with transaction.atomic():
            if 'name' in request.data:
                company.name = request.data.get('name').strip()
            if 'rif' in request.data:
                company.rif = (request.data.get('rif') or '').strip()
            if logo:
                company.logo = logo
            company.pos_x = _parse_percent(request.data.get('pos_x'), company.pos_x, 0, 100)
            company.pos_y = _parse_percent(request.data.get('pos_y'), company.pos_y, 0, 100)
            company.width = _parse_percent(request.data.get('width'), company.width, 5, 100)
            company.save()
            if lotes is not None:
                company.lotes.all().delete()
                CompanyLote.objects.bulk_create([CompanyLote(company=company, lote=lote) for lote in lotes])

        # Borrar de disco el logo anterior
        if old_logo_name and old_logo_name != company.logo.name:
            _delete_logo_file(storage, old_logo_name)

        return Response(_company_to_dict(request, company))

    @require_admin_token
    def delete(self, request, company_id):
        try:
            company = CompanyLogo.objects.get(pk=company_id)
        except CompanyLogo.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        logo_name = company.logo.name
        storage = company.logo.storage
        company.delete()

        # Borrar archivo de disco
        if logo_name:
            _delete_logo_file(storage, logo_name)

        return Response({'message': 'Empresa eliminada'})


class LoteListView(APIView):
    """GET /api/admin/lotes/ — Lotes existentes en SAP, para asociarlos a una empresa."""

    @require_admin_token
    def get(self, request):
        if USE_MOCK:
            counts = {}
            for gc in MOCK_GIFTCARDS:
                if gc.get('lote'):
                    counts[gc['lote']] = counts.get(gc['lote'], 0) + 1
            return Response([{'lote': lote, 'total_giftcards': n} for lote, n in sorted(counts.items())])

        try:
            query, params = get_lotes()
            return Response(execute_query(query, params))
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo lotes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
