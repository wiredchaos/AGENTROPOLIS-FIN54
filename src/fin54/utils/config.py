import os

from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")
FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
CACHE_PATH: str = os.getenv("FIN54_CACHE_PATH", ".cache/fin54.duckdb")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
