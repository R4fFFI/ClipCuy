import re
import uuid
import logging
import subprocess
import json
from pathlib import Path
from typing import Optional

from backend.config import FFPROBE_BIN

logger = logging.getLogger(__name__)


def generate_id() -> str:
    return uuid.uuid4().hex[:12]


def parse_timestamp(ts: str) -> int:
    ts = ts.strip()
    if re.match(r"^\d+$", ts):
        return int(ts)
    if re.match(r"^\d+\.\d+$", ts):
        return int(float(ts))
    parts = ts.split(":")
    if len(parts) == 2:
        return int(float(parts[0]) * 60 + float(parts[1]))
    if len(parts) == 3:
        return int(float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]))
    raise ValueError(f"Invalid timestamp format: {ts}")


def validate_youtube_url(url: str) -> bool:
    pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)"
    return bool(re.match(pattern, url))


def get_video_info(filepath: Path) -> Optional[dict]:
    try:
        result = subprocess.run(
            [
                FFPROBE_BIN, "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(filepath),
            ],
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(result.stdout)
    except Exception:
        logger.exception("ffprobe failed for %s", filepath)
        return None


def get_video_duration(filepath: Path) -> float:
    info = get_video_info(filepath)
    if not info:
        return 0.0
    return float(info.get("format", {}).get("duration", 0))
