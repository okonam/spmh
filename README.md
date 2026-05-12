# Self Portable Media Hub (SPMH) 🎬
### *By Okonam*

**SPMH** is a cinematic, zero-config, "Netflix-style" media portal designed for total portability. It transforms any folder containing video files into a premium streaming experience with live previews, custom player controls, and an elegant UI.

![Project Status](https://img.shields.io/badge/Version-1.0.0-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

---

## ✨ Features

- **Cinematic Hero Preview**: Background video loops with random seeking for a live dashboard feel.
- **Intelligent Favorites**: One-click to save your movies; automatically prunes favorites if files are deleted from the disk.
- **Deep Scanning Engine**: Asynchronous scanner that maps your local drive and organizes content into sections.
- **Custom Video Player**: Advanced controls including speed selector (0.5x to 2x), quick skip (±15s), and language/subtitle hints.
- **Zero-Config Portability**: Designed to run directly from a portable drive or local folder with no complex setup.
- **Real-time Search**: Instant filtering of movies and sections.

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI), Uvicorn.
- **Frontend**: Alpine.js, Tailwind CSS, Vanilla CSS.
- **Processing**: FFmpeg (for instant thumbnail generation).
- **Core Architecture**: Split design with a portable C# launcher and a Python-powered motor.

---

## 🚀 Quick Start

1. **Prerequisites**: Ensure you have [Python 3.10+](https://python.org) and [FFmpeg](https://ffmpeg.org) installed.
2. **Setup**: Run the setup script to install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. **Run**: Execute the `main.py` (or use the provided C# Launcher).
   ```bash
   python core/backend/main.py
   ```
4. **Enjoy**: Open your browser at `http://localhost:8888`.

---

## 📂 Project Structure

```text
spmh/
├── core/
│   ├── backend/      # FastAPI Motor & Logic
│   ├── frontend/     # Netflix-style UI (HTML/Alpine.js)
│   └── data/         # Auto-generated metadata & thumbnails
├── Launcher.exe      # C# Portable Launcher
└── README.md
```

---

## 🤝 Credits

Developed with ❤️ by **Okonam**.  
*Turning local files into a cinematic experience.*

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
