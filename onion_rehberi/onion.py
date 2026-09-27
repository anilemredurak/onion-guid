"""
Onion (v3) adreslerini çözümleme ve doğrulama.

Bir v3 onion adresi 56 karakterlik bir base32 metnidir ve içinde üç parça saklar:

    adres = base32( ACIK_ANAHTAR (32 bayt) | SAGLAMA (2 bayt) | SURUM (1 bayt) ) + ".onion"

    SAGLAMA = SHA3-256(".onion checksum" | ACIK_ANAHTAR | SURUM) ilk 2 baytı
    SURUM   = 0x03

Sağlama toplamı yalnızca YAZIM HATALARINI yakalar. Geçerli bir sağlama toplamı,
adresin "doğru kuruma" ait olduğunu KANITLAMAZ. Bu yüzden bu araç her adresi
ayrıca güvenilir listeyle karşılaştırır.
"""

import base64
import hashlib
import os
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

V3_UZUNLUK = 56
V2_UZUNLUK = 16
SURUM_V3 = 3
BASE32_KARAKTERLER = "abcdefghijklmnopqrstuvwxyz234567"
_ONION_ETIKETI = re.compile(r"([a-z2-7]{16}|[a-z2-7]{56})\.onion$")


@dataclass
class AdresAnalizi:
    girdi: str
    adres: Optional[str]          # yalnızca 56 karakterlik kısım (".onion" olmadan)
    tur: str                      # "v3", "v2", "gecersiz"
    acik_anahtar: bytes = b""
    saglama_bulunan: bytes = b""
    saglama_hesaplanan: bytes = b""
    surum: Optional[int] = None
    hata: str = ""

    @property
    def saglama_gecerli(self) -> bool:
        return self.tur == "v3" and self.saglama_bulunan == self.saglama_hesaplanan

    @property
    def surum_gecerli(self) -> bool:
        return self.surum == SURUM_V3

    @property
    def gecerli_v3(self) -> bool:
        return self.tur == "v3" and self.saglama_gecerli and self.surum_gecerli


def adres_cikar(metin: str) -> Optional[str]:
    """URL ya da ana makine adından onion adresini (".onion" olmadan) çıkarır.

    Örnek: "https://www.bbcweb3...onion/turkce" -> "bbcweb3..."
    """
    metin = metin.strip().lower()
    if not metin:
        return None
    if "://" not in metin:
        metin = "http://" + metin
    host = urlparse(metin).hostname or ""
    eslesme = _ONION_ETIKETI.search(host)
    if not eslesme:
        return None
    return eslesme.group(1)


def saglama_hesapla(acik_anahtar: bytes, surum: int = SURUM_V3) -> bytes:
    veri = b".onion checksum" + acik_anahtar + bytes([surum])
    return hashlib.sha3_256(veri).digest()[:2]


def analiz_et(metin: str) -> AdresAnalizi:
    adres = adres_cikar(metin)
    if adres is None:
        # Kullanıcı ".onion" yazmadan yalnızca 56 karakteri de verebilir
        yalin = metin.strip().lower()
        if re.fullmatch(r"[a-z2-7]{56}", yalin):
            adres = yalin
        else:
            return AdresAnalizi(metin, None, "gecersiz",
                                hata="Geçerli bir .onion adresi bulunamadı (56 karakter, a-z ve 2-7).")
    if len(adres) == V2_UZUNLUK:
        return AdresAnalizi(metin, adres, "v2",
                            hata="Bu eski bir v2 adresi. v2 adresleri 2021'den beri Tor tarafından desteklenmiyor.")
    ham = base64.b32decode(adres.upper())
    acik_anahtar, saglama, surum = ham[:32], ham[32:34], ham[34]
    return AdresAnalizi(
        girdi=metin, adres=adres, tur="v3", acik_anahtar=acik_anahtar,
        saglama_bulunan=saglama, saglama_hesaplanan=saglama_hesapla(acik_anahtar, surum),
        surum=surum,
    )


def adres_olustur(acik_anahtar: bytes, surum: int = SURUM_V3) -> str:
    """32 baytlık açık anahtardan v3 adresi üretir (".onion" olmadan)."""
    ham = acik_anahtar + saglama_hesapla(acik_anahtar, surum) + bytes([surum])
    return base64.b32encode(ham).decode().lower()


def rastgele_gecerli_adres() -> str:
    """Sağlama toplamı geçerli ama HİÇBİR kuruma ait olmayan bir adres üretir.

    Not: Rastgele baytlar her zaman geçerli bir ed25519 anahtarı değildir;
    bu adres yalnızca "biçimi doğru ama sahibi belirsiz" örneği olarak kullanılır.
    """
    return adres_olustur(os.urandom(32))


def harf_degistir(adres: str, konum: Optional[int] = None) -> str:
    """Adreste tek bir karakteri değiştirir: tipik bir yazım hatası / kaba taklit."""
    import random
    konum = random.randrange(8, 50) if konum is None else konum
    eski = adres[konum]
    yeni = random.choice([k for k in BASE32_KARAKTERLER if k != eski])
    return adres[:konum] + yeni + adres[konum + 1:]


def benzer_taklit(adres: str) -> str:
    """Başı ve sonu gerçeğe benzeyen ama sağlama toplamı GEÇERLİ olan bir taklit üretir.

    Açık anahtarın ortasındaki birkaç baytı değiştirip sağlama toplamını yeniden
    hesaplarız. Sonuç: ilk karakterleri aynı, biçimsel olarak kusursuz, ama
    tamamen başka bir adres. Gerçek saldırganlar benzerini "vanity" araçlarıyla üretir.
    """
    ham = bytearray(base64.b32decode(adres.upper())[:32])
    for i in range(12, 20):
        ham[i] = os.urandom(1)[0]
    return adres_olustur(bytes(ham))


def ortak_onek(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def fark_sayisi(a: str, b: str) -> int:
    if len(a) != len(b):
        return max(len(a), len(b))
    return sum(1 for x, y in zip(a, b) if x != y)


def benzerlik_nedeni(aday: str, bilinen: str) -> Optional[str]:
    """İki farklı adres şüpheli derecede benziyorsa nedenini döndürür."""
    if aday == bilinen:
        return None
    onek = ortak_onek(aday, bilinen)
    fark = fark_sayisi(aday, bilinen)
    if fark <= 4:
        return f"yalnızca {fark} karakter farklı"
    if onek >= 6:
        return f"ilk {onek} karakteri aynı"
    return None
