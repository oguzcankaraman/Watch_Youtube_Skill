# watch-youtube

YouTube videolarını Claude Code'a "izlettiren" bir pipeline. Transcript + ekran görüntülerini birleştirerek bir storyboard grid oluşturur, Claude bunu Vision LLM ile analiz eder ve bilgileri `docs/wiki/` altında Obsidian formatında saklar.

## Nasıl Çalışır

```
YouTube URL
    ↓
Transcript İndir (VTT/SRT → Groq Whisper fallback)
    ↓
NLP Analizi → Akıllı Timestamp Seçimi
    ↓
FFmpeg → Sadece O Anların Frame'leri
    ↓
Storyboard Grid (JPEG)
    ↓
Claude (Vision LLM) → Analiz
    ↓
docs/wiki/ → Obsidian Knowledge Base
```

Sadece transcript kullanmak yeterli değil — önemli bilgilerin büyük kısmı ekranda gösterilir, sesle anlatılmaz. Bu pipeline transcript'i NLP ile okuyarak *nerede* ekran görüntüsü alınacağını öğrenir; sabit aralıklı frame extraction yerine semantik olarak değerli anları seçer.

## Kurulum

**Gereksinimler:** Python 3.11+, ffmpeg, Claude Code

### 1. Repoyu klonla

```bash
git clone <https://github.com/oguzcankaraman/Watch_Youtube_Skill>
cd YouTube
```

### 2. Virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
```

### 3. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. spaCy dil modelini indir

```bash
python -m spacy download en_core_web_sm
```

### 5. ffmpeg yükle

```bash
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu/Debian
# Windows: https://ffmpeg.org/download.html
```

### 6. (Opsiyonel) Groq API Key

YouTube altyazısı olmayan videolar için Whisper fallback:

```bash
export GROQ_API_KEY="gsk_..."
```

[Groq API key al](https://console.groq.com) — ücretsiz tier yeterli.

## Kullanım

### CLI

```bash
source .venv/bin/activate

watch-youtube "https://www.youtube.com/watch?v=VIDEO_ID" \
  --output-dir ./output \
  --max-frames 20 \
  --verbose
```

Storyboard JPEG'leri `output/VIDEO_ID/` altına kaydedilir.

### Claude Code ile

Claude Code kuruluysa projeyi açın ve bir YouTube URL paylaşın. `CLAUDE.md` sayesinde Claude otomatik olarak `watch-youtube` skill'ini devreye alır, videoyu analiz eder ve `docs/wiki/` altına yazar.

```
# Claude Code'a şunu yapıştırın:
https://www.youtube.com/watch?v=VIDEO_ID
```

## CLI Seçenekleri

| Seçenek | Varsayılan | Açıklama |
|---|---|---|
| `--output-dir / -o` | `.` | Storyboard JPEG'lerinin kaydedileceği klasör |
| `--max-frames / -n` | `30` | Maksimum frame sayısı |
| `--jpeg-quality / -q` | `85` | JPEG kalitesi (1–95) |
| `--silence-gap / -g` | `5.0` | Sessizlik eşiği (saniye) |
| `--groq-api-key / -k` | env `GROQ_API_KEY` | Whisper fallback için Groq key |
| `--keep-temp` | kapalı | Geçici video/frame dosyalarını sakla |
| `--no-learn` | kapalı | Bu çalıştırmada keyword öğrenmesini atla |
| `--verbose / -v` | kapalı | Debug log'larını göster |

## Proje Yapısı

```
watch_youtube/
  __init__.py      # Veri modelleri (dataclass'lar)
  downloader.py    # yt-dlp ile transcript + video indirme
  analyzer.py      # NLP timestamp seçimi + self-learning
  extractor.py     # ffmpeg frame extraction
  compiler.py      # Pillow storyboard grid
  main.py          # CLI entry point

.claude/skills/
  watch-youtube/   # Claude Code skill talimatları
  wiki-schema/     # Wiki yazma kuralları

docs/wiki/
  Index.md         # Ana harita
  Videos.md        # Analiz edilmiş videoların kayıtları
  *.md             # Konu bazlı wiki sayfaları

data/
  keyword_store.json   # Self-learning keyword veritabanı

output/
  VIDEO_ID/
    storyboard_page_001.jpg
    storyboard_page_002.jpg
    ...
```

## Nasıl Çalışıyor: Teknik Detay

### Akıllı Timestamp Seçimi

İki kural birlikte çalışır:

**Kural A — Keyword eşleşmesi:** Transcript'te "look at this", "here we have", "diagram", "terminal" gibi konuşmacının ekrana işaret ettiği ifadeler tespit edilir. spaCy ile fiil + demonstrative kombinasyonları da yakalanır.

**Kural B — Sessizlik tespiti:** Konuşmacının 5+ saniye sessiz kaldığı anlar genellikle demo veya görsel içerik gösteriyor demektir.

### Self-Learning

Her video bittikten sonra TF-IDF çalışır: seçilen timestamp'lere yakın metinler ile arka plan metinleri karşılaştırılır, yüksek lift'li terimler `data/keyword_store.json`'a yazılır. Sistem izledikçe domain'e özgü vocabulary öğrenir.

### Storyboard Grid

Frame sayısına göre adaptif çözünürlük:

| Frame | Grid | Hücre |
|---|---|---|
| 1 | 1×1 | 1280px |
| 2 | 2×1 | 1024px |
| 3–4 | 2×2 | 960px |
| 5–6 | 3×2 | 800px |
| 7–9 | 3×3 | 720px |
| 10–12 | 4×3 | 640px |
| 13+ | 3×3 sayfalar | 720px |

12'den fazla frame otomatik olarak birden fazla JPEG sayfasına bölünür.

## Bağımlılıklar

| Paket | Amaç |
|---|---|
| `yt-dlp` | YouTube transcript + video indirme |
| `Pillow` | Storyboard grid oluşturma |
| `spaCy` | NLP timestamp analizi |
| `scikit-learn` | TF-IDF self-learning |
| `webvtt-py` | VTT altyazı parse |
| `click` | CLI |
| `groq` | Whisper API fallback |

## Sorun Giderme

| Hata | Çözüm |
|---|---|
| `ffmpeg not found` | `brew install ffmpeg` |
| `No module named spacy` | `pip install spacy && python -m spacy download en_core_web_sm` |
| `Cannot access video` | Video private, yaş kısıtlı veya bölge engelinde olabilir |
| Transcript bulunamadı | `--groq-api-key` ile Whisper fallback kullan |
| `Module import error` | Venv aktif mi kontrol et: `source .venv/bin/activate && pip install -e .` |
