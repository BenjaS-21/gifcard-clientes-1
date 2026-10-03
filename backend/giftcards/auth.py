"""
auth.py — Sesiones del portal: cliente, caja y admin.

- Cliente: al hacer login por cédula/RIF recibe un token firmado con su
  cédula. Se envía en el header X-Client-Token y solo da acceso a sus tarjetas.
- Caja: el PIN se valida en el servidor (settings.CAJA_PIN) y devuelve un
  token firmado que se envía en el header X-Caja-Token.
- Admin: token de AdminToken en el header Authorization: Token <uuid>,
  con vencimiento (ADMIN_TOKEN_MAX_AGE).

Los tokens firmados usan SECRET_KEY: no se pueden falsificar sin ella.
"""
from datetime import timedelta
from functools import wraps

from django.core import signing
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from .models import AdminToken

CLIENT_TOKEN_MAX_AGE = 8 * 60 * 60     # 8 horas
CAJA_TOKEN_MAX_AGE = 12 * 60 * 60      # 12 horas (un turno)
ADMIN_TOKEN_MAX_AGE = timedelta(hours=12)

_CLIENT_SALT = 'giftcards.cliente'
_CAJA_SALT = 'giftcards.caja'


def _unauthorized(message, code):
    # `code` le permite al frontend saber qué sesión venció
    return Response({'error': message, 'code': code}, status=status.HTTP_401_UNAUTHORIZED)


# ── Cliente ──────────────────────────────────────────────

def make_client_token(cedula):
    return signing.dumps({'cedula': cedula}, salt=_CLIENT_SALT)


def get_client_cedula(request):
    """Cédula/RIF del cliente autenticado, o None si no hay token válido."""
    token = request.headers.get('X-Client-Token')
    if not token:
        return None
    try:
        return signing.loads(token, salt=_CLIENT_SALT, max_age=CLIENT_TOKEN_MAX_AGE).get('cedula')
    except signing.BadSignature:
        return None


# ── Caja ─────────────────────────────────────────────────

def make_caja_token():
    return signing.dumps({'caja': True}, salt=_CAJA_SALT)


def is_caja(request):
    token = request.headers.get('X-Caja-Token')
    if not token:
        return False
    try:
        return bool(signing.loads(token, salt=_CAJA_SALT, max_age=CAJA_TOKEN_MAX_AGE).get('caja'))
    except signing.BadSignature:
        return False


def require_caja(view_func):
    """Decorator: solo con sesión de caja (PIN validado)."""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not is_caja(request):
            return _unauthorized('Sesión de caja vencida. Ingresa el PIN de nuevo.', 'caja_auth')
        return view_func(self, request, *args, **kwargs)
    return wrapper


# ── Admin ────────────────────────────────────────────────

def get_admin_token(request):
    """AdminToken vigente del header Authorization: Token <uuid>, o None."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return None
    try:
        admin_token = AdminToken.objects.get(token=auth_header.split(' ', 1)[1].strip(), is_active=True)
    except (AdminToken.DoesNotExist, ValidationError, ValueError):
        return None
    if admin_token.created_at < timezone.now() - ADMIN_TOKEN_MAX_AGE:
        admin_token.is_active = False
        admin_token.save(update_fields=['is_active'])
        return None
    return admin_token


def require_admin_token(view_func):
    """Decorator: solo con token admin vigente."""
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        admin_token = get_admin_token(request)
        if not admin_token:
            return _unauthorized('Sesión de administrador vencida o inválida', 'admin_auth')
        request.admin_token = admin_token
        return view_func(self, request, *args, **kwargs)
    return wrapper
