"""
Veri kaynağı katmanı / Data source layer.
USE_SAMPLE_DATA=true  -> örnek veri (demo)
USE_SAMPLE_DATA=false -> gerçek SambaPOS MSSQL
"""

import os
from .sample_data import generate_tickets, generate_stock


def _use_sample():
    return os.getenv("USE_SAMPLE_DATA", "true").lower() != "false"


SAMBA_QUERY = """
SELECT
    t.Id                    AS ticket_id,
    t.Date                  AS date,
    o.MenuItemName          AS item_name,
    mi.GroupCode            AS category,
    o.Quantity              AS quantity,
    o.Price                 AS unit_price,
    ISNULL(mip.Cost, 0)     AS unit_cost,
    (o.Price * o.Quantity)  AS line_total,
    (ISNULL(mip.Cost,0) * o.Quantity) AS line_cost,
    p.PaymentTypeName       AS payment_type,
    t.TicketTags            AS table_name,
    t.LastModifiedUserName  AS cashier,
    CAST(o.CalculatePrice AS INT) AS is_active,
    0                       AS discount_total
FROM Tickets t
JOIN Orders o   ON o.TicketId = t.Id
LEFT JOIN MenuItems mi  ON mi.Id = o.MenuItemId
LEFT JOIN MenuItemPrices mip ON mip.MenuItemId = o.MenuItemId
LEFT JOIN Payments p    ON p.TicketId = t.Id
WHERE t.Date >= DATEADD(day, -?, GETDATE())
"""


def _fetch_real(days_back):
    import pyodbc

    server = os.getenv("SAMBA_DB_SERVER")
    db = os.getenv("SAMBA_DB_NAME", "SambaPOS5")
    user = os.getenv("SAMBA_DB_USER")
    pwd = os.getenv("SAMBA_DB_PASSWORD")
    driver = os.getenv("SAMBA_DB_DRIVER", "ODBC Driver 17 for SQL Server")

    conn_str = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={db};"
        f"UID={user};PWD={pwd};TrustServerCertificate=yes"
    )
    rows = []
    with pyodbc.connect(conn_str, timeout=10) as conn:
        cur = conn.cursor()
        cur.execute(SAMBA_QUERY, days_back)
        cols = [c[0] for c in cur.description]
        for r in cur.fetchall():
            d = dict(zip(cols, r))
            d["is_void"] = not bool(d.pop("is_active", 1))
            rows.append(d)
    return rows


def get_tickets(days_back=30):
    if _use_sample():
        return generate_tickets(days_back=days_back)
    return _fetch_real(days_back)


def get_stock():
    return generate_stock()


def data_mode():
    return "sample" if _use_sample() else "live"
