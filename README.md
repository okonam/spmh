# Self Portable Media Hub (SPMH) 🎬
### *By Okonam*

**SPMH** is a cinematic, zero-config, "Netflix-style" media portal designed for total portability. It transforms any folder containing video files into a premium streaming experience with live previews, custom player controls, and an elegant UI.

![Project Status](https://img.shields.io/badge/Version-1.2.0-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge)

---

## ✨ Features

- **Professional Launcher**: Dedicated `.exe` launcher with a built-in Console Tips system.
- **Cinematic Hero Preview**: Background video loops with random seeking for a live dashboard feel.
- **Intelligent Favorites**: One-click to save your movies; automatically prunes favorites if files are deleted from the disk.
- **Deep Scanning Engine**: Asynchronous scanner that maps your local drive and organizes content into sections.
- **Zero-Config Portability**: Designed to run directly from a portable drive or local folder with no complex setup.

---

## 🚀 How to Run (Windows)

1.  Run **`Install_Dependencies.exe`** once to prepare the environment.
2.  Launch **`SPMH.exe`** to start the hub.
3.  Enjoy the cinematic experience and follow the **Tips** in the console.

---

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI), Uvicorn.
- **Frontend**: Alpine.js, Tailwind CSS.
- **Launchers**: C# (.NET 4.8) compiled native executables.
- **Processing**: FFmpeg (for instant thumbnail generation).

---

## 📂 Project Structure

```text
spmh/
├── core/
│   ├── backend/      # FastAPI Motor & Logic
│   ├── frontend/     # Netflix-style UI
│   └── data/         # Metadata & thumbnails
├── SPMH.exe          # Professional Launcher
├── Install_Dependencies.exe
└── README.md
```

---

## 🤝 Credits

Developed with ❤️ by **Okonam**.  
*Turning local files into a cinematic experience.*

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
