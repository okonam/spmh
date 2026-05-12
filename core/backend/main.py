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
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
import queue
from collections import deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- GLOBAL LOCKS & QUEUES ---
FFMPEG_LOCK = threading.Lock()
THUMB_QUEUE = queue.Queue()
PENDING_THUMBS = set()

# --- SMART PATH DETECTION ---
current_file = Path(__file__).resolve()
# spmh/core/backend/main.py -> parent x 3 -> spmh
project_folder = current_file.parent.parent.parent 
# VIDEO_ROOT is the folder CONTAINING spmh
VIDEO_ROOT = project_folder.parent

# Fallback for safety
if not VIDEO_ROOT.exists():
    VIDEO_ROOT = project_folder

# --- PATHS ---
CORE_DIR = project_folder / "core"
DATA_DIR = CORE_DIR / "data"
THUMB_DIR = DATA_DIR / "thumbs"
CACHE_FILE = DATA_DIR / "library_cache.json"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm", ".mpg", ".mpeg", ".flv"}
# AUDIO/IMAGE EXTENSIONS TO STRICTLY IGNORE
IGNORE_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".txt", ".pdf", ".zip", ".rar", ".exe", ".bat", ".py", ".md", ".json", ".vbs"}

DATA_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    load_cache()
    # Check for ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_scan("FFmpeg engine detected and ready.")
    except FileNotFoundError:
        log_scan("WARNING: FFmpeg not found. Thumbnails will not be generated. Please install FFmpeg and add it to PATH.")
    
    # Start background scanner thread
    threading.Thread(target=background_scanner, daemon=True).start()
    # Start thumbnail worker thread
    threading.Thread(target=thumbnail_worker, daemon=True).start()
    yield
    # Shutdown Logic
    save_cache()

app = FastAPI(title="SPMH API", lifespan=lifespan)

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

def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "sections": LIBRARY_STATE["sections"],
                "total": LIBRARY_STATE["total_videos"],
                "updated": LIBRARY_STATE["last_update"]
            }, f, indent=2)
        log_scan("Library cache saved to disk.")
    except Exception as e:
        log_scan(f"Failed to save cache: {e}")

def thumbnail_worker():
    """Regulated worker to process thumbnail generation in the background."""
    while True:
        try:
            video_id, video_path, thumb_path = THUMB_QUEUE.get()
            if video_path and os.path.exists(video_path):
                with FFMPEG_LOCK:
                    try:
                        cmd = ["ffmpeg", "-y", "-ss", "00:00:01", "-i", video_path, "-frames:v", "1", "-q:v", "2", str(thumb_path)]
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=True)
                    except:
                        pass
            
            if video_id in PENDING_THUMBS:
                PENDING_THUMBS.remove(video_id)
            THUMB_QUEUE.task_done()
        except Exception as e:
            # We don't want to crash the worker thread
            time.sleep(0.1)
        finally:
            time.sleep(0.5) # Gentle pacing

def load_cache():
    global LIBRARY_STATE, VIDEO_PATH_CACHE
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                LIBRARY_STATE["sections"] = data.get("sections", [])
                LIBRARY_STATE["total_videos"] = data.get("total", 0)
                LIBRARY_STATE["last_update"] = data.get("updated")
                
                # Rebuild path cache recursively
                def load_recursive(sections):
                    for s in sections:
                        # Use all_videos if available (more comprehensive)
                        v_list = s.get("all_videos", []) or s.get("videos", [])
                        for v in v_list:
                            VIDEO_PATH_CACHE[v["id"]] = v["path"]
                        if "sub_sessions" in s:
                            load_recursive(s["sub_sessions"])
                
                load_recursive(LIBRARY_STATE["sections"])
            log_scan(f"Loaded {LIBRARY_STATE['total_videos']} videos from cache.")
            return True
        except Exception as e:
            log_scan(f"Cache load error: {e}")
    return False

def get_id(path_str):
    """Generate a unique ID based on the relative path from VIDEO_ROOT for portability."""
    try:
        rel_path = os.path.relpath(path_str, str(VIDEO_ROOT))
        # Normalize to forward slashes for cross-platform/consistency
        portable_path = rel_path.replace("\\", "/")
        return hashlib.md5(portable_path.encode()).hexdigest()
    except:
        return hashlib.md5(path_str.replace("\\", "/").encode()).hexdigest()

