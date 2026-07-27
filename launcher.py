import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    print("[ClipCuy] Starting backend server on http://localhost:8000")
    print("[ClipCuy] Opening web browser...")
    
    proc = subprocess.Popen(backend_cmd, cwd=str(Path(__file__).parent))
    
    time.sleep(3)
    
    try:
        webbrowser.open("http://localhost:8000")
    except Exception as e:
        print(f"[ClipCuy] Could not open browser: {e}")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("[ClipCuy] Shutting down...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
