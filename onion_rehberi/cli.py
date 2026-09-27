"""Komut satırı arayüzü. Çalıştırmak için: python3 rehber.py  (ya da python3 -m onion_rehberi)"""

import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import List

from . import __version__, ag, alistirma, onion, rapor, veri
from .tablo import (ayrac, camgobegi, cubuk_grafik, kalin, kirmizi, mavi, mor, panel,
                    renkleri_ayarla, sari, soluk, tablo, yesil)

# ------------------------------------------------------------------ yardımcılar


def _yukle(securedrop: bool = True) -> List[veri.Site]:
    try:
        siteler = veri.yukle(securedrop=securedrop)
    except ValueError as e:
        sys.exit(kirmizi(f"Veri dosyası okunamadı: {e}"))
    if not siteler:
        sys.exit(kirmizi(f"Veri bulunamadı. '{veri.ANA_LISTE}' dosyası var mı?"))
    return siteler


def _sema(s: veri.Site) -> str:
    return yesil("HTTPS") if s.sema == "HTTPS" else sari("HTTP")


def _durum(s: veri.Site) -> str:
    etiketler = []
    if s.turkce:
        etiketler.append(mavi("Türkçe"))
    if s.kararsiz:
        etiketler.append(kirmizi("Kararsız"))
    return " ".join(etiketler) or soluk("—")


def _kategori_filtrele(siteler, sorgu):
    if not sorgu:
        return siteler
    eslesen = veri.kategori_bul(siteler, sorgu)
    if not eslesen:
        sys.exit(kirmizi(f"'{sorgu}' ile eşleşen kategori yok. Kategorileri görmek için: python3 rehber.py kategoriler"))
    return [s for s in siteler if s.kategori in eslesen]


# ------------------------------------------------------------------ komutlar


def cmd_ozet(args):
    siteler = _yukle()
    gruplar = veri.kategorilere_ayir(siteler)
    https = sum(1 for s in siteler if s.sema == "HTTPS")
    turkce = [s for s in siteler if s.turkce]

    print(ayrac("GENEL BAKIŞ"))
    print(panel("Real-World Onion Sites", [
        f"Toplam adres        : {kalin(str(len(siteler)))}",
        f"Kategori            : {kalin(str(len(gruplar)))}",
        f"HTTPS kullanan      : {kalin(str(https))} (%{https * 100 // len(siteler)})",
        f"Türkçe yayın        : {kalin(str(len(turkce)))}",
        f"Kararsız erişimli   : {kalin(str(sum(s.kararsiz for s in siteler)))}",
    ]))
    print()
    print(cubuk_grafik(sorted(((v[0].kategori_tr, len(v)) for v in gruplar.values()), key=lambda x: -x[1]),
                       "Kategorilere göre adres sayısı"))
    print()
    kanit = Counter(s.kanit_turu for s in siteler)
    print(cubuk_grafik(kanit.most_common(), "Adresin kuruma ait olduğu nasıl kanıtlanmış?", renk=mor))
    print()
    print(tablo(["Türkçe yayın", "Onion adresi", "Şifreleme"],
                [[s.site_adi, s.url, _sema(s)] for s in turkce], esnek=[1], baslik="Türkçe yayınlar"))
    print(soluk("\nİpucu: Tüm listeyi görmek için 'liste', güzel bir rapor için 'rapor' komutunu deneyin."))


def cmd_kategoriler(args):
    siteler = _yukle()
    gruplar = veri.kategorilere_ayir(siteler)
    satirlar = [[v[0].kategori_tr, k, str(len(v)), str(sum(s.sema == "HTTPS" for s in v))]
                for k, v in gruplar.items()]
    print(tablo(["Kategori", "Özgün ad", "Adres", "HTTPS"], satirlar, baslik="Kategoriler"))
    print(soluk("\nBir kategoriyi listelemek için: python3 rehber.py liste -k haber"))


