# # server/app.py
# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from openenv.core.env_server import create_fastapi_app
# from environment import OmniSupportEnvironment
# from models import SupportAction, SupportObservation

# app = create_fastapi_app(OmniSupportEnvironment, SupportAction, SupportObservation)

# server/app.py
import sys
import os

# Add /app/server to path so 'environment', 'models' etc. are found
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_fastapi_app
from environment import OmniSupportEnvironment
from models import SupportAction, SupportObservation

app = create_fastapi_app(OmniSupportEnvironment, SupportAction, SupportObservation)