def format_video_data(path: Path, vid_id: str, temp_cache: dict):
    try:
        suffix = path.suffix.lower()
        if suffix not in VIDEO_EXTENSIONS or suffix in IGNORE_EXTENSIONS:
            return None

        stats = path.stat()
        size_gb = stats.st_size / (1024**3)
        temp_cache[vid_id] = str(path.resolve())
        
        # Determine category (folder name)
        try:
            rel_to_root = path.parent.relative_to(VIDEO_ROOT)
            category = rel_to_root.parts[0] if rel_to_root.parts else "Root"
        except:
            category = "External"
        
        res = {
            "id": vid_id,
            "title": path.stem.replace(".", " ").replace("_", " ").title(),
            "path": str(path.resolve()),
            "size": f"{size_gb:.2f} GB",
            "modified": stats.st_mtime,
            "format": path.suffix.upper()[1:],
            "duration": "N/A",
            "category": category
        }

        # Queue thumbnail if missing
        thumb_path = THUMB_DIR / f"{vid_id}.jpg"
        if not thumb_path.exists() and vid_id not in PENDING_THUMBS:
            PENDING_THUMBS.add(vid_id)
            THUMB_QUEUE.put((vid_id, str(path.resolve()), thumb_path))
            
        return res
    except Exception as e:
        print(f"[ERROR] Failed to format video data for {path}: {e}")
        return None

def log_scan(msg):
    global LIBRARY_STATE
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg, flush=True)
    LIBRARY_STATE["scan_log"].append(full_msg)
    if len(LIBRARY_STATE["scan_log"]) > 100:
        LIBRARY_STATE["scan_log"].pop(0)

def background_scanner():
    global LIBRARY_STATE, VIDEO_PATH_CACHE
    LIBRARY_STATE["is_scanning"] = True
    
    # NEW: We use temporary holders to avoid breaking the UI during scan
    new_sections = []
    new_cache = {}
    new_total = 0
    new_scan_log = []
    
    def log_scan_tmp(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        print(full_msg, flush=True)
        new_scan_log.append(full_msg)
        # Update global log too
        LIBRARY_STATE["scan_log"].append(full_msg)
        if len(LIBRARY_STATE["scan_log"]) > 100:
            LIBRARY_STATE["scan_log"].pop(0)

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
                    if item.is_file():
                        suffix = item.suffix.lower()
                        if suffix in VIDEO_EXTENSIONS and suffix not in IGNORE_EXTENSIONS:
                            vid_id = get_id(str(item.resolve()))
                            vdata = format_video_data(item, vid_id, new_cache)
                            if vdata:
                                root_videos.append(vdata)
                                new_total += 1
                except StopIteration:
                    break
                except Exception as e:
                    continue
            log_scan_tmp(f"Found {len(root_videos)} videos in root.")
        except Exception as e:
            log_scan_tmp(f"Error scanning root: {e}")
        
        if root_videos:
            # We build the section but don't swap global state yet
            new_sections.append({
                "name": "Root Files",
                "slug": "root-files",
                "videos": sorted(root_videos, key=lambda v: v["modified"], reverse=True)
            })
            # INCREMENTAL UPDATE
            LIBRARY_STATE["sections"] = list(new_sections)
            LIBRARY_STATE["total_videos"] = new_total
            VIDEO_PATH_CACHE.update(new_cache)
        
        # New Hierarchical Scan
        def scan_directory(path: Path, depth=0):
            try:
                if not path.is_dir() or path.name.startswith("."): return None
                
                # Check for generic skip names
                if path.name.lower() in {"node_modules", "venv", ".git", "__pycache__", "brain", ".agent", ".gemini", "brain_storage", "spmh"}:
                    return None
                
                # Path-based skip (prevent scanning hub itself)
                try:
                    if path.resolve() == abs_project or path.resolve() in SYSTEM_PATHS:
                        return None
                except: pass

                session_videos = []
                sub_sessions = []
                all_videos_recursive = []
                
                # 1. Direct videos in this folder
                try:
                    for item in path.iterdir():
                        if item.is_file():
                            suffix = item.suffix.lower()
                            if suffix in VIDEO_EXTENSIONS and suffix not in IGNORE_EXTENSIONS:
                                vid_id = get_id(str(item.resolve()))
                                vdata = format_video_data(item, vid_id, new_cache)
                                if vdata:
                                    session_videos.append(vdata)
                                    all_videos_recursive.append(vdata)
                                    nonlocal new_total
                                    new_total += 1
                        elif item.is_dir():
                            # Recursive call for children
                            child_session = scan_directory(item, depth + 1)
                            if child_session:
                                sub_sessions.append(child_session)
                                all_videos_recursive.extend(child_session.get("all_videos", []))
                except Exception as e:
                    log_scan(f"Error reading {path.name}: {e}")

                # Only return session if it has content
                if session_videos or sub_sessions:
                    return {
                        "name": path.name.replace("_", " ").title(),
                        "slug": get_id(str(path.resolve())),
                        "path": str(path.resolve()),
                        "videos": sorted(session_videos, key=lambda v: v["modified"], reverse=True),
                        "all_videos": sorted(all_videos_recursive, key=lambda v: v["modified"], reverse=True),
                        "sub_sessions": sorted(sub_sessions, key=lambda s: s["name"]),
                        "depth": depth
                    }
                return None
            except:
                return None

        # Execute scan from root
        new_sections = []
        try:
            for entry in VIDEO_ROOT.iterdir():
                if entry.is_dir():
                    session = scan_directory(entry)
                    if session:
                        new_sections.append(session)
                        # INCREMENTAL UPDATE for UX
                        LIBRARY_STATE["sections"] = list(new_sections)
                        LIBRARY_STATE["total_videos"] = new_total
                        VIDEO_PATH_CACHE.update(new_cache)
        except Exception as e:
            log_scan(f"Global scan loop error: {e}")

        log_scan(f"Scan complete. Total: {new_total} videos.")
                
    except Exception as e:
        log_scan_tmp(f"Global scan error: {e}")
    finally:
        # ATOMIC SWAP: Only update global state when done
        LIBRARY_STATE["sections"] = new_sections
        VIDEO_PATH_CACHE = new_cache
        LIBRARY_STATE["total_videos"] = new_total
        LIBRARY_STATE["scan_log"] = new_scan_log
        LIBRARY_STATE["is_scanning"] = False
        LIBRARY_STATE["last_update"] = datetime.now().isoformat()
        log_scan(f"Scan complete. Total: {LIBRARY_STATE['total_videos']} videos.")
        save_cache()

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

# The @app.on_event("startup") is now handled by the lifespan context manager above.

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
    
    # Try to generate thumbnail with concurrency lock
    if video_path and os.path.exists(video_path):
        with FFMPEG_LOCK:
            try:
                cmd = ["ffmpeg", "-y", "-ss", "00:00:01", "-i", video_path, "-frames:v", "1", "-q:v", "2", str(thumb_path)]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=True)
                if thumb_path.exists(): return FileResponse(thumb_path)
            except Exception as e:
                print(f"[THUMB ERROR] FFmpeg failed for {video_id}: {e}")
    
    # FALLBACK: If everything fails, return a default image instead of 404
    # We check if a placeholder exists in frontend/assets
    default_thumb = CORE_DIR / "frontend" / "assets" / "placeholder.jpg"
    if default_thumb.exists():
        return FileResponse(default_thumb)
        
    return HTTPException(status_code=404, detail="Thumbnail not found") 

