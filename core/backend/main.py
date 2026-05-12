"""
SPMH — Self Portable Media Hub (Backend v1.5.7-stable)
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

# --- SMART PATH DETECTION ---
# We find where 'core' is, then we set VIDEO_ROOT to the PARENT of the project folder
current_file = Path(__file__).resolve()
project_folder = current_file.parent
for parent in current_file.parents:
    if (parent / "core").exists():
        project_folder = parent
        break

# The user wants to scan "behind" (parent of) the hub folder
VIDEO_ROOT = project_folder.parent
CORE_DIR = project_folder / "core"
THUMB_DIR = CORE_DIR / "data" / "thumbs"
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v"}

# We MUST skip the hub's own folder to avoid scanning source files/thumbs as media
SKIP_DIRS = {"core", ".gemini", "node_modules", "venv", ".git", "data", "frontend", "__pycache__", project_folder.name}

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
    
    # Resolve paths once to avoid comparison issues
    abs_project = project_folder.resolve()
    abs_root = VIDEO_ROOT.resolve()
    
    print(f"\n[SCAN] Deep scanning library at: {abs_root}")
    print(f"[SCAN] Project path: {abs_project}")
    
    try:
        # 1. Root Scan (Files in the same level as the Hub folder)
        root_videos = []
        try:
            for item in abs_root.iterdir():
                if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                    vid_id = get_id(str(item))
                    root_videos.append(format_video_data(item, vid_id))
                    LIBRARY_STATE["total_videos"] += 1
                    print(f" -> Found in root: {item.name}")
        except Exception as e:
            print(f"[WARN] Error scanning root files: {e}")
        
        if root_videos:
            update_section("Root Files", "root-files", root_videos)
        
        # 2. Folder Scan (Subfolders in the parent directory)
        # We collect entries first to avoid issues with changing directory state
        entries = []
        try:
            entries = sorted(list(abs_root.iterdir()))
        except Exception as e:
            print(f"[ERROR] Could not list root directory: {e}")
            return

        for entry in entries:
            try:
                # Skip if not a directory
                if not entry.is_dir():
                    continue
                
                # Skip project folder itself by path, not just name
                if entry.resolve() == abs_project:
                    print(f"[SCAN] Skipping project folder: {entry.name}")
                    continue
                
                # Skip hidden folders or known system folders
                if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                    continue
                    
                videos = []
                print(f"[SCAN] Checking folder: {entry.name}")
                
                for root, dirs, files in os.walk(entry):
                    # Prune dirs in-place to avoid system/hidden folders
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
                    
                    # Check if this subfolder is the project folder (safety check)
                    if Path(root).resolve() == abs_project:
                        dirs[:] = [] # Stop recursion here
                        continue

                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                            vid_id = get_id(str(file_path))
                            videos.append(format_video_data(file_path, vid_id))
                            LIBRARY_STATE["total_videos"] += 1
                            # print(f"   + {file}") # Excessive logging
                
                if videos:
                    print(f" -> Found {len(videos)} videos in {entry.name}")
                    update_section(entry.name.replace("_", " ").title(), get_id(str(entry)), videos)
            except Exception as e:
                print(f"[WARN] Failed to scan folder {entry.name}: {e}")
                
    except Exception as e:
        print(f"[ERROR] Global scan failed: {e}")
    finally:
        LIBRARY_STATE["is_scanning"] = False
        LIBRARY_STATE["last_update"] = datetime.now().isoformat()
        print(f"[OK] Scan complete. Total: {LIBRARY_STATE['total_videos']} videos found.\n")

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
    return HTTPException(status_code=404, detail="Thumbnail not found") 

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
    print(" -> Scanning media in: " + str(VIDEO_ROOT))
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="critical")
