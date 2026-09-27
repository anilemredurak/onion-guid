"""
Ağ işlemleri: listeyi güncelleme ve (yalnızca Whonix Workstation içinde) erişilebilirlik kontrolü.

GÜVENLİK NOTU
Normal bir bilgisayarda bir .onion adresine bağlanmaya çalışmak, adresin DNS
sorgusunun internet sağlayıcınıza gitmesine yol açabilir (DNS sızıntısı). Bu
yüzden `kontrol` komutu yalnızca Whonix Workstation içinde çalışır: orada tüm
trafik ve DNS, Gateway üzerinden Tor'a gider.
"""

import csv
import io
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple

from . import veri

GUNCEL_LISTE_URL = "https://raw.githubusercontent.com/alecmuffett/real-world-onion-sites/master/master.csv"
GUNCEL_SECUREDROP_URL = "https://raw.githubusercontent.com/alecmuffett/real-world-onion-sites/master/securedrop-api.csv"
ZAMAN_ASIMI = 60
TARAYICI_KIMLIGI = "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0"

# Whonix'in uygulamalar için önerdiği işaret dosyaları
# (https://www.whonix.org/wiki/Dev/Project_friendly_applications_best_practices)
WHONIX_WS_ISARETI = Path("/usr/share/anon-ws-base-files/workstation")
WHONIX_GW_ISARETI = Path("/usr/share/anon-gw-base-files/gateway")


def ortam() -> str:
    """'workstation', 'gateway' ya da 'diger' döndürür."""
    if WHONIX_GW_ISARETI.exists():
        return "gateway"
    if WHONIX_WS_ISARETI.exists():
        return "workstation"
    return "diger"


# ------------------------------------------------------------------ güncelleme

def _indir(url: str) -> str:
    istek = urllib.request.Request(url, headers={"User-Agent": TARAYICI_KIMLIGI})
    with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI) as yanit:
        return yanit.read().decode("utf-8")


def _adresler(metin: str) -> dict:
    okuyucu = csv.DictReader(io.StringIO(metin))
    eksik = veri.BEKLENEN_SUTUNLAR - set(okuyucu.fieldnames or [])
    if eksik:
        raise ValueError("İndirilen dosya beklenen biçimde değil: " + ", ".join(sorted(eksik)))
    return {s["onion_url"].strip(): s["site_name"].strip() for s in okuyucu}


def guncelle() -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Listeyi GitHub'dan indirir, eski dosyayı yedekler, eklenen/çıkarılan siteleri döndürür."""
    sonuc_eklenen, sonuc_cikan = [], []
    for url, hedef in ((GUNCEL_LISTE_URL, veri.ANA_LISTE), (GUNCEL_SECUREDROP_URL, veri.SECUREDROP_LISTESI)):
        yeni = _indir(url)
        yeni_adresler = _adresler(yeni)  # biçim kontrolü: bozuksa dosyaya yazmadan hata verir
        eski_adresler = _adresler(hedef.read_text(encoding="utf-8")) if hedef.exists() else {}
        sonuc_eklenen += [(ad, u) for u, ad in yeni_adresler.items() if u not in eski_adresler]
        sonuc_cikan += [(ad, u) for u, ad in eski_adresler.items() if u not in yeni_adresler]
        if hedef.exists():
            shutil.copy2(hedef, hedef.with_suffix(".onceki.csv"))
        hedef.write_text(yeni, encoding="utf-8")
    return sonuc_eklenen, sonuc_cikan


# ------------------------------------------------------------------ erişim kontrolü

def eris(url: str) -> Tuple[str, Optional[int], float, str]:
    """Bir onion URL'sine istek atar. Dönüş: (durum, http_kodu, süre_sn, açıklama)

    Whonix'te `curl`, uwt sarmalayıcısı sayesinde Tor'a ve ayrı bir devreye
    (stream isolation) yönlendirilir; bu yüzden varsa curl tercih edilir.
    """
    baslangic = time.monotonic()
    if shutil.which("curl"):
        komut = ["curl", "--silent", "--output", "/dev/null", "--max-time", str(ZAMAN_ASIMI),
                 "--user-agent", TARAYICI_KIMLIGI, "--write-out", "%{http_code}", url]
        try:
            p = subprocess.run(komut, capture_output=True, text=True, timeout=ZAMAN_ASIMI + 10)
        except subprocess.TimeoutExpired:
            return "zaman_asimi", None, time.monotonic() - baslangic, "zaman aşımı"
        sure = time.monotonic() - baslangic
        kod = int(p.stdout.strip() or 0)
        if p.returncode == 0 and kod:
            return _yorumla(kod), kod, sure, ""
        aciklama = {
            6: "adres çözümlenemedi", 7: "bağlanılamadı", 28: "zaman aşımı",
            35: "TLS el sıkışması başarısız", 60: "sertifika doğrulanamadı", 97: "SOCKS/Tor bağlantı hatası",
        }.get(p.returncode, f"curl hata kodu {p.returncode}")
        return "hata", None, sure, aciklama

    istek = urllib.request.Request(url, headers={"User-Agent": TARAYICI_KIMLIGI})
    try:
        with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI) as yanit:
            kod = yanit.status
        return _yorumla(kod), kod, time.monotonic() - baslangic, ""
    except urllib.error.HTTPError as e:
        return _yorumla(e.code), e.code, time.monotonic() - baslangic, ""
    except Exception as e:  # noqa: BLE001 - öğrenciye hatayı olduğu gibi göstermek istiyoruz
        return "hata", None, time.monotonic() - baslangic, type(e).__name__


def _yorumla(kod: int) -> str:
    if 200 <= kod < 300:
        return "acik"
    if 300 <= kod < 400:
        return "yonlendirme"
    if 400 <= kod < 500:
        return "istemci_hatasi"
    return "sunucu_hatasi"
