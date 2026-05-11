"""Compile extracted frames into adaptive-resolution storyboard grids."""

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import ExtractedFrame

logger = logging.getLogger(__name__)

PADDING = 12
BACKGROUND_COLOR = (20, 20, 20)
TEXT_COLOR = (240, 240, 240)
TIMESTAMP_COLOR = (255, 220, 0)
TIMESTAMP_BG = (0, 0, 0)


# ---------------------------------------------------------------------------
# Grid layout — adaptive resolution based on density
# ---------------------------------------------------------------------------

def compute_grid_layout(frame_count: int) -> tuple[int, int, int]:
    """Return (cols, rows, cell_width_px) for the given frame count.

    Resolution shrinks as grid grows to keep canvas manageable,
    but stays >= 720px per cell when frames fit in 3x3 — wide enough for code.
    """
    if frame_count <= 0:
        return 1, 1, 1280
    if frame_count == 1:
        return 1, 1, 1280
    if frame_count == 2:
        return 2, 1, 1024
    if frame_count <= 4:
        return 2, 2, 960
    if frame_count <= 6:
        return 3, 2, 800
    if frame_count <= 9:
        return 3, 3, 720
    if frame_count <= 12:
        return 4, 3, 640
    # Beyond 12: chunk into 3x3 pages at 720px instead of degrading further
    return 3, 3, 720


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compile_storyboards(
    frames: list[ExtractedFrame],
    output_dir: Path,
    jpeg_quality: int = 85,
    max_per_board: int = 9,
) -> list[Path]:
    """Split frames into pages and compile each page into a storyboard JPEG."""
    if not frames:
        logger.warning("No frames to compile")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    pages = [frames[i:i + max_per_board] for i in range(0, len(frames), max_per_board)]
    paths: list[Path] = []

    for page_idx, page_frames in enumerate(pages):
        cols, rows, cell_width = compute_grid_layout(len(page_frames))
        out_path = output_dir / f"storyboard_page_{page_idx + 1:03d}.jpg"
        _compile_single_storyboard(page_frames, out_path, cols, rows, cell_width, jpeg_quality)
        paths.append(out_path)
        logger.debug(f"Compiled page {page_idx + 1}: {cols}x{rows} grid @ {cell_width}px/cell → {out_path.name}")

    return paths


# ---------------------------------------------------------------------------
# Core grid builder
# ---------------------------------------------------------------------------

def _compile_single_storyboard(
    frames: list[ExtractedFrame],
    output_path: Path,
    cols: int,
    rows: int,
    cell_width: int,
    jpeg_quality: int,
) -> None:
    """Render a single storyboard grid with burned-in captions."""
    aspect = 9 / 16
    frame_h = int(cell_width * aspect)
    caption_h = max(60, cell_width // 10)
    cell_h = frame_h + caption_h
    font_size = max(13, cell_width // 55)
    ts_font_size = max(11, cell_width // 70)

    canvas_w = cols * cell_width + (cols + 1) * PADDING
    canvas_h = rows * cell_h + (rows + 1) * PADDING

    canvas = Image.new("RGB", (canvas_w, canvas_h), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(canvas)
    font = _get_font(font_size)
    ts_font = _get_font(ts_font_size)

    for idx, frame in enumerate(frames):
        col = idx % cols
        row = idx // cols
        x = PADDING + col * (cell_width + PADDING)
        y = PADDING + row * (cell_h + PADDING)

        # Frame image
        img = _load_and_resize_frame(frame.path, cell_width, frame_h)
        canvas.paste(img, (x, y))

        # Timestamp badge (top-left of frame)
        ts_label = f" {frame.time_sec:.1f}s "
        badge_w = int(draw.textlength(ts_label, font=ts_font)) + 4
        badge_h = ts_font_size + 6
        draw.rectangle([x, y, x + badge_w, y + badge_h], fill=TIMESTAMP_BG)
        draw.text((x + 2, y + 2), ts_label, font=ts_font, fill=TIMESTAMP_COLOR)

        # Caption area below frame
        caption_y = y + frame_h + 4
        lines = _wrap_text(frame.transcript_text, font, cell_width - 8, draw)
        line_height = font_size + 4
        for line_idx, line in enumerate(lines[:3]):
            draw.text(
                (x + 4, caption_y + line_idx * line_height),
                line,
                font=font,
                fill=TEXT_COLOR,
            )

    canvas.save(str(output_path), "JPEG", quality=jpeg_quality, optimize=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_and_resize_frame(path: Path, target_w: int, target_h: int) -> Image.Image:
    """Open frame and center-crop-resize to exactly (target_w, target_h)."""
    try:
        img = Image.open(path).convert("RGB")
    except Exception:
        # Return a dark placeholder if the frame can't be opened
        return Image.new("RGB", (target_w, target_h), (40, 40, 40))

    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a system font, falling back to Pillow's built-in default."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",           # macOS
        "/System/Library/Fonts/Helvetica.ttc",                    # macOS alternate
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",        # Linux
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
) -> list[str]:
    """Word-wrap text to fit within max_width pixels. Max 3 lines, truncates with '...'."""
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()
        try:
            width = draw.textlength(test, font=font)
        except AttributeError:
            width = len(test) * (font.size // 2 if hasattr(font, "size") else 7)

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) >= 2:
                # We're at the 3rd line limit — add truncated remainder
                remaining_words = words[words.index(word):]
                lines.append((" ".join(remaining_words))[:60] + "...")
                return lines[:3]

    if current:
        lines.append(current)
    return lines[:3]
