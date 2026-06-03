"""SQLite-backed persistent store for AgentMagnet.

Replaces all in-memory dicts with on-disk SQLite.
Thread-safe, survives restarts, zero dependencies (stdlib sqlite3)."""

import sqlite3
import json
import time
import threading
import os
from pathlib import Path


DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "agentmagnet.db"


def _get_conn():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


class Store:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        self._local = threading.local()
        schema = [
            "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, expires_at REAL)",
            "CREATE TABLE IF NOT EXISTS usage_v2 (agent_id TEXT, date TEXT, count INTEGER DEFAULT 0, PRIMARY KEY (agent_id, date))",
            "CREATE TABLE IF NOT EXISTS subscriptions (agent_id TEXT PRIMARY KEY, plan TEXT, max_searches INTEGER, started_at REAL)",
            "CREATE TABLE IF NOT EXISTS referral_balance (agent_id TEXT PRIMARY KEY, balance INTEGER DEFAULT 0)",
            "CREATE TABLE IF NOT EXISTS referral_codes (agent_id TEXT PRIMARY KEY, code TEXT, created_at REAL)",
            "CREATE TABLE IF NOT EXISTS referral_network (agent_id TEXT, referrer_id TEXT, referred_at REAL, PRIMARY KEY (agent_id, referrer_id))",
            "CREATE TABLE IF NOT EXISTS used_tx_hashes (tx_hash TEXT PRIMARY KEY, used_at REAL)",
            "CREATE TABLE IF NOT EXISTS total_usage (agent_id TEXT PRIMARY KEY, count INTEGER DEFAULT 0)",
            "CREATE TABLE IF NOT EXISTS trend_queries (day_key TEXT, query TEXT, language TEXT, country TEXT, source TEXT, count INTEGER DEFAULT 1, PRIMARY KEY (day_key, query, language, country, source))",
            "CREATE TABLE IF NOT EXISTS agent_deals (deal_id TEXT PRIMARY KEY, title TEXT, price REAL, source TEXT, affiliate_url TEXT, commission_pct REAL, agent_id TEXT, markup_pct REAL, created_at TEXT)",
        ]
        conn = self.conn
        for s in schema:
            conn.execute(s)
        conn.commit()

    @property
    def conn(self):
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = _get_conn()
        return self._local.conn

    # --- Cache ---
    def cache_get(self, key: str) -> list | None:
        row = self.conn.execute("SELECT value, expires_at FROM cache WHERE key=?", (key,)).fetchone()
        if row and row["expires_at"] > time.time():
            return json.loads(row["value"])
        if row:
            self.conn.execute("DELETE FROM cache WHERE key=?", (key,))
            self.conn.commit()
        return None

    def cache_set(self, key: str, value: list, ttl: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time() + ttl),
        )
        self.conn.commit()

    def cache_clear(self):
        self.conn.execute("DELETE FROM cache")
        self.conn.commit()

    def cache_stats(self) -> dict:
        total = self.conn.execute("SELECT COUNT(*) as c FROM cache").fetchone()["c"]
        return {"cached_entries": total}

    # --- Usage ---
    def get_usage(self, agent_id: str) -> int:
        row = self.conn.execute("SELECT count FROM total_usage WHERE agent_id=?", (agent_id,)).fetchone()
        return row["count"] if row else 0

    def record_usage(self, agent_id: str, count: int = 1):
        today = time.strftime("%Y-%m-%d")
        self.conn.execute(
            "INSERT OR REPLACE INTO usage_v2 (agent_id, date, count) VALUES (?, ?, COALESCE((SELECT count FROM usage_v2 WHERE agent_id=? AND date=?), 0) + ?)",
            (agent_id, today, agent_id, today, count),
        )
        self.conn.execute(
            "INSERT OR REPLACE INTO total_usage (agent_id, count) VALUES (?, COALESCE((SELECT count FROM total_usage WHERE agent_id=?), 0) + ?)",
            (agent_id, agent_id, count),
        )
        self.conn.commit()

    def daily_usage(self, agent_id: str) -> int:
        today = time.strftime("%Y-%m-%d")
        row = self.conn.execute("SELECT count FROM usage_v2 WHERE agent_id=? AND date=?", (agent_id, today)).fetchone()
        return row["count"] if row else 0

    # --- Subscriptions ---
    def get_subscription(self, agent_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM subscriptions WHERE agent_id=?", (agent_id,)).fetchone()
        if row:
            return {"plan": row["plan"], "max_searches": row["max_searches"], "started_at": row["started_at"]}
        return None

    def set_subscription(self, agent_id: str, plan: str, max_searches: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO subscriptions (agent_id, plan, max_searches, started_at) VALUES (?, ?, ?, ?)",
            (agent_id, plan, max_searches, int(time.time())),
        )
        self.conn.commit()

    # --- Referral Balance ---
    def get_referral_balance(self, agent_id: str) -> int:
        row = self.conn.execute("SELECT balance FROM referral_balance WHERE agent_id=?", (agent_id,)).fetchone()
        return row["balance"] if row else 0

    def add_referral_searches(self, agent_id: str, count: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO referral_balance (agent_id, balance) VALUES (?, COALESCE((SELECT balance FROM referral_balance WHERE agent_id=?), 0) + ?)",
            (agent_id, agent_id, count),
        )
        self.conn.commit()

    def use_referral_search(self, agent_id: str) -> bool:
        bal = self.get_referral_balance(agent_id)
        if bal > 0:
            self.conn.execute("UPDATE referral_balance SET balance=? WHERE agent_id=?", (bal - 1, agent_id))
            self.conn.commit()
            return True
        return False

    # --- Referral Codes ---
    def store_referral_code(self, agent_id: str, code: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO referral_codes (agent_id, code, created_at) VALUES (?, ?, ?)",
            (agent_id, code, time.time()),
        )
        self.conn.commit()

    def get_referral_code(self, agent_id: str) -> str | None:
        row = self.conn.execute("SELECT code FROM referral_codes WHERE agent_id=?", (agent_id,)).fetchone()
        return row["code"] if row else None

    def find_referrer_by_code(self, code: str) -> str | None:
        row = self.conn.execute("SELECT agent_id FROM referral_codes WHERE code=?", (code,)).fetchone()
        return row["agent_id"] if row else None

    # --- Referral Network ---
    def add_referral(self, agent_id: str, referrer_id: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO referral_network (agent_id, referrer_id, referred_at) VALUES (?, ?, ?)",
            (agent_id, referrer_id, time.time()),
        )
        self.conn.commit()

    def get_referral_count(self, agent_id: str) -> int:
        row = self.conn.execute("SELECT COUNT(*) as c FROM referral_network WHERE referrer_id=?", (agent_id,)).fetchone()
        return row["c"]

    def get_network_size(self, agent_id: str) -> int:
        direct = self.get_referral_count(agent_id)
        rows = self.conn.execute("SELECT agent_id FROM referral_network WHERE referrer_id=?", (agent_id,)).fetchall()
        total = direct
        for r in rows:
            sub = self.conn.execute("SELECT COUNT(*) as c FROM referral_network WHERE referrer_id=?", (r["agent_id"],)).fetchone()
            total += sub["c"]
        return total

    # --- Used TX Hashes ---
    def is_tx_used(self, tx_hash: str) -> bool:
        row = self.conn.execute("SELECT 1 FROM used_tx_hashes WHERE tx_hash=?", (tx_hash,)).fetchone()
        return row is not None

    def mark_tx_used(self, tx_hash: str):
        self.conn.execute("INSERT OR IGNORE INTO used_tx_hashes (tx_hash, used_at) VALUES (?, ?)", (tx_hash, time.time()))
        self.conn.commit()

    # --- Stats ---
    # --- Generic query helpers for tools ---
    def execute(self, sql: str, params: tuple = ()):
        self.conn.execute(sql, params)
        self.conn.commit()

    def fetchone(self, sql: str, params: tuple = ()):
        return self.conn.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()):
        return self.conn.execute(sql, params).fetchall()

    def get_agent_stats(self, agent_id: str) -> dict:
        return {
            "agent_id": agent_id,
            "searches_used": self.get_usage(agent_id),
            "referral_balance": self.get_referral_balance(agent_id),
            "referral_code": self.get_referral_code(agent_id),
            "subscription": self.get_subscription(agent_id),
        }


store = Store()
