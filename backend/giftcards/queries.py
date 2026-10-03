"""
queries.py — Queries SQL contra SAP (DAMASCO_PRODUCTIVA).

Tablas principales:
    @DM_GC_FICHA      — Ficha de Gift Card (UDO master)
    @DM_GC_TRX         — Transacciones (child table de FICHA, DocEntry+LineId)
    @DM_GC_PRODUCTOS   — Catálogo de productos/denominaciones
    @DM_GC_CANALES     — Canales de venta
    @DM_GC_CFG         — Configuración general

Tablas externas (cross-database):
    [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROHDR]   — Cabecera de cobros POS
    [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROLINE]   — Líneas de cobros POS

Estados conocidos: NULL, GENERADA, VENDIDA
Tipos de transacción: VENTA, GENERACION, RECARGA, CONSUMO, USO-PENDIENTE, etc.

NOTA: Todos los queries usan '?' como placeholder (pyodbc/ODBC estándar).
"""


# ============================================================
# QUERIES DE GIFT CARDS (@DM_GC_FICHA)
# ============================================================

def get_all_giftcards(search=None, status=None, lote=None):
    """Obtener todas las gift cards con filtros opcionales."""
    query = """
        SELECT
            T0."DocEntry"            AS id,
            T0."U_Codigo"            AS numero_tarjeta,
            T0."U_Estado"            AS estado,
            T0."U_MontoOriginal"     AS saldo_inicial,
            T0."U_Saldo"             AS saldo,
            T0."U_CedulaBenef"       AS cliente_cedula,
            T0."U_Beneficiario"      AS cliente_nombre,
            T0."U_Lote"              AS lote,
            T0."U_FechaGeneracion"   AS fecha_emision,
            T0."U_FechaVenta"        AS fecha_venta,
            T0."U_FechaExpiracion"   AS fecha_vencimiento,
            T0."U_FechaActivacion"   AS fecha_activacion,
            T0."U_FechaUltimoUso"    AS fecha_ultimo_uso,
            T0."U_Canal"             AS canal,
            T0."U_Sucursal"          AS sucursal,
            T0."U_ProductoCode"      AS producto_code,
            T0."U_Gratuita"          AS gratuita,
            T0."U_Campana"           AS campana,
            T0."U_CardCodeBenef"     AS cardcode_beneficiario
        FROM "@DM_GC_FICHA" T0
        WHERE 1=1
    """
    params = []

    if search:
        query += """ AND (
            T0."U_Codigo" LIKE ?
            OR T0."U_Beneficiario" LIKE ?
            OR T0."U_CedulaBenef" LIKE ?
            OR T0."U_Lote" LIKE ?
        )"""
        like = f'%{search}%'
        params.extend([like, like, like, like])

    if status:
        query += ' AND T0."U_Estado" = ?'
        params.append(status)

    if lote:
        query += ' AND T0."U_Lote" = ?'
        params.append(lote)

    query += ' ORDER BY T0."DocEntry" DESC'

    return (query, params)


def get_giftcard_detail(giftcard_id):
    """Obtener detalle completo de una gift card por DocEntry."""
    return (
        """
        SELECT
            T0."DocEntry"            AS id,
            T0."U_Codigo"            AS numero_tarjeta,
            T0."U_Estado"            AS estado,
            T0."U_MontoOriginal"     AS saldo_inicial,
            T0."U_Saldo"             AS saldo,
            T0."U_CedulaBenef"       AS cliente_cedula,
            T0."U_Beneficiario"      AS cliente_nombre,
            T0."U_Lote"              AS lote,
            T0."U_FechaGeneracion"   AS fecha_emision,
            T0."U_FechaVenta"        AS fecha_venta,
            T0."U_FechaExpiracion"   AS fecha_vencimiento,
            T0."U_FechaActivacion"   AS fecha_activacion,
            T0."U_FechaUltimoUso"    AS fecha_ultimo_uso,
            T0."U_Canal"             AS canal,
            T0."U_Sucursal"          AS sucursal,
            T0."U_ProductoCode"      AS producto_code,
            T0."U_Gratuita"          AS gratuita,
            T0."U_Campana"           AS campana,
            T0."U_Motivo"            AS motivo,
            T0."U_CardCodeBenef"     AS cardcode_beneficiario,
            T0."CreateDate"          AS fecha_creacion
        FROM "@DM_GC_FICHA" T0
        WHERE T0."DocEntry" = ?
        """,
        [giftcard_id]
    )


