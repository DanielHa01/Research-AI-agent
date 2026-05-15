"""
Database: SQLite persistence layer for research reports.
Stores topic, sub-questions, report markdown, and timestamp.
Uses Python's built-in sqlite3 — no external dependencies.

Schema:
  reports(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic       TEXT NOT NULL,
    sub_questions TEXT NOT NULL,   -- JSON array stored as string
    report      TEXT NOT NULL,     -- Full Markdown report
    created_at  TEXT NOT NULL      -- ISO 8601 timestamp
  )
"""

import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "research_agent.db")


def get_connection() -> sqlite3.Connection:
    """Open a connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the reports table if it doesn't exist. Call once on startup."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                topic         TEXT NOT NULL,
                sub_questions TEXT NOT NULL,
                report        TEXT NOT NULL,
                created_at    TEXT NOT NULL
            )
        """)
        conn.commit()


def save_report(topic: str, sub_questions: list[str], report: str) -> int:
    """
    Save a completed research report to the database.

    Args:
        topic:         The original research topic string.
        sub_questions: List of sub-questions the agent researched.
        report:        Full Markdown report string.

    Returns:
        The new row's integer ID.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reports (topic, sub_questions, report, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                topic,
                json.dumps(sub_questions),
                report,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_reports(limit: int = 50) -> list[dict]:
    """
    Fetch all saved reports ordered by most recent first.
    Returns lightweight summaries (no full report text) for the sidebar.

    Returns list of dicts with keys: id, topic, sub_questions, created_at.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, topic, sub_questions, created_at
            FROM reports
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "topic": row["topic"],
            "sub_questions": json.loads(row["sub_questions"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def get_report_by_id(report_id: int) -> dict | None:
    """
    Fetch a single report by ID including the full report text.

    Returns dict with keys: id, topic, sub_questions, report, created_at.
    Returns None if not found.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "topic": row["topic"],
        "sub_questions": json.loads(row["sub_questions"]),
        "report": row["report"],
        "created_at": row["created_at"],
    }


def delete_report(report_id: int) -> bool:
    """
    Delete a report by ID.

    Returns True if a row was deleted, False if ID not found.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM reports WHERE id = ?", (report_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def search_reports(query: str, limit: int = 20) -> list[dict]:
    """
    Full-text search across topic and report content.
    Uses SQLite LIKE for simplicity — good enough for a portfolio project.

    Returns lightweight summaries (no full report text).
    """
    pattern = f"%{query}%"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, topic, sub_questions, created_at
            FROM reports
            WHERE topic LIKE ? OR report LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (pattern, pattern, limit),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "topic": row["topic"],
            "sub_questions": json.loads(row["sub_questions"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
