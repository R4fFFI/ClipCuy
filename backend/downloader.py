import logging
import subprocess
from pathlib import Path
from typing import Optional

from backend.config import TEMP_DIR
from backend.utils import generate_id, validate_youtube_url

logger = logging.getLogger(__name__)


def download_clip(
    url: str,
    start_seconds: float,
    end_seconds: float,
    output_dir: Optional[Path] = None,
) -> Path:
    if not validate_youtube_url(url):
        raise ValueError(f"Invalid YouTube URL: {url}")

    duration = end_seconds - start_seconds
    if duration <= 0:
        raise ValueError("end_time must be greater than start_time")

    target_dir = output_dir or TEMP_DIR
    clip_id = generate_id()
    output_path = target_dir / f"{clip_id}.mp4"

    cmd = [
        "yt-dlp",
        "--no-warnings",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--download-sections", f"*{start_seconds}-{end_seconds}",
        "--force-keyframes-at-cuts",
        "--merge-output-format", "mp4",
        "--output", str(output_path),
        url,
    ]

    logger.info("Downloading clip: %s [%.1f-%.1f]", url, start_seconds, end_seconds)

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
