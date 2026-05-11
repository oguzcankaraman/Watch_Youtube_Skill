---
name: watch-youtube
description: Analyze a YouTube video by downloading its transcript, extracting semantically relevant frames using NLP, and compiling them into annotated storyboard grids optimized for Vision LLM token efficiency. After analysis, writes extracted knowledge to docs/wiki/ following wiki-schema rules. Use this skill whenever the user provides a YouTube URL and wants to analyze, summarize, or understand a video's visual content. Trigger on: "analyze this YouTube video", "understand what's shown in this video", "extract key frames", "summarize this tutorial", "what does this video show", "create a storyboard", "compress this video for LLM", "vision LLM video input".
---

# watch-youtube: YouTube Video Storyboard for Vision LLMs

Turns a YouTube video into annotated JPEG storyboard grids, analyzes them with Vision LLM, and writes the extracted knowledge to `docs/wiki/` using wiki-schema rules.

## When the user invokes this skill

1. Confirm the YouTube URL and desired output directory.
2. Check that dependencies are installed (see **Setup** below).
3. Run the pipeline via the `watch-youtube` CLI.
4. Read storyboards from `output/<video_id>/storyboard_page_*.jpg` and analyze with Vision LLM.
5. Show the user a structured analysis.
6. Write the extracted knowledge to `docs/wiki/` following **wiki-schema** rules (see section below).
7. **Add a video record to `docs/wiki/Videos.md`** (see section below).
8. Update `docs/wiki/Index.md`.

---

## Setup (run once per environment)

```bash
cd /Users/oguzcan/PycharmProjects/YouTube
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install the spaCy English model (required for NLP)
python -m spacy download en_core_web_sm

# Install the CLI in editable mode
pip install -e .

# Install ffmpeg (required for frame extraction)
brew install ffmpeg   # macOS
```

---

## Running the pipeline

```bash
watch-youtube "<YOUTUBE_URL>" \
    --output-dir ./output \
    --max-frames 20 \
    --jpeg-quality 85 \
    --verbose
```

### Key options

| Flag | Default | Purpose |
|------|---------|---------|
| `--output-dir / -o` | `.` | Where to save storyboard JPEGs |
| `--max-frames / -n` | `30` | Cap on smart frames extracted |
| `--jpeg-quality / -q` | `85` | JPEG quality 1–95 |
| `--silence-gap / -g` | `5.0` | Seconds of silence that triggers a frame |
| `--groq-api-key / -k` | env `GROQ_API_KEY` | Whisper fallback when no transcript |
| `--no-learn` | off | Skip self-learning keyword store update |
| `--keep-temp` | off | Keep raw frames and video file |
| `--verbose / -v` | off | Show per-timestamp debug output |

---

## Pipeline architecture

```
YouTube URL
    │
    ▼
downloader.py        Download transcript (VTT/SRT) + video MP4
    │                Fallback: download audio → Groq Whisper API
    ▼
analyzer.py          NLP timestamp extraction (spaCy + learned keyword store)
    │                Rule A: keyword/deictic pattern matching
    │                Rule B: silence gap detection (>= silence_gap seconds)
    │                Post-run: TF-IDF self-learning updates data/keyword_store.json
    ▼
extractor.py         ffmpeg frame extraction at smart timestamps only
    │                Adaptive quality; skips black/corrupt frames
    ▼
compiler.py          Pillow storyboard grid compilation
    │                Adaptive cell resolution (720–1280px depending on grid density)
    │                Transcript captions burned in below each frame
    ▼
output/<video_id>/storyboard_page_NNN.jpg  (one or more JPEG grids, isolated per video)
    │
    ▼
Vision LLM analysis  Read storyboard images → structured summary
    │
    ├──▶ docs/wiki/<title>.md      Write topic pages (wiki-schema rules)
    ├──▶ docs/wiki/Videos.md       Append video record (URL, date, pages)
    └──▶ docs/wiki/Index.md        Update index with new pages
```

---

## Writing to docs/wiki (wiki-schema integration)

After analyzing the storyboard, **always** write a wiki entry to `docs/wiki/` following these rules from `wiki-schema`:

### Required frontmatter structure for each wiki page

```markdown
**Özet:** [Max 3 sentences describing what was learned]
**Kütüphaneler/Teknolojiler:** [Key technologies/tools covered]
**Bağlantılar:** [[Related_Topic]], [[Another_Topic]]
```

### Wiki file naming

- Use descriptive, PascalCase filenames: `OperatingSystemFundamentals.md`, `VirtualMemory.md`
- After writing, update `[[docs/wiki/Index.md]]` with a pointer to the new file

### What to write in the wiki entry

- Main concepts explained in the video
- Key diagrams or visual structures (describe them in text)
- Relationships to other topics (with Obsidian-style `[[links]]`)
- Sponsor segments or tool mentions (tagged as such)

### Example wiki entry

```markdown
**Özet:** Bu video işletim sisteminin temel bileşenlerini anlatıyor: süreçler, kernel modu, sanal bellek ve dosya sistemi. CPU'nun tek bir hard-coded adresten boot ettiğini ve kernel'in Ring 0 ayrıcalığıyla çalıştığını gösteriyor.
**Kütüphaneler/Teknolojiler:** Linux Kernel, C, ffmpeg, spaCy
**Bağlantılar:** [[VirtualMemory]], [[FileSystem_Inodes]], [[DeviceDrivers]]

## İçerik
...
```

### Always update Index.md

After writing a new wiki page, open `docs/wiki/Index.md` and add a link:
```markdown
- [[NewPageTitle]] — one-line summary
```

---

## Recording the video in docs/wiki/Videos.md

**Always** append a record to `docs/wiki/Videos.md` after each analysis:

```markdown
### [Video Başlığı](https://www.youtube.com/watch?v=VIDEO_ID)
- **ID:** `VIDEO_ID`
- **Analiz tarihi:** YYYY-MM-DD
- **Süre:** ~X dakika
- **Transcript:** vtt / srt / whisper / synthetic
- **Kare sayısı:** N kare, M storyboard sayfası
- **Oluşturulan wiki sayfaları:** [[Sayfa1]], [[Sayfa2]]
- **Özet:** Tek cümlelik içerik özeti
```

This is the single source of truth for "which videos have been analyzed." Always check `Videos.md` before re-analyzing a URL that may already exist.

---

## Adaptive resolution table

| Frames | Grid | Cell width |
|--------|------|-----------|
| 1 | 1×1 | 1280px |
| 2 | 2×1 | 1024px |
| 3–4 | 2×2 | 960px |
| 5–6 | 3×2 | 800px |
| 7–9 | 3×3 | 720px |
| 10–12 | 4×3 | 640px |
| 13+ | 3×3 pages | 720px |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ffmpeg not found` | `brew install ffmpeg` |
| `No module named spacy` | `pip install spacy && python -m spacy download en_core_web_sm` |
| `Cannot access video` | Video may be private, age-restricted, or region-blocked |
| No transcript found | Pass `--groq-api-key` or set `GROQ_API_KEY` env var |
| Module import error | Run `pip install -e .` from project root with venv active |
