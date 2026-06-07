"""
Gerçekçi örnek veri üreteci / Realistic sample data generator.

SambaPOS veritabanına bağlanamadığımız demo aşamasında, gerçek SambaPOS
şemasındaki alanlara (Tickets, Orders, Payments) birebir karşılık gelen
veri üretir. Böylece gerçek veriye geçince hiçbir analiz kodu değişmez.

When real MSSQL connection is unavailable (demo mode), this produces data
that mirrors the real SambaPOS schema so the analytics layer stays identical.
"""

import random
from datetime import datetime, timedelta, time

# Menü: (ad, kategori, satış fiyatı, maliyet) - kâr marjı analizinin temeli
MENU = [
    ("Türk Kahvesi", "İçecek", 45, 9),
    ("Latte", "İçecek", 70, 18),
    ("Filtre Kahve", "İçecek", 55, 12),
    ("Çay", "İçecek", 20, 3),
    ("Limonata", "İçecek", 65, 20),
    ("Cheesecake", "Tatlı", 120, 38),
    ("Brownie", "Tatlı", 95, 30),
    ("Tiramisu", "Tatlı", 130, 45),
    ("Tavuklu Salata", "Yemek", 165, 70),
    ("Köfte Burger", "Yemek", 220, 95),
    ("Margherita Pizza", "Yemek", 240, 88),
    ("Mantı", "Yemek", 185, 72),
    ("Çıtır Tavuk", "Yemek", 210, 90),
    ("Sezar Salata", "Yemek", 155, 60),
    ("Patates Kızartması", "Atıştırma", 75, 22),
    ("Soğan Halkası", "Atıştırma", 80, 25),
]

PAYMENT_TYPES = ["Nakit", "Kredi Kartı", "Yemek Çeki"]


def _busyness(hour: int) -> float:
    """Saate göre yoğunluk katsayısı - gerçek kafe ritmini taklit eder."""
    if 12 <= hour <= 14:      # öğle
        return 1.6
    if 18 <= hour <= 21:      # akşam
        return 1.9
    if 9 <= hour <= 11:       # sabah kahvesi
        return 1.1
    if 15 <= hour <= 17:      # ikindi
        return 1.0
    if hour < 9 or hour > 22:
        return 0.25
    return 0.7


def generate_tickets(days_back: int = 30, seed: int = 42):
    """
    SambaPOS 'Tickets' + 'Orders' + 'Payments' karşılığı düzleştirilmiş kayıtlar.
    Her satır bir sipariş kalemi (order line).
    """
    rng = random.Random(seed)
    rows = []
    ticket_no = 10000
    now = datetime.now()
    start = (now - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)

    day = start
    while day <= now:
        weekday = day.weekday()
        day_factor = 1.3 if weekday >= 4 else 1.0  # hafta sonu yoğun

        for hour in range(8, 24):
            base = _busyness(hour) * day_factor
            n_tickets = max(0, int(rng.gauss(base * 4, base * 1.5)))

            for _ in range(n_tickets):
                ticket_no += 1
                minute = rng.randint(0, 59)
                ticket_time = day.replace(hour=hour, minute=minute)
                if ticket_time > now:
                    continue

                n_items = rng.choices([1, 2, 3, 4, 5], weights=[25, 35, 22, 12, 6])[0]
                pay_type = rng.choices(PAYMENT_TYPES, weights=[35, 58, 7])[0]
                table = f"Masa {rng.randint(1, 20)}"

                ticket_total = 0
                line_items = []
                for _ in range(n_items):
                    name, cat, price, cost = rng.choice(MENU)
                    qty = rng.choices([1, 2, 3], weights=[78, 18, 4])[0]
                    line_items.append((name, cat, price, cost, qty))
                    ticket_total += price * qty

                cashier = rng.choices(
                    ["Ayşe", "Mehmet", "Zeynep", "Can"], weights=[30, 28, 27, 15]
                )[0]
                # Can kasiyeri demoda anormal yüksek iptal/ikram yapsın (kaçak sinyali).
                # Gerçek hayatta bu, kasten yapılan kayıt dışı işleme işaret edebilir.
                is_void_p = 0.10 if cashier == "Can" else 0.025
                disc_p = 0.16 if cashier == "Can" else 0.04
                is_void = rng.random() < is_void_p
                discount = 0
                if rng.random() < disc_p:
                    discount = round(ticket_total * rng.uniform(0.15, 0.45))

                for idx, (name, cat, price, cost, qty) in enumerate(line_items):
                    rows.append({
                        "ticket_id": ticket_no,
                        "date": ticket_time,
                        "item_name": name,
                        "category": cat,
                        "quantity": qty,
                        "unit_price": price,
                        "unit_cost": cost,
                        "line_total": price * qty,
                        "line_cost": cost * qty,
                        "payment_type": pay_type,
                        "table_name": table,
                        "cashier": cashier,
                        "is_void": is_void,
                        "discount_total": discount if idx == 0 else 0,
                    })
        day += timedelta(days=1)

    return rows


# Basit stok modeli: ürün -> (mevcut stok, kritik eşik, birim)
def generate_stock():
    return [
        {"item": "Kahve Çekirdeği", "unit": "kg", "current": 2.4, "critical": 5.0},
        {"item": "Süt", "unit": "lt", "current": 8.0, "critical": 15.0},
        {"item": "Un", "unit": "kg", "current": 22.0, "critical": 10.0},
        {"item": "Tavuk", "unit": "kg", "current": 3.1, "critical": 8.0},
        {"item": "Dana Kıyma", "unit": "kg", "current": 6.5, "critical": 7.0},
        {"item": "Domates", "unit": "kg", "current": 14.0, "critical": 6.0},
        {"item": "Mozzarella", "unit": "kg", "current": 1.8, "critical": 4.0},
        {"item": "Patates", "unit": "kg", "current": 30.0, "critical": 12.0},
    ]
