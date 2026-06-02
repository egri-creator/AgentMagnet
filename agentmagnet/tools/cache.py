"""In-memory result cache with TTL for ultra-fast agent responses."""

import time
import hashlib
import json
from ..config import settings


class SearchCache:
    def __init__(self):
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._hits = 0
        self._misses = 0

    def _make_key(self, query: str, source: str | None, language: str) -> str:
        raw = f"{query.lower().strip()}:{source or 'all'}:{language}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, query: str, source: str | None, language: str) -> list[dict] | None:
        key = self._make_key(query, source, language)
        entry = self._cache.get(key)
        if entry:
            ts, data = entry
            if time.time() - ts < settings.cache_ttl_seconds:
                self._hits += 1
                return data
            del self._cache[key]
        self._misses += 1
        return None

    def set(self, query: str, source: str | None, language: str, results: list[dict]):
        key = self._make_key(query, source, language)
        self._cache[key] = (time.time(), results)

    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total else 0
        return {
            "cache_size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_pct": round(hit_rate, 1),
        }

    def clear(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0


search_cache = SearchCache()
