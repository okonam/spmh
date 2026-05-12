# Self Portable Media Hub (SPMH) 🎬
### *By Okonam*

**SPMH** is a cinematic, zero-config, "Netflix-style" media portal designed for total portability. It transforms any folder containing video files into a premium streaming experience with live previews, custom player controls, and an elegant UI.

![Project Status](https://img.shields.io/badge/Version-1.1.0-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green?style=for-the-badge)

---

## ✨ Features

- **Cross-Platform Support**: Works seamlessly on Windows, Linux, and macOS.
- **Cinematic Hero Preview**: Background video loops with random seeking for a live dashboard feel.
- **Intelligent Favorites**: One-click to save your movies; automatically prunes favorites if files are deleted from the disk.
- **Deep Scanning Engine**: Asynchronous scanner that maps your local drive and organizes content into sections.
- **Console Tips System**: Rotational tips in the terminal to help you get the most out of the Hub.
- **Zero-Config Portability**: Designed to run directly from a portable drive or local folder with no complex setup.

---

## 🚀 How to Run

### 🪟 Windows
1.  Run **`SETUP_SPMH.bat`** once to install dependencies.
2.  Launch **`RUN_SPMH.bat`** to start the hub.
3.  Keep the terminal window open to see helpful **Tips**.

### 🐧 Linux / 🍎 macOS
1.  Open your terminal in the project folder.
2.  Make the scripts executable: `chmod +x install.sh run.sh`
3.  Run the installer: `./install.sh`
4.  Start the hub: `./run.sh`

---

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI), Uvicorn.
- **Frontend**: Alpine.js, Tailwind CSS.
- **Processing**: FFmpeg (for instant thumbnail generation).
- **Core Architecture**: Universal Python motor with simple shell/batch launchers for maximum compatibility.

---

## 📂 Project Structure

```text
spmh/
├── core/
│   ├── backend/      # FastAPI Motor & Logic
│   ├── frontend/     # Netflix-style UI
│   └── data/         # Metadata & thumbnails
├── RUN_SPMH.bat      # Windows Launcher
├── SETUP_SPMH.bat    # Windows Installer
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
