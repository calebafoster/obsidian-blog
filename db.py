import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT NOT NULL UNIQUE,
            token      TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS posts (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            slug     TEXT NOT NULL UNIQUE,
            title    TEXT NOT NULL,
            date     TEXT NOT NULL,
            notified INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
