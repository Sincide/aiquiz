import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

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


def get_favorite_questions(conn: sqlite3.Connection) -> List[str]:
    """Get list of favorite question IDs"""
    cur = conn.cursor()
    cur.execute("SELECT question_id FROM favorites")
    return [row[0] for row in cur.fetchall()]


def get_results_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Get overall quiz performance statistics"""
    cur = conn.cursor()
    
    # Overall stats
    cur.execute("SELECT COUNT(*), SUM(correct) FROM results")
    total_row = cur.fetchone()
    if not total_row or total_row[0] == 0:
        return {
            'overall_attempts': 0,
            'overall_correct': 0,
            'domain_stats': {},
            'recent_results': [],
            'favorite_count': 0
        }
    
    overall_attempts, overall_correct = total_row
    
    # Domain-specific stats
    cur.execute("""
        SELECT domain, COUNT(*) as attempts, SUM(correct) as correct
        FROM results 
        GROUP BY domain 
        ORDER BY domain
    """)
    domain_stats = {}
    for row in cur.fetchall():
        domain, attempts, correct = row
        domain_stats[domain] = {
            'attempts': attempts,
            'correct': correct or 0
        }
    
    # Recent results
    cur.execute("""
        SELECT domain, correct, timestamp
        FROM results 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    recent_results = []
    for row in cur.fetchall():
        recent_results.append({
            'domain': row[0],
            'correct': bool(row[1]),
            'timestamp': row[2]
        })
    
    # Favorite count
    cur.execute("SELECT COUNT(*) FROM favorites")
    favorite_count = cur.fetchone()[0]
    
    return {
        'overall_attempts': overall_attempts,
        'overall_correct': overall_correct or 0,
        'domain_stats': domain_stats,
        'recent_results': recent_results,
        'favorite_count': favorite_count
    }


def get_recent_results(conn: sqlite3.Connection, limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent quiz results for review"""
    cur = conn.cursor()
    cur.execute("""
        SELECT question_id, user_answer, correct_answer, correct, domain, timestamp
        FROM results 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    results = []
    for row in cur.fetchall():
        results.append({
            'question_id': row[0],
            'user_answer': row[1],
            'correct_answer': row[2],
            'correct': bool(row[3]),
            'domain': row[4],
            'timestamp': row[5]
        })
    
    return results


def clear_all_statistics(conn: sqlite3.Connection) -> int:
    """Clear all quiz results and reset statistics"""
    cur = conn.cursor()
    cur.execute('DELETE FROM results')
    conn.commit()
    return cur.rowcount
