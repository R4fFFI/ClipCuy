"use client";

import { useState, useRef, useCallback } from "react";
import {
  createPreview,
  generateCaption,
  editCaption,
  renderVideo,
  type WordTimestamp,
} from "./api-client";

type Step = "clip" | "caption" | "render" | "done";

export default function Home() {
  const [step, setStep] = useState<Step>("clip");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [url, setUrl] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  const [previewUrl, setPreviewUrl] = useState("");
  const [clipPath, setClipPath] = useState("");

  const [words, setWords] = useState<WordTimestamp[]>([]);
  const [assPath, setAssPath] = useState("");

  const [watermark, setWatermark] = useState<File | null>(null);
  const [watermarkPos, setWatermarkPos] = useState("top_right");
  const [endorsement, setEndorsement] = useState<File | null>(null);
  const [endorsePos, setEndorsePos] = useState("intro");
  const [aspectRatio, setAspectRatio] = useState("");
  const [arMode, setArMode] = useState("center_crop");

  const [downloadUrl, setDownloadUrl] = useState("");
  const videoRef = useRef<HTMLVideoElement>(null);

  const clearError = useCallback(() => setError(""), []);

  const handlePreview = async () => {
    clearError();
    if (!url || !startTime || !endTime) {
      setError("URL, Start Time, dan End Time wajib diisi");
      return;
    }
    setLoading(true);
    try {
      const res = await createPreview(url, startTime, endTime);
      setPreviewUrl(res.preview_url);
      setClipPath(res.clip_path);
      setStep("caption");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Preview failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCaption = async () => {
    clearError();
    setLoading(true);
    try {
      const res = await generateCaption(clipPath);
      setWords(res.words);
      setAssPath(res.ass_path);
      setStep("render");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Caption failed");
    } finally {
      setLoading(false);
    }
  };

  const handleWordEdit = (idx: number, newWord: string) => {
    setWords((prev) => prev.map((w, i) => (i === idx ? { ...w, word: newWord } : w)));
  };

  const handleDeleteWord = (idx: number) => {
    setWords((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSaveCaption = async () => {
    clearError();
    setLoading(true);
    try {
      const res = await editCaption(words);
      setAssPath(res.ass_path);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save caption failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRender = async () => {
    clearError();
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("clip_path", clipPath);
      if (watermark) {
        fd.append("watermark", watermark);
        fd.append("watermark_position", watermarkPos);
      }
      if (endorsement) {
        fd.append("endorsement", endorsement);
        fd.append("endorsement_position", endorsePos);
      }
      if (aspectRatio) {
        fd.append("aspect_ratio", aspectRatio);
        fd.append("aspect_ratio_mode", arMode);
      }
      if (assPath) {
        fd.append("ass_path", assPath);
      }
      const res = await renderVideo(fd);
      setDownloadUrl(res.download_url);
      setStep("done");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Render failed");
    } finally {
      setLoading(false);
    }
  };

  const positions = [
    "top_left", "top_center", "top_right",
    "center_left", "center", "center_right",
    "bottom_left", "bottom_center", "bottom_right",
  ];

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-accent">ClipCuy</h1>
        <p className="text-muted text-sm mt-1">AI Video Clip Studio</p>
      </header>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-danger/10 border border-danger/30 text-danger text-sm">
          {error}
        </div>
      )}

      <section className="bg-card border border-card-border rounded-xl p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">1. YouTube Clip</h2>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="YouTube URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full px-4 py-2.5 bg-background border border-card-border rounded-lg focus:border-accent focus:outline-none"
          />
          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Start (00:30 atau 30)"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="px-4 py-2.5 bg-background border border-card-border rounded-lg focus:border-accent focus:outline-none"
            />
            <input
              type="text"
              placeholder="End (01:30 atau 90)"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="px-4 py-2.5 bg-background border border-card-border rounded-lg focus:border-accent focus:outline-none"
            />
          </div>
          <button
            onClick={handlePreview}
            disabled={loading}
            className="w-full py-2.5 bg-accent hover:bg-accent-hover text-white font-medium rounded-lg disabled:opacity-50 transition-colors"
          >
            {loading && step === "clip" ? "Processing..." : "Generate Preview"}
          </button>
        </div>
      </section>

      {previewUrl && (
        <section className="bg-card border border-card-border rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Preview</h2>
          <video
            ref={videoRef}
            src={previewUrl}
            controls
            className="w-full rounded-lg bg-black"
          />
        </section>
      )}

      {step !== "clip" && (
        <section className="bg-card border border-card-border rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">2. AI Caption</h2>
          {words.length === 0 ? (
            <button
              onClick={handleCaption}
              disabled={loading}
              className="w-full py-2.5 bg-accent hover:bg-accent-hover text-white font-medium rounded-lg disabled:opacity-50 transition-colors"
            >
              {loading ? "Generating..." : "Generate AI Caption"}
            </button>
          ) : (
            <div>
              <div className="max-h-60 overflow-y-auto mb-3 space-y-1">
                {words.map((w, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="text-muted w-20 shrink-0 font-mono">
                      {w.start.toFixed(2)}s
                    </span>
                    <input
                      type="text"
                      value={w.word}
                      onChange={(e) => handleWordEdit(i, e.target.value)}
                      className="flex-1 px-2 py-1 bg-background border border-card-border rounded focus:border-accent focus:outline-none"
                    />
                    <button
                      onClick={() => handleDeleteWord(i)}
                      className="text-danger hover:text-danger/80 text-xs px-2"
                    >
                      X
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={handleSaveCaption}
                disabled={loading}
                className="w-full py-2 bg-success/20 hover:bg-success/30 text-success font-medium rounded-lg disabled:opacity-50 transition-colors"
              >
                {loading ? "Saving..." : "Save Edited Caption"}
              </button>
            </div>
          )}
        </section>
      )}

      {step === "render" && (
        <section className="bg-card border border-card-border rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">3. Render Options</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-muted mb-1">Watermark (PNG/JPG)</label>
              <input
                type="file"
                accept="image/png,image/jpeg"
                onChange={(e) => setWatermark(e.target.files?.[0] || null)}
                className="w-full text-sm file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-accent/20 file:text-accent hover:file:bg-accent/30"
              />
              {watermark && (
                <select
                  value={watermarkPos}
                  onChange={(e) => setWatermarkPos(e.target.value)}
                  className="mt-2 w-full px-3 py-2 bg-background border border-card-border rounded-lg"
                >
                  {positions.map((p) => (
                    <option key={p} value={p}>
                      {p.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div>
              <label className="block text-sm text-muted mb-1">Endorsement Video</label>
              <input
                type="file"
                accept="video/mp4,video/*"
                onChange={(e) => setEndorsement(e.target.files?.[0] || null)}
                className="w-full text-sm file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-accent/20 file:text-accent hover:file:bg-accent/30"
              />
              {endorsement && (
                <select
                  value={endorsePos}
                  onChange={(e) => setEndorsePos(e.target.value)}
                  className="mt-2 w-full px-3 py-2 bg-background border border-card-border rounded-lg"
                >
                  <option value="intro">Intro</option>
                  <option value="outro">Outro</option>
                </select>
              )}
            </div>

            <div>
              <label className="block text-sm text-muted mb-1">Aspect Ratio</label>
              <select
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full px-3 py-2 bg-background border border-card-border rounded-lg"
              >
                <option value="">Original</option>
                <option value="9:16">9:16 (Vertical/Shorts)</option>
                <option value="1:1">1:1 (Square)</option>
                <option value="16:9">16:9 (Landscape)</option>
              </select>
              {aspectRatio && (
                <select
                  value={arMode}
                  onChange={(e) => setArMode(e.target.value)}
                  className="mt-2 w-full px-3 py-2 bg-background border border-card-border rounded-lg"
                >
                  <option value="center_crop">Center Crop</option>
                  <option value="blurred_background">Blurred Background</option>
                </select>
              )}
            </div>

            <button
              onClick={handleRender}
              disabled={loading}
              className="w-full py-3 bg-accent hover:bg-accent-hover text-white font-bold rounded-lg disabled:opacity-50 transition-colors text-lg"
            >
              {loading ? "Rendering..." : "Render Final Video"}
            </button>
          </div>
        </section>
      )}

      {step === "done" && downloadUrl && (
        <section className="bg-card border border-success/30 rounded-xl p-6 mb-6 text-center">
          <h2 className="text-lg font-semibold mb-4 text-success">Video Ready!</h2>
          <video src={downloadUrl} controls className="w-full rounded-lg bg-black mb-4" />
          <a
            href={downloadUrl}
            download
            className="inline-block px-8 py-3 bg-success hover:bg-success/80 text-white font-bold rounded-lg transition-colors"
          >
            Download MP4
          </a>
        </section>
      )}
    </main>
  );
}
