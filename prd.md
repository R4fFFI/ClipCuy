# Product Requirements Document (PRD)

# YT Clip Studio

**Version:** 1.0.0  
**Status:** Draft  
**Author:** Product Team  
**Last Updated:** July 2026

---

# 1. Executive Summary

YT Clip Studio adalah aplikasi web berbasis AI yang memungkinkan pengguna membuat video pendek dari YouTube secara cepat melalui proses clipping, editing, branding, dan pembuatan subtitle otomatis.

Aplikasi ditujukan untuk content creator, editor video, affiliate marketer, dan social media manager yang membutuhkan workflow cepat dalam membuat konten Shorts, TikTok, Instagram Reels, maupun video promosi.

Fokus utama produk adalah mengurangi proses editing manual menjadi beberapa klik saja.

---

# 2. Product Vision

Menyediakan platform AI yang mampu mengubah video YouTube menjadi konten pendek siap dipublikasikan lengkap dengan:

- Auto clipping
- Watermark branding
- Intro / Outro endorsement
- AI subtitle
- Aspect ratio converter
- Fast rendering

---

# 3. Goals

## Primary Goals

- Memotong video YouTube berdasarkan timestamp.
- Membuat preview dengan cepat.
- Menghasilkan subtitle otomatis menggunakan AI.
- Mendukung watermark branding.
- Mendukung video endorsement.
- Mendukung rendering ke berbagai aspect ratio.
- Menghasilkan video MP4 siap upload.

## Success Metrics

- Preview clip < 5 detik
- Render video 60 detik < 20 detik (GPU)
- Subtitle word-level accuracy tinggi
- UI sederhana dan mudah digunakan

---

# 4. Target Users

## 4.1 Content Creator

Membuat Shorts dari video panjang.

## 4.2 Video Editor

Menghemat waktu editing.

## 4.3 Affiliate Marketer

Menambahkan branding dan video sponsor.

## 4.4 Social Media Manager

Produksi konten pendek secara massal.

---

# 5. User Stories

### US-001

Sebagai content creator,
saya ingin memotong video YouTube,
agar dapat membuat Shorts.

### US-002

Sebagai marketer,
saya ingin menambahkan watermark,
agar branding tetap terlihat.

### US-003

Sebagai editor,
saya ingin subtitle otomatis,
agar tidak perlu mengetik manual.

### US-004

Sebagai affiliate,
saya ingin menyisipkan video endorse,
agar promosi menjadi otomatis.

---

# 6. Features

---

# 6.1 YouTube Video Clipping

### Deskripsi

Mengambil potongan video dari URL YouTube.

### Input

- URL
- Start Time
- End Time

### Supported Format

- YouTube
- YouTube Shorts

### Timestamp Format

- MM:SS
- HH:MM:SS
- Total Seconds

---

# 6.2 Preview Generation

Generate proxy video resolusi rendah.

Tujuan:

- Preview cepat
- Tidak perlu render penuh

Output:

- MP4 Preview
- Streaming URL

---

# 6.3 Watermark

Upload:

- PNG
- JPG

Posisi:

- Top Left
- Top Center
- Top Right

- Center Left
- Center

- Center Right

- Bottom Left
- Bottom Center
- Bottom Right

Support:

- Opacity
- Margin
- Scale

---

# 6.4 Endorsement Clip

Upload video sponsor.

Pilihan posisi:

- Intro
- Outro
- Custom Timestamp

Metode:

- FFmpeg concat

---

# 6.5 Aspect Ratio Converter

Supported:

## 16:9

Landscape

## 9:16

Vertical

Mode:

- Center Crop
- Blurred Background

## 1:1

Square

---

# 6.6 AI Auto Caption

Engine:

- stable-ts
- faster-whisper

Kemampuan:

- Speech-to-Text
- Word Timestamp
- Sentence Timestamp

Support:

- GPU CUDA
- CPU INT8

---

# 6.7 Subtitle Generator

Output:

- ASS Subtitle

Style:

Alignment:

5

Artinya:

Center Center

Support:

- Karaoke Highlight
- Active Word Highlight
- Outline
- Shadow
- Font Size
- Font Family

---

# 6.8 Manual Caption Editor

Pengguna dapat:

- Mengubah kata
- Menghapus kata
- Menambah kata

Sebelum proses render.

---

