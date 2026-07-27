const API_BASE = "";

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
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
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
    const err = await res.json().catch(() => ({ detail: "Caption failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
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
    const err = await res.json().catch(() => ({ detail: "Edit failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function renderVideo(formData: FormData): Promise<RenderResponse> {
  const res = await fetch(`${API_BASE}/api/render/render`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Render failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
