"""
SPMH — Self Portable Media Hub (Backend v1.0.5)
By Okonam - Cinematic Cross-Platform Media Hub
"""

import os
import json
import hashlib
import random
import subprocess
import threading
import time
import platform
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- FAIL-SAFE PATH DETECTION ---
# We want to find the root folder of the project (where core/ is located)
current_file = Path(__file__).resolve()
# Try to find 'core' folder in parents
project_root = current_file.parent
for parent in current_file.parents:
    if (parent / "core").exists():
        project_root = parent
        break

CORE_DIR = project_root / "core"
VIDEO_ROOT = project_root
THUMB_DIR = CORE_DIR / "data" / "thumbs"
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v"}
SKIP_DIRS = {"core", ".gemini", "node_modules", "venv", ".git", "data", "frontend", "__pycache__"}

THUMB_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SPMH API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE ---
LIBRARY_STATE = {
    "sections": [],
    "is_scanning": False,
    "total_videos": 0,
    "last_update": None
}

def get_id(path_str):
    return hashlib.md5(path_str.encode()).hexdigest()

def format_video_data(path: Path, vid_id: str):
    stats = path.stat()
    size_gb = stats.st_size / (1024**3)
    return {
        "id": vid_id,
        "title": path.stem.replace(".", " ").replace("_", " ").title(),
        "path": str(path),
        "size": f"{size_gb:.2f} GB",
        "modified": stats.st_mtime,
        "format": path.suffix.upper()[1:],
        "duration": "N/A"
    }

def background_scanner():
    global LIBRARY_STATE
    LIBRARY_STATE["is_scanning"] = True
    LIBRARY_STATE["total_videos"] = 0
    LIBRARY_STATE["sections"] = []
    
    print(f"\n[SCAN] Deep scanning: {VIDEO_ROOT}")
    
    try:
        # 1. Root Scan
        root_videos = []
        for item in VIDEO_ROOT.iterdir():
            if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                vid_id = get_id(str(item))
                root_videos.append(format_video_data(item, vid_id))
                LIBRARY_STATE["total_videos"] += 1
                print(f" -> Found: {item.name}")
        
        if root_videos:
            update_section("Root Files", "root-files", root_videos)
        
        # 2. Folder Scan
        for entry in sorted(VIDEO_ROOT.iterdir()):
            if entry.is_dir() and entry.name not in SKIP_DIRS and not entry.name.startswith(".") and entry.name != "core":
                videos = []
                print(f"[SCAN] Checking folder: {entry.name}")
                for root, dirs, files in os.walk(entry):
                    # Filter out skip dirs in-place
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                            vid_id = get_id(str(file_path))
                            videos.append(format_video_data(file_path, vid_id))
                            LIBRARY_STATE["total_videos"] += 1
                            print(f"   + {file}")
                
                if videos:
                    update_section(entry.name.replace("_", " ").title(), get_id(str(entry)), videos)
    except Exception as e:
        print(f"[ERROR] Scan failed: {e}")
    finally:
        LIBRARY_STATE["is_scanning"] = False
        LIBRARY_STATE["last_update"] = datetime.now().isoformat()
        print(f"[OK] Total videos found: {LIBRARY_STATE['total_videos']}")

def update_section(name, slug, videos):
    global LIBRARY_STATE
    LIBRARY_STATE["sections"].append({
        "name": name,
        "slug": slug,
        "videos": sorted(videos, key=lambda v: v["modified"], reverse=True)
    })

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=background_scanner, daemon=True).start()

@app.get("/api/hub")
def get_hub():
    return {
        "title": "SPMH - Portable Media Hub",
        "sections": LIBRARY_STATE["sections"],
        "is_scanning": LIBRARY_STATE["is_scanning"],
        "total": LIBRARY_STATE["total_videos"]
    }

@app.get("/api/thumb/{video_id}")
def get_thumb(video_id: str):
    thumb_path = THUMB_DIR / f"{video_id}.jpg"
    if thumb_path.exists(): return FileResponse(thumb_path)
    
    video_path = None
    for sec in LIBRARY_STATE["sections"]:
        for v in sec["videos"]:
            if v["id"] == video_id:
                video_path = v["path"]; break
    
    if video_path and os.path.exists(video_path):
        try:
            cmd = ["ffmpeg", "-y", "-ss", "00:00:01", "-i", video_path, "-frames:v", "1", "-q:v", "2", str(thumb_path)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if thumb_path.exists(): return FileResponse(thumb_path)
        except: pass
    return FileResponse(CORE_DIR / "frontend" / "assets" / "logo.png") 

@app.get("/api/stream/{video_id}")
async def stream_video(video_id: str):
    video_path = None
    for sec in LIBRARY_STATE["sections"]:
        for v in sec["videos"]:
            if v["id"] == video_id:
                video_path = v["path"]; break
    if not video_path: raise HTTPException(404)
    return FileResponse(video_path)

@app.post("/api/open/{video_id}")
def open_explorer(video_id: str):
    video_path = None
    for sec in LIBRARY_STATE["sections"]:
        for v in sec["videos"]:
            if v["id"] == video_id:
                video_path = v["path"]; break
    
    if video_path and os.path.exists(video_path):
        system = platform.system()
        try:
            if system == "Windows": subprocess.run(["explorer", "/select,", video_path])
            elif system == "Darwin": subprocess.run(["open", "-R", video_path])
            else: subprocess.run(["xdg-open", os.path.dirname(video_path)])
            return {"status": "opened"}
        except: return {"status": "error"}
    return {"status": "not_found"}

@app.post("/api/stop")
def stop_server():
    print("[!] Shutdown command received. Closing...")
    def shutdown(): time.sleep(0.5); os._exit(0)
    threading.Thread(target=shutdown).start()
    return {"status": "stopping"}

FRONTEND_DIR = CORE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    
    TIPS = [
        "TIP: Use the search bar to quickly find any movie in your library.",
        "TIP: Right-click the player for audio and subtitle options.",
        "TIP: Click the heart icon to save movies to your Favorites list.",
        "TIP: The Hero section features a cinematic live preview of your movies.",
        "TIP: Shutdown the hub using the Power icon to safely close all processes.",
        "TIP: SPMH is zero-config. Just drop movies in folders and they will appear here.",
        "TIP: Press ESC to quickly close any open modal or the video player."
    ]
    
    def console_tips():
        i = 0
        while True:
            print(f"\n[SPMH ACTIVE] {TIPS[i % len(TIPS)]}")
            i += 1
            time.sleep(15)

    threading.Thread(target=console_tips, daemon=True).start()
    
    print("\n" + "="*50)
    print("      SELF PORTABLE MEDIA HUB - BY OKONAM")
    print("="*50)
    print(" -> Access the portal at: http://localhost:8888")
    print(" -> Keep this window open while using the Hub.")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="critical")
