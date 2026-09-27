# Onion Rehberi

Gerçek kurumların (BBC, Deutsche Welle, Debian, Tor Project, DuckDuckGo…) **doğrulanmış** onion adreslerini terminalde tablolar ve grafiklerle inceleyen, adresleri doğrulayan ve sahte adresleri yakalamayı öğreten bir Python eğitim aracı.

Veri kaynağı [Real-World Onion Sites](https://github.com/alecmuffett/real-world-onion-sites) listesidir (Alec Muffett, CC BY-SA). Bu proje o listeyi Türkçe bir sınıf aracına dönüştürür.

> **Eğitim amaçlıdır ve eğitmen denetiminde kullanılmak üzere tasarlanmıştır.**
> Araç yalnızca güvenilir listedeki adreslerle çalışır; rastgele onion adreslerini taramaz, arama yapmaz, dosya indirmez.

---

## Ne öğretir?

| Kavram | Hangi komut? |
|---|---|
| Onion adresleri neden ezberlenemez, içinde ne var? | `anatomi` |
| Sağlama toplamı neyi yakalar, neyi **yakalayamaz**? | `dogrula`, `alistirma` |
| Bir adresi arama motorundan değil, kaynağından doğrulamak | `dogrula`, `ara` |
| Oltalama (phishing): başı benzeyen sahte adresler | `alistirma` |
| HTTP ve HTTPS'in onion üzerindeki farkı | `ozet`, `rapor` |
| DNS sızıntısı neden önemlidir? | `kontrol` (Whonix dışında neden çalışmadığını açıklar) |
| Verinin zamanla değişmesi, farkları izlemek | `guncelle` |

## Gereksinimler

- Python **3.8 veya üstü** (Whonix 17/18, Debian, Ubuntu, Kali, Parrot, Windows ve macOS'ta hazır bulunur)
- **Hiçbir ek paket gerekmez.** Yalnızca Python'un standart kütüphanesi kullanılır; `pip install` yok.

## Kurulum

```bash
git clone https://github.com/<kullanici-adi>/onion-rehberi.git
cd onion-rehberi
python3 rehber.py
```

Whonix Workstation içinde `git clone` otomatik olarak Tor üzerinden çalışır (biraz yavaş olabilir). Git yoksa GitHub'dan ZIP olarak indirip açabilirsiniz.

## Kullanım

Parametresiz çalıştırınca **menü** açılır:

```
python3 rehber.py
```

Ya da doğrudan komut verin:

| Komut | Ne yapar? | Örnek |
|---|---|---|
| `ozet` | Sayılar, kategori grafiği, kanıt türleri, Türkçe yayınlar | `python3 rehber.py ozet` |
| `kategoriler` | Kategorileri Türkçe ve özgün adlarıyla listeler | `python3 rehber.py kategoriler` |
| `liste` | Siteleri tablo halinde listeler | `python3 rehber.py liste -k haber --turkce` |
| `ara` | Site adında, adreste veya kategoride arar | `python3 rehber.py ara debian` |
| `dogrula` | Bir adresi sağlama toplamı ve listeyle doğrular, benzer sahte adresleri yakalar | `python3 rehber.py dogrula https://www.bbcweb3...onion/turkce` |
| `anatomi` | Adresin parçalarını (açık anahtar, sağlama, sürüm) gösterir | `python3 rehber.py anatomi duckduckgogg42...onion` |
| `alistirma` | "Sahte adresi yakala" oyunu | `python3 rehber.py alistirma -n 8` |
| `rapor` | Tor Browser'da açılacak HTML raporu üretir | `python3 rehber.py rapor` |
| `disa-aktar` | CSV (Excel uyumlu) ya da JSON olarak dışa aktarır | `python3 rehber.py disa-aktar -f json --turkce` |
| `guncelle` | Listenin en güncel halini indirir, eklenen/çıkan siteleri gösterir | `python3 rehber.py guncelle` |
| `kontrol` | **Yalnızca Whonix Workstation'da:** servislere Tor üzerinden bağlanıp erişilebilirliği ölçer | `python3 rehber.py kontrol -k teknoloji -n 5` |

Her komutun ayrıntılı yardımı: `python3 rehber.py <komut> --help`. Renkleri kapatmak için: `--renksiz`.

### Örnek çıktı

```
━━ GENEL BAKIŞ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╭─ Real-World Onion Sites ──────────╮
│ Toplam adres        : 171         │
│ Kategori            : 13          │
│ HTTPS kullanan      : 122 (%71)   │
│ Türkçe yayın        : 3           │
╰───────────────────────────────────╯

Kategorilere göre adres sayısı
  Haber · BBC World Service    █████████████████████████████████████████████ 42
  Haber · Deutsche Welle       █████████████████████████████████ 31
  SecureDrop (ihbar kutuları)  ██████████████████████████ 24
  ...
```

```
$ python3 rehber.py dogrula bbcweb3hytmzhn5d532ec7pnvceq2xlz3ar726vq5kgwwn6aucdlvjad.onion

╭─ SONUÇ: ŞÜPHELİ ───────────────────────────────────────────────────────────────╮
│ ⚠ Biçim doğru ama bu adres listede YOK ve listedeki bir adrese çok benziyor!   │
│   → BBC Learning English: ilk 19 karakteri aynı                                │
│     gerçek: bbcweb3hytmzhn5d532owbu6oqadra5z3ar726vq5kgwwn6aucdccrad           │
│     sizin : bbcweb3hytmzhn5d532ec7pnvceq2xlz3ar726vq5kgwwn6aucdlvjad           │
│ Bu tam olarak bir oltalama (phishing) sitesinden beklenecek durumdur.          │
╰────────────────────────────────────────────────────────────────────────────────╯
```

### HTML raporu

`python3 rehber.py rapor` komutu `onion_raporu.html` dosyasını üretir. Tor Browser'da **Dosya → Dosya Aç** (Ctrl+O) ile açın. Raporda özet kartlar, grafikler, bir adresin anatomisi, Türkçe yayınlar ve kategorilere göre tüm liste bulunur.

Rapor dışarıdan **hiçbir şey yüklemez** ve **JavaScript kullanmaz**. Bu yüzden Tor Browser'ın en sıkı güvenlik seviyesinde (Safest) de tam çalışır.

## Güvenlik tasarımı

- **Yalnızca standart kütüphane.** Dışarıdan paket kurulmaz; tedarik zinciri riski yoktur ve kod baştan sona okunabilir.
- **`kontrol` yalnızca Whonix Workstation'da çalışır.** Normal bir bilgisayarda bir `.onion` adresine bağlanmaya çalışmak, adresin DNS sorgusunun internet sağlayıcınıza gitmesine yol açabilir (DNS sızıntısı). Araç Whonix dışında bu komutu çalıştırmayı reddeder ve nedenini açıklar. Gateway üzerinde de çalışmaz.
- **Yalnızca listedeki adreslere istek atılır.** `kontrol` kullanıcıdan adres almaz; en fazla 50 servis, sırayla ve aralarında bekleyerek denenir.
- **`guncelle` önce doğrular, sonra yazar.** İndirilen dosya beklenen biçimde değilse eski listeye dokunulmaz; eski liste `.onceki.csv` olarak yedeklenir.
- **Whonix'te `curl` tercih edilir.** Whonix'in curl sarmalayıcısı her uygulamayı ayrı Tor devresine yönlendirir (stream isolation).

## Proje yapısı

```
onion-rehberi/
├── rehber.py                # başlatıcı
├── onion_rehberi/
│   ├── cli.py               # komutlar ve menü
│   ├── onion.py             # v3 adres çözümleme, sağlama toplamı, benzerlik
│   ├── veri.py              # CSV okuma, kategoriler
│   ├── tablo.py             # terminal tabloları, grafikler, renkler
│   ├── rapor.py             # HTML raporu
│   ├── alistirma.py         # "sahte adresi yakala"
│   └── ag.py                # güncelleme ve erişim kontrolü
├── veri/
│   ├── master.csv           # Real-World Onion Sites listesi
│   ├── securedrop-api.csv   # SecureDrop dizini
│   └── KAYNAK.md            # veri kaynağı ve lisansı
├── tests/test_onion.py
└── GOREVLER.md              # öğrenci görevleri
```

Kodu okumak da dersin parçasıdır: sağlama toplamının nasıl hesaplandığını görmek için `onion_rehberi/onion.py` dosyasındaki `saglama_hesapla` fonksiyonuna bakın.

## Testler

```bash
python3 -m unittest -v
```

Testler, listedeki **tüm** adreslerin sağlama toplamının geçerli olduğunu da doğrular.

## Öğrenci görevleri

Sınıfta kullanılacak adım adım görevler için [GOREVLER.md](GOREVLER.md) dosyasına bakın.

## Lisans ve atıf

- **Kod:** MIT Lisansı ([LICENSE](LICENSE)).
- **Veri** (`veri/` klasörü): [Real-World Onion Sites](https://github.com/alecmuffett/real-world-onion-sites), Alec Muffett, **CC BY-SA** lisanslıdır. SecureDrop kayıtları [securedrop.org dizininden](https://securedrop.org/directory/) derlenmiştir. Ayrıntılar: [veri/KAYNAK.md](veri/KAYNAK.md).

Bu liste, kurumların kendilerinin duyurduğu adreslerden oluşur. Bir kurumun listede olmaması onion adresi olmadığı anlamına gelmez; listede olması da içeriğini onayladığımız anlamına gelmez.