def cmd_liste(args):
    siteler = _kategori_filtrele(_yukle(), args.kategori)
    if args.turkce:
        siteler = [s for s in siteler if s.turkce]
    if args.http:
        siteler = [s for s in siteler if s.sema == "HTTP"]
    if not siteler:
        print(sari("Bu filtrelere uyan site yok."))
        return
    for grup in veri.kategorilere_ayir(siteler).values():
        grup = sorted(grup, key=lambda s: s.site_adi.lower())
        if args.genis:
            basliklar = ["#", "Site", "Onion adresi", "Şifreleme", "Kanıt", "Not"]
            satirlar = [[str(i), s.site_adi, s.url, _sema(s), s.kanit_turu, s.yorum or _durum(s)]
                        for i, s in enumerate(grup, 1)]
            esnek = [5, 4, 1, 2]
        else:
            basliklar = ["#", "Site", "Onion adresi", "Şifreleme", "Etiket"]
            satirlar = [[str(i), s.site_adi, s.url, _sema(s), _durum(s)] for i, s in enumerate(grup, 1)]
            esnek = [1, 2]
        print(tablo(basliklar, satirlar, esnek=esnek, baslik=f"{grup[0].kategori_tr}  ({len(grup)} site)"))
        print()
    print(soluk(f"Toplam {len(siteler)} adres. Bir adresi doğrulamak için: python3 rehber.py dogrula <adres>"))


def cmd_ara(args):
    siteler = _yukle()
    terim = args.terim.lower()
    bulunan = [s for s in siteler if terim in s.site_adi.lower() or terim in s.url.lower()
               or terim in s.kategori.lower() or terim in s.kategori_tr.lower()]
    if not bulunan:
        print(sari(f"'{args.terim}' için sonuç yok."))
        print(soluk("Unutmayın: Bir kurum bu listede yoksa, onion adresi olmadığı anlamına gelmez; "
                    "ama adresi kurumun kendi sitesinden (Onion-Location) doğrulamanız gerekir."))
        return
    print(tablo(["Site", "Kategori", "Onion adresi", "Şifreleme", "Kanıt"],
                [[s.site_adi, s.kategori_tr, s.url, _sema(s), s.kanit_turu] for s in bulunan],
                esnek=[0, 1, 2], baslik=f"'{args.terim}' için {len(bulunan)} sonuç"))


def cmd_dogrula(args):
    siteler = _yukle()
    a = onion.analiz_et(args.adres)
    print(ayrac("ADRES DOĞRULAMA"))
    if a.tur == "gecersiz":
        print(panel("SONUÇ: GEÇERSİZ", [kirmizi("✖ " + a.hata),
              "Bir v3 onion adresi 56 karakterdir ve yalnızca a-z harfleri ile 2-7 rakamlarını içerir."], renk=kirmizi))
        return 1
    if a.tur == "v2":
        print(panel("SONUÇ: ESKİ ADRES", [sari("⚠ " + a.hata)], renk=sari))
        return 1

    kontroller = [
        ["1. Biçim (56 karakter, base32)", yesil("✔ uygun")],
        ["2. Sürüm baytı", yesil("✔ 3 (v3)") if a.surum_gecerli else kirmizi(f"✖ {a.surum} (3 olmalı)")],
        ["3. Sağlama toplamı", yesil("✔ geçerli") if a.saglama_gecerli else
         kirmizi(f"✖ bozuk (bulunan {a.saglama_bulunan.hex()}, olması gereken {a.saglama_hesaplanan.hex()})")],
    ]
    # Aynı onion servisi birden çok sayfada kullanılabilir (ör. BBC'nin dil sayfaları).
    # Girilen URL listedeki bir URL ile birebir eşleşiyorsa o kaydı öne alıyoruz.
    girdi_url = args.adres.strip().lower().rstrip("/")
    listede = sorted((s for s in siteler if s.adres == a.adres),
                     key=lambda s: s.url.lower().rstrip("/") != girdi_url)
    kontroller.append(["4. Güvenilir listede mi?",
                       yesil(f"✔ evet: {listede[0].site_adi}") if listede else sari("✖ hayır")])
    print(tablo(["Kontrol", "Sonuç"], kontroller, esnek=[1]))
    print()

    benzerler, gorulen = [], set()
    if not listede:
        for s in siteler:
            neden = onion.benzerlik_nedeni(a.adres, s.adres)
            if neden and s.adres not in gorulen:
                gorulen.add(s.adres)
                benzerler.append((s, neden))

    if listede:
        s = listede[0]
        ek = [f"Kurum      : {kalin(s.site_adi)}", f"Kategori   : {s.kategori_tr}",
              f"Kanıt türü : {s.kanit_turu}"]
        if s.kanit.lower().startswith("http"):
            ek.append(f"Kanıt      : {s.kanit}")
        if len(listede) > 1:
            ek.append(f"Aynı onion servisi listede {len(listede)} sayfada kullanılıyor (aynı kurumun farklı dil/bölüm sayfaları).")
        print(panel("SONUÇ: DOĞRULANDI", [yesil("✔ Bu adres güvenilir listede kayıtlı.")] + ek, renk=yesil))
    elif not a.gecerli_v3:
        print(panel("SONUÇ: SAHTE YA DA HATALI", [
            kirmizi("✖ Sağlama toplamı tutmuyor. Bu adres ya yanlış yazılmış ya da kaba bir taklit."),
            "Tor Browser bu adresi zaten açmaz. Adresi kaynağından yeniden kopyalayın."]
            + [f"  → Listedeki {kalin(s.site_adi)} adresine benziyor: {neden}" for s, neden in benzerler[:2]],
            renk=kirmizi))
    elif benzerler:
        satirlar = [kirmizi("⚠ Biçim doğru ama bu adres listede YOK ve listedeki bir adrese çok benziyor!")]
        for s, neden in benzerler[:3]:
            satirlar.append(f"  → {kalin(s.site_adi)}: {neden}")
            satirlar.append(f"    gerçek: {s.adres}")
            satirlar.append(f"    sizin : {a.adres}")
        satirlar.append("Bu tam olarak bir oltalama (phishing) sitesinden beklenecek durumdur. Bu adresi KULLANMAYIN.")
        print(panel("SONUÇ: ŞÜPHELİ", satirlar, renk=kirmizi))
    else:
        print(panel("SONUÇ: DOĞRULANAMADI", [
            sari("⚠ Adresin biçimi doğru, ama güvenilir listede yok."),
            "Bu, adresin sahte olduğunu kanıtlamaz; yalnızca bu araçla doğrulanamadığını gösterir.",
            "Kurumun normal sitesine gidin ve Tor Browser'daki '.onion available' düğmesiyle karşılaştırın."], renk=sari))
    return 0


