import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def set_env(tmp_path, monkeypatch):
    monkeypatch.setenv("BREVO_API_KEY", "test_key")
    monkeypatch.setenv("SITE_BASE_URL", "http://example.com")
    monkeypatch.setenv("SENDER_EMAIL", "sender@example.com")
    monkeypatch.setenv("SENDER_NAME", "Sender")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    for k in ("POSTS_DIR", "PUBLIC_DIR"):
        monkeypatch.setenv(k, str(tmp_path))

    import importlib, config
    importlib.reload(config)

    import db
    conn = db.get_connection(config.DB_PATH)
    db.init_db(conn)
    conn.execute("INSERT INTO subscribers (email, token) VALUES (?, ?)", ("sub@example.com", "tok1"))
    conn.execute("INSERT INTO posts (slug, title, date) VALUES (?, ?, ?)", ("my-post", "My Post", "2026-03-30"))
    conn.commit()
    conn.close()

def test_notify_sends_email_and_marks_notified(tmp_path):
    import config, db
    import importlib
    import notifier
    importlib.reload(notifier)

    mock_resp = MagicMock()
    mock_resp.status_code = 201

    with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
        notifier.notify_post("my-post")

    assert mock_post.called
    call_json = mock_post.call_args[1]["json"]
    assert call_json["to"][0]["email"] == "sub@example.com"
    assert "My Post" in call_json["subject"]

    conn = db.get_connection(config.DB_PATH)
    notified = conn.execute("SELECT notified FROM posts WHERE slug=?", ("my-post",)).fetchone()[0]
    conn.close()
    assert notified == 1

def test_notify_skips_already_notified(tmp_path):
    import config, db
    import importlib
    import notifier
    importlib.reload(notifier)

    conn = db.get_connection(config.DB_PATH)
    conn.execute("UPDATE posts SET notified=1 WHERE slug='my-post'")
    conn.commit()
    conn.close()

    with patch("notifier.requests.post") as mock_post:
        notifier.notify_post("my-post")

    assert not mock_post.called

def test_notify_unsubscribe_link_in_email():
    import importlib
    import notifier
    importlib.reload(notifier)

    mock_resp = MagicMock()
    mock_resp.status_code = 201

    with patch("notifier.requests.post", return_value=mock_resp) as mock_post:
        notifier.notify_post("my-post")

    body = mock_post.call_args[1]["json"]["htmlContent"]
    assert "/unsubscribe?token=tok1" in body