def get_giftcard_by_number(numero):
    """Buscar gift card por código (U_Codigo)."""
    return (
        """
        SELECT
            T0."DocEntry"            AS id,
            T0."U_Codigo"            AS numero_tarjeta,
            T0."U_Estado"            AS estado,
            T0."U_MontoOriginal"     AS saldo_inicial,
            T0."U_Saldo"             AS saldo,
            T0."U_CedulaBenef"       AS cliente_cedula,
            T0."U_Beneficiario"      AS cliente_nombre,
            T0."U_Lote"              AS lote,
            T0."U_FechaGeneracion"   AS fecha_emision,
            T0."U_FechaVenta"        AS fecha_venta,
            T0."U_FechaExpiracion"   AS fecha_vencimiento,
            T0."U_FechaActivacion"   AS fecha_activacion,
            T0."U_FechaUltimoUso"    AS fecha_ultimo_uso,
            T0."U_Canal"             AS canal,
            T0."U_Sucursal"          AS sucursal,
            T0."U_ProductoCode"      AS producto_code,
            T0."U_Gratuita"          AS gratuita,
            T0."U_CardCodeBenef"     AS cardcode_beneficiario
        FROM "@DM_GC_FICHA" T0
        WHERE T0."U_Codigo" = ?
        """,
        [numero]
    )


def get_lotes():
    """Lotes existentes con su cantidad de gift cards."""
    return (
        """
        SELECT
            T0."U_Lote"   AS lote,
            COUNT(*)      AS total_giftcards
        FROM "@DM_GC_FICHA" T0
        WHERE T0."U_Lote" IS NOT NULL AND T0."U_Lote" != ''
        GROUP BY T0."U_Lote"
        ORDER BY T0."U_Lote" DESC
        """,
        []
    )


# ============================================================
# QUERIES DE TRANSACCIONES (@DM_GC_TRX — child table)
# ============================================================

def get_giftcard_transactions(giftcard_id):
    """
    Movimientos de una gift card por DocEntry.
    @DM_GC_TRX es child table de @DM_GC_FICHA (relacionada por DocEntry).
    Incluye columna 'origen' para consistencia con el query por código.
    """
    return (
        """
        SELECT
            T1."LineId"              AS id,
            T1."U_FechaHora"         AS fecha,
            T1."U_Tipo"              AS tipo,
            T1."U_Monto"             AS monto,
            T1."U_Referencia"        AS descripcion,
            T1."U_NumFactura"        AS referencia,
            T1."U_ClienteCardCode"   AS cliente,
            T1."U_SaldoAnterior"     AS saldo_anterior,
            T1."U_SaldoNuevo"        AS saldo_posterior,
            T1."U_Usuario"           AS usuario,
            CAST(T1."U_Sucursal" AS NVARCHAR(100)) AS sucursal,
            'SAP'                    AS origen,
            T0."U_Codigo"            AS numero_tarjeta,
            T0."U_Beneficiario"      AS cliente_nombre
        FROM "@DM_GC_FICHA" T0
        INNER JOIN "@DM_GC_TRX" T1 ON T1."DocEntry" = T0."DocEntry"
        WHERE T0."DocEntry" = ?
        ORDER BY T1."U_FechaHora" DESC
        """,
        [giftcard_id]
    )


