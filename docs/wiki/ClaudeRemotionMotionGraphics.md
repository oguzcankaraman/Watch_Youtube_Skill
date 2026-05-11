**Özet:** Claude AI ve Remotion (React tabanlı video framework'ü) kullanarak animasyonlu sayaç grafikleri ve premium motion graphics üretme yöntemi; Claude prompt ile kod üretir, Remotion bu kodu videoya render eder.
**Teknolojiler:** Claude AI (claude.ai), Remotion, React, JavaScript/TypeScript
**Bağlantılar:** [[CinematicPastelLUT]], [[ClaudeCodeWatchYoutube]]
**Kaynak Video:** [[Videos#8oIFBQ9BhVU]] — Made with Claude + Remotion

---

## 1. Genel Akış

```
Claude AI  →  Remotion kodu üret  →  React bileşeni render et  →  Video overlay
```

Claude, doğal dil promptlarıyla Remotion için React kodu yazar. Bu kod Remotion aracılığıyla video frame'lerine render edilir ve motion graphic overlay olarak kullanılır.

---

## 2. Remotion Nedir?

[Remotion](https://www.remotion.dev/), React ile programatik video üretmeyi sağlayan bir framework'tür.

- Her video frame, bir React bileşenidir
- CSS animasyonları ve JavaScript ile tam kontrol sağlar
- `npm run build` ile MP4/WebM çıktısı alınır
- Stil sahibi animasyonlar için kod tabanlı bir yaklaşım sunar

---

## 3. Animasyonlu Sayaç Grafiği (Örnek Kullanım)

Videoda gösterilen örnek: **animasyonlu sayı sayacı** ($123, $409 gibi değerlere ulaşan sayaçlar).

### Claude'a Gönderilecek Prompt Yapısı
```
"Remotion kullanarak animasyonlu sayı sayacı bileşeni yaz.
Başlangıç: 0
Bitiş: 409
Süre: 2 saniye
Stil: turuncu/amber, büyük yazı tipi, soldan içeri giren animasyon"
```

### Claude'un Ürettiği Çıktı
- Hazır Remotion React bileşeni (`.tsx`)
- `useCurrentFrame()` ve `interpolate()` hook'larını kullanan sayaç mantığı
- Direkt kullanılabilir, düzenleme gerektirmeyen kod

---

## 4. Kullanım Senaryoları

| Grafik Türü | Claude Prompt Fikri |
|---|---|
| Para sayacı | "$0'dan $409'a 2sn'de say" |
| İstatistik vurgusu | "1M views animasyonu, scale-up ile gir" |
| Yüzde göstergesi | "%0'dan %82'ye dolu progress bar" |
| Geri sayım | "10'dan 0'a sayaç, kırmızı renk" |

---

## 5. Kurulum (Remotion)

```bash
npm create remotion@latest
cd my-video
npm install
npm run dev   # tarayıcıda önizleme
npm run build # MP4 çıktısı
```

---

## 6. Claude + Remotion İpuçları

- Claude, Remotion API'sini iyi tanır — doğrudan "Remotion ile X yap" diyebilirsin
- Kodu claude.ai'deki **Artifacts** özelliğiyle önizleyebilirsin
- Renk, font, hız gibi parametreleri promptta belirt; Claude bileşene yansıtır
- Üretilen bileşeni Premiere Pro veya DaVinci Resolve'e video dosyası olarak import edip overlay kullanabilirsin
