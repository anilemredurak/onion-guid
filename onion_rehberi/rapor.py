"""
Tek dosyalık HTML raporu üretir.

- Dışarıdan hiçbir şey yüklemez (yazı tipi, betik, görsel yok): Tor Browser'ın
  en sıkı güvenlik seviyesinde (Safest, JavaScript kapalı) de tam çalışır.
- Açık ve koyu temayı otomatik uygular.
"""

import html
from collections import Counter
from datetime import datetime, timezone
from typing import List

from . import __version__
from .veri import Site, kategorilere_ayir

CSS = """
:root{--bg:#f6f7f9;--kart:#ffffff;--yazi:#1d2533;--soluk:#5b6576;--cizgi:#d9dee6;--vurgu:#2e6da4;
--yesil:#237a4b;--turuncu:#a8610b;--kirmizi:#a8352a;--seritt:#eef2f7;--kod:#8a2a1e}
@media (prefers-color-scheme:dark){:root{--bg:#12161d;--kart:#1a2029;--yazi:#e4e8ee;--soluk:#9aa5b5;
--cizgi:#2c3542;--vurgu:#6fa8dc;--yesil:#5cc08a;--turuncu:#e3a24a;--kirmizi:#e07a6f;--seritt:#1f2631;--kod:#f0a58f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--yazi);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:34px;margin:4px 0 6px;line-height:1.2}
h2{font-size:24px;margin:44px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--vurgu)}
h3{font-size:18px;margin:28px 0 8px}
.ust{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--vurgu);font-weight:700}
.alt{color:var(--soluk);margin:0 0 20px}
.kartlar{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:20px 0}
.kart{background:var(--kart);border:1px solid var(--cizgi);border-radius:12px;padding:16px}
.kart b{display:block;font-size:30px;line-height:1.1}
.kart span{color:var(--soluk);font-size:14px}
.kutu{background:var(--kart);border:1px solid var(--cizgi);border-left:6px solid var(--vurgu);border-radius:10px;padding:14px 18px;margin:16px 0}
.kutu.uyari{border-left-color:var(--kirmizi)}
.kutu.ipucu{border-left-color:var(--turuncu)}
.kutu p{margin:6px 0}
.grafik{background:var(--kart);border:1px solid var(--cizgi);border-radius:12px;padding:16px 18px}
.satir{display:grid;grid-template-columns:minmax(120px,260px) 1fr 44px;gap:10px;align-items:center;margin:6px 0;font-size:14px}
.cubuk{height:14px;border-radius:7px;background:var(--vurgu)}
.sayi{text-align:right;font-variant-numeric:tabular-nums;color:var(--soluk)}
.dizin{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.dizin a{background:var(--kart);border:1px solid var(--cizgi);border-radius:20px;padding:4px 12px;text-decoration:none;color:var(--yazi);font-size:14px}
.tablo-sar{overflow-x:auto;background:var(--kart);border:1px solid var(--cizgi);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:14px}
th{text-align:left;background:var(--seritt);padding:10px 12px;font-size:13px;color:var(--soluk);letter-spacing:.02em}
td{padding:10px 12px;border-top:1px solid var(--cizgi);vertical-align:top}
td.adres{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;word-break:break-all;min-width:260px}
td.adres a{color:var(--kod)}
.etiket{display:inline-block;font-size:12px;font-weight:600;padding:1px 8px;border-radius:10px;border:1px solid currentColor;white-space:nowrap;margin:1px 2px 1px 0}
.https{color:var(--yesil)}.http{color:var(--turuncu)}.kararsiz{color:var(--kirmizi)}.tr{color:var(--vurgu)}
.not{color:var(--soluk);font-size:13px}
a{color:var(--vurgu)}
code{font-family:ui-monospace,Menlo,Consolas,monospace;word-break:break-all}
footer{margin-top:48px;color:var(--soluk);font-size:13px;border-top:1px solid var(--cizgi);padding-top:16px}
.anatomi{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:15px;word-break:break-all;background:var(--kart);border:1px solid var(--cizgi);border-radius:10px;padding:14px}
.anatomi .k{color:var(--vurgu)}.anatomi .s{color:var(--turuncu);font-weight:700}
"""


