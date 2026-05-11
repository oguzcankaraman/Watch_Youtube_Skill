"""Extract video frames at smart timestamps via ffmpeg subprocess calls."""

import logging
import shutil
import subprocess
from pathlib import Path

from . import ExtractedFrame, SmartTimestamp

logger = logging.getLogger(__name__)

_FFMPEG_TIMEOUT = 30  # seconds per frame extraction
_MIN_FRAME_BYTES = 100  # skip black/corrupt frames smaller than this


def check_ffmpeg() -> str:
    """Return path to ffmpeg binary or raise EnvironmentError with install tip."""
    binary = shutil.which("ffmpeg")
    if binary:
        return binary

    # Common macOS Homebrew path
    homebrew_path = Path("/opt/homebrew/bin/ffmpeg")
    if homebrew_path.exists():
        return str(homebrew_path)

    raise EnvironmentError(
        "ffmpeg not found. Install it with:\n"
        "  macOS:  brew install ffmpeg\n"
        "  Ubuntu: sudo apt install ffmpeg\n"
        "  Windows: https://ffmpeg.org/download.html"
    )


def get_video_duration(video_path: Path) -> float | None:
    """Use ffprobe to get video duration in seconds. Returns None on failure."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [
                ffprobe, "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def extract_frames(
    video_path: Path,
    timestamps: list[SmartTimestamp],
    output_dir: Path,
    quality: int = 2,
    fmt: str = "jpg",
) -> list[ExtractedFrame]:
    """Extract one frame per smart timestamp. Skips failures gracefully."""
    ffmpeg_bin = check_ffmpeg()
    frames: list[ExtractedFrame] = []

    for idx, ts in enumerate(timestamps):
        out_path = output_dir / f"frame_{idx:04d}_{int(ts.time_sec):05d}s.{fmt}"
        success = _extract_single_frame(ffmpeg_bin, video_path, ts.time_sec, out_path, quality)
        if success:
            frames.append(ExtractedFrame(
                time_sec=ts.time_sec,
                path=out_path,
                transcript_text=ts.transcript_text,
            ))
        else:
            logger.debug(f"Skipping frame at {ts.time_sec:.1f}s (extraction failed or empty)")

    return frames


def _extract_single_frame(
    ffmpeg_bin: str,
    video_path: Path,
    time_sec: float,
    output_path: Path,
    quality: int,
) -> bool:
    """
    Extract a single frame using input-seeking (-ss before -i) for speed.
    Returns True if a valid non-empty frame was written.
    """
    cmd = [
        ffmpeg_bin,
        "-ss", f"{time_sec:.3f}",   # fast input seek
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", str(quality),        # JPEG quality: 1=best, 31=worst
        "-y",                        # overwrite without prompting
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_FFMPEG_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        logger.warning(f"ffmpeg timed out at {time_sec:.1f}s")
        return False

    if result.returncode != 0:
        logger.debug(f"ffmpeg error at {time_sec:.1f}s: {result.stderr[-200:]}")
        return False

    # Reject suspiciously small files (black frame / seek past end of video)
    if not output_path.exists() or output_path.stat().st_size < _MIN_FRAME_BYTES:
        return False

    return True