def get_giftcard_transactions_by_code(gift_code):
    """
    Movimientos de una gift card por código (U_Codigo).

    UNION ALL entre:
      1. SAP (@DM_GC_TRX) — solo entradas/créditos (VENTA, GENERACION,
         RECARGA, etc.). Se excluyen los débitos porque esos vienen de KLK.
      2. KLK (KLK_CONSOLIDADO_V2) — todas las salidas/consumos POS.
         No necesita NOT EXISTS porque SAP ya no aporta débitos al resultado.

    Esto evita duplicados: las entradas solo vienen de SAP y las salidas
    solo de KLK, sin importar que las referencias sean diferentes.

    La columna 'origen' indica la fuente: 'SAP' o 'KLK'.
    """
    return (
        """
        SELECT
            T1."LineId"              AS id,
            T1."U_FechaHora"         AS fecha,
            T1."U_Tipo"              AS tipo,
            T1."U_Monto"             AS monto,
            T1."U_Referencia"        AS descripcion,
            T1."U_NumFactura"        AS referencia,
            T1."U_ClienteCardCode"   AS cliente,
            T1."U_SaldoAnterior"     AS saldo_anterior,
            T1."U_SaldoNuevo"        AS saldo_posterior,
            T1."U_Usuario"           AS usuario,
            CAST(T1."U_Sucursal" AS NVARCHAR(100)) AS sucursal,
            'SAP'                    AS origen
        FROM "@DM_GC_FICHA" T0
        INNER JOIN "@DM_GC_TRX" T1 ON T1."DocEntry" = T0."DocEntry"
        WHERE T0."U_Codigo" = ?
          AND T1."U_Tipo" NOT IN ('USO', 'REDENCION', 'CONSUMO')

        UNION ALL

        SELECT
            0                                 AS id,
            C1.Fecha                          AS fecha,
            'USO-PENDIENTE'                   AS tipo,
            C2.MontoUsd                       AS monto,
            'Pago en tienda (pendiente SAP)'  AS descripcion,
            C1.NFactura COLLATE SQL_Latin1_General_CP1_CI_AS  AS referencia,
            ''                                AS cliente,
            GC."U_Saldo"                      AS saldo_anterior,
            CASE WHEN GC."U_Saldo" - C2.MontoUsd < 0 THEN 0
                 ELSE GC."U_Saldo" - C2.MontoUsd END AS saldo_posterior,
            C1.NomCaja COLLATE SQL_Latin1_General_CP1_CI_AS   AS usuario,
            CAST(C1.Sucursal AS NVARCHAR(100)) AS sucursal,
            'KLK'                             AS origen
        FROM [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROHDR] C1
        INNER JOIN [KLK_CONSOLIDADO_V2].[dbo].[KLK_COBROLINE] C2
            ON C2.NroCobro = C1.NroCobro AND C2.Sucursal = C1.Sucursal
        INNER JOIN "@DM_GC_FICHA" GC ON GC."U_Codigo" = ?
        WHERE C2.CuentaSAP COLLATE SQL_Latin1_General_CP1_CI_AS = '2.1.02.01.03.96'
          AND C2.NTransaccion COLLATE SQL_Latin1_General_CP1_CI_AS = ?

        ORDER BY id ASC
        """,
        [gift_code, gift_code, gift_code]
    )


def get_recent_transactions(limit=10):
    """Transacciones más recientes (global)."""
    return (
        f"""
        SELECT TOP {limit}
            T1."U_FechaHora"         AS fecha,
            T1."U_Tipo"              AS tipo,
            T1."U_Monto"             AS monto,
            T1."U_Referencia"        AS descripcion,
            T1."U_NumFactura"        AS referencia,
            T1."U_SaldoAnterior"     AS saldo_anterior,
            T1."U_SaldoNuevo"        AS saldo_posterior,
            T1."U_Usuario"           AS usuario,
            T0."U_Codigo"            AS numero_tarjeta,
            T0."U_Beneficiario"      AS cliente_nombre
        FROM "@DM_GC_FICHA" T0
        INNER JOIN "@DM_GC_TRX" T1 ON T1."DocEntry" = T0."DocEntry"
        ORDER BY T1."U_FechaHora" DESC
        """,
        []
    )


# ============================================================
# QUERIES DE CLIENTES (derivados de @DM_GC_FICHA)
# ============================================================

def get_all_clients(search=None):
    """Lista de clientes agrupados por cédula."""
    query = """
        SELECT
            T0."U_CedulaBenef"                     AS cedula,
            MAX(T0."U_Beneficiario")               AS nombre,
            MAX(T0."U_CardCodeBenef")              AS cardcode,
            COUNT(*)                               AS total_giftcards,
            COALESCE(SUM(T0."U_Saldo"), 0)         AS saldo_total,
            COALESCE(SUM(T0."U_MontoOriginal"), 0) AS emision_total
        FROM "@DM_GC_FICHA" T0
        WHERE T0."U_CedulaBenef" IS NOT NULL AND T0."U_CedulaBenef" != ''
    """
    params = []

    if search:
        query += ' AND (T0."U_Beneficiario" LIKE ? OR T0."U_CedulaBenef" LIKE ?)'
        like = f'%{search}%'
        params.extend([like, like])

    query += """
        GROUP BY T0."U_CedulaBenef"
        ORDER BY nombre
    """

    return (query, params)


def get_client_detail(cedula):
    """Detalle de un cliente por cédula."""
    return (
        """
        SELECT
            T0."U_CedulaBenef"                     AS cedula,
            MAX(T0."U_Beneficiario")               AS nombre,
            MAX(T0."U_CardCodeBenef")              AS cardcode,
            COUNT(*)                               AS total_giftcards,
            COALESCE(SUM(T0."U_Saldo"), 0)         AS saldo_total,
            COALESCE(SUM(T0."U_MontoOriginal"), 0) AS emision_total
        FROM "@DM_GC_FICHA" T0
        WHERE T0."U_CedulaBenef" = ?
        GROUP BY T0."U_CedulaBenef"
        """,
        [cedula]
    )