# 6.9 Final Rendering

Pipeline:

Video

↓

Watermark

↓

Endorse

↓

Aspect Ratio

↓

Subtitle

↓

MP4 Output

---

# 7. Functional Requirements

## FR-001

Input URL YouTube.

## FR-002

Input timestamp.

## FR-003

Generate preview.

## FR-004

Upload watermark.

## FR-005

Upload endorsement.

## FR-006

Generate subtitle AI.

## FR-007

Edit subtitle.

## FR-008

Render video.

## FR-009

Download MP4.

---

# 8. Non Functional Requirements

## Performance

Preview:

< 5 detik

Render:

< 20 detik (60s GPU)

---

## Reliability

Menangani:

- URL invalid
- Watermark invalid
- Video unavailable
- Subtitle gagal
- Timeout

---

## Scalability

Task Queue:

Celery

Broker:

Redis

Background Rendering:

Ya

---

## Temporary Storage

Semua file temporary dihapus otomatis setelah:

1 jam

---

# 9. Technical Stack

## Backend

- Python 3.11+
- FastAPI
- Uvicorn

Video:

- FFmpeg
- FFprobe

Downloader:

- yt-dlp
- curl_cffi

AI:

- stable-ts
- faster-whisper

Queue:

- Celery
- Redis

---

## Frontend

- Next.js
- React
- Tailwind CSS

Player:

- HTML5 Video
- HLS.js

---

# 10. Backend Architecture

/backend

```
backend/
│
├── main.py
├── downloader.py
├── processor.py
├── caption.py
├── worker.py
├── config.py
├── utils.py
│
├── routes/
│
├── services/
│
├── temp/
│
└── outputs/
```

---

# 11. API Specification

## POST

/api/clip/preview

Request

```
{
  "url": "",
  "start_time": "",
  "end_time": ""
}
```

Response

```
{
  "preview_url": ""
}
```

---

## POST

/api/caption/generate

Response

```
{
  "words":[]
}
```

---

## POST

/api/clip/render

Response

```
{
  "download_url":""
}
```

---

# 12. Frontend UI

Halaman utama terdiri dari:

- Input URL YouTube
- Timestamp Start
- Timestamp End
- Upload Watermark
- Upload Endorse
- Aspect Ratio Dropdown
- Preview Video
- Generate Caption
- Caption Editor
- Render Button
- Download Button

---

# 13. Rendering Workflow

1. User memasukkan URL.

2. Backend memotong video menggunakan yt-dlp + FFmpeg.

3. Preview dibuat.

4. Subtitle AI diproses.

5. User mengedit subtitle.

6. Worker melakukan rendering:

- Watermark
- Endorse
- Subtitle
- Aspect Ratio

7. MP4 final dibuat.

8. User mengunduh hasil.

---

# 14. Error Handling

Kasus yang ditangani:

- URL tidak valid
- Video private
- Geo blocked
- Watermark rusak
- Subtitle gagal dibuat
- FFmpeg error
- Timeout rendering
- Storage penuh

---

# 15. Future Roadmap

Versi berikutnya akan mendukung:

- TikTok URL
- Instagram Reels URL
- Facebook Video
- Batch Processing
- AI Highlight Detection
- Auto Viral Clip Detection
- Multi-language Subtitle
- Voice Translation
- Cloud Storage Integration
- User Authentication
- Team Workspace
- Subscription System

---

# 16. Dependencies

Python Packages

- fastapi
- uvicorn
- yt-dlp
- stable-ts
- faster-whisper
- celery
- redis
- python-multipart
- curl_cffi
- ffmpeg-python
- aiofiles
- pydantic
- python-dotenv

---

# 17. Deployment

Development

- FastAPI
- React
- Redis
- FFmpeg

Production

- Docker
- Docker Compose
- Nginx
- HTTPS
- GPU CUDA (Optional)

---

# 18. Acceptance Criteria

Produk dianggap memenuhi kebutuhan apabila:

- Video YouTube dapat dipotong berdasarkan timestamp.
- Preview dapat diputar.
- Subtitle AI berhasil dibuat.
- Subtitle berada di tengah layar (Alignment: 5).
- Watermark muncul sesuai posisi.
- Video endorse berhasil disisipkan.
- Aspect ratio berhasil dikonversi.
- Video final dapat diunduh dalam format MP4.