def _e(m: str) -> str:
    return html.escape(m, quote=True)


def _satir(s: Site) -> str:
    etiketler = [f'<span class="etiket {s.sema.lower()}">{s.sema}</span>']
    if s.turkce:
        etiketler.append('<span class="etiket tr">Türkçe</span>')
    if s.kararsiz:
        etiketler.append('<span class="etiket kararsiz">Kararsız erişim</span>')
    kanit = _e(s.kanit_turu)
    if s.kanit.lower().startswith("http"):
        kanit = f'<a href="{_e(s.kanit)}" rel="noreferrer">{kanit}</a>'
    yorum = f'<div class="not">{_e(s.yorum)}</div>' if s.yorum else ""
    return (f"<tr><td><b>{_e(s.site_adi)}</b>{yorum}</td>"
            f'<td class="adres"><a href="{_e(s.url)}" rel="noreferrer">{_e(s.url)}</a></td>'
            f"<td>{''.join(etiketler)}</td><td>{kanit}</td></tr>")


def olustur(siteler: List[Site]) -> str:
    gruplar = kategorilere_ayir(siteler)
    toplam = len(siteler)
    https = sum(1 for s in siteler if s.sema == "HTTPS")
    kurum = len({s.adres for s in siteler})
    turkce = [s for s in siteler if s.turkce]
    zaman = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    en_buyuk = max(len(v) for v in gruplar.values())

    kategori_satirlari = "".join(
        f'<div class="satir"><span>{_e(v[0].kategori_tr)}</span>'
        f'<div class="cubuk" style="width:{len(v) / en_buyuk * 100:.1f}%"></div>'
        f'<span class="sayi">{len(v)}</span></div>'
        for v in sorted(gruplar.values(), key=len, reverse=True))

    kanit = Counter(s.kanit_turu for s in siteler)
    kanit_satirlari = "".join(
        f'<div class="satir"><span>{_e(k)}</span><div class="cubuk" style="width:{n / toplam * 100:.1f}%;background:var(--turuncu)"></div>'
        f'<span class="sayi">{n}</span></div>' for k, n in kanit.most_common())

    dizin = "".join(f'<a href="#k{i}">{_e(v[0].kategori_tr)} · {len(v)}</a>' for i, v in enumerate(gruplar.values()))

    bolumler = []
    for i, (kategori, liste) in enumerate(gruplar.items()):
        satirlar = "".join(_satir(s) for s in sorted(liste, key=lambda x: x.site_adi.lower()))
        bolumler.append(
            f'<h3 id="k{i}">{_e(liste[0].kategori_tr)} <span class="not">({_e(kategori)} · {len(liste)} site)</span></h3>'
            f'<div class="tablo-sar"><table><thead><tr><th>Site</th><th>Onion adresi</th><th>Özellikler</th><th>Kanıt</th></tr></thead>'
            f"<tbody>{satirlar}</tbody></table></div>")

    turkce_tablo = "".join(_satir(s) for s in turkce)
    ornek = next((s for s in siteler if s.adres.startswith("bbcweb3")), siteler[0])

    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Onion Rehberi Raporu</title><style>{CSS}</style></head>
<body><main>
<div class="ust">Siber Güvenlik Eğitimi · Onion Rehberi</div>
<h1>Gerçek Kurumların Onion Adresleri</h1>
<p class="alt">Kaynak: Real-World Onion Sites (Alec Muffett, CC BY-SA) · Rapor oluşturma zamanı: {zaman}</p>

