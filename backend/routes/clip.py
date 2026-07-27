import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from backend.downloader import download_clip
from backend.processor import generate_preview
from backend.utils import parse_timestamp, validate_youtube_url

logger = logging.getLogger(__name__)
router = APIRouter()


class ClipRequest(BaseModel):
    url: str
    start_time: str
    end_time: str

    @field_validator("url")
    @classmethod
    def check_url(cls, v: str) -> str:
        if not validate_youtube_url(v):
            raise ValueError("Invalid YouTube URL")
        return v


class PreviewResponse(BaseModel):
    preview_url: str
    clip_path: str
    clip_id: str


@router.post("/preview", response_model=PreviewResponse)
async def create_preview(req: ClipRequest):
    try:
        start_sec = parse_timestamp(req.start_time)
        end_sec = parse_timestamp(req.end_time)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if end_sec <= start_sec:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    try:
        clip_path = download_clip(req.url, start_sec, end_sec)
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        logger.error("Download failed: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    try:
        preview_path = generate_preview(clip_path)
    except RuntimeError as e:
        logger.error("Preview failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    clip_id = clip_path.stem
    return PreviewResponse(
        preview_url=f"/temp/{preview_path.name}",
        clip_path=str(clip_path),
        clip_id=clip_id,
    )
