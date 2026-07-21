import requests
import time
import logging
from typing import Dict, Any, List, Optional
from config import USER_STATUS_URL, USER_RATING_URL, USER_INFO_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CodeforcesFetcher:
    def __init__(self, handle: str):
        self.handle = handle.strip()

    def _make_request(self, url: str, params: Dict[str, Any], retries: int = 3, backoff: float = 2.0) -> Optional[Dict[str, Any]]:
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK":
                        return data.get("result")
                    else:
                        logging.warning(f"API returned non-OK status: {data.get('comment')}")
                        return None
                elif response.status_code == 429:
                    logging.warning(f"Rate limited by Codeforces API. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logging.warning(f"HTTP {response.status_code} received from {url}")
            except requests.RequestException as e:
                logging.warning(f"Request error (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(backoff)
        return None

    def fetch_user_info(self) -> Optional[Dict[str, Any]]:
        """Fetch basic profile info for the user."""
        logging.info(f"Fetching user info for handle: {self.handle}")
        result = self._make_request(USER_INFO_URL, {"handles": self.handle})
        if result and len(result) > 0:
            return result[0]
        return None

    def fetch_user_rating(self) -> List[Dict[str, Any]]:
        """Fetch rating history for the user."""
        logging.info(f"Fetching rating history for handle: {self.handle}")
        result = self._make_request(USER_RATING_URL, {"handle": self.handle})
        return result if result is not None else []

    def fetch_user_submissions(self, count: int = 10000) -> List[Dict[str, Any]]:
        """Fetch submission history for the user."""
        logging.info(f"Fetching submissions for handle: {self.handle} (max {count})")
        result = self._make_request(USER_STATUS_URL, {"handle": self.handle, "from": 1, "count": count})
        return result if result is not None else []