<div class="kartlar">
<div class="kart"><b>{toplam}</b><span>listelenen onion adresi</span></div>
<div class="kart"><b>{len(gruplar)}</b><span>kategori</span></div>
<div class="kart"><b>%{https / toplam * 100:.0f}</b><span>HTTPS kullanıyor ({https}/{toplam})</span></div>
<div class="kart"><b>{kurum}</b><span>farklı onion servisi</span></div>
<div class="kart"><b>{len(turkce)}</b><span>Türkçe yayın</span></div>
</div>

<div class="kutu uyari"><p><b>Bu listeyi neden kullanıyoruz?</b> Onion adresleri 56 karakterlik, ezberlenemeyen dizilerdir ve sahte kopyaları çok yaygındır.
Bu liste, yalnızca kurumların kendilerinin duyurduğu ya da sertifikayla kanıtlanmış adresleri içerir. Bir adresi <b>arama motorundan değil, güvenilir kaynaktan</b> alın.</p></div>

<h2>Özet</h2>
<h3>Kategorilere göre dağılım</h3>
<div class="grafik">{kategori_satirlari}</div>
<h3>Adresin kuruma ait olduğu nasıl kanıtlanmış?</h3>
<div class="grafik">{kanit_satirlari}</div>
<div class="kutu ipucu">
<p><b>TLS sertifikası:</b> Kurum, onion adresi için bir sertifika almış; sertifika kurumun adını taşır.</p>
<p><b>Kurumun kendi duyurusu:</b> Kurum, normal web sitesinde bu onion adresini yayımlamış (Kanıt bağlantısına tıklayın).</p>
<p><b>Doğrulama bekliyor:</b> Liste editörü henüz bağımsız bir kanıt eklememiş. Bu adreslere ekstra dikkat.</p>
</div>

<h2>Bir onion adresinin anatomisi</h2>
<p>Örnek: <b>{_e(ornek.site_adi)}</b></p>
<div class="anatomi"><span class="k">{_e(ornek.adres[:51])}</span><span class="s">{_e(ornek.adres[51:])}</span>.onion</div>
<p class="not"><span style="color:var(--vurgu)">Mavi kısım</span> ≈ servisin 32 baytlık açık anahtarı. <span style="color:var(--turuncu)">Turuncu kısım</span> ≈ 2 baytlık sağlama toplamı ve sürüm (3).
Sağlama toplamı yazım hatalarını yakalar ama bir adresin gerçek sahibini <b>kanıtlamaz</b>. Terminalde deneyin: <code>python3 rehber.py anatomi {_e(ornek.adres)}.onion</code></p>

<h2>HTTP mi, HTTPS mi?</h2>
<div class="kutu"><p>Onion servislerinde trafik, HTTP olsa bile Tor tarafından uçtan uca şifrelenir. <b>HTTPS</b> ek olarak sertifika yoluyla sitenin kimliğini kanıtlar.
Bu yüzden onion üzerinde HTTP, normal internetteki HTTP kadar tehlikeli değildir; ama HTTPS daha güçlü bir kimlik güvencesi verir.</p></div>

<h2>Türkçe yayınlar</h2>
<div class="tablo-sar"><table><thead><tr><th>Site</th><th>Onion adresi</th><th>Özellikler</th><th>Kanıt</th></tr></thead><tbody>{turkce_tablo}</tbody></table></div>

<h2>Tüm liste</h2>
<div class="dizin">{dizin}</div>
{''.join(bolumler)}

<footer>
<p>Veri: <a href="https://github.com/alecmuffett/real-world-onion-sites">Real-World Onion Sites</a> — Alec Muffett, CC BY-SA. SecureDrop kayıtları: securedrop.org dizini.
Bu rapor Onion Rehberi {__version__} ile oluşturuldu. Liste zamanla değişir; güncellemek için <code>python3 rehber.py guncelle</code>.</p>
<p>Bu rapor dışarıdan hiçbir kaynak yüklemez ve JavaScript kullanmaz; Tor Browser'ın “Safest” seviyesinde de çalışır.</p>
</footer>
</main></body></html>
"""
