from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "monitor.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_total INTEGER NOT NULL,
                memory_used INTEGER NOT NULL,
                memory_usage REAL NOT NULL,
                load_avg_1 REAL NOT NULL,
                load_avg_5 REAL NOT NULL,
                load_avg_15 REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS process_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                event_type TEXT NOT NULL,
                pid INTEGER NOT NULL,
                ppid INTEGER NOT NULL,
                uid INTEGER NOT NULL,
                comm TEXT NOT NULL,
                filename TEXT,
                exit_code INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()

