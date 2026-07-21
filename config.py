import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"
DB_PATH = BASE_DIR / "codeforces_analytics.db"

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
CHARTS_DIR.mkdir(exist_ok=True, parents=True)

# Codeforces API Endpoints
API_BASE_URL = "https://codeforces.com/api"
USER_STATUS_URL = f"{API_BASE_URL}/user.status"
USER_RATING_URL = f"{API_BASE_URL}/user.rating"
USER_INFO_URL = f"{API_BASE_URL}/user.info"

# Default handle if none provided
DEFAULT_HANDLE = "tourist"

# Chart & Theme Configuration
PLOT_STYLE = "dark_background"
ACCENT_COLOR = "#00ADB5"
SECONDARY_COLOR = "#EEEEEE"
CARD_BG_COLOR = "#222831"
HIGHLIGHT_COLOR = "#FFD369"
FAILURE_COLOR = "#FF5722"
SUCCESS_COLOR = "#4CAF50"
