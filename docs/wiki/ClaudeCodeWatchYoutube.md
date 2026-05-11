# Claude Code — YouTube Video İzleme Skill'i

**Özet:** Claude Code'a YouTube videolarını "izleme" yeteneği kazandıran bir skill; transcript + ekran görüntülerini birleştirerek Claude'un hem söylenenlerİ hem görülenleri anlamasını sağlar.
**Teknolojiler:** Claude Code, YouTube-DL, FFmpeg, VTT transcript, storyboard grid, Vision LLM
**Bağlantılar:** [[Videos]]
**Kaynak Video:** [QZMljuD10sU](https://www.youtube.com/watch?v=QZMljuD10sU)

---

## Problem

Sadece transcript çekmek yeterli değildir çünkü önemli bilgilerin büyük kısmı ekranda gösterilir, sesli anlatılmaz. Örneğin bir kodlama videosunda ekrandaki kod satırları, grafikler veya diagram değişiklikleri transcript'e yansımaz.

## Çözüm: Frames + Transcript Birleşimi

Bu skill iki şeyi birleştirir:

1. **Frame-by-frame ekran görüntüleri** — FFmpeg ile belirli timestamp'lerde alınan kareler
2. **Transcript** — VTT/SRT altyazı dosyası

İkisi birleştirilerek **storyboard grid** oluşturulur: her kare altında o andaki transcript metni yazar. Claude bu grid'i okuyunca hem görseli hem de sözlü içeriği birlikte görür.

## Pipeline Mimarisi

```
YouTube URL
    │
    ▼
YouTube-DL       → Transcript (VTT/SRT) + Video MP4 indir
    │
    ▼
NLP Analiz       → spaCy ile akıllı timestamp seçimi
    │              (keyword eşleşmesi + sessizlik tespiti)
    ▼
FFmpeg           → Sadece seçilen timestamp'lerde kare çek
    │
    ▼
Pillow           → Storyboard grid JPEG derle
    │              (her kare altına transcript caption yaz)
    ▼
Vision LLM       → Claude grid'i okur, analiz eder
```

## Neden Sabit Aralık Değil, Akıllı Timestamp?

Pipeline transcript metnini NLP ile analiz ederek kare çekmeye en değer anları seçer:
- **Keyword eşleşmesi** — "screen", "graph", "right here", "pipeline" gibi deictic ifadeler
- **Sessizlik boşlukları** — konuşmacının durduğu anlar genellikle görsel içeriğe işaret eder
- **Self-learning** — Her videodan sonra TF-IDF ile yeni keyword'ler öğrenir (`~/.calm-quill/keyword_store.json`)

## Storyboard Grid Formatı

Kare sayısına göre adaptif çözünürlük kullanılır:

| Kare | Grid | Hücre genişliği |
|------|------|----------------|
| 1–2 | 1×1 / 2×1 | 1024–1280px |
| 3–4 | 2×2 | 960px |
| 5–9 | 3×2 / 3×3 | 720–800px |
| 10+ | Çok sayfalı | 720px/sayfa |

## Pratik Sonuç

Videodaki görseller + ses birleşince Claude:
- Ekranda gösterilen kod, grafik veya diyagramı okuyabilir
- "Bunu terminalde çalıştır" gibi bir komutun tam bağlamını kavrar
- 45 dakikalık videoyu dakikalar içinde analiz eder

## CLI Kullanımı

```bash
source .venv/bin/activate
watch-youtube "<URL>" --output-dir ./output --max-frames 20 --verbose
```
