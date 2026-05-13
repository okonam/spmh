# Self Portable Media Hub (SPMH) 🎬 
### *The World's Only Ultra-Lightweight, Zero-Config Open Source Cinema Portal*

**SPMH** is a revolutionary, patterns-breaking media hub designed for those who demand a premium cinematic experience without the bloat. It is the only open-source project of its kind that is **extremely lightweight (< 2MB)**, requires **zero pre-configuration**, and delivers a dynamic, user-friendly interface that rivals multi-gigabyte commercial alternatives.

![Project Status](https://img.shields.io/badge/Version-1.5.7--stable-red?style=for-the-badge)
![Build Date](https://img.shields.io/badge/Build-2026.05.12-gold?style=for-the-badge)
![Lightweight](https://img.shields.io/badge/Size-%3C%202MB-green?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Type-Open%20Source-blue?style=for-the-badge)

> [!CAUTION]
> ### ⚠️ BETA VERSION - UNDER DEVELOPMENT
> This project is in continuous testing and development phase. Bugs may occur.
> **Best Experience:** For optimal animation and streaming performance, use **Chromium-based** browsers (Google Chrome, Microsoft Edge, Brave, etc).

---

## 💎 What is SPMH?

**SPMH** is a zero-config, portable media engine that transforms any folder into a cinematic streaming portal. It is designed to provide an elite viewing experience with minimal footprint.

### Core Features:
*   **High-Efficiency Player**: A robust video engine with support for multiple audio tracks, subtitles, and playback speed control.
*   **Smart Discovery**: Automatically scans your directories and provides random suggestions to help you decide what to watch.
*   **Auto-Thumbnails**: Generates high-quality previews for your entire library on-the-fly.
*   **Brain Rot Mode 🥵**: A TikTok-inspired infinite scroll experience for your local videos—perfect for non-stop entertainment.
*   **Diagnostics HUD**: Built-in telemetry for power users. Just press **'D'** while a video is playing to see real-time buffer, resolution, and network state.

---

## 🚀 How to Use

SPMH is built for total portability. No complex installers or database setups are required.

1.  **Deployment**: Simply extract the SPMH folder to **any location** where you want it to read your videos.
2.  **Launch**: Run `SPMH.exe`. The portal will automatically open in your default browser.
3.  **Proper Shutdown**: For the best experience, always close the system using the **Shutdown** button within the portal. This ensures the "Personal Server" engine is safely terminated and all resources are released.

---

## 🛠️ Coder-Friendly: Technical Architecture

SPMH is not just a tool; it's a masterclass in modular, lightweight software design. We invite developers to study the following solutions:

### 🧠 Modern Solutions for Complex Problems

*   **The Stealth Guard (C# / .NET 4.0)**: We utilized C# to create a non-interactive launcher that suppresses console windows and manages the Python lifecycle. It acts as a "Silent Process Manager," ensuring the hub disappears completely when closed.
*   **Asynchronous Streaming (Python / FastAPI)**: The core engine uses FastAPI for its industry-leading performance. It handles **Chunked Range Requests** for video streaming and uses FFmpeg for real-time thumbnail generation.
*   **Reactive Glassmorphism (Alpine.js + Tailwind CSS)**: We avoided heavy frameworks (React/Vue) to maintain the <2MB goal. Alpine.js provides the "State Management" needed for the Netflix-style HUD, while Tailwind delivers a "Glass-Hardened" aesthetic.
*   **Connection Hardening**: To prevent browser connection exhaustion during active browsing, we implemented a custom **Video Cleanup Logic** that explicitly aborts streaming sockets on `mouseleave` events.

### 📚 Tech Stack & References
*   **Backend**: Python 3.10+, FastAPI, Uvicorn.
*   **Frontend**: Alpine.js, Tailwind CSS (via CDN), Google Fonts (Outfit).
*   **Process Mgmt**: .NET 4.0 `ProcessStartInfo` (WindowStyle.Hidden).
*   **Media Motor**: FFmpeg (Integrated via dynamic path detection).

---

## 📂 Structural Integrity

```text
spmh/
├── core/
│   ├── backend/      # Python Motor (FastAPI)
│   ├── frontend/     # Hardened UI (index.html)
│   ├── Launcher.cs   # Silent Launcher Source (C#)
│   └── Setup.cs      # Installer Engine Source (C#)
├── SPMH.exe          # Professional Entry Point (< 2MB)
├── SETUP.bat         # One-click environment builder
└── README.md         # Documentation
```

---

## 🤝 Project by Okonam
*Building elite, patterns-breaking digital tools.*

**License**: Distributed under the MIT License. Open to the world for study and improvement.
