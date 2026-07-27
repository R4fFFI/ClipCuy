import logging
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from backend.config import TEMP_DIR, OUTPUT_DIR
from backend.processor import (
    apply_watermark,
    concat_endorsement,
    convert_aspect_ratio,
    burn_subtitles,
)
from backend.utils import generate_id

logger = logging.getLogger(__name__)
router = APIRouter()


class RenderResponse(BaseModel):
    download_url: str
    output_path: str


async def _save_upload(upload: UploadFile, prefix: str) -> Path:
    ext = Path(upload.filename).suffix or ".bin"
    dest = TEMP_DIR / f"{prefix}_{generate_id()}{ext}"
    with dest.open("wb") as f:
        content = await upload.read()
        f.write(content)
    return dest


@router.post("/render", response_model=RenderResponse)
async def render_final(
    clip_path: str = Form(...),
    watermark: Optional[UploadFile] = File(None),
    watermark_position: str = Form("top_right"),
    watermark_opacity: float = Form(0.8),
    watermark_margin: int = Form(10),
    watermark_scale: float = Form(0.15),
    endorsement: Optional[UploadFile] = File(None),
    endorsement_position: str = Form("intro"),
    aspect_ratio: Optional[str] = Form(None),
    aspect_ratio_mode: str = Form("center_crop"),
    ass_path: Optional[str] = Form(None),
):
    current = Path(clip_path)
    if not current.exists():
        raise HTTPException(status_code=404, detail="Clip file not found")

    pipeline_steps = []

    try:
        if watermark:
            wm_path = await _save_upload(watermark, "wm")
            current = apply_watermark(
                current, wm_path,
                position=watermark_position,
                opacity=watermark_opacity,
                margin=watermark_margin,
                scale=watermark_scale,
            )
            pipeline_steps.append("watermark")

        if endorsement:
            endorse_path = await _save_upload(endorsement, "endorse")
            current = concat_endorsement(
                current, endorse_path,
                position=endorsement_position,
            )
            pipeline_steps.append("endorsement")

        if aspect_ratio:
            current = convert_aspect_ratio(
                current,
                ratio=aspect_ratio,
                mode=aspect_ratio_mode,
            )
            pipeline_steps.append("aspect_ratio")

        if ass_path:
            ass_file = Path(ass_path)
            if not ass_file.exists():
                raise HTTPException(status_code=404, detail="Subtitle file not found")
            current = burn_subtitles(current, ass_file)
            pipeline_steps.append("subtitles")

    except (ValueError, RuntimeError) as e:
        logger.error("Render pipeline failed at %s: %s", pipeline_steps, e)
        raise HTTPException(status_code=500, detail=str(e))

    final_id = generate_id()
    final_path = OUTPUT_DIR / f"clipcuy_{final_id}.mp4"
    shutil.move(str(current), str(final_path))

    logger.info("Render complete [%s]: %s", "+".join(pipeline_steps), final_path.name)

    return RenderResponse(
        download_url=f"/outputs/{final_path.name}",
        output_path=str(final_path),
    )
