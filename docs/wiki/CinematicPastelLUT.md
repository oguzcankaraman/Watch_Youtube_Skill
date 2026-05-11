**Özet:** YouTube içerik üreticileri için "Soft Pastel Studio" adlı sinematik bir LUT (Look-Up Table) renk düzeltme tekniği; kaldırılmış gölgeler, yumuşak vurgular, teal-turuncu renk tonu ve düşük kontrastle stüdyo estetiği sağlar.
**Teknolojiler:** .cube LUT, Adobe Premiere Pro, DaVinci Resolve, Final Cut Pro, OBS, Lumetri Color
**Bağlantılar:** [[ClaudeRemotionMotionGraphics]]
**Kaynak Video:** [[Videos#8oIFBQ9BhVU]] — Made with Claude + Remotion

---

## 1. Soft Pastel Studio LUT Nedir?

Soft Pastel Studio, 33×33 boyutunda bir `.cube` LUT dosyasıdır. YouTube stüdyo videolarına sinematik, temiz bir görünüm kazandırmak için tasarlanmıştır.

### Görsel Karakteristikler (The Look)

| Özellik | Açıklama |
|---|---|
| Lifted shadows | Gölgeler siyaha düşmez — matte/film hissi |
| Soft highlight rolloff | Vurgular patlamaz, doğal solar |
| Subtle teal in shadows | Gölgelerde hafif teal renk tonu |
| Warm peach in highlights | Vurgularda sıcak şeftali rengi |
| Skin-tone friendly | Ten renkleri için tasarlanmış midtone ısısı |
| Reduced saturation | ~%82 doygunluk — aşırı canlılığı önler |
| Low contrast | Temiz stüdyo estetiği için düşük kontrast |

---

## 2. Uygulanacak Yazılıma Göre Adımlar

### Adobe Premiere Pro
```
Lumetri Color → Creative → Look → Browse → .cube dosyasını seç
```

### DaVinci Resolve
```
LUT klasörüne .cube dosyasını koy
→ Node üzerinde sağ klik → 3D LUT → Soft Pastel Studio
```

### Final Cut Pro
```
Effects → Custom LUT → Import
```

### OBS
```
Filters → Apply LUT → Browse → dosyayı seç
```

---

## 3. Kullanım İpuçları

- **Opaklık**: LUT'u %70–100 opaklık/yoğunlukta uygula
- **Sıralama**: Pozlama ve beyaz dengesi düzeltmesinden **sonra** uygula; önce temel renk düzeltmesini yap
- **Teal sorunu**: Teal etkisi fazla geliyorsa LUT'tan önce ilgili kanalı kaldır, ardından intensiti %50'ye düşür
- **İnce ayar**: İstediğin zaman sıcaklık, doygunluk veya kontrast değerlerini üstüne ekleyebilirsin

---

## 4. LUT Ne Zaman Kullanılmalı?

- Stüdyo/podcast tarzı YouTube videoları için idealdir
- Sabit arka plan ışığıyla çekilmiş çekimler için en iyi sonucu verir
- Dış mekan veya yüksek kontrastlı sahnelerde teal etkisi aşırıya kaçabilir → intensiti düşür
