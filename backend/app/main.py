"""
Dinamik Tech — FastAPI ana uygulaması.
"""

import os
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .datasource import get_tickets, get_stock, data_mode
from . import analytics
from . import assistant

REFRESH_MINUTES = int(os.getenv("REFRESH_MINUTES", "30"))
HISTORY_DAYS = int(os.getenv("HISTORY_DAYS", "30"))

_state = {"report": None, "last_refresh": None}
_lock = threading.Lock()


def refresh_data():
    rows = get_tickets(days_back=HISTORY_DAYS)
    stock = get_stock()
    report = analytics.end_of_day(rows, stock)
    with _lock:
        _state["report"] = report
        _state["last_refresh"] = time.time()
    return report


def _background_loop():
    while True:
        try:
            refresh_data()
            print(f"[Dinamik Tech] Veri yenilendi ({data_mode()} modu).")
        except Exception as e:
            print(f"[Dinamik Tech] Yenileme hatası: {e}")
        time.sleep(REFRESH_MINUTES * 60)


@asynccontextmanager
async def lifespan(app):
    refresh_data()
    t = threading.Thread(target=_background_loop, daemon=True)
    t.start()
    yield


app = FastAPI(title="Dinamik Tech", lifespan=lifespan)


def _get_report():
    with _lock:
        if _state["report"] is None:
            return refresh_data()
        return _state["report"]


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": data_mode(),
            "ai_enabled": bool(os.getenv("ANTHROPIC_API_KEY"))}


@app.get("/api/report")
def report():
    r = _get_report()
    return JSONResponse({**r, "mode": data_mode(),
                         "refresh_minutes": REFRESH_MINUTES})


@app.post("/api/refresh")
def manual_refresh():
    r = refresh_data()
    return {"ok": True, "generated_at": r["generated_at"], "mode": data_mode()}


class ChatIn(BaseModel):
    message: str
    lang: str = "tr"


@app.post("/api/chat")
def chat(body: ChatIn):
    r = _get_report()
    return assistant.ask(body.message, r, lang=body.lang)


class IngestIn(BaseModel):
    rows: list


@app.post("/api/ingest")
def ingest(body: IngestIn):
    from datetime import datetime as _dt
    norm = []
    for r in body.rows:
        try:
            d = r.get("Date") or r.get("date")
            dt = _dt.fromisoformat(d) if isinstance(d, str) else d
            price = float(r.get("Price", r.get("unit_price", 0)) or 0)
            qty = float(r.get("Quantity", r.get("quantity", 0)) or 0)
            norm.append({
                "ticket_id": r.get("Id", r.get("ticket_id")),
                "date": dt,
                "item_name": r.get("MenuItemName", r.get("item_name", "?")),
                "category": r.get("category", "?"),
                "quantity": qty,
                "unit_price": price,
                "unit_cost": float(r.get("unit_cost", 0) or 0),
                "line_total": price * qty,
                "line_cost": float(r.get("unit_cost", 0) or 0) * qty,
                "payment_type": r.get("PaymentTypeName", r.get("payment_type", "?")),
                "table_name": r.get("table_name", ""),
                "cashier": r.get("LastModifiedUserName", r.get("cashier", "?")),
                "is_void": bool(r.get("is_void", False)),
                "discount_total": float(r.get("discount_total", 0) or 0),
            })
        except Exception:
            continue
    stock = get_stock()
    report = analytics.end_of_day(norm, stock)
    with _lock:
        _state["report"] = report
        _state["last_refresh"] = time.time()
    return {"ok": True, "received": len(norm)}


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

if os.path.isdir(FRONTEND_DIR):
    @app.get("/")
    def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static")
