"""
Cached data loader for demo mode
"""

import os
import json
from typing import Dict, Optional


CACHED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cached_data')


def load_cached_july_2020() -> Optional[Dict]:
    """
    Load cached July 2020 response

    Returns:
        Complete cached response or None if not found
    """
    cache_path = os.path.join(CACHED_DATA_DIR, 'july_2020_response.json')

    if not os.path.exists(cache_path):
        print(f"[CachedLoader] Warning: Cache file not found at {cache_path}")
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("[CachedLoader] Successfully loaded cached July 2020 response")
        return data

    except Exception as e:
        print(f"[CachedLoader] Error loading cache: {e}")
        return None


def is_cached_data_available() -> bool:
    """Check if cached data exists"""
    cache_path = os.path.join(CACHED_DATA_DIR, 'july_2020_response.json')
    return os.path.exists(cache_path)
