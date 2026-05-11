# YouTube Knowledge Base — Claude Talimatları

Bu proje, YouTube videolarından bilgi çıkaran ve `docs/wiki/` içinde Obsidian formatında saklayan bir sistemdir.

## Genel Çalışma Kuralı

Kullanıcı bir konu veya video hakkında soru sorduğunda şu sırayı takip et:

### 1. Önce wiki'yi kontrol et

`docs/wiki/Index.md` dosyasını oku. İlgili konu orada varsa:
- Doğrudan ilgili wiki sayfasını oku
- Cevabı wiki içeriğinden ver
- Cevabın sonuna hangi wiki sayfasından geldiğini ve kaynağı olan videoyu belirt

### 2. URL ile soru sorulursa — önce Videos.md'yi kontrol et

Kullanıcı bir YouTube URL'si paylaşırsa veya belirli bir video hakkında soru sorarsa:
- `docs/wiki/Videos.md` dosyasını aç, video ID'yi ara
- **Zaten analiz edilmişse**: o videoya ait sayfaları listele ve doğrudan cevapla
- **Analiz edilmemişse**: `watch-youtube` skill'ini çalıştır

### 3. Wiki'de konu yoksa YouTube linki iste

Konu wiki'de bulunamadıysa şunu söyle:

> "Bu konu hakkında henüz wiki'de bilgi yok. Konuyla ilgili bir YouTube videosu varsa linkini paylaş, analiz edip wiki'ye ekleyeyim."

Kullanıcı link verirse `watch-youtube` skill'ini kullan.

### 4. watch-youtube skill'ini çalıştır

`watch-youtube` skill'i şunları yapar:
1. Videoyu indirir, transcript + frame'leri çıkarır
2. Storyboard grid'leri oluşturur
3. Vision LLM ile analiz eder
4. `docs/wiki/` içine wiki-schema kurallarıyla konu sayfaları yazar
5. `docs/wiki/Videos.md` içine video kaydı ekler
6. `docs/wiki/Index.md` dosyasını günceller

Skill tamamlandıktan sonra kullanıcının sorusunu artık wiki'den cevapla.

---

## Video Bazlı Arama

Bir video URL'si verildiğinde hangi sayfaların o videodan türediğini bulmak için:

1. `docs/wiki/Videos.md` → ilgili video kaydını bul → **Oluşturulan wiki sayfaları** listesine bak
2. İlgili her wiki sayfasının başındaki **Kaynak Video** alanını kontrol et

Her knowledge sayfası hangi video(lar)dan türediğini `**Kaynak Video:**` alanıyla açıkça belirtir.

---

## Proje Yapısı

```
watch_youtube/       # Python paketi — CLI ve pipeline
.claude/skills/
  watch-youtube/     # watch-youtube skill talimatları
  wiki-schema/       # Wiki format kuralları
docs/wiki/
  Index.md           # Ana harita — HER ZAMAN buradan başla
  Videos.md          # Analiz edilmiş videoların kayıt defteri
  *.md               # Konu bazlı wiki sayfaları
output/              # Oluşturulan storyboard JPEG'leri
```

## CLI Kullanımı

```bash
source .venv/bin/activate
watch-youtube "<URL>" --output-dir ./output --max-frames 30 --verbose
```

## Bağımlılıklar

- Python 3.11+, `.venv` aktif olmalı
- `ffmpeg` kurulu olmalı (`brew install ffmpeg`)
- `spaCy` en_core_web_sm modeli kurulu olmalı

## wiki-schema Kuralları

Yeni wiki sayfası yazarken `.claude/skills/wiki-schema/SKILL.md` kurallarını uygula:
- Her sayfanın başında **Özet**, **Teknolojiler**, **Bağlantılar**, **Kaynak Video** bloğu zorunlu
- Dosya adı PascalCase, İngilizce
- Her yeni sayfadan sonra `docs/wiki/Index.md` ve `docs/wiki/Videos.md` güncellenir
- Obsidian `[[link]]` formatı kullan
