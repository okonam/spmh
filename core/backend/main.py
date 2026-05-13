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
# VIDEO_ROOT is the folder CONTAINING spmh (the 'projects' folder)
VIDEO_ROOT = project_folder.parent.resolve()

# Fallback for safety - Ensure it exists and is absolute
if not VIDEO_ROOT.exists():
    VIDEO_ROOT = project_folder.resolve()


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

def log_scan(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg, flush=True)
    if "LIBRARY_STATE" in globals() and "scan_log" in LIBRARY_STATE:
        LIBRARY_STATE["scan_log"].append(full_msg)
        if len(LIBRARY_STATE["scan_log"]) > 100:
            LIBRARY_STATE["scan_log"].pop(0)

log_scan(f"ENGINE STARTUP: VIDEO_ROOT set to {VIDEO_ROOT}")

VIDEO_PATH_CACHE = {} # Fast lookup for ID -> Path

def resolve_path_enhanced(video_id: str) -> Optional[str]:
    """Robustly resolve a video ID to an absolute filesystem path with self-healing."""
    # 1. Check Global Cache first (Fastest)
    rel_path = VIDEO_PATH_CACHE.get(video_id)
    
    # 2. Fallback: Search all sections in LIBRARY_STATE
    if not rel_path:
        def find_in_sections(sections):
            for s in sections:
                v_list = s.get("all_videos", []) or s.get("videos", [])
                for v in v_list:
                    if v["id"] == video_id: return v["path"]
                if "sub_sessions" in s:
                    res = find_in_sections(s["sub_sessions"])
                    if res: return res
            return None
        rel_path = find_in_sections(LIBRARY_STATE["sections"])

    if not rel_path:
        return None

    # 3. Direct Resolution (Normalize drive letters for comparison)
    clean_rel = rel_path.lstrip("/").lstrip("\\")
    
    # Ensure VIDEO_ROOT is absolute and normalized (DRIVE LETTER CASE INSENSITIVITY)
    v_root_str = str(VIDEO_ROOT.resolve())
    if len(v_root_str) > 1 and v_root_str[1] == ":": v_root_str = v_root_str[0].upper() + v_root_str[1:]
    
    absolute_path = Path(v_root_str) / clean_rel
    
    if absolute_path.exists():
        return str(absolute_path.resolve())
    
    # 4. Fallback: Search recursively for the filename (Auto-healing)
    filename = Path(clean_rel).name
    log_scan(f"Path direct match failed for {video_id}. Attempting recursive self-healing for: {filename}")
    
    # Global search within VIDEO_ROOT (Prototype Strategy)
    # This is extremely effective if folders were renamed or moved within the projects root
    v_root_search = str(VIDEO_ROOT.resolve())
    for root, _, files in os.walk(v_root_search):
        if filename in files:
            found_path = Path(root) / filename
            log_scan(f"Self-healing successful: found {filename} at {found_path}")
            return str(found_path.resolve())
                    
    return None

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
                
                # Rebuild path cache recursively (Storing RELATIVE paths)
                def load_recursive(sections):
                    for s in sections:
                        v_list = s.get("all_videos", []) or s.get("videos", [])
                        for v in v_list:
                            # v["path"] is now a relative path string
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
        # Use absolute resolved paths for both
        abs_path = Path(path_str).resolve()
        abs_root = VIDEO_ROOT.resolve()
        
        # Normalize drive letters to uppercase for Windows consistency
        p_str = str(abs_path)
        r_str = str(abs_root)
        if len(p_str) > 1 and p_str[1] == ":": p_str = p_str[0].upper() + p_str[1:]
        if len(r_str) > 1 and r_str[1] == ":": r_str = r_str[0].upper() + r_str[1:]
        
        rel_path = os.path.relpath(p_str, r_str)
        # Normalize to forward slashes and LOWERCASE for total case-insensitive ID consistency
        portable_path = rel_path.replace("\\", "/").lower()
        return hashlib.md5(portable_path.encode()).hexdigest()
    except Exception as e:
        # Fallback normalization
        p_norm = path_str.replace("\\", "/").lower()
        return hashlib.md5(p_norm.encode()).hexdigest()

