"""
views.py — API Views para el portal de Gift Cards Damasco.

Endpoints conectados a SAP (SQL Server) vía pyodbc.
Si USE_MOCK_DATA=true en .env, usa datos de ejemplo.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
    activate_giftcard,
)
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


# ============================================================
# Datos mock para desarrollo (cuando USE_MOCK_DATA=true)
# ============================================================
MOCK_CLIENTS = [
    {"id": 1, "nombre": "María García López", "cedula": "V-12345678", "email": "maria@email.com", "telefono": "0414-1234567", "direccion": "Caracas, Venezuela", "fecha_registro": "2024-01-15", "total_giftcards": 3, "saldo_total": 450.00},
    {"id": 2, "nombre": "Carlos Rodríguez", "cedula": "V-23456789", "email": "carlos@email.com", "telefono": "0424-2345678", "direccion": "Valencia, Venezuela", "fecha_registro": "2024-02-20", "total_giftcards": 1, "saldo_total": 150.00},
    {"id": 3, "nombre": "Ana Martínez", "cedula": "V-34567890", "email": "ana@email.com", "telefono": "0412-3456789", "direccion": "Maracaibo, Venezuela", "fecha_registro": "2024-03-10", "total_giftcards": 2, "saldo_total": 300.00},
]

MOCK_GIFTCARDS = [
    {"id": 1, "numero_tarjeta": "DAM-2024-0001", "saldo": 150.00, "saldo_inicial": 200.00, "estado": "activa", "fecha_emision": "2024-01-15", "cliente_id": 1, "cliente_nombre": "María García López", "cliente_cedula": "V-12345678"},
    {"id": 2, "numero_tarjeta": "DAM-2024-0002", "saldo": 200.00, "saldo_inicial": 200.00, "estado": "activa", "fecha_emision": "2024-01-20", "cliente_id": 1, "cliente_nombre": "María García López", "cliente_cedula": "V-12345678"},
    {"id": 3, "numero_tarjeta": "DAM-2024-0003", "saldo": 0.00, "saldo_inicial": 100.00, "estado": "agotada", "fecha_emision": "2024-03-10", "cliente_id": 3, "cliente_nombre": "Ana Martínez", "cliente_cedula": "V-34567890"},
]

MOCK_TRANSACTIONS = [
    {"id": 1, "fecha": "2024-12-20 14:30:00", "tipo": "compra", "monto": -25.00, "descripcion": "Compra en tienda Damasco", "referencia": "TXN-001", "saldo_anterior": 175.00, "saldo_posterior": 150.00, "giftcard_id": 1, "numero_tarjeta": "DAM-2024-0001", "cliente_nombre": "María García López"},
]

USE_MOCK = settings.USE_MOCK_DATA


class DashboardStatsView(APIView):
    """GET /api/dashboard/stats/ — Estadísticas generales"""

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
    """GET /api/clients/ — Lista de clientes"""

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
    """GET /api/clients/<cedula>/ — Detalle de un cliente por cédula"""

    def get(self, request, client_id):
        if USE_MOCK:
            client = next((c for c in MOCK_CLIENTS if c['id'] == client_id or c['cedula'] == str(client_id)), None)
            if not client:
                return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            client_cards = [gc for gc in MOCK_GIFTCARDS if gc.get('cliente_cedula') == client.get('cedula')]
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

            return Response({**client, 'giftcards': giftcards})
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo cliente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GiftCardListView(APIView):
    """GET /api/giftcards/ — Lista de gift cards"""

    def get(self, request):
        search = request.query_params.get('search', None)
        card_status = request.query_params.get('status', None)
        cedula = request.query_params.get('cedula', None)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        if USE_MOCK:
            results = MOCK_GIFTCARDS
            if cedula:
                results = [gc for gc in results if gc.get('cliente_cedula', '').lower() == cedula.lower()]
            if search:
                sl = search.lower()
                results = [gc for gc in results if sl in gc['numero_tarjeta'].lower() or sl in gc['cliente_nombre'].lower()]
            if card_status:
                results = [gc for gc in results if gc['estado'] == card_status]
            total = len(results)
            start = (page - 1) * page_size
            return Response({
                'results': results[start:start + page_size],
                'page': page, 'page_size': page_size,
                'total': total, 'total_pages': (total + page_size - 1) // page_size,
            })

        try:
            # Si viene cédula, buscar gift cards del cliente
            if cedula:
                query, params = get_client_giftcards(cedula)
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
                return Response(data)

            query, params = get_all_giftcards(search, card_status)
            data = execute_query_paginated(query, params, page, page_size)
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo gift cards: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GiftCardDetailView(APIView):
    """GET /api/giftcards/<id>/ — Detalle de una gift card"""

    def get(self, request, giftcard_id):
        if USE_MOCK:
            gc = next((g for g in MOCK_GIFTCARDS if g['id'] == giftcard_id), None)
            if not gc:
                return Response({'error': 'Gift Card no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            txns = [t for t in MOCK_TRANSACTIONS if t['giftcard_id'] == giftcard_id]
            return Response({**gc, 'transactions': txns})

        try:
            query, params = get_giftcard_detail(giftcard_id)
            giftcard = execute_query_single(query, params)

            if not giftcard:
                return Response({'error': 'Gift Card no encontrada'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({**giftcard, 'transactions': transactions})
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo gift card: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GiftCardTransactionsView(APIView):
    """GET /api/giftcards/<id>/transactions/ — Movimientos de una gift card"""

    def get(self, request, giftcard_id):
        if USE_MOCK:
            txns = [t for t in MOCK_TRANSACTIONS if t['giftcard_id'] == giftcard_id]
            return Response({'results': txns})

        try:
            # Obtener el código de la tarjeta para incluir transacciones KLK
            query_gc, params_gc = get_giftcard_detail(giftcard_id)
            giftcard = execute_query_single(query_gc, params_gc)
            if not giftcard:
                return Response({'results': [], 'error': 'Gift Card no encontrada'})
            query, params = get_giftcard_transactions_by_code(giftcard['numero_tarjeta'])
            transactions = execute_query(query, params)
            return Response({'results': transactions})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error obteniendo transacciones para GC {giftcard_id}: {e}")
            return Response({'results': [], 'error': str(e)})


class GiftCardLookupView(APIView):
    """GET /api/giftcards/lookup/?numero=XXX — Buscar gift card por número"""

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
            return Response({**giftcard, 'transactions': transactions})
        except Exception as e:
            return Response(
                {'error': f'Error buscando tarjeta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActivateGiftCardView(APIView):
    """POST /api/giftcards/activate/ — Activar gift card (nombre + cédula)"""

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


class AuthLoginView(APIView):
    """POST /api/auth/login/ — Login por cédula o número de tarjeta"""

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
                return Response({'error': 'Cédula no registrada'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'tipo': 'cliente', 'cliente': client})

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
                return Response({'tipo': 'cliente', 'cliente': client})

            return Response(
                {'error': 'No se encontró tarjeta ni cliente con ese identificador'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al verificar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
from .models import CardTemplate, AdminToken
from functools import wraps


def require_admin_token(view_func):
    """Decorator que valida el token admin en Authorization header o query param."""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        # Buscar token en header: Authorization: Token <uuid>
        auth_header = request.headers.get('Authorization', '')
        token_str = None
        if auth_header.startswith('Token '):
            token_str = auth_header.split(' ', 1)[1]
        # Fallback: query param ?token=<uuid>
        if not token_str:
            token_str = request.query_params.get('token')
        if not token_str:
            return Response({'error': 'Token requerido'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            admin_token = AdminToken.objects.get(token=token_str, is_active=True)
        except AdminToken.DoesNotExist:
            return Response({'error': 'Token inválido o expirado'}, status=status.HTTP_401_UNAUTHORIZED)
        request.admin_token = admin_token
        return view_func(self, request, *args, **kwargs)
    return wrapper


class AdminLoginView(APIView):
    """POST /api/admin/login/ — Login con credenciales Django, devuelve token."""

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
