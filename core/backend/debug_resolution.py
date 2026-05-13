import os
import hashlib
from pathlib import Path

# Mock VIDEO_ROOT based on main.py logic
# Assuming project is at X:\OKONAM\Agente\projects\spmh
VIDEO_ROOT = Path(r"X:\OKONAM\Agente\projects")

def get_id(path_str):
    try:
        rel_path = os.relpath(path_str, str(VIDEO_ROOT))
        portable_path = rel_path.replace("\\", "/")
        return hashlib.md5(portable_path.encode()).hexdigest()
    except Exception as e:
        print(f"Error in get_id: {e}")
        return hashlib.md5(path_str.replace("\\", "/").encode()).hexdigest()

test_path = r"X:\OKONAM\Agente\projects\videos XXX\XXX\Extra XXX\Video.mp4"
vid_id = get_id(test_path)

print(f"VIDEO_ROOT: {VIDEO_ROOT}")
print(f"Test Path: {test_path}")
print(f"Generated ID: {vid_id}")

rel_path = os.relpath(test_path, str(VIDEO_ROOT))
print(f"Relative Path: {rel_path}")

abs_path = VIDEO_ROOT / rel_path
print(f"Reconstructed Path: {abs_path}")
print(f"Exists: {abs_path.exists()}")
