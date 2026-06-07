"""
Dinamik Tech — Masaüstü Veri Ajanı / Desktop Data Agent
========================================================

Bu script, SambaPOS'un çalıştığı işletme bilgisayarında arka planda çalışır.
Yerel MSSQL veritabanından veriyi çeker ve buluttaki Dinamik Tech paneline
gönderir. Böylece panel internetten her yerden açılabilir, ama veri
işletmenin kendi bilgisayarından gelir.

KULLANIM (işletme PC'sinde):
  1) pip install pyodbc requests
  2) Bu dosyayı SambaPOS PC'sine kopyala
  3) Aşağıdaki AYARLAR bölümünü doldur
  4) python desktop_agent.py    (ya da Windows'ta otomatik başlatmaya ekle)

NOT: Demo için buna gerek YOK. Panel zaten kendi başına örnek veriyle çalışır.
Bu ajan, GERÇEK SambaPOS verisini kullanmaya geçtiğinde devreye girer.
"""

import os
import time

# ===================== AYARLAR / SETTINGS ============================
# Buluttaki panelin adresi (Render'dan alacağın URL):
PANEL_URL = os.getenv("PANEL_URL", "https://dinamiktech.onrender.com")

# Yerel SambaPOS veritabanı:
DB_SERVER   = os.getenv("SAMBA_DB_SERVER", r"localhost\SQLEXPRESS")
DB_NAME     = os.getenv("SAMBA_DB_NAME", "SambaPOS5")
DB_USER     = os.getenv("SAMBA_DB_USER", "sa")
DB_PASSWORD = os.getenv("SAMBA_DB_PASSWORD", "")
DB_DRIVER   = os.getenv("SAMBA_DB_DRIVER", "ODBC Driver 17 for SQL Server")

INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", "30"))
# =====================================================================


def fetch_local():
    import pyodbc
    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_NAME};"
        f"UID={DB_USER};PWD={DB_PASSWORD};TrustServerCertificate=yes"
    )
    query = """
    SELECT t.Id, t.Date, o.MenuItemName, o.Quantity, o.Price,
           p.PaymentTypeName, t.LastModifiedUserName
    FROM Tickets t
    JOIN Orders o ON o.TicketId = t.Id
    LEFT JOIN Payments p ON p.TicketId = t.Id
    WHERE t.Date >= DATEADD(day, -30, GETDATE())
    """
    rows = []
    with pyodbc.connect(conn_str, timeout=10) as conn:
        cur = conn.cursor()
        cur.execute(query)
        cols = [c[0] for c in cur.description]
        for r in cur.fetchall():
            d = dict(zip(cols, r))
            d["Date"] = d["Date"].isoformat() if d.get("Date") else None
            rows.append(d)
    return rows


def push_to_panel(rows):
    import requests
    resp = requests.post(f"{PANEL_URL}/api/ingest", json={"rows": rows}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run_once():
    rows = fetch_local()
    print(f"[Ajan] {len(rows)} kayıt çekildi, panele gönderiliyor…")
    result = push_to_panel(rows)
    print(f"[Ajan] Gönderildi: {result}")


def main():
    print("=" * 50)
    print("  DİNAMİK TECH — Masaüstü Veri Ajanı")
    print(f"  Panel: {PANEL_URL}")
    print(f"  Her {INTERVAL_MINUTES} dakikada bir veri gönderilecek.")
    print("=" * 50)
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"[Ajan] Hata: {e}")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
