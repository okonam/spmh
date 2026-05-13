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

## 💎 Why SPMH is Unique

While tools like Plex or Jellyfin are powerful, they are heavy, require complex database management, and force you into account-based ecosystems. **SPMH is the antithesis of bloat.**

1.  **Extreme Lightness**: The entire system, including the silent backend engine and the cinematic frontend, is optimized to run under **2MB**. It is the most portable media hub ever built.
2.  **Zero Configuration**: No databases. No accounts. No setup screens. Drop SPMH in your media collection, and it instantly maps your library.
3.  **Dynamic Discovery**: Unlike static servers, SPMH uses a recursive parent-mapping logic that looks "behind" the application folder to find your movies without needing permission to your entire drive.
4.  **Hardened Memory Assets**: To ensure maximum speed and prevent UI tampering, all branding assets (logos, icons) are baked into the core as **Base64 memory strings**. It loads instantly, every time.

---

## 🚀 One-Click Cinematic Setup

1.  **Preparation**: Run `SETUP.bat` once. It automatically builds your Python environment and configures the streaming engine.
2.  **Launch**: Open `SPMH.exe`. 
3.  **Experience**: A professional, Netflix-inspired portal will open. Explore with **horizontal drag-to-scroll**, **hover video previews**, and **dynamic section modals**.
4.  **Stealth Shutdown**: To close the system, use the integrated **Shutdown** button in the portal to safely clean up all background processes.

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
