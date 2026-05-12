# Self Portable Media Hub (SPMH) 🎬
### *By Okonam*

**SPMH** is a cinematic, zero-config, "Netflix-style" media portal designed for total portability. It transforms any folder containing video files into a premium streaming experience with live previews, custom player controls, and an elegant UI.

![Project Status](https://img.shields.io/badge/Version-1.0.2-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green?style=for-the-badge)

---

## ✨ Features

- **Cross-Platform Support**: Works seamlessly on Windows, Linux, and macOS.
- **Cinematic Hero Preview**: Background video loops with random seeking for a live dashboard feel.
- **Intelligent Favorites**: One-click to save your movies; automatically prunes favorites if files are deleted from the disk.
- **Deep Scanning Engine**: Asynchronous scanner that maps your local drive and organizes content into sections.
- **Custom Video Player**: Advanced controls including speed selector (0.5x to 2x), quick skip (±15s), and language/subtitle hints.
- **Zero-Config Portability**: Designed to run directly from a portable drive or local folder with no complex setup.

---

## 🚀 How to Run

### 🪟 Windows (Recommended)
1.  Run **`Install_Dependencies.exe`** once to prepare the environment.
2.  Launch **`SPMH.exe`** to start the hub.

### 🐧 Linux / 🍎 macOS
1.  Open your terminal in the project folder.
2.  Make the scripts executable:
    ```bash
    chmod +x install.sh run.sh
    ```
3.  Run the installer:
    ```bash
    ./install.sh
    ```
4.  Start the hub:
    ```bash
    ./run.sh
    ```

---

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI), Uvicorn.
- **Frontend**: Alpine.js, Tailwind CSS.
- **Processing**: FFmpeg (for instant thumbnail generation).
- **Core Architecture**: Cross-platform Python motor with native launchers for Windows and shell scripts for Unix systems.

---

## 📂 Project Structure

```text
spmh/
├── core/
│   ├── backend/      # FastAPI Motor & Logic
│   ├── frontend/     # Netflix-style UI
│   └── data/         # Metadata & thumbnails
├── SPMH.exe          # Windows Launcher
├── Install_Dependencies.exe
├── install.sh        # Linux/Mac Installer
├── run.sh            # Linux/Mac Launcher
└── README.md
```

---

## 🤝 Credits

Developed with ❤️ by **Okonam**.  
*Turning local files into a cinematic experience, everywhere.*

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
