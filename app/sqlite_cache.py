import hashlib
import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

DB_PATH = "/data/cache.sqlite3"


def get_conn():
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE,
            text TEXT,
            cefr_level TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        conn.commit()


def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def check_cache(text: str) -> Optional[str]:
    h = get_text_hash(text)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT cefr_level FROM texts WHERE hash = ? AND status = 'done'", (h,)
        ).fetchone()
        return row[0] if row else None


def save_pending(text: str):
    h = get_text_hash(text)
    with get_conn() as conn:
        try:
            conn.execute(
                """
                INSERT INTO texts (hash, text, status)
                VALUES (?, ?, 'pending')
            """,
                (h, text),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # already exists


def mark_done(text: str, level: str):
    h = get_text_hash(text)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE texts
            SET cefr_level = ?, status = 'done', updated_at = ?
            WHERE hash = ?
        """,
            (level, datetime.utcnow(), h),
        )
        conn.commit()


def get_pending_texts(limit: int = 10) -> List[Tuple[str, str]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT hash, text FROM texts
            WHERE status = 'pending'
            LIMIT ?
        """,
            (limit,),
        ).fetchall()
    return rows
