import subprocess
import time
import os
import sys

def main():
    print("Starting OmniSupportEnv Multi-Service Bootloader...")

    # 1. Start FastAPI in the background on port 8000
    print("Starting FastAPI server on port 8000...")
    api_process = subprocess.Popen([
        "uvicorn", "server.app:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])

    # 2. Wait a bit for API to warm up
    time.sleep(2)

    # 3. Start Streamlit on port 7860 (Main HF Port)
    print("Starting Streamlit UI on port 7860...")
    # We pass the API URL to streamlit via env var if needed
    os.environ["API_URL"] = "http://localhost:8000"
    
    try:
        subprocess.run([
            "streamlit", "run", "app_streamlit.py",
            "--server.port", "7860",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        api_process.terminate()

if __name__ == "__main__":
    main()
