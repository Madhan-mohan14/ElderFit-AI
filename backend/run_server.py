"""
Backend server runner - can be run from backend directory
"""
import sys
import os
from pathlib import Path

# Change to project root directory
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Add project root to path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import and run
if __name__ == "__main__":
    import uvicorn
    from backend.config import Config
    
    print(f"Starting server from: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print(f"Server will run on http://{Config.API_HOST}:{Config.API_PORT}")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(
        "backend.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )

