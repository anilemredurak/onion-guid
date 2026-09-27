"""Real-World Onion Sites (RWOS) veri dosyalarını okur."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from . import onion

PROJE_KOKU = Path(__file__).resolve().parent.parent
VERI_KLASORU = PROJE_KOKU / "veri"
ANA_LISTE = VERI_KLASORU / "master.csv"
SECUREDROP_LISTESI = VERI_KLASORU / "securedrop-api.csv"

BEKLENEN_SUTUNLAR = {"category", "flaky", "site_name", "onion_url", "proof_url", "comment"}

KATEGORI_ADLARI = {
    "Blogs": "Bloglar",
    "Civil Society and Community": "Sivil Toplum ve Topluluk",
    "Education": "Eğitim",
    "Government": "Devlet",
    "News": "Haber",
    "News BBC World Service": "Haber · BBC World Service",
    "News Deutsche Welle World": "Haber · Deutsche Welle",
    "News RFERL & VOA": "Haber · RFE/RL ve VOA",
    "Search Engines": "Arama Motorları",
    "Social Networks": "Sosyal Ağlar",
    "Tech and Software": "Teknoloji ve Yazılım",
    "Web and Internet": "Web ve İnternet",
    "SecureDrop": "SecureDrop (ihbar kutuları)",
}

TURKCE_IPUCLARI = ("türkçe", "turkish", "turkce", "/turkce", "/tr/", "amerika'nın sesi")


@dataclass
class Site:
    kategori: str
    site_adi: str
    url: str
    kanit: str
    yorum: str
    kararsiz: bool
    kaynak: str                     # "RWOS" veya "SecureDrop"
    adres: str = field(init=False)  # 56 karakterlik onion adresi

    def __post_init__(self):
        self.adres = onion.adres_cikar(self.url) or ""

    @property
    def kategori_tr(self) -> str:
        return KATEGORI_ADLARI.get(self.kategori, self.kategori)

    @property
    def sema(self) -> str:
        return "HTTPS" if self.url.lower().startswith("https://") else "HTTP"

    @property
    def turkce(self) -> bool:
        metin = (self.site_adi + " " + self.url).lower()
        return any(ipucu in metin for ipucu in TURKCE_IPUCLARI)

    @property
    def kanit_turu(self) -> str:
        k = self.kanit.strip().lower()
        if k == "ssl":
            return "TLS sertifikası"
        if k in ("tbc", ""):
            return "Doğrulama bekliyor"
        return "Kurumun kendi duyurusu"


def _oku(yol: Path, kaynak: str) -> List[Site]:
    if not yol.exists():
        return []
    with yol.open(encoding="utf-8", newline="") as f:
        okuyucu = csv.DictReader(f)
        eksik = BEKLENEN_SUTUNLAR - set(okuyucu.fieldnames or [])
        if eksik:
            raise ValueError(f"{yol.name} beklenen sütunları içermiyor: {', '.join(sorted(eksik))}")
        siteler = []
        for satir in okuyucu:
            siteler.append(Site(
                kategori=satir["category"].strip(),
                site_adi=satir["site_name"].strip(),
                url=satir["onion_url"].strip(),
                kanit=(satir.get("proof_url") or "").strip(),
                yorum=(satir.get("comment") or "").strip(),
                kararsiz=(satir.get("flaky") or "").strip().upper() == "TRUE",
                kaynak=kaynak,
            ))
        return siteler


def yukle(securedrop: bool = True, klasor: Optional[Path] = None) -> List[Site]:
    klasor = klasor or VERI_KLASORU
    siteler = _oku(klasor / ANA_LISTE.name, "RWOS")
    if securedrop:
        siteler += _oku(klasor / SECUREDROP_LISTESI.name, "SecureDrop")
    return siteler


def kategorilere_ayir(siteler: List[Site]) -> Dict[str, List[Site]]:
    gruplar: Dict[str, List[Site]] = {}
    for s in siteler:
        gruplar.setdefault(s.kategori, []).append(s)
    # SecureDrop en sona, diğerleri alfabetik
    return dict(sorted(gruplar.items(), key=lambda kv: (kv[0] == "SecureDrop", kv[0])))


def kategori_bul(siteler: List[Site], sorgu: str) -> List[str]:
    """Kullanıcının yazdığı kategori adını (Türkçe ya da İngilizce, kısmi) eşleştirir."""
    sorgu = sorgu.lower().strip()
    tumu = sorted({s.kategori for s in siteler})
    return [k for k in tumu if sorgu in k.lower() or sorgu in KATEGORI_ADLARI.get(k, k).lower()]