def get_client_giftcards(cedula, lotes=None):
    """
    Gift cards de un cliente por cédula.
    Si se pasan lotes (empresa compradora), incluye también todas las tarjetas
    de esos lotes aunque ya estén a nombre de otro beneficiario.
    """
    query = """
        SELECT
            T0."DocEntry"            AS id,
            T0."U_Codigo"            AS numero_tarjeta,
            T0."U_Estado"            AS estado,
            T0."U_MontoOriginal"     AS saldo_inicial,
            T0."U_Saldo"             AS saldo,
            T0."U_Lote"              AS lote,
            T0."U_FechaGeneracion"   AS fecha_emision,
            T0."U_FechaVenta"        AS fecha_venta,
            T0."U_FechaExpiracion"   AS fecha_vencimiento,
            T0."U_FechaActivacion"   AS fecha_activacion,
            T0."U_Canal"             AS canal,
            T0."U_Sucursal"          AS sucursal,
            T0."U_ProductoCode"      AS producto_code,
            T0."U_Beneficiario"      AS cliente_nombre,
            T0."U_CedulaBenef"       AS cliente_cedula
        FROM "@DM_GC_FICHA" T0
        WHERE T0."U_CedulaBenef" = ?
    """
    params = [cedula]

    if lotes:
        placeholders = ', '.join('?' for _ in lotes)
        query += f' OR T0."U_Lote" IN ({placeholders})'
        params.extend(lotes)

    query += ' ORDER BY T0."DocEntry" DESC'

    return (query, params)


# ============================================================
# QUERIES DE DASHBOARD / ESTADÍSTICAS
# ============================================================

def get_dashboard_stats():
    """Estadísticas generales del dashboard."""
    return (
        """
        SELECT
            COUNT(*)                                                     AS total_giftcards,
            COALESCE(SUM(T0."U_Saldo"), 0)                              AS saldo_total,
            COALESCE(SUM(T0."U_MontoOriginal"), 0)                       AS emision_total,
            COUNT(CASE WHEN T0."U_Estado" = 'VENDIDA'   THEN 1 END)     AS vendidas,
            COUNT(CASE WHEN T0."U_Estado" = 'GENERADA'  THEN 1 END)     AS generadas,
            COUNT(CASE WHEN T0."U_Estado" = 'ACTIVA'    THEN 1 END)     AS activas,
            COUNT(CASE WHEN T0."U_Estado" = 'VENCIDA'   THEN 1 END)     AS vencidas,
            COUNT(CASE WHEN T0."U_Estado" = 'AGOTADA'   THEN 1 END)     AS agotadas,
            COUNT(CASE WHEN T0."U_Estado" = 'BLOQUEADA' THEN 1 END)     AS bloqueadas,
            COUNT(CASE WHEN T0."U_Estado" IS NULL        THEN 1 END)     AS sin_estado
        FROM "@DM_GC_FICHA" T0
        """,
        []
    )


def get_top_clients(limit=5):
    """Top clientes por cantidad de gift cards."""
    return (
        f"""
        SELECT TOP {limit}
            T0."U_CedulaBenef"                     AS cedula,
            MAX(T0."U_Beneficiario")               AS nombre,
            COUNT(*)                               AS total_giftcards,
            COALESCE(SUM(T0."U_Saldo"), 0)         AS saldo_total
        FROM "@DM_GC_FICHA" T0
        WHERE T0."U_CedulaBenef" IS NOT NULL AND T0."U_CedulaBenef" != ''
        GROUP BY T0."U_CedulaBenef"
        ORDER BY total_giftcards DESC
        """,
        []
    )


# ============================================================
# QUERIES DE ACTIVACIÓN / ESCRITURA
# ============================================================

def activate_giftcard(doc_entry, nombre, cedula):
    """
    Activa una gift card: asigna beneficiario, cédula, estado ACTIVA
    y fecha de activación.
    """
    return (
        """
        UPDATE "@DM_GC_FICHA"
        SET "U_Beneficiario"     = ?,
            "U_CedulaBenef"      = ?,
            "U_Estado"           = 'ACTIVA',
            "U_FechaActivacion"  = CONVERT(VARCHAR(10), GETDATE(), 120)
        WHERE "DocEntry" = ?
          AND ("U_Estado" IS NULL OR "U_Estado" IN ('GENERADA', 'VENDIDA'))
        """,
        [nombre, cedula, doc_entry]
    )
