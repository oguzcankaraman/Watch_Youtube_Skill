"""watch-youtube CLI entry point."""

import logging
import shutil
import tempfile
import time
from pathlib import Path

import click

from .extractor import check_ffmpeg, get_video_duration


@click.command()
@click.argument("url")
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("."),
    show_default=True,
    help="Directory to save storyboard images.",
)
@click.option(
    "--groq-api-key", "-k",
    envvar="GROQ_API_KEY",
    default=None,
    help="Groq API key for Whisper transcription fallback (or set GROQ_API_KEY env var).",
)
@click.option(
    "--max-frames", "-n",
    type=int,
    default=30,
    show_default=True,
    help="Maximum smart frames to extract.",
)
@click.option(
    "--jpeg-quality", "-q",
    type=click.IntRange(1, 95),
    default=85,
    show_default=True,
    help="JPEG compression quality for storyboard output (1–95).",
)
@click.option(
    "--silence-gap", "-g",
    type=float,
    default=5.0,
    show_default=True,
    help="Minimum silence gap in seconds to trigger frame extraction (Rule B).",
)
@click.option(
    "--frame-format",
    type=click.Choice(["jpg", "png"]),
    default="jpg",
    show_default=True,
    help="Intermediate frame format (jpg=faster, png=lossless).",
)
@click.option(
    "--keep-temp",
    is_flag=True,
    default=False,
    help="Keep temporary video/frame files after processing.",
)
@click.option(
    "--no-learn",
    is_flag=True,
    default=False,
    help="Skip self-learning keyword store update after this run.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable verbose (DEBUG) logging.",
)
def cli(
    url: str,
    output_dir: Path,
    groq_api_key: str | None,
    max_frames: int,
    jpeg_quality: int,
    silence_gap: float,
    frame_format: str,
    keep_temp: bool,
    no_learn: bool,
    verbose: bool,
) -> None:
    """watch-youtube: YouTube video storyboard generator for Vision LLMs.

    Downloads a YouTube video, extracts semantically relevant frames using
    transcript NLP analysis, and compiles them into annotated storyboard grids
    optimized for LLM token efficiency.

    \b
    Example:
      watch-youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o ./output -n 12 -v
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
        level=log_level,
    )
    log = logging.getLogger("watch_youtube")

    temp_dir = Path(tempfile.mkdtemp(prefix="watch_youtube_"))
    t_start = time.time()

    try:
        check_ffmpeg()

        log.info("Step 1/4 ▸ Downloading transcript + video...")
        from .downloader import download_video
        result = download_video(url, temp_dir, groq_api_key)
        log.info(
            f"          Transcript: {result.transcript_source} "
            f"({len(result.transcript_entries)} entries)"
        )

        # Each video gets its own subdirectory so storyboards never overwrite each other
        video_output_dir = output_dir / result.video_id
        video_output_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"          Output dir: {video_output_dir}")

        log.info("Step 2/4 ▸ Analyzing transcript for smart timestamps...")
        from .analyzer import extract_smart_timestamps
        timestamps = extract_smart_timestamps(
            result.transcript_entries,
            silence_threshold=silence_gap,
            max_timestamps=max_frames,
        )
        duration = get_video_duration(result.video_path)
        fixed_count = _estimate_fixed_count(duration)
        log.info(
            f"          Found {len(timestamps)} smart timestamps "
            f"(vs ~{fixed_count} at fixed 30s intervals)"
        )
        if verbose:
            for ts in timestamps:
                log.debug(f"    {ts.time_sec:7.1f}s  [{ts.reason}]  {ts.transcript_text[:60]}")

        log.info("Step 3/4 ▸ Extracting frames with ffmpeg...")
        from .extractor import extract_frames
        frames = extract_frames(
            result.video_path,
            timestamps,
            temp_dir,
            fmt=frame_format,
        )
        log.info(f"          Extracted {len(frames)} frames successfully")

        log.info("Step 4/4 ▸ Compiling storyboard grids...")
        from .compiler import compile_storyboards
        boards = compile_storyboards(frames, video_output_dir, jpeg_quality=jpeg_quality)

        if not no_learn and result.transcript_entries and timestamps:
            from .analyzer import update_keyword_store
            new_kw = update_keyword_store(result.transcript_entries, timestamps)
            if new_kw:
                log.info(f"          Keyword store: learned {new_kw} new term(s) from this video")

        elapsed = time.time() - t_start
        log.info("=" * 62)
        log.info(f"  Done in {elapsed:.1f}s")
        log.info(
            f"  Extracted {len(frames)} smart frames instead of "
            f"~{fixed_count} fixed-interval frames."
        )
        log.info(f"  Compressed into {len(boards)} storyboard grid(s).")
        for b in boards:
            size_kb = b.stat().st_size // 1024
            log.info(f"  → {video_output_dir.name}/{b.name}  ({size_kb} KB)")
        log.info("=" * 62)

    except ValueError as exc:
        logging.getLogger("watch_youtube").error(f"Video error: {exc}")
        raise click.Abort() from exc
    except EnvironmentError as exc:
        logging.getLogger("watch_youtube").error(str(exc))
        raise click.Abort() from exc
    finally:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _estimate_fixed_count(duration_sec: float | None, interval: int = 30) -> int:
    if duration_sec is None:
        return 100
    return max(1, int(duration_sec / interval))


if __name__ == "__main__":
    cli()
