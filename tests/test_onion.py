"""Testler. Çalıştırmak için proje klasöründe:  python3 -m unittest -v"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))

from onion_rehberi import alistirma, onion, rapor, veri  # noqa: E402

BBC = "bbcweb3hytmzhn5d532owbu6oqadra5z3ar726vq5kgwwn6aucdccrad"


class AdresTestleri(unittest.TestCase):
    def test_url_den_adres_cikar(self):
        self.assertEqual(onion.adres_cikar(f"https://www.{BBC}.onion/turkce"), BBC)
        self.assertEqual(onion.adres_cikar(f"{BBC}.onion"), BBC)
        self.assertEqual(onion.adres_cikar(f"http://forums.{BBC}.onion/x?y=1"), BBC)
        self.assertIsNone(onion.adres_cikar("https://example.com"))

    def test_gercek_adres_gecerli(self):
        a = onion.analiz_et(BBC + ".onion")
        self.assertTrue(a.gecerli_v3)
        self.assertEqual(a.surum, 3)
        self.assertEqual(len(a.acik_anahtar), 32)

    def test_listedeki_tum_adresler_gecerli(self):
        for s in veri.yukle():
            with self.subTest(site=s.site_adi):
                self.assertTrue(onion.analiz_et(s.url).gecerli_v3, s.url)

    def test_tek_harf_degisince_saglama_bozulur(self):
        bozuk = onion.harf_degistir(BBC, konum=20)
        self.assertNotEqual(bozuk, BBC)
        self.assertFalse(onion.analiz_et(bozuk).saglama_gecerli)

    def test_uretilen_adresler_gecerli(self):
        self.assertTrue(onion.analiz_et(onion.rastgele_gecerli_adres()).gecerli_v3)
        taklit = onion.benzer_taklit(BBC)
        self.assertTrue(onion.analiz_et(taklit).gecerli_v3)
        self.assertNotEqual(taklit, BBC)
        self.assertTrue(taklit.startswith(BBC[:19]))

    def test_adres_olustur_ters_islem(self):
        a = onion.analiz_et(BBC)
        self.assertEqual(onion.adres_olustur(a.acik_anahtar), BBC)

    def test_v2_ve_gecersiz(self):
        self.assertEqual(onion.analiz_et("expyuzz4wqqyqhjn.onion").tur, "v2")
        self.assertEqual(onion.analiz_et("google.com").tur, "gecersiz")

    def test_benzerlik(self):
        self.assertIsNone(onion.benzerlik_nedeni(BBC, BBC))
        self.assertIn("karakter farklı", onion.benzerlik_nedeni(onion.harf_degistir(BBC, 30), BBC))
        self.assertIn("ilk", onion.benzerlik_nedeni(onion.benzer_taklit(BBC), BBC))
        self.assertIsNone(onion.benzerlik_nedeni(onion.rastgele_gecerli_adres(), BBC))


class VeriTestleri(unittest.TestCase):
    def test_veri_yuklenir(self):
        siteler = veri.yukle()
        self.assertGreater(len(siteler), 100)
        self.assertTrue(any(s.turkce for s in siteler))
        self.assertTrue(all(s.adres for s in siteler))

    def test_kategori_turkce_eslesir(self):
        siteler = veri.yukle()
        self.assertIn("Tech and Software", veri.kategori_bul(siteler, "teknoloji"))
        self.assertIn("News BBC World Service", veri.kategori_bul(siteler, "bbc"))

    def test_alistirma(self):
        sorular = alistirma.sorular_uret(veri.yukle(), 8)
        self.assertEqual(len(sorular), 8)
        for s in sorular:
            self.assertEqual(s.gercek, s.tur == "gercek")
            self.assertTrue(s.gercek_adres)

    def test_rapor_dis_kaynak_icermez(self):
        html = rapor.olustur(veri.yukle())
        self.assertIn("<!doctype html>", html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("googleapis", html)


class KomutTestleri(unittest.TestCase):
    def calistir(self, *arg):
        return subprocess.run([sys.executable, str(KOK / "rehber.py"), "--renksiz", *arg],
                              capture_output=True, text=True, cwd=KOK)

    def test_komutlar_calisir(self):
        for arg in (["ozet"], ["kategoriler"], ["liste", "--turkce"], ["ara", "debian"],
                    ["anatomi", BBC], ["alistirma", "--cevaplari-goster"]):
            with self.subTest(komut=arg):
                p = self.calistir(*arg)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertTrue(p.stdout.strip())

    def test_dogrula_sonuclari(self):
        self.assertIn("DOĞRULANDI", self.calistir("dogrula", f"https://www.{BBC}.onion/turkce").stdout)
        self.assertIn("SAHTE", self.calistir("dogrula", onion.harf_degistir(BBC, 25)).stdout)
        self.assertIn("ŞÜPHELİ", self.calistir("dogrula", onion.benzer_taklit(BBC)).stdout)

    def test_kontrol_whonix_disinda_durur(self):
        p = self.calistir("kontrol")
        self.assertEqual(p.returncode, 2)
        self.assertIn("DNS sızıntısı", p.stdout)

    def test_disa_aktar_json(self):
        hedef = KOK / "tests" / "_gecici.json"
        try:
            p = self.calistir("disa-aktar", "-f", "json", "--turkce", "-o", str(hedef))
            self.assertEqual(p.returncode, 0, p.stderr)
            kayitlar = json.loads(hedef.read_text(encoding="utf-8"))
            self.assertTrue(all(k["turkce"] for k in kayitlar))
        finally:
            hedef.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
