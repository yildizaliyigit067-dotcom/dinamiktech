"""
store.py — Yönetici paneli verileri (ürün, malzeme, reçete) kalıcı saklama.

Basit JSON dosyası tabanlı. Pilot ve ilk müşteriler için yeterli.
Çok müşteri olunca gerçek veritabanına (PostgreSQL) geçilir.

NOT: Render'ın ücretsiz planında disk kalıcı DEĞİLDİR; servis yeniden
başlayınca dosya sıfırlanabilir. Kalıcılık için Render'da "Disk" eklenmeli
(ücretli) ya da PostgreSQL kullanılmalı. Pilot aşamasında bu kabul edilebilir.
"""

import json
import os
import threading

# Render'da kalıcı disk varsa oraya, yoksa geçici dizine yaz
DATA_DIR = os.getenv("DATA_DIR", "/tmp/dinamik_data")
STORE_FILE = os.path.join(DATA_DIR, "yonetim.json")
_lock = threading.Lock()

# Varsayılan boş yapı
_DEFAULT = {
    "products": [],     # {id, name, category, price}
    "ingredients": [],  # {id, name, unit, stock, cost}  unit: kg/adet/lt
    "recipes": {},      # { product_id: [ {ingredient_id, amount}, ... ] }
}


def _ensure_dir():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        pass


def load() -> dict:
    """Kayıtlı veriyi oku; yoksa boş yapı döndür."""
    with _lock:
        if not os.path.exists(STORE_FILE):
            return json.loads(json.dumps(_DEFAULT))
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # eksik anahtarları tamamla
            for k, v in _DEFAULT.items():
                data.setdefault(k, json.loads(json.dumps(v)))
            return data
        except Exception:
            return json.loads(json.dumps(_DEFAULT))


def save(data: dict) -> bool:
    """Veriyi diske yaz."""
    _ensure_dir()
    with _lock:
        try:
            tmp = STORE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, STORE_FILE)
            return True
        except Exception:
            return False


def has_data() -> bool:
    """Restoran kendi verisini girmiş mi? (ürün veya malzeme var mı)"""
    d = load()
    return bool(d.get("products") or d.get("ingredients"))
