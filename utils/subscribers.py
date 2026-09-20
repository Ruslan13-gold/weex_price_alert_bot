"""Хранение подписчиков бота (SQLite)."""

import sqlite3
from pathlib import Path
from typing import List
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "subscribers.db"


def _ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def add_subscriber(chat_id: int, username: str | None = None, first_name: str | None = None) -> bool:
    """Добавить подписчика. True если новый, False если уже был."""
    _ensure_db()
    with _connect() as conn:
        cur = conn.execute("SELECT 1 FROM subscribers WHERE chat_id = ?", (chat_id,))
        exists = cur.fetchone() is not None
        if exists:
            conn.execute(
                "UPDATE subscribers SET username = ?, first_name = ? WHERE chat_id = ?",
                (username, first_name, chat_id),
            )
            conn.commit()
            return False
        conn.execute(
            "INSERT INTO subscribers (chat_id, username, first_name) VALUES (?, ?, ?)",
            (chat_id, username, first_name),
        )
        conn.commit()
        return True


def remove_subscriber(chat_id: int) -> bool:
    """Удалить подписчика. True если был удалён."""
    _ensure_db()
    with _connect() as conn:
        cur = conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return cur.rowcount > 0


def get_all_chat_ids() -> List[int]:
    _ensure_db()
    with _connect() as conn:
        rows = conn.execute("SELECT chat_id FROM subscribers").fetchall()
    return [r[0] for r in rows]


def count_subscribers() -> int:
    _ensure_db()
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()
    return int(row[0]) if row else 0