# Onion Rehberi: Öğrenci Görevleri

Bu görevler, Whonix eğitiminin 2. günündeki **Föy 2 (Workstation)** ile birlikte kullanılmak üzere hazırlanmıştır. Görevleri **Whonix Workstation** içinde, eğitmen denetiminde yapın.

Her görevin sonunda cevaplarınızı laboratuvar defterinize yazın. Defterinizi `script` komutuyla tutuyorsanız, komut çıktıları zaten kayda geçer.

**Kurallar:** Yalnızca bu araçla ve eğitmenin verdiği adreslerle çalışın. Dosya indirmeyin, hiçbir yere kayıt olmayın, kişisel hesaplarınıza giriş yapmayın.

---

## Görev 1 · Keşif (10 dk)

```bash
python3 rehber.py ozet
python3 rehber.py kategoriler
```

1. Listede kaç adres var? Kaç **farklı** onion servisi var? (İpucu: `rapor` komutunun ürettiği sayfadaki kartlara bakın.) Bu iki sayı neden farklı?
2. BBC'nin 42 kaydı var ama hepsi aynı onion adresini kullanıyor. Bu nasıl mümkün? URL'nin hangi kısmı değişiyor?
3. HTTPS kullanan adreslerin oranı nedir? Hangi kategoride HTTP daha yaygın? Onion üzerinde HTTP kullanmak, normal internetteki kadar tehlikeli mi? Neden?

## Görev 2 · Türkçe yayınlar ve kaynak doğrulama (15 dk)

```bash
python3 rehber.py liste --turkce
```

1. Türkçe yayın yapan üç onion servisini not edin.
2. Tor Browser'da **BBC Türkçe**'nin normal sitesine (`bbc.com/turkce`) gidin. Adres çubuğunda **“.onion available”** düğmesi çıkıyor mu? Çıkıyorsa tıklayın; çıkmıyorsa bunu da bulgu olarak not edin ve aynı denemeyi Deutsche Welle (`dw.com/tr`) için yapın.
3. Tor Browser'ın gösterdiği onion adresini doğrulayın:
   ```bash
   python3 rehber.py dogrula <Tor Browser'dan kopyaladığınız adres>
   ```
4. Üç kaynak (araç, Onion-Location, liste) aynı adresi mi veriyor?

## Görev 3 · Bir adresin anatomisi (15 dk)

```bash
python3 rehber.py anatomi duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion
```

1. Adresin hangi kısmı açık anahtar, hangi kısmı sağlama toplamı?
2. DuckDuckGo'nun adresi neden "duckduckgo" ile başlıyor? Bu adres nasıl üretilmiş olabilir? (Araştırın: *vanity onion address*)
3. **Kod görevi:** Sağlama toplamını Python'da kendiniz hesaplayın. `python3` yazıp etkileşimli kabuğu açın:
   ```python
   import base64, hashlib
   adres = "duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad"
   ham = base64.b32decode(adres.upper())
   anahtar, saglama, surum = ham[:32], ham[32:34], ham[34]
   hesap = hashlib.sha3_256(b".onion checksum" + anahtar + bytes([surum])).digest()[:2]
   print(saglama.hex(), hesap.hex(), surum)
   ```
   İki değer aynı mı? Şimdi adresteki bir harfi değiştirip tekrar deneyin. Ne oldu?

## Görev 4 · Sahte adresi yakala (15 dk)

```bash
python3 rehber.py alistirma -n 8
```

1. Puanınız kaç? Hangi soruda yanıldınız?
2. Üç tür sahte adres var. Her birini kendi cümlenizle açıklayın:
   - tek harfi değişmiş adres
   - başı benzeyen ama sağlama toplamı **geçerli** adres
   - rastgele geçerli adres
3. Hangi tür sahte adresi yalnızca sağlama toplamına bakarak **yakalayamazsınız**? O zaman neye güvenmelisiniz?

## Görev 5 · Arama motoru doğrulama değildir (20 dk)

Bu görev Föy 2, Görev B ile birlikte yapılır.

1. Tor Browser'da Ahmia'ya gidin (güvenlik seviyesini geçici olarak **Safer** yapın). Eğitmenin verdiği terimleri arayın: *Debian, Tor Project, DuckDuckGo*.
2. Bulduğunuz her onion adresini araçla doğrulayın:
   ```bash
   python3 rehber.py dogrula <adres>
   ```
3. Sonuçları tabloya yazın: `DOĞRULANDI`, `DOĞRULANAMADI`, `ŞÜPHELİ` ya da `SAHTE`.
4. `DOĞRULANAMADI` sonucu, adresin sahte olduğunu kanıtlar mı? Neden?
5. İş bitince güvenlik seviyesini **Safest**'a geri alın.

## Görev 6 · Rapor (10 dk)

```bash
python3 rehber.py rapor
```

1. `onion_raporu.html` dosyasını Tor Browser'da açın (Ctrl+O). Güvenlik seviyesi **Safest** iken sayfa düzgün görünüyor mu?
2. Rapor neden JavaScript kullanmıyor? Tor Browser kullanıcısı için bunun önemi ne?
3. "Adresin kuruma ait olduğu nasıl kanıtlanmış?" grafiğini yorumlayın. Hangi kanıt türü en güçlü? "Doğrulama bekliyor" olanlara nasıl yaklaşmalısınız?

## Görev 7 · Erişim ölçümü (yalnızca Whonix, 15 dk)

```bash
python3 rehber.py kontrol -k teknoloji -n 5
```

1. Servislerin kaçı açık? Ortalama bağlantı süresi ne kadar?
2. Onion servislerine bağlanmak normal sitelerden neden daha uzun sürüyor? (İpucu: devrede kaç röle var; istemci ve servis tarafı.)
3. Aynı komutu Whonix dışında (ör. host bilgisayarda) çalıştırsaydınız araç ne derdi? Neden?

## Görev 8 · Liste değişiyor mu? (10 dk)

```bash
python3 rehber.py guncelle
```

1. Eklenen ya da çıkarılan site var mı?
2. Güvenilir bir listenin **güncel** olması neden önemli? Eski bir listeye güvenmenin riski ne olabilir?

## Görev 9 · İleri seviye: kod katkısı

1. Testleri çalıştırın: `python3 -m unittest -v`. Hepsi geçiyor mu?
2. `onion_rehberi/onion.py` içindeki `saglama_hesapla` fonksiyonunda `".onion checksum"` metnini bilerek bozun ve testleri tekrar çalıştırın. Hangi testler başarısız oldu? Neden? (Sonra düzeltin!)
3. Araca yeni bir özellik ekleyin. Örneğin `liste` komutuna yalnızca HTTPS adresleri gösteren bir `--https` seçeneği. Değişikliğinizi ayrı bir git dalında (`git switch -c ozellik/https-filtresi`) yapın ve eğitmene gösterin.

---

### Değerlendirme soruları

1. Bir onion adresinin "doğru" olduğunu kanıtlamak için hangi üç kontrolü birlikte kullanırsınız?
2. Sağlama toplamı ile dijital sertifika (TLS) arasındaki fark nedir? Hangisi kimliği kanıtlar?
3. Bu aracı kullanırken hangi güvenlik kararları sizi korudu? (İpucu: README'deki “Güvenlik tasarımı” bölümü.)