def format_video_data(path: Path, vid_id: str, temp_cache: dict):
    try:
        suffix = path.suffix.lower()
        if suffix not in VIDEO_EXTENSIONS or suffix in IGNORE_EXTENSIONS:
            return None

        stats = path.stat()
        size_gb = stats.st_size / (1024**3)
        
        # Calculate RELATIVE path for portability
        try:
            rel_path = str(path.relative_to(VIDEO_ROOT)).replace("\\", "/")
        except:
            rel_path = str(path.resolve()).replace("\\", "/")

        temp_cache[vid_id] = rel_path
        
        # Determine category (folder name)
        try:
            rel_to_root = path.parent.relative_to(VIDEO_ROOT)
            category = rel_to_root.parts[0] if rel_to_root.parts else "Root"
        except:
            category = "External"
        
        res = {
            "id": vid_id,
            "title": path.stem.replace(".", " ").replace("_", " ").title(),
            "path": rel_path,
            "full_path": str(path.resolve()),
            "size": f"{size_gb:.2f} GB",
            "modified": stats.st_mtime,
            "format": path.suffix.upper()[1:],
            "codec": "H.264" if suffix == ".mp4" else "AVC/HEVC",
            "duration": "N/A",
            "category": category
        }
        
        # Diagnostic Log
        if vid_id == "2db75058c64445f404d86657a5e2ef67":
             print(f"[DIAG] Metadata generated for {vid_id}: {res['full_path']}")

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

@app.get("/api/video/{video_id}")
def get_video_info(video_id: str):
    """Directly resolve path and metadata for the HUD."""
    full_path = resolve_path_enhanced(video_id)
    if not full_path:
        raise HTTPException(404, detail="Video not found")
    
    path_obj = Path(full_path)
    return {
        "id": video_id,
        "full_path": str(full_path),
        "codec": "H.264" if path_obj.suffix.lower() == ".mp4" else "AVC/HEVC",
        "format": path_obj.suffix.upper()[1:]
    }

@app.get("/api/thumb/{video_id}")
def get_thumb(video_id: str):
    thumb_path = THUMB_DIR / f"{video_id}.jpg"
    if thumb_path.exists(): return FileResponse(thumb_path)
    
    # Reconstruct absolute path via Resolver
    video_path = resolve_path_enhanced(video_id)
    
    # Try to generate thumbnail with concurrency lock
    if video_path:
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

from fastapi.responses import StreamingResponse

@app.get("/api/stream/{video_id}")
async def stream_video(video_id: str, request: Request):
    video_path = resolve_path_enhanced(video_id)
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(404, detail="Video file not found")

    file_size = os.path.getsize(video_path)
    mime_type = "video/mp4" if video_path.lower().endswith(".mp4") else (mimetypes.guess_type(video_path)[0] or "video/mp4")
    
    range_header = request.headers.get("Range")

    def get_file_chunk(path, start, end, chunk_size=1024*1024):
        with open(path, "rb") as f:
            f.seek(start)
            while (pos := f.tell()) <= end:
                read_size = min(chunk_size, end + 1 - pos)
                if read_size <= 0: break
                yield f.read(read_size)

    if range_header:
        try:
            parts = range_header.replace("bytes=", "").split("-")
            start = int(parts[0])
            end = int(parts[1]) if parts[1] else file_size - 1
        except:
            start, end = 0, file_size - 1
        
        if start >= file_size: raise HTTPException(416)
        
        content_length = end - start + 1
        return StreamingResponse(
            get_file_chunk(video_path, start, end),
            status_code=206,
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": mime_type,
            }
        )

    # Full file delivery
    return StreamingResponse(
        get_file_chunk(video_path, 0, file_size - 1),
        headers={
            "Content-Length": str(file_size),
            "Content-Type": mime_type,
            "Accept-Ranges": "bytes"
        }
    )

@app.post("/api/open/{video_id}")
def open_explorer(video_id: str):
    video_path = resolve_path_enhanced(video_id)
    
    if video_path:
        system = platform.system()
        try:
            if system == "Windows": subprocess.run(["explorer", "/select,", video_path])
            elif system == "Darwin": subprocess.run(["open", "-R", video_path])
            else: subprocess.run(["xdg-open", os.path.dirname(video_path)])
            return {"status": "opened"}
        except: return {"status": "error"}
    return {"status": "not_found"}

@app.post("/api/scan/reset")
def reset_library():
    """Wipe cache and force full re-scan."""
    global LIBRARY_STATE, VIDEO_PATH_CACHE
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        LIBRARY_STATE["sections"] = []
        VIDEO_PATH_CACHE = {}
        LIBRARY_STATE["total_videos"] = 0
        log_scan("User triggered CACHE RESET. Cleaning up...")
        # Restart scanner
        threading.Thread(target=background_scanner, daemon=True).start()
        return {"status": "reset_started"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

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
