"""
One-click launcher script for the Smart Placement Preparation Assistant.
Initializes and seeds the SQLite database, opens the frontend in the default browser,
and starts the FastAPI + Frontend server via Uvicorn.
"""

import threading
import time
import webbrowser
import uvicorn

from backend.database import get_db_path
from backend.seed import seed_database

HOST = "127.0.0.1"
PORT = 8000
APP_URL = f"http://{HOST}:{PORT}/index.html"
DOCS_URL = f"http://{HOST}:{PORT}/docs"


def _open_browser_when_ready() -> None:
    """Wait briefly for Uvicorn to bind the port, then open the dashboard in the browser."""
    time.sleep(1.5)
    try:
        webbrowser.open(APP_URL)
    except Exception:
        pass


def main() -> None:
    print("=" * 68)
    print("  SMART PLACEMENT PREPARATION ASSISTANT - FULL-STACK LAUNCHER")
    print("=" * 68)

    print("[1/3] Initializing & seeding SQLite database...")
    seed_database()
    print("      Database ready at: database/placement_assistant.db")

    print("[2/3] Launching browser tab...")
    print(f"      Frontend Dashboard : {APP_URL}")
    print(f"      Swagger API Docs   : {DOCS_URL}")
    threading.Thread(target=_open_browser_when_ready, daemon=True).start()

    print("[3/3] Starting FastAPI Uvicorn server (Press Ctrl+C to stop)...")
    print("=" * 68)
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    main()

