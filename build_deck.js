const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "Dinamik Tech";
pres.title = "Dinamik Tech — MVP";

// Marka renkleri (logodan)
const NAVY = "232553";
const NAVY2 = "2D3068";
const WHITE = "FFFFFF";
const ICE = "CADCFC";
const MUTED = "9AA0C0";
const GOOD = "2BB673";
const WARN = "E0A82E";
const BAD = "E0556A";
const INK = "1A1C2E";
const PAPER = "F4F5FA";

const HF = "Arial Black", BF = "Calibri";

function brand(slide, dark) {
  // sol üstte Dinamik Tech logosu
  slide.addText(
    [{ text: "DİNAMİK", options: { color: dark ? WHITE : NAVY, bold: true } }],
    { x: 0.5, y: 0.28, w: 1.9, h: 0.4, fontSize: 15, fontFace: "Arial", margin: 0, valign: "middle" }
  );
  slide.addShape(pres.shapes.RECTANGLE, { x: 1.78, y: 0.30, w: 0.95, h: 0.36, fill: { color: dark ? WHITE : NAVY } });
  slide.addText("TECH", { x: 1.78, y: 0.30, w: 0.95, h: 0.36, fontSize: 14, bold: true,
    color: dark ? NAVY : WHITE, align: "center", valign: "middle", fontFace: "Arial", margin: 0 });
}

// ---------- SLIDE 1: KAPAK ----------
let s = pres.addSlide();
s.background = { color: NAVY };
brand(s, true);
s.addText("İşletmenizin verisini\nkâra çeviren akıllı asistan", {
  x: 0.7, y: 2.2, w: 9.5, h: 2.0, fontSize: 40, bold: true, color: WHITE,
  fontFace: "Georgia", lineSpacing: 46, align: "left"
});
s.addText("SambaPOS verinizi otomatik okur · kâr önerileri verir · kaçakları yakalar", {
  x: 0.72, y: 4.3, w: 10, h: 0.6, fontSize: 16, color: ICE, fontFace: BF, align: "left"
});
// sağda büyük stat
s.addText("MVP", { x: 10.3, y: 5.4, w: 2.4, h: 0.8, fontSize: 28, bold: true,
  color: NAVY2, align: "right", fontFace: HF });

// ---------- SLIDE 2: PROBLEM ----------
s = pres.addSlide();
s.background = { color: PAPER };
brand(s, false);
s.addText("İşletme sahibi veriye boğuluyor,\nkarara aç kalıyor", {
  x: 0.6, y: 1.1, w: 8.5, h: 1.3, fontSize: 30, bold: true, color: INK, fontFace: "Georgia", lineSpacing: 34 });
const problems = [
  ["Veri SambaPOS'ta kilitli", "Rakamlar adisyon sisteminde kalıyor, anlamlı bilgiye dönüşmüyor."],
  ["Kâr nerede sızıyor belirsiz", "Hangi ürün kâr getiriyor, hangisi zarar — net değil."],
  ["Kaçak fark edilmiyor", "Anormal iptal, iskonto ve iade gözden kaçıyor."],
];
problems.forEach((p, i) => {
  const y = 2.9 + i * 1.25;
  s.addShape(pres.shapes.OVAL, { x: 0.7, y: y, w: 0.5, h: 0.5, fill: { color: NAVY } });
  s.addText((i + 1).toString(), { x: 0.7, y: y, w: 0.5, h: 0.5, color: WHITE, bold: true,
    align: "center", valign: "middle", fontSize: 18, fontFace: HF, margin: 0 });
  s.addText(p[0], { x: 1.4, y: y - 0.05, w: 6, h: 0.5, fontSize: 18, bold: true, color: INK, fontFace: BF, margin: 0 });
  s.addText(p[1], { x: 1.4, y: y + 0.42, w: 10.5, h: 0.5, fontSize: 14, color: "5A5E78", fontFace: BF, margin: 0 });
});

// ---------- SLIDE 3: ÇÖZÜM ----------
s = pres.addSlide();
s.background = { color: NAVY };
brand(s, true);
s.addText("Dinamik Tech ne yapar?", { x: 0.6, y: 1.0, w: 10, h: 0.8, fontSize: 30, bold: true,
  color: WHITE, fontFace: "Georgia" });
const cards = [
  ["Otomatik veri", "SambaPOS'tan 30 dakikada bir arka planda veri çeker. Eklenti gibi sessiz çalışır."],
  ["3 temel rapor", "Satış, ürün ve saat raporları. Gün sonunda net özet."],
  ["Kâr önerileri", "Düşük marjlı ürün, kâr lokomotifi, çapraz satış — somut aksiyon."],
  ["Kaçak uyarısı", "Kasiyer bazlı anormal iptal/iskonto ve yüksek iade istatistikle yakalanır."],
  ["AI asistan", "Doğal dille soru sor, sistem verisine göre cevap al."],
  ["Mobil panel", "Türkçe/İngilizce, telefonda da net. Her yerden eriş."],
];
cards.forEach((c, i) => {
  const col = i % 3, rowi = Math.floor(i / 3);
  const x = 0.6 + col * 4.15, y = 2.1 + rowi * 2.35;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.85, h: 2.05, fill: { color: NAVY2 }, rectRadius: 0.08 });
  s.addText(c[0], { x: x + 0.25, y: y + 0.2, w: 3.4, h: 0.5, fontSize: 18, bold: true, color: WHITE, fontFace: BF, margin: 0 });
  s.addText(c[1], { x: x + 0.25, y: y + 0.75, w: 3.4, h: 1.2, fontSize: 13, color: ICE, fontFace: BF, margin: 0, valign: "top" });
});

