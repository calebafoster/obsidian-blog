import os
import pytest

def test_config_reads_env_vars(monkeypatch):
    monkeypatch.setenv("BREVO_API_KEY", "test_key")
    monkeypatch.setenv("SITE_BASE_URL", "http://localhost")
    monkeypatch.setenv("SENDER_EMAIL", "a@b.com")
    monkeypatch.setenv("SENDER_NAME", "Test")
    monkeypatch.setenv("POSTS_DIR", "/tmp/posts")
    monkeypatch.setenv("PUBLIC_DIR", "/tmp/public")
    monkeypatch.setenv("DB_PATH", "/tmp/test.db")

    # Force reimport so monkeypatched env is picked up
    import importlib
    import config
    importlib.reload(config)

    assert config.BREVO_API_KEY == "test_key"
    assert config.SITE_BASE_URL == "http://localhost"
    assert config.SENDER_EMAIL == "a@b.com"
    assert config.SENDER_NAME == "Test"
    assert config.POSTS_DIR == "/tmp/posts"
    assert config.PUBLIC_DIR == "/tmp/public"
    assert config.DB_PATH == "/tmp/test.db"
