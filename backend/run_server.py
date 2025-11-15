"""
Startup script for Formula E Race Simulator FastAPI Server
Handles module imports and runs uvicorn
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for proper imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for testing
        log_level="info"
    )
