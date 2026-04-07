# server/app.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openenv.core.env_server import create_fastapi_app
from environment import OmniSupportEnvironment
from models import SupportAction, SupportObservation

app = create_fastapi_app(OmniSupportEnvironment, SupportAction, SupportObservation)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()