// ---------- SLIDE 4: NASIL ÇALIŞIR (akış) ----------
s = pres.addSlide();
s.background = { color: PAPER };
brand(s, false);
s.addText("Nasıl çalışır?", { x: 0.6, y: 1.0, w: 10, h: 0.8, fontSize: 30, bold: true, color: INK, fontFace: "Georgia" });
const flow = [
  ["SambaPOS", "Kasiyer satışı girer\n(adisyon, ödeme, iade)"],
  ["Veri çekimi", "Masaüstü ajan / DB\n30 dk'da bir okur"],
  ["Analiz", "Rapor + öneri +\nkaçak tespiti"],
  ["Panel & AI", "İşletme sahibi görür,\nsoru sorar"],
];
flow.forEach((f, i) => {
  const x = 0.6 + i * 3.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.6, w: 2.7, h: 2.0, fill: { color: WHITE },
    line: { color: "E0E2EF", width: 1 }, rectRadius: 0.08,
    shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.08 } });
  s.addText((i + 1).toString(), { x: x + 0.25, y: 2.8, w: 0.6, h: 0.6, fontSize: 26, bold: true, color: NAVY, fontFace: HF, margin: 0 });
  s.addText(f[0], { x: x + 0.25, y: 3.45, w: 2.2, h: 0.4, fontSize: 16, bold: true, color: INK, fontFace: BF, margin: 0 });
  s.addText(f[1], { x: x + 0.25, y: 3.85, w: 2.3, h: 0.7, fontSize: 12, color: "5A5E78", fontFace: BF, margin: 0 });
  if (i < 3) s.addText("→", { x: x + 2.72, y: 3.3, w: 0.4, h: 0.6, fontSize: 24, color: NAVY, align: "center", margin: 0 });
});

// ---------- SLIDE 5: ÖRNEK PANEL DEĞERLERİ ----------
s = pres.addSlide();
s.background = { color: NAVY };
brand(s, true);
s.addText("Panelden örnek görünüm", { x: 0.6, y: 1.0, w: 10, h: 0.8, fontSize: 28, bold: true, color: WHITE, fontFace: "Georgia" });
const stats = [["₺906.000", "30 günlük ciro", WHITE], ["%62", "kâr marjı", GOOD],
  ["2.381", "adisyon", WHITE], ["1", "kaçak uyarısı", BAD]];
stats.forEach((st, i) => {
  const x = 0.6 + i * 3.1;
  s.addText(st[0], { x, y: 2.5, w: 2.9, h: 0.9, fontSize: 36, bold: true, color: st[2], fontFace: HF, margin: 0 });
  s.addText(st[1], { x, y: 3.45, w: 2.9, h: 0.5, fontSize: 14, color: ICE, fontFace: BF, margin: 0 });
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.5, w: 12.1, h: 1.9, fill: { color: NAVY2 }, rectRadius: 0.08 });
s.addText("Kaçak uyarısı (gerçek veri örneği)", { x: 0.85, y: 4.7, w: 11, h: 0.4, fontSize: 14, bold: true, color: BAD, fontFace: BF, margin: 0 });
s.addText("\"Can\" kasiyerinde iptal+iskonto oranı %14,5 (işletme ortalaması %6,6). Toplam 19.760 TL. Bu fark kasten yapılmış olabilir; kayıtları incele.", {
  x: 0.85, y: 5.15, w: 11.5, h: 1.0, fontSize: 15, color: WHITE, fontFace: BF, margin: 0, lineSpacing: 22 });

// ---------- SLIDE 6: KAPANIŞ ----------
s = pres.addSlide();
s.background = { color: NAVY };
brand(s, true);
s.addText("Küçük ama gerçek kullanılan\nbir MVP", { x: 0.7, y: 2.5, w: 11, h: 1.6, fontSize: 38, bold: true,
  color: WHITE, fontFace: "Georgia", lineSpacing: 44 });
s.addText("Demo örnek veriyle çalışır · gerçek SambaPOS'a tek satırla geçer · telefondan deploy edilir", {
  x: 0.72, y: 4.4, w: 11.5, h: 0.6, fontSize: 16, color: ICE, fontFace: BF });

pres.writeFile({ fileName: "/home/claude/dinamiktech/docs/DinamikTech_Sunum.pptx" })
  .then(f => console.log("Sunum oluşturuldu:", f));
