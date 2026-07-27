import logging
from pathlib import Path
from typing import Optional

from backend.config import TEMP_DIR, WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
from backend.utils import generate_id

logger = logging.getLogger(__name__)


def transcribe_audio(
    video_path: Path,
    model_size: Optional[str] = None,
    device: Optional[str] = None,
) -> list[dict]:
    import stable_whisper

    _model = model_size or WHISPER_MODEL
    _device = device or WHISPER_DEVICE

    logger.info("Loading whisper model: %s on %s", _model, _device)

    try:
        model = stable_whisper.load_model(_model, device=_device)
        result = model.transcribe(str(video_path))
    except Exception:
        logger.exception("Transcription failed for %s", video_path.name)
        raise RuntimeError("AI transcription failed")

    words = []
    for segment in result.segments:
        for word in segment.words:
            words.append({
                "word": word.word.strip(),
                "start": round(word.start, 3),
                "end": round(word.end, 3),
            })

    logger.info("Transcribed %d words from %s", len(words), video_path.name)
    return words


def generate_ass_subtitle(
    words: list[dict],
    output_dir: Optional[Path] = None,
    font_name: str = "Arial",
    font_size: int = 18,
    highlight_color: str = "&H0000FFFF",
    primary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00000000",
    shadow_color: str = "&H80000000",
    outline_width: int = 2,
    shadow_depth: int = 1,
) -> Path:
    target_dir = output_dir or TEMP_DIR
    sub_id = generate_id()
    output_path = target_dir / f"subtitle_{sub_id}.ass"

    header = (
        "[Script Info]\n"
        "Title: ClipCuy Subtitle\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1920\n"
        "PlayResY: 1080\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font_name},{font_size},"
        f"{primary_color},{highlight_color},"
        f"{outline_color},{shadow_color},"
        f"-1,0,0,0,100,100,0,0,1,{outline_width},{shadow_depth},"
        f"5,10,10,40,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    events = []
    chunk_size = 6
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        start_time = _format_ass_time(chunk[0]["start"])
        end_time = _format_ass_time(chunk[-1]["end"])

        karaoke_parts = []
        for j, w in enumerate(chunk):
            dur_cs = int((w["end"] - w["start"]) * 100)
            karaoke_parts.append(f"{{\\kf{dur_cs}}}{w['word']}")

        text = " ".join(karaoke_parts)
        events.append(
            f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
        )

    content = header + "".join(events)
    output_path.write_text(content, encoding="utf-8")

    logger.info("Generated ASS subtitle: %s (%d events)", output_path.name, len(events))
    return output_path


def _format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"
