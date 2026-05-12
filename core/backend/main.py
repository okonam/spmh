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

# PORTABLE ENHANCEMENT: If we are inside an "Agente" or "projects" folder structure, 
# we go up to the parent of those folders to ensure we scan the user's main media root.
for parent in current_file.parents:
    if parent.name.lower() in ["agente", "projects"]:
        VIDEO_ROOT = parent.parent
        break

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
    "last_update": None,
    "scan_log": []
}

VIDEO_PATH_CACHE = {} # Fast lookup for ID -> Path

def get_id(path_str):
    return hashlib.md5(path_str.encode()).hexdigest()

def format_video_data(path: Path, vid_id: str):
    try:
        stats = path.stat()
        size_gb = stats.st_size / (1024**3)
        VIDEO_PATH_CACHE[vid_id] = str(path)
        return {
            "id": vid_id,
            "title": path.stem.replace(".", " ").replace("_", " ").title(),
            "path": str(path),
            "size": f"{size_gb:.2f} GB",
            "modified": stats.st_mtime,
            "format": path.suffix.upper()[1:],
            "duration": "N/A"
        }
    except:
        return None

def log_scan(msg):
    global LIBRARY_STATE
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    LIBRARY_STATE["scan_log"].append(full_msg)
    if len(LIBRARY_STATE["scan_log"]) > 100:
        LIBRARY_STATE["scan_log"].pop(0)

def background_scanner():
    global LIBRARY_STATE, VIDEO_PATH_CACHE
    LIBRARY_STATE["is_scanning"] = True
    LIBRARY_STATE["total_videos"] = 0
    LIBRARY_STATE["sections"] = []
    LIBRARY_STATE["scan_log"] = []
    VIDEO_PATH_CACHE = {} # Reset on new scan
    
    # Resolve paths once
    abs_project = project_folder.resolve()
    abs_root = VIDEO_ROOT.resolve()
    abs_core = (project_folder / "core").resolve()
    
    # Precise folders to skip (absolute paths)
    SYSTEM_PATHS = {
        abs_project,
        abs_core,
        (abs_core / "data").resolve(),
        (abs_core / "frontend").resolve(),
        (abs_core / "backend").resolve()
    }
    
    log_scan(f"Starting scan at: {abs_root}")
    log_scan(f"Project path: {abs_project}")
    
    try:
        # 1. Root Scan
        root_videos = []
        try:
            it = abs_root.iterdir()
            while True:
                try:
                    item = next(it)
                    if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                        vid_id = get_id(str(item.resolve()))
                        vdata = format_video_data(item, vid_id)
                        if vdata:
                            root_videos.append(vdata)
                            LIBRARY_STATE["total_videos"] += 1
                except StopIteration:
                    break
                except Exception as e:
                    continue
            log_scan(f"Found {len(root_videos)} videos in root.")
        except Exception as e:
            log_scan(f"Error scanning root: {e}")
        
        if root_videos:
            update_section("Root Files", "root-files", root_videos)
        
        # 2. Folder Scan
        entries = []
        try:
            it = abs_root.iterdir()
            while True:
                try:
                    entry = next(it)
                    entries.append(entry)
                except StopIteration:
                    break
                except:
                    continue
            entries.sort()
        except Exception as e:
            log_scan(f"Could not list root directory: {e}")
            return

        for entry in entries:
            try:
                # Basic checks
                if not entry.is_dir(): continue
                if entry.name.startswith("."): continue
                
                # Path-based skip
                try:
                    entry_abs = entry.resolve()
                except:
                    log_scan(f"Could not resolve path for {entry.name}, skipping.")
                    continue

                if entry_abs in SYSTEM_PATHS or entry_abs == abs_project:
                    log_scan(f"Skipping system folder: {entry.name}")
                    continue
                
                # Check for generic skip names
                if entry.name in {"node_modules", "venv", ".git", "__pycache__"}:
                    log_scan(f"Skipping dependency/temp folder: {entry.name}")
                    continue
                    
                videos = []
                log_scan(f"Scanning folder: {entry.name}")
                
                for root, dirs, files in os.walk(entry):
                    current_root_abs = Path(root).resolve()
                    
                    # Safety: skip if we somehow walked into the project folder
                    if current_root_abs == abs_project or current_root_abs in SYSTEM_PATHS:
                        dirs[:] = []
                        continue
                        
                    # Prune hidden dirs
                    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules", "venv", ".git"}]

                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                            vid_id = get_id(str(file_path.resolve()))
                            videos.append(format_video_data(file_path, vid_id))
                            LIBRARY_STATE["total_videos"] += 1
                
                if videos:
                    log_scan(f" -> Found {len(videos)} videos in '{entry.name}'")
                    update_section(entry.name.replace("_", " ").title(), get_id(str(entry_abs)), videos)
                else:
                    log_scan(f" -> No videos found in '{entry.name}' (recursive search)")

            except Exception as e:
                log_scan(f"Error scanning '{entry.name}': {e}")
                
    except Exception as e:
        log_scan(f"Global scan error: {e}")
    finally:
        LIBRARY_STATE["is_scanning"] = False
        LIBRARY_STATE["last_update"] = datetime.now().isoformat()
        log_scan(f"Scan complete. Total: {LIBRARY_STATE['total_videos']} videos.")

def update_section(name, slug, videos):
    global LIBRARY_STATE
    # Prevent duplicate sections by slug
    if any(s["slug"] == slug for s in LIBRARY_STATE["sections"]):
        return
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
        "total": LIBRARY_STATE["total_videos"],
        "scan_log": LIBRARY_STATE["scan_log"]
    }

@app.get("/api/thumb/{video_id}")
def get_thumb(video_id: str):
    thumb_path = THUMB_DIR / f"{video_id}.jpg"
    if thumb_path.exists(): return FileResponse(thumb_path)
    
    video_path = VIDEO_PATH_CACHE.get(video_id)
    if not video_path:
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
    video_path = VIDEO_PATH_CACHE.get(video_id)
    if not video_path:
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
