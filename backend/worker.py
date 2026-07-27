import logging
import time
from pathlib import Path

from backend.config import TEMP_DIR, OUTPUT_DIR, TEMP_FILE_TTL_SECONDS

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    from backend.config import REDIS_URL

    celery_app = Celery("clipcuy", broker=REDIS_URL, backend=REDIS_URL)
    celery_app.conf.task_track_started = True

    @celery_app.task(bind=True, max_retries=2)
    def render_task(self, clip_path: str, options: dict) -> dict:
        from backend.processor import (
            apply_watermark,
            concat_endorsement,
            convert_aspect_ratio,
            burn_subtitles,
        )
        from backend.utils import generate_id
        import shutil

        current = Path(clip_path)
        if not current.exists():
            raise FileNotFoundError(f"Clip not found: {clip_path}")

        try:
            if options.get("watermark_path"):
                current = apply_watermark(
                    current,
                    Path(options["watermark_path"]),
                    position=options.get("watermark_position", "top_right"),
                    opacity=options.get("watermark_opacity", 0.8),
                )

            if options.get("endorsement_path"):
                current = concat_endorsement(
                    current,
                    Path(options["endorsement_path"]),
                    position=options.get("endorsement_position", "intro"),
                )

            if options.get("aspect_ratio"):
                current = convert_aspect_ratio(
                    current,
                    ratio=options["aspect_ratio"],
                    mode=options.get("aspect_ratio_mode", "center_crop"),
                )

            if options.get("ass_path"):
                current = burn_subtitles(current, Path(options["ass_path"]))

        except Exception as exc:
            logger.exception("Render task failed")
            raise self.retry(exc=exc, countdown=5)

        final_id = generate_id()
        final_path = OUTPUT_DIR / f"clipcuy_{final_id}.mp4"
        shutil.move(str(current), str(final_path))

        return {"download_url": f"/outputs/{final_path.name}", "output_path": str(final_path)}

    @celery_app.task
    def cleanup_temp_files():
        now = time.time()
        cleaned = 0
        for f in TEMP_DIR.iterdir():
            if f.name == ".gitkeep":
                continue
            if f.is_file() and (now - f.stat().st_mtime) > TEMP_FILE_TTL_SECONDS:
                f.unlink()
                cleaned += 1
        logger.info("Cleaned %d temp files", cleaned)

    celery_app.conf.beat_schedule = {
        "cleanup-temp": {
            "task": "backend.worker.cleanup_temp_files",
            "schedule": 600.0,
        },
    }

except ImportError:
    logger.warning("Celery/Redis not available, background tasks disabled")
    celery_app = None
