"""Agent Speed Dial — save and recall named search templates.
Agent: "@monitor_4k" → expands to {"query": "monitor 4K 27 pulgadas", "max_price": 600, "country": "mx"}"""
import json
import time
from ..store.db import store


class SpeedDial:
    def __init__(self, store_conn=None):
        self.store = store_conn or store
        self._init_db()

    def _init_db(self):
        try:
            self.store.execute("""
                CREATE TABLE IF NOT EXISTS speed_dial (
                    agent_id TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    template_data TEXT NOT NULL,
                    created_at REAL,
                    updated_at REAL,
                    PRIMARY KEY (agent_id, template_name)
                )
            """)
        except Exception:
            pass

    def save(self, agent_id: str, name: str, params: dict) -> dict:
        if not agent_id or not name:
            return {"error": "agent_id and name required"}
        now = time.time()
        try:
            existing = self.store.fetchone(
                "SELECT * FROM speed_dial WHERE agent_id = ? AND template_name = ?",
                (agent_id, name),
            )
            if existing:
                self.store.execute(
                    "UPDATE speed_dial SET template_data=?, updated_at=? "
                    "WHERE agent_id=? AND template_name=?",
                    (json.dumps(params), now, agent_id, name),
                )
            else:
                self.store.execute(
                    "INSERT INTO speed_dial (agent_id, template_name, template_data, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (agent_id, name, json.dumps(params), now, now),
                )
            return {"saved": name, "params": params}
        except Exception as e:
            return {"error": str(e)}

    def get(self, agent_id: str, name: str) -> dict:
        if not agent_id or not name:
            return {"error": "agent_id and name required"}
        try:
            row = self.store.fetchone(
                "SELECT template_data FROM speed_dial WHERE agent_id=? AND template_name=?",
                (agent_id, name),
            )
            if row:
                return {"name": name, "params": json.loads(row["template_data"])}
            return {"error": f"Template '{name}' not found"}
        except Exception as e:
            return {"error": str(e)}

    def list_templates(self, agent_id: str) -> dict:
        if not agent_id:
            return {"error": "agent_id required"}
        try:
            rows = self.store.fetchall(
                "SELECT template_name, template_data, updated_at "
                "FROM speed_dial WHERE agent_id=? ORDER BY updated_at DESC",
                (agent_id,),
            )
            return {
                "templates": [
                    {"name": r["template_name"], "params": json.loads(r["template_data"])}
                    for r in rows
                ],
                "total": len(rows),
            }
        except Exception as e:
            return {"error": str(e)}

    def delete(self, agent_id: str, name: str) -> dict:
        if not agent_id or not name:
            return {"error": "agent_id and name required"}
        try:
            self.store.execute(
                "DELETE FROM speed_dial WHERE agent_id=? AND template_name=?",
                (agent_id, name),
            )
            return {"deleted": name}
        except Exception as e:
            return {"error": str(e)}

    def expand(self, agent_id: str, text: str) -> tuple[str, dict | None]:
        if text.startswith("@"):
            name = text[1:]
            result = self.get(agent_id, name)
            if "params" in result:
                return name, result["params"]
        return text, None


speed_dial = SpeedDial()
