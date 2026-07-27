import logging
import subprocess
from pathlib import Path
from typing import Optional

from backend.config import FFMPEG_BIN, TEMP_DIR, PREVIEW_SCALE, PREVIEW_CRF
from backend.utils import generate_id

logger = logging.getLogger(__name__)


def generate_preview(source: Path, output_dir: Optional[Path] = None) -> Path:
    target_dir = output_dir or TEMP_DIR
    preview_id = generate_id()
    output_path = target_dir / f"preview_{preview_id}.mp4"

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(source),
        "-vf", f"scale={PREVIEW_SCALE}",
        "-c:v", "libx264", "-crf", PREVIEW_CRF,
        "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "64k",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info("Generating preview for %s", source.name)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error("FFmpeg preview error: %s", result.stderr[-500:])
            raise RuntimeError(f"Preview generation failed: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Preview generation timed out")

    logger.info("Preview generated: %s", output_path.name)
    return output_path


def apply_watermark(
    source: Path,
    watermark: Path,
    position: str = "top_right",
    opacity: float = 0.8,
    margin: int = 10,
    scale: float = 0.15,
    output_dir: Optional[Path] = None,
) -> Path:
    target_dir = output_dir or TEMP_DIR
    out_id = generate_id()
    output_path = target_dir / f"wm_{out_id}.mp4"

    pos_map = {
        "top_left": f"x={margin}:y={margin}",
        "top_center": f"x=(W-w)/2:y={margin}",
        "top_right": f"x=W-w-{margin}:y={margin}",
        "center_left": f"x={margin}:y=(H-h)/2",
        "center": "x=(W-w)/2:y=(H-h)/2",
        "center_right": f"x=W-w-{margin}:y=(H-h)/2",
        "bottom_left": f"x={margin}:y=H-h-{margin}",
        "bottom_center": f"x=(W-w)/2:y=H-h-{margin}",
        "bottom_right": f"x=W-w-{margin}:y=H-h-{margin}",
    }

    pos_expr = pos_map.get(position, pos_map["top_right"])

    filter_complex = (
        f"[1:v]format=rgba,"
        f"colorchannelmixer=aa={opacity},"
        f"scale=iw*{scale}:-1[wm];"
        f"[0:v][wm]overlay={pos_expr}"
    )

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(source),
        "-i", str(watermark),
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info("Applying watermark [%s] to %s", position, source.name)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"Watermark failed: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Watermark processing timed out")

    return output_path


def concat_endorsement(
    source: Path,
    endorsement: Path,
    position: str = "intro",
    output_dir: Optional[Path] = None,
) -> Path:
    target_dir = output_dir or TEMP_DIR
    out_id = generate_id()
    output_path = target_dir / f"endorse_{out_id}.mp4"
    concat_list = target_dir / f"concat_{out_id}.txt"

    if position == "intro":
        order = [endorsement, source]
    else:
        order = [source, endorsement]

    concat_list.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in order),
        encoding="utf-8",
    )

    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info("Concatenating endorsement [%s] with %s", position, source.name)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"Concat failed: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Endorsement concat timed out")
    finally:
        concat_list.unlink(missing_ok=True)

    return output_path


def convert_aspect_ratio(
    source: Path,
    ratio: str = "9:16",
    mode: str = "center_crop",
    output_dir: Optional[Path] = None,
) -> Path:
    target_dir = output_dir or TEMP_DIR
    out_id = generate_id()
    output_path = target_dir / f"ar_{out_id}.mp4"

    ratio_map = {
        "9:16": (9, 16),
        "1:1": (1, 1),
        "16:9": (16, 9),
    }

    if ratio not in ratio_map:
        raise ValueError(f"Unsupported aspect ratio: {ratio}")

    rw, rh = ratio_map[ratio]

    if mode == "blurred_background":
        filter_complex = (
            f"[0:v]scale=ih*{rw}/{rh}:ih,boxblur=20:20[bg];"
            f"[0:v]scale=-1:ih*0.7[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,crop=ih*{rw}/{rh}:ih"
        )
    else:
        filter_complex = (
            f"crop=ih*{rw}/{rh}:ih"
            if rw / rh < 1
            else f"crop=iw:iw*{rh}/{rw}"
        )

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(source),
        "-vf", filter_complex,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info("Converting aspect ratio to %s [%s]", ratio, mode)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"Aspect ratio conversion failed: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Aspect ratio conversion timed out")

    return output_path


def burn_subtitles(
    source: Path,
    ass_file: Path,
    output_dir: Optional[Path] = None,
) -> Path:
    target_dir = output_dir or TEMP_DIR
    out_id = generate_id()
    output_path = target_dir / f"sub_{out_id}.mp4"

    ass_path_escaped = str(ass_file.resolve()).replace("\\", "/").replace(":", "\\:")

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(source),
        "-vf", f"ass='{ass_path_escaped}'",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info("Burning subtitles into %s", source.name)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            raise RuntimeError(f"Subtitle burn failed: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Subtitle burn timed out")

    return output_path
