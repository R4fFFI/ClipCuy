const API_BASE = "http://localhost:8000";

export interface PreviewResponse {
  preview_url: string;
  clip_path: string;
  clip_id: string;
}

export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
}

export interface CaptionResponse {
  words: WordTimestamp[];
  ass_path: string;
}

export interface RenderResponse {
  download_url: string;
  output_path: string;
}

async function handleResponseError(res: Response, defaultMessage: string) {
  const err = await res.json().catch(() => null);
  let errMsg = defaultMessage;
  if (err && err.detail) {
    if (typeof err.detail === "string") {
      errMsg = err.detail;
    } else if (Array.isArray(err.detail)) {
      errMsg = err.detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
    } else {
      errMsg = JSON.stringify(err.detail);
    }
  } else {
    errMsg = `HTTP ${res.status}: ${res.statusText || "Unknown Error"}`;
  }
  throw new Error(errMsg);
}

export async function createPreview(
  url: string,
  startTime: string,
  endTime: string
): Promise<PreviewResponse> {
  const res = await fetch(`${API_BASE}/api/clip/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, start_time: startTime, end_time: endTime }),
  });
  if (!res.ok) {
    await handleResponseError(res, "Preview request failed");
  }
  return res.json();
}

export async function generateCaption(
  clipPath: string,
  modelSize?: string
): Promise<CaptionResponse> {
  const res = await fetch(`${API_BASE}/api/caption/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ clip_path: clipPath, model_size: modelSize }),
  });
  if (!res.ok) {
    await handleResponseError(res, "Caption generation failed");
  }
  return res.json();
}

export async function editCaption(
  words: WordTimestamp[],
  fontName = "Arial",
  fontSize = 18
): Promise<{ ass_path: string }> {
  const res = await fetch(`${API_BASE}/api/caption/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ words, font_name: fontName, font_size: fontSize }),
  });
  if (!res.ok) {
    await handleResponseError(res, "Editing captions failed");
  }
  return res.json();
}

export async function renderVideo(formData: FormData): Promise<RenderResponse> {
  const res = await fetch(`${API_BASE}/api/render/render`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    await handleResponseError(res, "Rendering video failed");
  }
  return res.json();
}