def cmd_anatomi(args):
    a = onion.analiz_et(args.adres)
    if a.tur != "v3":
        print(kirmizi(a.hata or "v3 adresi değil."))
        return 1
    print(ayrac("BİR ONION ADRESİNİN ANATOMİSİ"))
    print()
    print("  " + kalin(mavi(a.adres[:51])) + kalin(sari(a.adres[51:])) + ".onion")
    print("  " + mavi("└" + "─" * 49 + "┘") + sari("└───┘"))
    print("  " + mavi("≈ açık anahtar (32 bayt)".center(51)) + sari("sağlama+sürüm"))
    print()
    anahtar = a.acik_anahtar.hex()
    print(tablo(["Parça", "Değer", "Açıklama"], [
        ["Açık anahtar", anahtar[:32] + "\n" + anahtar[32:], "Servisin ed25519 açık anahtarı. Adresin kendisi bu anahtardır."],
        ["Sağlama (adreste)", a.saglama_bulunan.hex(), "Adresin içinde yazan 2 bayt"],
        ["Sağlama (hesaplanan)", a.saglama_hesaplanan.hex(), "SHA3-256('.onion checksum' + anahtar + sürüm) ilk 2 baytı"],
        ["Sürüm", str(a.surum), "v3 adresleri için her zaman 3"],
        ["Sonuç", yesil("✔ tutarlı") if a.gecerli_v3 else kirmizi("✖ tutarsız"),
         "İki sağlama değeri aynıysa adreste yazım hatası yoktur"],
    ], esnek=[2]))
    print()
    print(panel("Ne öğrendik?", [
        "• Onion adresi rastgele bir isim değil, servisin açık anahtarıdır. Bu yüzden 'bbc.onion' gibi kısa adresler olamaz.",
        "• Adres, sahibinin anahtarından türediği için başkası aynı adresi kullanamaz; ama BENZER bir adres üretebilir.",
        "• Sağlama toplamı yazım hatalarını yakalar; adresin DOĞRU KURUMA ait olduğunu kanıtlamaz.",
        f"• Deneyin: {camgobegi('python3 rehber.py alistirma')}",
    ]))


def cmd_rapor(args):
    siteler = _yukle()
    hedef = Path(args.cikti).resolve()
    hedef.write_text(rapor.olustur(siteler), encoding="utf-8")
    print(yesil(f"✔ Rapor oluşturuldu: {hedef}"))
    print(soluk("Tor Browser'da açın: Dosya → Dosya Aç (Ctrl+O). Rapor JavaScript kullanmaz, 'Safest' seviyesinde de çalışır."))


