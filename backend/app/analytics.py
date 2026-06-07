"""
Analiz motoru / Analytics engine.
Raporlar, kâr önerileri, anomali/kaçak tespiti.
"""

from collections import defaultdict
from datetime import datetime
from statistics import mean, pstdev


def _active(rows):
    return [r for r in rows if not r.get("is_void")]


def sales_report(rows):
    act = _active(rows)
    revenue = sum(r["line_total"] for r in act)
    cost = sum(r["line_cost"] for r in act)
    discounts = sum(r.get("discount_total", 0) for r in act)
    profit = revenue - cost - discounts
    tickets = len({r["ticket_id"] for r in act})

    by_day = defaultdict(float)
    for r in act:
        by_day[r["date"].date().isoformat()] += r["line_total"]

    by_payment = defaultdict(float)
    for r in act:
        by_payment[r["payment_type"]] += r["line_total"]

    return {
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "discounts": round(discounts, 2),
        "profit": round(profit, 2),
        "margin_pct": round(profit / revenue * 100, 1) if revenue else 0,
        "ticket_count": tickets,
        "avg_ticket": round(revenue / tickets, 2) if tickets else 0,
        "by_day": [{"day": k, "total": round(v, 2)} for k, v in sorted(by_day.items())],
        "by_payment": [{"type": k, "total": round(v, 2)} for k, v in
                       sorted(by_payment.items(), key=lambda x: -x[1])],
    }


def product_report(rows):
    act = _active(rows)
    agg = defaultdict(lambda: {"qty": 0, "revenue": 0.0, "profit": 0.0,
                               "category": "", "unit_price": 0, "unit_cost": 0})
    for r in act:
        a = agg[r["item_name"]]
        a["qty"] += r["quantity"]
        a["revenue"] += r["line_total"]
        a["profit"] += r["line_total"] - r["line_cost"]
        a["category"] = r["category"]
        a["unit_price"] = r["unit_price"]
        a["unit_cost"] = r["unit_cost"]

    items = []
    for name, a in agg.items():
        margin = (a["profit"] / a["revenue"] * 100) if a["revenue"] else 0
        items.append({
            "name": name,
            "category": a["category"],
            "qty": a["qty"],

def comparison(rows):
    from datetime import timedelta
    act = _active(rows)
    if not act:
        return {"today": 0, "yesterday": 0, "change_pct": 0,
                "week": 0, "prev_week": 0, "week_change_pct": 0}
    dates = [r["date"] for r in act]
    last = max(dates).date()
    prev = last - timedelta(days=1)
    def day_rev(d):
        return sum(r["line_total"] for r in act if r["date"].date() == d)
    def range_rev(start, end):
        return sum(r["line_total"] for r in act if start <= r["date"].date() <= end)
    today = day_rev(last)
    yesterday = day_rev(prev)
    week = range_rev(last - timedelta(days=6), last)
    prev_week = range_rev(last - timedelta(days=13), last - timedelta(days=7))
    def pct(now, before):
        if before <= 0:
            return 0
        return round((now - before) / before * 100, 1)
    return {
        "today": round(today, 2),
        "yesterday": round(yesterday, 2),
        "change_pct": pct(today, yesterday),
        "week": round(week, 2),
        "prev_week": round(prev_week, 2),
        "week_change_pct": pct(week, prev_week),
        "last_date": last.isoformat(),
    }

            "revenue": round(a["revenue"], 2),
            "profit": round(a["profit"], 2),
            "margin_pct": round(margin, 1),
        })
    items.sort(key=lambda x: -x["revenue"])
    return {
        "items": items,
        "top_sellers": items[:5],
        "top_profit": sorted(items, key=lambda x: -x["profit"])[:5],
        "low_margin": sorted([i for i in items if i["qty"] >= 5],
                             key=lambda x: x["margin_pct"])[:5],
    }


def hourly_report(rows):
    act = _active(rows)
    by_hour = defaultdict(lambda: {"revenue": 0.0, "tickets": set()})
    for r in act:
        h = r["date"].hour
        by_hour[h]["revenue"] += r["line_total"]
        by_hour[h]["tickets"].add(r["ticket_id"])

    out = []
    for h in range(8, 24):
        d = by_hour.get(h)
        out.append({
            "hour": f"{h:02d}:00",
            "revenue": round(d["revenue"], 2) if d else 0,
            "tickets": len(d["tickets"]) if d else 0,
        })
    peak = max(out, key=lambda x: x["revenue"]) if out else None
    return {"hours": out, "peak_hour": peak["hour"] if peak else None}


