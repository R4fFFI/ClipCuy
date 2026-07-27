# ClipCuy 🎬

ClipCuy adalah platform pemrosesan dan ekstraksi klip video YouTube otomatis berbasis AI. Aplikasi ini dirancang untuk mengubah video berdurasi panjang dari YouTube menjadi klip pendek siap rilis (Shorts, Reels, TikTok) lengkap dengan penyesuaian rasio layar, watermark kustom, penyisipan iklan/endorsement, serta auto-captioning berstempel waktu presisi dengan posisi teks di tengah layar.

## 🌟 Fitur Utama

- **Remote Timestamp Clipping**: Mengunduh dan memotong fragmen video YouTube berdasarkan spesifikasi detik/menit tanpa perlu mengunduh seluruh berkas video.
- **AI Auto-Captioning (Stable Whisper)**: Transkripsi suara otomatis menggunakan model AI stable-ts dengan tingkat akurasi tinggi per kata (word-level timestamps).
- **Center-Aligned Animated Subtitles**: Format subtitel SubStation Alpha (.ass) otomatis dengan posisi Center-Center (Alignment: 5) dan efek karaoke highlight.
- **Dynamic Aspect Ratio Conversion**: Dukungan konversi rasio aspek instan ke 9:16 (Vertikal), 1:1 (Persegi), dan 16:9 (Widescreen) dengan metode center-crop atau blurred background.
- **Branding & Media Overlay**: Penempelan watermark gambar (PNG/JPEG) serta penyisipan klip endorsement (intro/outro) secara langsung.
- **Fast Live Preview**: Pemutaran preview video resolusi cepat pada antarmuka web sebelum proses rendering akhir.

## 🛠️ Tech Stack

### Backend & AI Engine
- **Framework**: Python 3.11+ / FastAPI
- **Media Engine**: FFmpeg, yt-dlp
- **AI / ASR**: stable-ts (Stable Whisper), faster-whisper
- **Task Queue**: Celery & Redis

### Frontend
- **Framework**: Next.js / React, Tailwind CSS
- **Media Player**: HTML5 Video / HLS.js

## 🚀 Panduan Instalasi & Penggunaan

### Prasyarat System
- Python 3.10+
- FFmpeg terinstal dan terkonfigurasi di System PATH
- Node.js 18+ (untuk frontend)
- GPU dengan dukungan CUDA (opsional, untuk akselerasi transkripsi AI)

### 1. Clone Repositori
```bash
git clone https://github.com/R4fFFI/ClipCuy.git
cd ClipCuy
```

### 2. Setup Backend
```bash
# Buat dan aktifkan virtual environment
python -m venv venv
source venv/bin/activate  # Untuk Linux/macOS
# venv\Scripts\activate  # Untuk Windows

# Instal dependensi
pip install -r requirements.txt
```

### 3. Jalankan Server Development
```bash
# Jalankan FastAPI Backend
uvicorn backend.main:app --reload --port 8000
```

## 📁 Project Structure

```
ClipCuy/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── downloader.py
│   ├── processor.py
│   ├── caption.py
│   ├── worker.py
│   ├── utils.py
│   ├── routes/
│   ├── services/
│   ├── temp/
│   └── outputs/
├── frontend/
├── requirements.txt
├── prd.md
└── README.md
```

## 📄 License

MIT
