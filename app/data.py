import os
import time
import logging
from pathlib import Path
from io import StringIO

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# Publish the Google Sheet to the web as CSV (File > Share > Publish to web > CSV)
# and set GOOGLE_SHEET_CSV_URL to that link. If unset (or the fetch fails), the
# local pred_food.csv is used instead.
GOOGLE_SHEET_CSV_URL = os.getenv("GOOGLE_SHEET_CSV_URL")
CACHE_TTL_SECONDS = int(os.getenv("GOOGLE_SHEET_CACHE_TTL", "300"))

_LOCAL_CSV_PATH = Path(__file__).parent / "pred_food.csv"

_cached_df = None
_cached_at = 0.0


def _load_from_local():
    return pd.read_csv(_LOCAL_CSV_PATH)


def _load_from_sheet():
    response = requests.get(GOOGLE_SHEET_CSV_URL, timeout=10)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))


def _refresh():
    global _cached_df, _cached_at

    if GOOGLE_SHEET_CSV_URL:
        try:
            _cached_df = _load_from_sheet()
            _cached_at = time.time()
            return _cached_df
        except Exception:
            logger.exception("Failed to load food data from Google Sheet, falling back to local CSV")

    _cached_df = _load_from_local()
    _cached_at = time.time()
    return _cached_df


def get_df():
    """Return the food dataframe, refreshing from Google Sheets if the cache expired."""
    if _cached_df is None or (time.time() - _cached_at) > CACHE_TTL_SECONDS:
        return _refresh()
    return _cached_df


# Backwards-compatible eager load for any code that still imports `df` directly.
df = get_df()
