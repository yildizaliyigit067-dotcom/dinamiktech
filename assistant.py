"""
AI Asistan / AI Assistant.

İşletme sahibinin doğal dille sorduğu soruları, GERÇEK sistem verisini
özet olarak modele vererek Claude ile yanıtlar.

API anahtarı SADECE ortam değişkeninden (.env -> ANTHROPIC_API_KEY) okunur.
Koda asla gömülmez, GitHub'a asla gitmez.
"""

import os
import json
import urllib.request
import urllib.error

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-20250514")


def _build_context(report: dict, lang: str) -> str:
    """Modele verilecek kompakt veri özeti (token tasarrufu için sadeleştirilmiş)."""
    s = report["sales"]
    prod = report["products"]
    top = ", ".join(f"{i['name']}({i['qty']})" for i in prod["top_sellers"])
    low = ", ".join(f"{i['name']} %%{i['margin_pct']}" for i in prod["low_margin"])
    anomalies = "; ".join(a["title"] for a in report["anomalies"]) or "yok"
    stock = ", ".join(f"{a['item']}" for a in report["stock_alerts"]) or "yok"
    return (
        f"Ciro: {s['revenue']} TL | Kâr: {s['profit']} TL | Marj: %%{s['margin_pct']} | "
        f"Adisyon: {s['ticket_count']} | Ort. sepet: {s['avg_ticket']} TL | "
        f"En çok satan: {top} | Düşük marjlı: {low} | "
        f"Yoğun saat: {report['hourly']['peak_hour']} | "
        f"İade oranı: %%{report['refunds']['void_rate_pct']} | "
        f"Kritik stok: {stock} | Anomali: {anomalies}"
    )


def _system_prompt(context: str, lang: str) -> str:
    if lang == "en":
        return (
            "You are Dinamik Tech's business assistant for a restaurant/cafe owner. "
            "Answer ONLY based on the data summary below. Be concrete, give numbers, "
            "and suggest profit-improving actions. If data is insufficient, say so. "
            "Keep answers short and practical.\n\nDATA: " + context
        )
    return (
        "Sen Dinamik Tech'in işletme asistanısın; bir restoran/kafe sahibine "
        "yardım ediyorsun. SADECE aşağıdaki veri özetine dayanarak cevap ver. "
        "Somut ol, sayı ver, kârı artıracak aksiyon öner. Veri yetersizse bunu "
        "açıkça söyle. Cevaplar kısa ve pratik olsun.\n\nVERİ: " + context
    )


def ask(question: str, report: dict, lang: str = "tr") -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        msg = ("AI asistan henüz aktif değil: ANTHROPIC_API_KEY ortam değişkeni "
               "tanımlı değil. .env dosyana ekleyip uygulamayı yeniden başlat."
               if lang == "tr" else
               "AI assistant not active: ANTHROPIC_API_KEY is not set. "
               "Add it to your .env and restart.")
        return {"ok": False, "answer": msg}

    context = _build_context(report, lang)
    payload = {
        "model": MODEL,
        "max_tokens": 700,
        "system": _system_prompt(context, lang),
        "messages": [{"role": "user", "content": question}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ANTHROPIC_URL, data=data, method="POST")
    req.add_header("content-type", "application/json")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")

    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = "".join(b.get("text", "") for b in body.get("content", [])
                       if b.get("type") == "text")
        return {"ok": True, "answer": text.strip() or "(boş yanıt)"}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        return {"ok": False, "answer": f"AI hatası ({e.code}): {detail}"}
    except Exception as e:
        return {"ok": False, "answer": f"AI bağlantı hatası: {e}"}
