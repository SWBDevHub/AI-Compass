import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "aicompass.db"


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Creates the evaluations table if it doesn't already exist. Safe to call every startup."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                business_problem TEXT,
                proposed_tool TEXT,
                decision TEXT,
                decision_class TEXT,
                intake_json TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
        """)


def save_evaluation(eval_id, intake, result, decision, decision_class):
    with _connect() as conn:
        conn.execute(
            """INSERT INTO evaluations
               (id, created_at, business_problem, proposed_tool, decision, decision_class, intake_json, result_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                eval_id,
                datetime.utcnow().isoformat(timespec="seconds"),
                intake.get("business_problem", ""),
                intake.get("proposed_tool", ""),
                decision,
                decision_class,
                json.dumps(intake),
                json.dumps(result),
            ),
        )


def get_evaluation(eval_id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM evaluations WHERE id = ?", (eval_id,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "business_problem": row["business_problem"],
            "proposed_tool": row["proposed_tool"],
            "decision": row["decision"],
            "decision_class": row["decision_class"],
            "intake": json.loads(row["intake_json"]),
            "result": json.loads(row["result_json"]),
        }


def list_evaluations():
    """Newest first — used by the dashboard."""
    with _connect() as conn:
        rows = conn.execute(
            """SELECT id, created_at, business_problem, proposed_tool, decision, decision_class
               FROM evaluations ORDER BY created_at DESC"""
        ).fetchall()
        return [dict(row) for row in rows]
