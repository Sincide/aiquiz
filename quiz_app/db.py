import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = 'quiz_results.db'


def init_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT,
            user_answer TEXT,
            correct_answer TEXT,
            correct INTEGER,
            domain TEXT,
            timestamp TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS favorites (
            question_id TEXT PRIMARY KEY
        )"""
    )
    conn.commit()
    return conn


def save_result(conn: sqlite3.Connection, question_id: str, user_answer: str,
                correct_answer: str, correct: bool, domain: str) -> None:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO results (question_id, user_answer, correct_answer, correct, domain, timestamp)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (question_id, user_answer, correct_answer, int(correct), domain, datetime.utcnow().isoformat())
    )
    conn.commit()


def mark_favorite(conn: sqlite3.Connection, question_id: str, fav: bool) -> None:
    cur = conn.cursor()
    if fav:
        cur.execute("INSERT OR IGNORE INTO favorites (question_id) VALUES (?)", (question_id,))
    else:
        cur.execute("DELETE FROM favorites WHERE question_id = ?", (question_id,))
    conn.commit()


def is_favorite(conn: sqlite3.Connection, question_id: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM favorites WHERE question_id = ?", (question_id,))
    return cur.fetchone() is not None
