"""Terminal çıktısı: renkler, kutulu tablolar, çubuk grafikler. Yalnızca standart kütüphane."""

import os
import shutil
import sys
import unicodedata
from typing import List, Optional, Sequence

# ------------------------------------------------------------------ renkler

RENK_ACIK = True


def renkleri_ayarla(zorla_kapat: bool = False) -> None:
    global RENK_ACIK
    if os.name == "nt":
        os.system("")  # Windows terminalinde ANSI renklerini etkinleştirir
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    RENK_ACIK = not zorla_kapat and sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _r(kod: str, metin: str) -> str:
    return f"\033[{kod}m{metin}\033[0m" if RENK_ACIK else metin


def kalin(m): return _r("1", m)
def soluk(m): return _r("2", m)
def yesil(m): return _r("32", m)
def kirmizi(m): return _r("31", m)
def sari(m): return _r("33", m)
def mavi(m): return _r("34", m)
def camgobegi(m): return _r("36", m)
def mor(m): return _r("35", m)


# ------------------------------------------------------------------ genişlik hesabı

def _gorunur(metin: str) -> str:
    """ANSI renk kodlarını çıkarır."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", metin)


def genislik(metin: str) -> int:
    """Terminalde kaplanan sütun sayısı (Çince/Japonca karakterler 2 sütun)."""
    toplam = 0
    for ch in _gorunur(metin):
        if unicodedata.combining(ch):
            continue
        toplam += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return toplam


def terminal_genisligi() -> int:
    return max(60, min(shutil.get_terminal_size((100, 24)).columns, 160))


def sar(metin: str, en: int) -> List[str]:
    """Metni verilen genişliğe böler; sığmayan uzun kelimeleri (ör. onion adresleri) keser."""
    if en <= 0:
        return [metin]
    satirlar, simdiki = [], ""
    for kelime in metin.split(" "):
        aday = f"{simdiki} {kelime}" if simdiki else kelime
        if genislik(aday) <= en:
            simdiki = aday
            continue
        if simdiki:
            satirlar.append(simdiki)
            simdiki = ""
        while genislik(kelime) > en:
            parca, kelime = _kes(kelime, en)
            satirlar.append(parca)
        simdiki = kelime
    satirlar.append(simdiki)
    return satirlar


def _kes(kelime: str, en: int):
    parca = ""
    for i, ch in enumerate(kelime):
        if genislik(parca + ch) > en:
            if not parca:  # tek karakter bile sığmıyorsa yine de ilerle
                return ch, kelime[i + 1:]
            return parca, kelime[i:]
        parca += ch
    return parca, ""


# ------------------------------------------------------------------ tablo

def tablo(basliklar: Sequence[str], satirlar: Sequence[Sequence[str]],
          esnek: Optional[Sequence[int]] = None, baslik: str = "") -> str:
    """Kutulu tablo çizer. `esnek`: gerektiğinde daraltılabilecek sütunların indeksleri."""
    sutun_sayisi = len(basliklar)
    dogal = [genislik(b) for b in basliklar]
    for satir in satirlar:
        for i, hucre in enumerate(satir):
            dogal[i] = max(dogal[i], max((genislik(p) for p in str(hucre).split("\n")), default=0))

    toplam_sinir = 3 * sutun_sayisi + 1
    hedef = terminal_genisligi()
    en = list(dogal)
    # Sığmıyorsa esnek sütunları VERİLEN SIRAYLA daraltırız: listede önce yazılan sütun önce daralır.
    esnek = list(esnek) if esnek is not None else list(range(sutun_sayisi))
    for i in esnek:
        taban = min(dogal[i], 12)
        while sum(en) + toplam_sinir > hedef and en[i] > taban:
            en[i] -= 1

    def cizgi(sol, orta, sag):
        return sol + orta.join("─" * (w + 2) for w in en) + sag

    def satir_ciz(hucreler, bicim=lambda x: x):
        parcali = []
        for i, h in enumerate(hucreler):
            satirlar_ = []
            for p in str(h).split("\n"):
                satirlar_.extend(sar(p, en[i]))
            parcali.append(satirlar_)
        yukseklik = max(len(p) for p in parcali)
        cikti = []
        for r in range(yukseklik):
            hucre_metinleri = []
            for i, p in enumerate(parcali):
                m = p[r] if r < len(p) else ""
                hucre_metinleri.append(" " + bicim(m) + " " * (en[i] - genislik(m)) + " ")
            cikti.append("│" + "│".join(hucre_metinleri) + "│")
        return cikti

    parcalar = []
    if baslik:
        parcalar.append(kalin(baslik))
    parcalar.append(cizgi("┌", "┬", "┐"))
    parcalar.extend(satir_ciz(basliklar, lambda x: kalin(camgobegi(x))))
    parcalar.append(cizgi("├", "┼", "┤"))
    for satir in satirlar:
        parcalar.extend(satir_ciz(satir))
    parcalar.append(cizgi("└", "┴", "┘"))
    return "\n".join(parcalar)


# ------------------------------------------------------------------ çubuk grafik ve paneller

def cubuk_grafik(veriler: Sequence[tuple], baslik: str = "", renk=mavi) -> str:
    """veriler: [(etiket, sayı), ...] -> yatay çubuk grafik."""
    if not veriler:
        return ""
    etiket_en = max(genislik(e) for e, _ in veriler)
    en_buyuk = max(s for _, s in veriler) or 1
    cubuk_alani = max(10, terminal_genisligi() - etiket_en - 12)
    satirlar = [kalin(baslik)] if baslik else []
    for etiket, sayi in veriler:
        uzunluk = max(1, round(sayi / en_buyuk * cubuk_alani)) if sayi else 0
        satirlar.append(f"  {etiket}{' ' * (etiket_en - genislik(etiket))}  {renk('█' * uzunluk)} {sayi}")
    return "\n".join(satirlar)


def panel(baslik: str, satirlar: List[str], renk=camgobegi) -> str:
    en = min(terminal_genisligi() - 4, max([genislik(baslik) + 4] + [genislik(s) + 4 for s in satirlar]))
    ust = "╭─ " + kalin(renk(baslik)) + " " + "─" * max(0, en - genislik(baslik) - 3) + "╮"
    govde = []
    for s in satirlar:
        girinti = len(s) - len(s.lstrip(" "))
        for p in sar(s.lstrip(" "), en - 2 - girinti):
            p = " " * girinti + p
            govde.append("│ " + p + " " * (en - 2 - genislik(p)) + " │")
    return "\n".join([ust] + govde + ["╰" + "─" * en + "╯"])


def ayrac(baslik: str = "") -> str:
    en = terminal_genisligi()
    if not baslik:
        return soluk("─" * en)
    return kalin(camgobegi(f"━━ {baslik} ")) + camgobegi("━" * max(0, en - genislik(baslik) - 4))
