"""watch-youtube: YouTube video storyboard generator for Vision LLMs."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TranscriptEntry:
    start_sec: float
    end_sec: float
    text: str


@dataclass
class SmartTimestamp:
    time_sec: float
    # "keyword:<phrase>" | "silence_gap:<N>s" | "combined" | "spacy:<pattern>"
    reason: str
    transcript_text: str


@dataclass
class ExtractedFrame:
    time_sec: float
    path: Path
    transcript_text: str


@dataclass
class DownloadResult:
    video_path: Path
    transcript_entries: list[TranscriptEntry]
    # "vtt" | "srt" | "whisper" | "synthetic" | "none"
    transcript_source: str
    temp_dir: Path
    video_id: str = ""


@dataclass
class KeywordEntry:
    phrase: str
    weight: float          # 1.0 = builtin, 0.8 = confirmed learned, 0.5 = candidate
    source: str            # "builtin" | "learned"
    occurrences: int = 1   # how many videos confirmed this keyword


@dataclass
class KeywordStore:
    version: int
    keywords: list[KeywordEntry] = field(default_factory=list)
    domain_clusters: dict[str, list[str]] = field(default_factory=dict)
