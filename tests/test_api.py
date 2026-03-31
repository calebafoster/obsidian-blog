import pytest
import tempfile
import os

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    for k in ("BREVO_API_KEY", "SITE_BASE_URL", "SENDER_EMAIL", "SENDER_NAME",
              "POSTS_DIR", "PUBLIC_DIR"):
        monkeypatch.setenv(k, "x")

    import importlib, config
    importlib.reload(config)

    import db
    conn = db.get_connection(config.DB_PATH)
    db.init_db(conn)
    conn.close()

    import api
    importlib.reload(api)
    api.app.config["TESTING"] = True
    with api.app.test_client() as c:
        yield c

def test_subscribe_stores_email(client):
    resp = client.post("/subscribe", data={"email": "test@example.com"})
    assert resp.status_code == 200
    assert b"subscribed" in resp.data.lower()

    import config, db
    conn = db.get_connection(config.DB_PATH)
    row = conn.execute("SELECT email FROM subscribers WHERE email=?", ("test@example.com",)).fetchone()
    conn.close()
    assert row is not None

def test_subscribe_duplicate_is_idempotent(client):
    client.post("/subscribe", data={"email": "dup@example.com"})
    resp = client.post("/subscribe", data={"email": "dup@example.com"})
    assert resp.status_code == 200

def test_unsubscribe_removes_subscriber(client):
    client.post("/subscribe", data={"email": "unsub@example.com"})

    import config, db
    conn = db.get_connection(config.DB_PATH)
    token = conn.execute("SELECT token FROM subscribers WHERE email=?", ("unsub@example.com",)).fetchone()[0]
    conn.close()

    resp = client.get(f"/unsubscribe?token={token}")
    assert resp.status_code == 200
    assert b"unsubscribed" in resp.data.lower()

    conn = db.get_connection(config.DB_PATH)
    row = conn.execute("SELECT email FROM subscribers WHERE email=?", ("unsub@example.com",)).fetchone()
    conn.close()
    assert row is None

def test_unsubscribe_unknown_token_returns_200(client):
    resp = client.get("/unsubscribe?token=doesnotexist")
    assert resp.status_code == 200
