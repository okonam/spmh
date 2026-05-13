import urllib.request
import json
import sys

ID = "8c46dda0a30eb4ce992f42c0cde06395"
URL = f"http://localhost:8888/api/stream/{ID}"

print(f"Testing stream for ID: {ID}")
try:
    req = urllib.request.Request(URL, headers={"Range": "bytes=0-100"})
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print(f"Headers: {response.info()}")
    
    with urllib.request.urlopen("http://localhost:8888/api/hub") as r:
        data = json.loads(r.read().decode())
        print(f"Hub Scanning: {data.get('is_scanning')}")
        print(f"Total Videos: {data.get('total')}")

except Exception as e:
    print(f"Error: {e}")
