# Dinamik Tech

SambaPOS adisyon verisini arka planda otomatik çekip, restoran/kafe sahibine
**kâr artırıcı somut öneriler**, **stok uyarıları**, **iade takibi** ve
**kaçak/anomali uyarıları** veren; ayrıca **AI sohbet asistanı** ile doğal
dilde soru sormaya izin veren mobil uyumlu panel.

> Türkçe + İngilizce dil seçeneği. Sağ üstten değiştirilir.

---

## Ne yapar?

- **3 temel rapor:** Satış · Ürün · Saat
- **Kâr marjı önerileri:** düşük marjlı çok satanlar, kâr lokomotifi ürün, çapraz satış
- **Kaçak / anomali uyarısı:** kasiyer bazlı anormal iptal/iskonto, yüksek iade oranı,
  düşük nakit oranı — *uydurma değil, veriden çıkan istatistiksel sinyal*
- **Stok uyarıları** ve **iade/iptal oranı**
- **AI asistan:** Claude'a bağlı, sistem verisine göre cevap verir
- **30 dakikada bir** otomatik veri yenileme (SambaPOS eklentisi gibi arka planda)

---

## Hızlı başlangıç (demo, yerel)

```bash
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```
Tarayıcıda: http://localhost:8000

Demo, gerçek SambaPOS şemasına uyan örnek veriyle çalışır. Bağlantı gerekmez.

---

## Telefondan deploy (Render — en kolay)

1. Projeyi GitHub'a yükle (aşağıda anlatıldı).
2. Telefondan **render.com** → giriş yap → **New** → **Blueprint**.
3. GitHub reponu seç. Render `render.yaml`'ı otomatik okur.
4. **Environment** bölümünde `ANTHROPIC_API_KEY` değerini elle gir (koda yazma!).
5. **Deploy**. Birkaç dakikada `https://dinamiktech.onrender.com` gibi bir adres alırsın.

> AI asistanı kullanmak istemiyorsan anahtarı boş bırak; panel yine çalışır,
> sadece sohbet "anahtar tanımlı değil" der.

---

## AI Asistan anahtarı (ÖNEMLİ — güvenlik)

API anahtarı **asla** koda veya GitHub'a girmez. Sadece ortam değişkeninden okunur:

- **Yerelde:** `.env.example` dosyasını `.env` olarak kopyala, `ANTHROPIC_API_KEY=` satırını doldur.
- **Render'da:** panelden Environment → `ANTHROPIC_API_KEY` ekle.

`.env` dosyası `.gitignore` içindedir, repoya gitmez.

---

## Gerçek SambaPOS verisine geçiş

İki yol var:

**A) Panel doğrudan veritabanına bağlanır** (panel, SambaPOS ile aynı ağdaysa):
`.env` içinde:
```
USE_SAMPLE_DATA=false
SAMBA_DB_SERVER=localhost\SQLEXPRESS
SAMBA_DB_NAME=SambaPOS5
SAMBA_DB_USER=sa
SAMBA_DB_PASSWORD=********
```
Bağlantı bilgisi: SambaPOS → Manage → Settings → Local Settings → Database.

**B) Masaüstü ajan** (panel bulutta, veri işletme PC'sinden gelir — önerilen):
SambaPOS PC'sinde:
```bash
pip install pyodbc requests
python desktop_agent.py
```
`desktop_agent.py` içindeki `PANEL_URL` ve veritabanı bilgilerini doldur.
Ajan 30 dakikada bir yerel veriyi çekip buluttaki panele gönderir.

---

## VS Code ile düzenleme

Proje düzenli ve modüler. Önemli dosyalar:

| Dosya | Görevi |
|------|--------|
| `backend/app/main.py` | API + otomatik yenileme + panel servisi |
| `backend/app/analytics.py` | Tüm raporlar, öneriler, anomali tespiti |
| `backend/app/datasource.py` | Örnek veri ↔ gerçek SambaPOS anahtarı |
| `backend/app/assistant.py` | Claude AI sohbet |
| `backend/app/sample_data.py` | Demo verisi |
| `frontend/index.html` | Panel (tek dosya, TR/EN) |
| `desktop_agent.py` | İşletme PC'sinde çalışan veri ajanı |

Menü fiyat/maliyetlerini değiştirmek için `sample_data.py` içindeki `MENU` listesini düzenle.

---

## GitHub'a yükleme

```bash
cd dinamiktech
git init
git add .
git commit -m "Dinamik Tech MVP"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/dinamiktech.git
git push -u origin main
```
> `git add .` `.env`'i otomatik atlar (`.gitignore` sayesinde).

---

## API uçları

| Uç | Açıklama |
|----|----------|
| `GET /` | Panel |
| `GET /api/health` | Durum + mod + AI aktif mi |
| `GET /api/report` | Tüm rapor verisi |
| `POST /api/refresh` | Elle yenile |
| `POST /api/chat` | AI asistana soru |
| `POST /api/ingest` | Masaüstü ajanından veri al |

---

Dinamik Tech · MVP demo