def cmd_alistirma(args):
    siteler = _yukle(securedrop=False)
    sorular = alistirma.sorular_uret(siteler, args.adet)
    etkilesimli = sys.stdin.isatty() and not args.cevaplari_goster
    print(ayrac("SAHTE ADRESİ YAKALA"))
    print("Her soruda bir kurum adı ve bir onion adresi göreceksiniz.")
    print("Adres gerçekten o kuruma mı ait? " + kalin("g") + " = gerçek, " + kalin("s") + " = sahte\n")
    puan = 0
    for i, soru in enumerate(sorular, 1):
        print(kalin(f"Soru {i}/{len(sorular)}  ") + f"Kurum: {kalin(soru.kurum)}")
        print("  " + camgobegi(soru.adres + ".onion"))
        if etkilesimli:
            cevap = ""
            while cevap not in ("g", "s"):
                try:
                    cevap = input("  Tahmininiz (g/s): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return
            dogru = (cevap == "g") == soru.gercek
            puan += dogru
            print("  " + (yesil("✔ Doğru!") if dogru else kirmizi("✖ Yanlış.")), end=" ")
        print(("GERÇEK. " if soru.gercek else "SAHTE. ") + soru.aciklama)
        if not soru.gercek:
            print(soluk("  Listedeki gerçek adres: ") + soru.gercek_adres + soluk(".onion"))
        a = onion.analiz_et(soru.adres)
        print(soluk(f"  Sağlama toplamı: {'geçerli' if a.saglama_gecerli else 'BOZUK'}  ·  "
                    f"Listede: {'evet' if soru.gercek else 'hayır'}\n"))
    if etkilesimli:
        print(panel("Puanınız", [f"{puan} / {len(sorular)}",
                                 "Sağlama toplamı geçerli olan sahteleri nasıl yakaladınız? "
                                 "Yakalayamadıysanız: tek güvenilir yöntem adresi kaynağıyla karşılaştırmak."]))


def cmd_disa_aktar(args):
    siteler = _kategori_filtrele(_yukle(), args.kategori)
    if args.turkce:
        siteler = [s for s in siteler if s.turkce]
    if not siteler:
        sys.exit(sari("Bu filtrelere uyan site yok."))
    kayitlar = [{"kategori": s.kategori_tr, "site": s.site_adi, "onion_url": s.url, "adres": s.adres,
                 "sifreleme": s.sema, "kanit_turu": s.kanit_turu, "kanit": s.kanit, "turkce": s.turkce,
                 "kararsiz": s.kararsiz, "not": s.yorum, "kaynak": s.kaynak} for s in siteler]
    hedef = Path(args.cikti or f"onion_listesi.{args.bicim}")
    if args.bicim == "json":
        hedef.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        with hedef.open("w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: Excel Türkçe karakterleri doğru açar
            yazici = csv.DictWriter(f, fieldnames=list(kayitlar[0].keys()))
            yazici.writeheader()
            yazici.writerows(kayitlar)
    print(yesil(f"✔ {len(kayitlar)} kayıt yazıldı: {hedef.resolve()}"))


def cmd_guncelle(args):
    print("Liste GitHub'dan indiriliyor… (Whonix'te Tor üzerinden gider, biraz sürebilir)")
    try:
        eklenen, cikan = ag.guncelle()
    except Exception as e:  # noqa: BLE001
        sys.exit(kirmizi(f"Güncelleme başarısız: {e}"))
    print(yesil("✔ Liste güncellendi. Önceki sürüm '.onceki.csv' olarak yedeklendi."))
    if not eklenen and not cikan:
        print(soluk("Değişiklik yok."))
    if eklenen:
        print(tablo(["Eklenen site", "Adres"], [[a, u] for a, u in eklenen], esnek=[1], baslik=f"{len(eklenen)} yeni kayıt"))
    if cikan:
        print(tablo(["Çıkarılan site", "Adres"], [[a, u] for a, u in cikan], esnek=[1], baslik=f"{len(cikan)} kayıt çıkarıldı"))


def cmd_kontrol(args):
    yer = ag.ortam()
    if yer != "workstation" and not args.ortami_zorla:
        print(panel("DURDURULDU: Whonix Workstation değil", [
            kirmizi("Bu komut yalnızca Whonix Workstation içinde çalışır."),
            "Normal bir bilgisayarda .onion adreslerine bağlanmaya çalışmak, adreslerin DNS sorgusunun "
            "internet sağlayıcınıza gitmesine yol açabilir. Bu bir DNS sızıntısıdır (1. gün, Bölüm 10).",
            "Whonix'te ise tüm trafik ve DNS, Gateway üzerinden Tor'a gider.",
        ] + (["Gateway üzerinde çalıştırmayın: Gateway'de gezinti ve bağlantı denemesi yapılmaz."] if yer == "gateway" else []),
            renk=kirmizi))
        return 2
    siteler = _kategori_filtrele(_yukle(), args.kategori)
    siteler = list({s.adres: s for s in siteler}.values())  # aynı servise bir kez bağlan
    siteler = siteler[: args.adet]
    print(f"{len(siteler)} onion servisine sırayla bağlanılacak (her biri en fazla {ag.ZAMAN_ASIMI} sn).")
    print(soluk("Yalnızca güvenilir listedeki adreslere istek atılır. İptal: Ctrl+C\n"))
    renkler = {"acik": yesil, "yonlendirme": camgobegi, "istemci_hatasi": sari, "sunucu_hatasi": sari}
    etiketler = {"acik": "AÇIK", "yonlendirme": "YÖNLENDİRME", "istemci_hatasi": "ERİŞİM REDDİ",
                 "sunucu_hatasi": "SUNUCU HATASI", "hata": "ULAŞILAMADI", "zaman_asimi": "ZAMAN AŞIMI"}
    sonuclar = []
    try:
        for i, s in enumerate(siteler, 1):
            print(f"  [{i}/{len(siteler)}] {s.site_adi} … ", end="", flush=True)
            durum, kod, sure, aciklama = ag.eris(s.url)
            renk = renkler.get(durum, kirmizi)
            print(renk(etiketler[durum]) + soluk(f" ({kod or aciklama}, {sure:.1f} sn)"))
            sonuclar.append([s.site_adi, renk(etiketler[durum]), str(kod or "—"), f"{sure:.1f}", aciklama or "—"])
            time.sleep(1)  # servisleri gereksiz yormamak için
    except KeyboardInterrupt:
        print(sari("\nKullanıcı tarafından durduruldu."))
    if sonuclar:
        print()
        print(tablo(["Site", "Durum", "HTTP", "Süre (sn)", "Açıklama"], sonuclar, esnek=[0, 4], baslik="Erişim kontrolü"))
        print(soluk("\nDüşünün: Onion servislerine bağlanmak neden normal sitelerden daha uzun sürüyor? "
                    "(İpucu: kaç röle, iki taraflı devre)"))


# ------------------------------------------------------------------ menü


MENU = [
    ("Genel bakış", ["ozet"]),
    ("Kategoriler", ["kategoriler"]),
    ("Türkçe yayınları listele", ["liste", "--turkce"]),
    ("Tüm listeyi göster", ["liste"]),
    ("Arama yap", None),
    ("Bir adresi doğrula", None),
    ("Adres anatomisi (BBC örneği)", ["anatomi", "bbcweb3hytmzhn5d532owbu6oqadra5z3ar726vq5kgwwn6aucdccrad.onion"]),
    ("Sahte adresi yakala (alıştırma)", ["alistirma"]),
    ("HTML raporu oluştur", ["rapor"]),
]


def menu(parser):
    while True:
        print()
        print(ayrac(f"ONION REHBERİ {__version__}"))
        for i, (ad, _) in enumerate(MENU, 1):
            print(f"  {kalin(str(i))}. {ad}")
        print(f"  {kalin('0')}. Çıkış")
        try:
            secim = input("\nSeçiminiz: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if secim == "0":
            return 0
        if not secim.isdigit() or not 1 <= int(secim) <= len(MENU):
            print(sari("Geçersiz seçim."))
            continue
        ad, arg = MENU[int(secim) - 1]
        try:
            if arg is None and ad.startswith("Arama"):
                arg = ["ara", input("Aranacak kelime: ").strip() or "bbc"]
            elif arg is None:
                arg = ["dogrula", input("Onion adresi: ").strip()]
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        args = parser.parse_args(arg)
        args.func(args)
        try:
            input(soluk("\nDevam etmek için Enter'a basın…"))
        except (EOFError, KeyboardInterrupt):
            print()
            return 0


# ------------------------------------------------------------------ argparse


def parser_olustur():
    p = argparse.ArgumentParser(
        prog="rehber.py",
        description="Onion Rehberi: gerçek kurumların onion adreslerini inceleme ve doğrulama aracı (eğitim amaçlı).",
        epilog="Örnekler:\n  python3 rehber.py ozet\n  python3 rehber.py liste -k haber --turkce\n"
               "  python3 rehber.py dogrula https://www.bbcweb3...onion/turkce\n  python3 rehber.py rapor",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--renksiz", action="store_true", help="renkli çıktıyı kapat")
    p.add_argument("--surum", action="version", version=f"Onion Rehberi {__version__}")
    alt = p.add_subparsers(title="komutlar", metavar="KOMUT")

    k = alt.add_parser("ozet", help="genel bakış: sayılar ve grafikler")
    k.set_defaults(func=cmd_ozet)

    k = alt.add_parser("kategoriler", help="kategorileri listele")
    k.set_defaults(func=cmd_kategoriler)

    k = alt.add_parser("liste", help="siteleri tablo halinde listele")
    k.add_argument("-k", "--kategori", help="kategori adı ya da bir kısmı (ör. haber, bbc, teknoloji)")
    k.add_argument("--turkce", action="store_true", help="yalnızca Türkçe yayınlar")
    k.add_argument("--http", action="store_true", help="yalnızca HTTP (sertifikasız) adresler")
    k.add_argument("--genis", action="store_true", help="kanıt ve not sütunlarını da göster")
    k.set_defaults(func=cmd_liste)

    k = alt.add_parser("ara", help="site adında, adreste veya kategoride ara")
    k.add_argument("terim")
    k.set_defaults(func=cmd_ara)

    k = alt.add_parser("dogrula", help="bir onion adresini listeyle ve sağlama toplamıyla doğrula")
    k.add_argument("adres", help="onion adresi ya da URL")
    k.set_defaults(func=cmd_dogrula)

    k = alt.add_parser("anatomi", help="bir onion adresinin parçalarını açıkla")
    k.add_argument("adres")
    k.set_defaults(func=cmd_anatomi)

    k = alt.add_parser("rapor", help="Tor Browser'da açılacak HTML raporu oluştur")
    k.add_argument("-o", "--cikti", default="onion_raporu.html", help="dosya adı (varsayılan: onion_raporu.html)")
    k.set_defaults(func=cmd_rapor)

    k = alt.add_parser("alistirma", help="'sahte adresi yakala' alıştırması")
    k.add_argument("-n", "--adet", type=int, default=6, help="soru sayısı (varsayılan 6)")
    k.add_argument("--cevaplari-goster", action="store_true", help="soru sormadan cevaplarıyla yazdır (eğitmen için)")
    k.set_defaults(func=cmd_alistirma)

    k = alt.add_parser("disa-aktar", help="listeyi CSV ya da JSON olarak dışa aktar")
    k.add_argument("-f", "--bicim", choices=["csv", "json"], default="csv")
    k.add_argument("-k", "--kategori")
    k.add_argument("--turkce", action="store_true", help="yalnızca Türkçe yayınlar")
    k.add_argument("-o", "--cikti")
    k.set_defaults(func=cmd_disa_aktar)

    k = alt.add_parser("guncelle", help="listenin en güncel halini GitHub'dan indir ve farkları göster")
    k.set_defaults(func=cmd_guncelle)

    k = alt.add_parser("kontrol", help="(yalnızca Whonix Workstation) servislerin erişilebilirliğini Tor üzerinden test et")
    k.add_argument("-k", "--kategori")
    k.add_argument("-n", "--adet", type=int, default=10, choices=range(1, 51), metavar="1-50",
                   help="en fazla kaç servis denensin (varsayılan 10)")
    k.add_argument("--ortami-zorla", action="store_true", help=argparse.SUPPRESS)
    k.set_defaults(func=cmd_kontrol)
    return p


def main(argv=None) -> int:
    parser = parser_olustur()
    args = parser.parse_args(argv)
    renkleri_ayarla(args.renksiz)
    if not hasattr(args, "func"):
        if sys.stdin.isatty():
            return menu(parser) or 0
        parser.print_help()
        return 0
    try:
        return args.func(args) or 0
    except BrokenPipeError:  # ör. çıktı 'head' komutuna yönlendirilip kesildiğinde
        sys.stderr.close()
        return 0
    except KeyboardInterrupt:
        print()
        return 130
