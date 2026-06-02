"""SQLite-backed search result cache for ultra-fast agent responses."""

import hashlib
from ..config import settings
from ..store.db import store


class SearchCache:
    def _make_key(self, query: str, source: str | None, language: str) -> str:
        raw = f"{query.lower().strip()}:{source or 'all'}:{language}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, query: str, source: str | None, language: str) -> list[dict] | None:
        return store.cache_get(self._make_key(query, source, language))

    def set(self, query: str, source: str | None, language: str, results: list[dict]):
        store.cache_set(self._make_key(query, source, language), results, settings.cache_ttl_seconds)

    def stats(self) -> dict:
        s = store.cache_stats()
        s["hit_rate_pct"] = 0
        return s

    def clear(self):
        store.cache_clear()


search_cache = SearchCache()
