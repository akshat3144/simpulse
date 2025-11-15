"""
Startup script for FastAPI server
Handles module imports properly
"""

if __name__ == "__main__":
    import sys
    import os
    
    # Add parent directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    # Now run the server
    import uvicorn
    
    print("🏎️  Starting Formula E Race Simulator API Server")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/race")
    print("📖 API docs: http://localhost:8000/docs")
    print("")
    
    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
