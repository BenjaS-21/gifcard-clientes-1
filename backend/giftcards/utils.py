"""
utils.py — Helpers para ejecutar queries SQL contra SAP (SQL Server vía pyodbc).

Uso:
    from giftcards.utils import execute_query, execute_query_single

    # Retorna lista de diccionarios
    results = execute_query("SELECT * FROM tabla WHERE id = ?", [1])

    # Retorna un solo diccionario o None
    result = execute_query_single("SELECT * FROM tabla WHERE id = ?", [1])

NOTA: Los queries usan '?' como placeholder (estándar pyodbc/ODBC).
"""

import re
import logging
from decimal import Decimal
from datetime import datetime, date

import pyodbc
from django.conf import settings

logger = logging.getLogger(__name__)


def get_sap_connection():
    """Crea una conexión nueva a la BD SAP (SQL Server)."""
    sap = settings.SAP_DB
    conn_str = (
        f"DRIVER={{{sap['DRIVER']}}};"
        f"SERVER={sap['HOST']};"
        f"DATABASE={sap['NAME']};"
        f"UID={sap['USER']};"
        f"PWD={sap['PASSWORD']};"
        "TrustServerCertificate=yes;"
        "Connection Timeout=10;"
    )
    return pyodbc.connect(conn_str)


def _serialize_value(val):
    """Convierte tipos no serializables a JSON-friendly."""
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='replace')
    return val


def _serialize_row(row_dict):
    """Serializa todos los valores de un diccionario."""
    return {k: _serialize_value(v) for k, v in row_dict.items()}


def execute_query(query, params=None):
    """
    Ejecuta un query SQL contra SAP y retorna una lista de diccionarios.

    Args:
        query (str): Query SQL con placeholders ?
        params (list): Lista de parámetros para el query

    Returns:
        list[dict]: Lista de diccionarios con los resultados
    """
    params = params or []

    try:
        conn = get_sap_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [
            _serialize_row(dict(zip(columns, row)))
            for row in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error ejecutando query SAP: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise


def execute_query_single(query, params=None):
    """
    Ejecuta un query SQL y retorna un solo diccionario (la primera fila).

    Returns:
        dict | None: Diccionario con el resultado o None si no hay resultados
    """
    results = execute_query(query, params)
    return results[0] if results else None


def execute_query_paginated(query, params=None, page=1, page_size=20):
    """
    Ejecuta un query SQL con paginación (SQL Server OFFSET/FETCH).

    El query DEBE contener ORDER BY para que OFFSET/FETCH funcione.

    Returns:
        dict: { 'results': [...], 'page': int, 'page_size': int, 'total': int }
    """
    params = params or []

    try:
        # 1. Obtener total (quitamos ORDER BY para que SQL Server acepte el subquery)
        count_base = re.sub(
            r'\bORDER\s+BY\b.*$', '', query,
            flags=re.IGNORECASE | re.DOTALL
        )
        count_query = f"SELECT COUNT(*) AS total FROM ({count_base}) AS count_sq"
        total_result = execute_query_single(count_query, list(params))
        total = total_result['total'] if total_result else 0

        # 2. Query paginado con OFFSET/FETCH (SQL Server)
        offset = (page - 1) * page_size
        paginated_query = f"{query} OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        paginated_params = list(params) + [offset, page_size]

        results = execute_query(paginated_query, paginated_params)

        return {
            'results': results,
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': (total + page_size - 1) // page_size if total > 0 else 0,
        }
    except Exception as e:
        logger.error(f"Error en query paginado: {e}")
        raise


def execute_update(query, params=None):
    """
    Ejecuta un query de escritura (INSERT, UPDATE, DELETE) contra SAP.

    Args:
        query (str): Query SQL con placeholders ?
        params (list): Lista de parámetros para el query

    Returns:
        int: Número de filas afectadas
    """
    params = params or []

    try:
        conn = get_sap_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return rows_affected
    except Exception as e:
        logger.error(f"Error ejecutando UPDATE SAP: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise
