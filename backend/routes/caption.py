import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.caption import transcribe_audio, generate_ass_subtitle

logger = logging.getLogger(__name__)
router = APIRouter()


class CaptionRequest(BaseModel):
    clip_path: str
    model_size: Optional[str] = None


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float


class CaptionResponse(BaseModel):
    words: list[WordTimestamp]
    ass_path: str


class CaptionEditRequest(BaseModel):
    words: list[WordTimestamp]
    font_name: str = "Arial"
    font_size: int = 18


class CaptionEditResponse(BaseModel):
    ass_path: str


@router.post("/generate", response_model=CaptionResponse)
async def generate_caption(req: CaptionRequest):
    clip = Path(req.clip_path)
    if not clip.exists():
        raise HTTPException(status_code=404, detail="Clip file not found")

    try:
        words = transcribe_audio(clip, model_size=req.model_size)
    except RuntimeError as e:
        logger.error("Transcription error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    try:
        ass_path = generate_ass_subtitle(words)
    except Exception as e:
        logger.error("ASS generation error: %s", e)
        raise HTTPException(status_code=500, detail="Subtitle generation failed")

    return CaptionResponse(
        words=[WordTimestamp(**w) for w in words],
        ass_path=str(ass_path),
    )


@router.post("/edit", response_model=CaptionEditResponse)
async def edit_caption(req: CaptionEditRequest):
    words = [w.model_dump() for w in req.words]

    try:
        ass_path = generate_ass_subtitle(
            words,
            font_name=req.font_name,
            font_size=req.font_size,
        )
    except Exception as e:
        logger.error("ASS regeneration error: %s", e)
        raise HTTPException(status_code=500, detail="Subtitle regeneration failed")

    return CaptionEditResponse(ass_path=str(ass_path))
