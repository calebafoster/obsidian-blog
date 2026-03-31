import sqlite3
import tempfile
import os
import pytest

def test_init_db_creates_tables(tmp_path):
    db_path = str(tmp_path / "test.db")
    import db
    conn = db.get_connection(db_path)
    db.init_db(conn)

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = {row[0] for row in tables}
    assert "subscribers" in table_names
    assert "posts" in table_names
    conn.close()

def test_subscribers_schema(tmp_path):
    db_path = str(tmp_path / "test.db")
    import db
    conn = db.get_connection(db_path)
    db.init_db(conn)

    conn.execute(
        "INSERT INTO subscribers (email, token) VALUES (?, ?)",
        ("a@b.com", "tok123")
    )
    conn.commit()
    row = conn.execute("SELECT email, token FROM subscribers").fetchone()
    assert tuple(row) == ("a@b.com", "tok123")
    conn.close()

def test_posts_schema(tmp_path):
    import db
    conn = db.get_connection(str(tmp_path / "test.db"))
    db.init_db(conn)

    conn.execute(
        "INSERT INTO posts (slug, title, date) VALUES (?, ?, ?)",
        ("my-post", "My Post", "2026-03-30")
    )
    conn.commit()
    row = conn.execute("SELECT slug, title, date, notified FROM posts").fetchone()
    assert tuple(row) == ("my-post", "My Post", "2026-03-30", 0)
    conn.close()
