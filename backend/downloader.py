import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

from backend.config import TEMP_DIR, FFMPEG_BIN
from backend.utils import generate_id, validate_youtube_url, parse_timestamp

logger = logging.getLogger(__name__)


def download_clip(
    url: str,
    start_seconds: float,
    end_seconds: float,
    output_dir: Optional[Path] = None,
) -> Path:
    if not validate_youtube_url(url):
        raise ValueError(f"Invalid YouTube URL: {url}")

    start_sec_int = int(start_seconds)
    end_sec_int = int(end_seconds)

    duration = end_sec_int - start_sec_int
    if duration <= 0:
        raise ValueError("end_time must be greater than start_time")

    target_dir = output_dir or TEMP_DIR
    clip_id = generate_id()
    output_path = target_dir / f"{clip_id}.mp4"

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-warnings",
        "--no-check-certificates",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--download-sections", f"*{start_sec_int}-{end_sec_int}",
        "--force-keyframes-at-cuts",
        "--merge-output-format", "mp4",
        "--output", str(output_path),
    ]

    ffmpeg_path = Path(FFMPEG_BIN)
    if ffmpeg_path.parent != Path(".") and ffmpeg_path.parent.exists():
        cmd.extend(["--ffmpeg-location", str(ffmpeg_path.parent)])

    cmd.append(url)

    logger.info("Downloading clip: %s [%d-%d]", url, start_sec_int, end_sec_int)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            logger.error("yt-dlp stderr: %s", result.stderr)
            raise RuntimeError(f"yt-dlp failed: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Download timed out after 120 seconds")

    if not output_path.exists():
        webm_path = output_path.with_suffix(".mp4")
        candidates = list(target_dir.glob(f"{clip_id}.*"))
        if candidates:
            output_path = candidates[0]
        else:
            raise FileNotFoundError("Downloaded file not found")

    logger.info("Clip downloaded: %s", output_path)
    return output_path