@app.get("/api/stream/{video_id}")
async def stream_video(video_id: str, request: Request):
    video_path = VIDEO_PATH_CACHE.get(video_id)
    range_header = request.headers.get("Range")
    
    if not video_path:
        print(f"[CACHE MISS] ID: {video_id} - Recursive Search...")
        def find_recursive(sections):
            for s in sections:
                v_list = s.get("all_videos", []) or s.get("videos", [])
                for v in v_list:
                    if v["id"] == video_id: return v["path"]
                if "sub_sessions" in s:
                    res = find_recursive(s["sub_sessions"])
                    if res: return res
            return None
        
        video_path = find_recursive(LIBRARY_STATE["sections"])
        if video_path:
            VIDEO_PATH_CACHE[video_id] = video_path
    
    if not video_path or not os.path.exists(video_path):
        print(f"[STREAM ERROR] Video ID {video_id} not found.")
        raise HTTPException(404)

    mime_type, _ = mimetypes.guess_type(video_path)
    if not mime_type: mime_type = "video/mp4"

    print(f"[STREAM] Serving: {os.path.basename(video_path)} | Mime: {mime_type} | Range: {range_header}")
    return FileResponse(video_path, media_type=mime_type)

@app.post("/api/open/{video_id}")
def open_explorer(video_id: str):
    video_path = VIDEO_PATH_CACHE.get(video_id)
    
    if not video_path:
        # Recursive search fallback
        def find_path(sections):
            for s in sections:
                v_list = s.get("all_videos", []) or s.get("videos", [])
                for v in v_list:
                    if v["id"] == video_id: return v["path"]
                if "sub_sessions" in s:
                    res = find_path(s["sub_sessions"])
                    if res: return res
            return None
        video_path = find_path(LIBRARY_STATE["sections"])
    
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
