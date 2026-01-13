#!/usr/bin/env python3
"""
Startup script for FastAPI backend.
Sets up Python path before starting uvicorn.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path so both 'backend' and 'src' modules are found
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set PYTHONPATH environment variable for subprocesses
os.environ['PYTHONPATH'] = str(backend_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",  # Changed from backend.api.main
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=[str(backend_dir)]
    )