def stock_alerts(stock):
    alerts = []
    for s in stock:
        if s["current"] <= s["critical"]:
            severity = "critical" if s["current"] <= s["critical"] * 0.5 else "warning"
            alerts.append({
                "item": s["item"],
                "current": s["current"],
                "critical": s["critical"],
                "unit": s["unit"],
                "severity": severity,
            })
    alerts.sort(key=lambda x: (x["severity"] != "critical", x["current"]))
    return alerts


def refund_report(rows):
    voids = [r for r in rows if r.get("is_void")]
    void_total = sum(r["line_total"] for r in voids)
    total = sum(r["line_total"] for r in rows) or 1
    return {
        "void_count": len({r["ticket_id"] for r in voids}),
        "void_total": round(void_total, 2),
        "void_rate_pct": round(void_total / total * 100, 1),
    }


def profit_suggestions(rows):
    prod = product_report(rows)
    sug = []

    for it in prod["low_margin"]:
        if it["margin_pct"] < 58 and it["qty"] >= 8:
            sug.append({
                "type": "margin",
                "title": f"{it['name']} marjı düşük",
                "detail": (f"{it['name']} iyi satıyor ({it['qty']} adet) ama kâr marjı "
                           f"%{it['margin_pct']}. 5-10 TL fiyat artışı veya porsiyon/maliyet "
                           f"düzenlemesi toplam kârı belirgin artırır."),
                "impact": "yüksek",
            })

    if prod["top_profit"]:
        star = prod["top_profit"][0]
        sug.append({
            "type": "promote",
            "title": f"{star['name']} kâr lokomotifin",
            "detail": (f"{star['name']} en çok kâr getiren ürün "
                       f"({star['profit']:.0f} TL). Menüde üst sıraya al, "
                       f"personel önersin, kampanyada bunu kullan."),
            "impact": "orta",
        })

    if prod["top_sellers"]:
        best = prod["top_sellers"][0]
        sug.append({
            "type": "upsell",
            "title": f"{best['name']} ile çapraz satış",
            "detail": (f"{best['name']} en çok satan ürünün ({best['qty']} adet). "
                       f"Yanına yüksek marjlı bir tatlı/içecek menüsü öner; "
                       f"sepet ortalamasını yükseltir."),
            "impact": "orta",
        })

    return sug[:6]


def anomaly_signals(rows):
    signals = []

    by_cashier = defaultdict(lambda: {"total": 0.0, "void": 0.0, "disc": 0.0})
    for r in rows:
        c = r.get("cashier", "?")
        by_cashier[c]["total"] += r["line_total"]
        if r.get("is_void"):
            by_cashier[c]["void"] += r["line_total"]
        by_cashier[c]["disc"] += r.get("discount_total", 0)

    rates = []
    for c, d in by_cashier.items():
        if d["total"] > 0:
            rate = (d["void"] + d["disc"]) / d["total"] * 100
            rates.append((c, rate, d["void"] + d["disc"]))

    if len(rates) >= 3:
        avg = mean([r[1] for r in rates])
        sd = pstdev([r[1] for r in rates]) or 1
        for c, rate, amount in rates:
            if rate > avg + 1.5 * sd and rate > 8 and amount > 200:
                signals.append({
                    "level": "high",
                    "title": f"Kasiyer '{c}' iptal/iskonto oranı yüksek",
                    "detail": (f"'{c}' kasiyerinde iptal+iskonto oranı %{rate:.1f} "
                               f"(işletme ortalaması %{avg:.1f}). Toplam {amount:.0f} TL. "
                               f"Bu fark kasten yapılmış olabilir; kayıtları incele."),
                })

    rr = refund_report(rows)
    if rr["void_rate_pct"] > 6:
        signals.append({
            "level": "medium",
            "title": "Genel iptal oranı yüksek",
            "detail": (f"İptal/iade oranı %{rr['void_rate_pct']} "
                       f"({rr['void_total']:.0f} TL). %5 üstü dikkat gerektirir."),
        })

    sales = sales_report(rows)
    pay = {p["type"]: p["total"] for p in sales["by_payment"]}
    cash = pay.get("Nakit", 0)
    tot = sum(pay.values()) or 1
    cash_pct = cash / tot * 100
    if cash_pct < 12:
        signals.append({
            "level": "low",
            "title": "Nakit oranı çok düşük",
            "detail": (f"Nakit satış oranı %{cash_pct:.0f}. Bilgi amaçlı; "
                       f"nakit işlemlerin kasaya tam girip girmediğini kontrol et."),
        })

    return signals


def end_of_day(rows, stock):
    return {
        "generated_at": datetime.now().isoformat(),
        "sales": sales_report(rows),
        "products": product_report(rows),
        "hourly": hourly_report(rows),
        "stock_alerts": stock_alerts(stock),
        "refunds": refund_report(rows),
        "suggestions": profit_suggestions(rows),
        "anomalies": anomaly_signals(rows),
        "comparison": comparison(rows),
    }

