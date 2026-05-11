"""Download YouTube transcripts, audio, and video via yt-dlp."""

import re
import time
import logging
from pathlib import Path

import yt_dlp
import webvtt

from . import DownloadResult, TranscriptEntry

logger = logging.getLogger(__name__)

_TIMECODE_RE = re.compile(r"(\d+):(\d{2}):(\d{2})[.,](\d+)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL. Falls back to 'unknown'."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return "unknown"


def download_video(url: str, output_dir: Path, groq_api_key: str | None = None) -> DownloadResult:
    """Orchestrate transcript + video download with Whisper fallback."""
    video_id = extract_video_id(url)
    transcript_path, fmt = _download_transcript(url, output_dir)

    entries: list[TranscriptEntry] = []
    source = "none"

    if transcript_path is not None:
        entries = _parse_transcript_file(transcript_path, fmt)
        source = fmt
        logger.debug(f"Parsed {len(entries)} entries from {fmt} transcript")
    elif groq_api_key:
        logger.info("No transcript found — downloading audio for Whisper transcription...")
        audio_path = _download_audio(url, output_dir)
        entries = _transcribe_with_whisper(audio_path, groq_api_key)
        source = "whisper"
        logger.debug(f"Whisper returned {len(entries)} entries")
    else:
        logger.warning("No transcript and no GROQ_API_KEY — using synthetic 30s intervals")
        source = "synthetic"

    video_path = _download_video_file(url, output_dir)
    return DownloadResult(
        video_path=video_path,
        transcript_entries=entries,
        transcript_source=source,
        temp_dir=output_dir,
        video_id=video_id,
    )


def _download_transcript(url: str, output_dir: Path) -> tuple[Path | None, str]:
    """Try manual then auto-generated subtitles; return (path, format) or (None, 'none')."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US", "en-GB"],
        "subtitlesformat": "vtt",
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        raise ValueError(f"Cannot access video: {e}") from e

    for ext in ("vtt", "srt"):
        matches = list(output_dir.glob(f"*.{ext}"))
        if matches:
            return matches[0], ext

    return None, "none"


def _download_audio(url: str, output_dir: Path) -> Path:
    """Download audio-only as .mp3 for Whisper transcription."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s_audio.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    matches = list(output_dir.glob("*_audio.mp3"))
    if not matches:
        raise RuntimeError("Audio download produced no file")
    return matches[0]


def _download_video_file(url: str, output_dir: Path) -> Path:
    """Download best quality MP4 video for frame extraction."""
    opts = {
        "outtmpl": str(output_dir / "%(id)s_video.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best",
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    matches = list(output_dir.glob("*_video.mp4"))
    if not matches:
        # Some videos download without the _video suffix when merge happens
        matches = list(output_dir.glob("*.mp4"))
    if not matches:
        raise RuntimeError("Video download produced no .mp4 file")
    return matches[0]


def _transcribe_with_whisper(audio_path: Path, api_key: str) -> list[TranscriptEntry]:
    """Transcribe audio via Groq Whisper API with segment-level timestamps."""
    from groq import Groq, RateLimitError

    client = Groq(api_key=api_key)

    for attempt in range(2):
        try:
            with audio_path.open("rb") as f:
                response = client.audio.transcriptions.create(
                    file=(audio_path.name, f),
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )
            break
        except RateLimitError:
            if attempt == 0:
                logger.warning("Groq rate limit hit — retrying in 60s...")
                time.sleep(60)
            else:
                raise

    entries = []
    for seg in response.segments or []:
        text = _WHITESPACE_RE.sub(" ", seg.text.strip())
        if text:
            entries.append(TranscriptEntry(
                start_sec=float(seg.start),
                end_sec=float(seg.end),
                text=text,
            ))
    return entries


def _parse_transcript_file(path: Path, fmt: str) -> list[TranscriptEntry]:
    if fmt == "vtt":
        return _parse_vtt(path)
    return _parse_srt(path)


def _parse_vtt(path: Path) -> list[TranscriptEntry]:
    """Parse WebVTT using webvtt-py; strips HTML tags and deduplicates rolling-window lines."""
    entries = []
    try:
        captions = webvtt.read(str(path))
    except Exception:
        # Some auto-captions have malformed headers; fall back to raw read
        captions = webvtt.read_buffer(path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True))

    seen: set[str] = set()
    for cap in captions:
        clean = _HTML_TAG_RE.sub("", cap.text)
        clean = _WHITESPACE_RE.sub(" ", clean).strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        entries.append(TranscriptEntry(
            start_sec=_timecode_to_seconds(cap.start),
            end_sec=_timecode_to_seconds(cap.end),
            text=clean,
        ))
    return entries


_SRT_BLOCK_RE = re.compile(
    r"\d+\r?\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\r?\n"
    r"([\s\S]*?)(?=\n\s*\n|\Z)",
    re.MULTILINE,
)


def _parse_srt(path: Path) -> list[TranscriptEntry]:
    """Parse SRT subtitle file with pure regex."""
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = []
    for m in _SRT_BLOCK_RE.finditer(text):
        start_raw, end_raw, body = m.groups()
        clean = _HTML_TAG_RE.sub("", body).strip()
        clean = _WHITESPACE_RE.sub(" ", clean)
        if clean:
            entries.append(TranscriptEntry(
                start_sec=_timecode_to_seconds(start_raw),
                end_sec=_timecode_to_seconds(end_raw),
                text=clean,
            ))
    return entries


def _timecode_to_seconds(tc: str) -> float:
    """Convert HH:MM:SS.mmm or HH:MM:SS,mmm to float seconds."""
    tc = tc.strip().replace(",", ".")
    parts = tc.split(":")
    h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + s
