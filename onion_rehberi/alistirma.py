"""
"Sahte adresi yakala" alıştırması.

Öğrenciye bir kurum adı ve bir onion adresi gösterilir; öğrenci adresin gerçek mi
sahte mi olduğunu tahmin eder. Üç tür sahte adres vardır:

  1. Tek harfi değişmiş adres      -> sağlama toplamı BOZUK (araç yakalar)
  2. Başı benzeyen, geçerli taklit  -> sağlama toplamı GEÇERLİ ama listede YOK
  3. Rastgele geçerli adres         -> biçim doğru, sahibi belirsiz

Ders: Sağlama toplamı yalnızca yazım hatasını yakalar. Asıl güvence, adresi
güvenilir kaynakla karşılaştırmaktır.
"""

import random
from dataclasses import dataclass
from typing import List

from . import onion
from .veri import Site


@dataclass
class Soru:
    kurum: str
    adres: str
    gercek: bool
    tur: str          # "gercek", "harf", "taklit", "rastgele"
    aciklama: str
    gercek_adres: str = ""


def sorular_uret(siteler: List[Site], adet: int = 6) -> List[Soru]:
    havuz = [s for s in siteler if s.adres and s.kaynak == "RWOS"]
    secilen = random.sample(havuz, min(adet, len(havuz)))
    turler = (["gercek", "harf", "taklit", "rastgele"] * adet)[:adet]
    random.shuffle(turler)
    sorular = []
    for site, tur in zip(secilen, turler):
        onceki = len(sorular)
        if tur == "gercek":
            sorular.append(Soru(site.site_adi, site.adres, True, tur,
                                "Adres listedeki adresle birebir aynı ve sağlama toplamı geçerli."))
        elif tur == "harf":
            sorular.append(Soru(site.site_adi, onion.harf_degistir(site.adres), False, tur,
                                "Tek bir karakter değiştirilmiş. Sağlama toplamı tutmuyor: bu bir yazım hatası ya da kaba bir taklit."))
        elif tur == "taklit":
            sorular.append(Soru(site.site_adi, onion.benzer_taklit(site.adres), False, tur,
                                "Başı ve sonu gerçeğe benziyor, sağlama toplamı da GEÇERLİ. Ama listede yok! "
                                "Yalnızca sağlama toplamına güvenen biri kandırılırdı."))
        else:
            sorular.append(Soru(site.site_adi, onion.rastgele_gecerli_adres(), False, tur,
                                "Biçimi kusursuz ama bu kurumla hiçbir ilgisi yok. Sahibi belirsiz bir adres."))
        sorular[onceki].gercek_adres = site.adres
    return sorular
