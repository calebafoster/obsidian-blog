import pytest

def test_parse_frontmatter_extracts_title_date_tags():
    from build import parse_frontmatter
    content = """---
title: Hello World
date: 2026-03-30
tags: [python, blog]
---
Body text here."""
    meta, body = parse_frontmatter(content)
    assert meta["title"] == "Hello World"
    assert meta["date"] == "2026-03-30"
    assert meta["tags"] == ["python", "blog"]
    assert body.strip() == "Body text here."

def test_parse_frontmatter_no_tags():
    from build import parse_frontmatter
    content = "---\ntitle: No Tags\ndate: 2026-01-01\n---\nBody."
    meta, body = parse_frontmatter(content)
    assert meta.get("tags", []) == []
    assert "title" in meta

def test_render_markdown_returns_html():
    from build import render_markdown
    html = render_markdown("# Hello\n\nParagraph.")
    assert "<h1" in html
    assert "Hello" in html
    assert "<p>" in html

def test_parse_frontmatter_no_frontmatter():
    from build import parse_frontmatter
    content = "Just plain body text with no frontmatter."
    meta, body = parse_frontmatter(content)
    assert meta == {}
    assert body == content

def test_callout_note_renders_div():
    from build import render_markdown
    md = "> [!note]\n> This is a note."
    html = render_markdown(md)
    assert 'class="callout callout-note"' in html
    assert "This is a note." in html

def test_callout_warning_renders_div():
    from build import render_markdown
    md = "> [!warning]\n> Watch out."
    html = render_markdown(md)
    assert 'class="callout callout-warning"' in html

def test_callout_unknown_type_renders_div():
    from build import render_markdown
    md = "> [!custom]\n> Custom callout."
    html = render_markdown(md)
    assert 'class="callout callout-custom"' in html

def test_image_embed_renders_img_tag():
    from build import render_markdown
    md = "![[photo.png]]"
    html = render_markdown(md)
    assert '<img' in html
    assert 'src="/assets/photo.png"' in html

def test_file_embed_renders_anchor_tag():
    from build import render_markdown
    md = "![[document.pdf]]"
    html = render_markdown(md)
    assert '<a' in html
    assert 'href="/assets/document.pdf"' in html

def test_non_embed_markdown_unchanged():
    from build import render_markdown
    md = "Normal **bold** text."
    html = render_markdown(md)
    assert "<strong>bold</strong>" in html

import os
import tempfile

def _make_post_file(tmp_path, slug, content):
    post_path = tmp_path / "posts" / f"{slug}.md"
    post_path.parent.mkdir(parents=True, exist_ok=True)
    post_path.write_text(content)
    return post_path

def test_build_post_writes_html_file(tmp_path, monkeypatch):
    import importlib
    monkeypatch.setenv("POSTS_DIR", str(tmp_path / "posts"))
    monkeypatch.setenv("PUBLIC_DIR", str(tmp_path / "public"))
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    # Remaining config vars (unused by build but required by config module)
    for k in ("BREVO_API_KEY", "SITE_BASE_URL", "SENDER_EMAIL", "SENDER_NAME"):
        monkeypatch.setenv(k, "x")
    import config
    importlib.reload(config)

    _make_post_file(tmp_path, "hello-world", "---\ntitle: Hello World\ndate: 2026-03-30\n---\n# Hello\n\nWorld.")

    from build import build_all
    build_all()

    output = tmp_path / "public" / "posts" / "hello-world.html"
    assert output.exists()
    html = output.read_text()
    assert "Hello World" in html
    assert "<h1" in html

def test_build_all_writes_index(tmp_path, monkeypatch):
    import importlib
    monkeypatch.setenv("POSTS_DIR", str(tmp_path / "posts"))
    monkeypatch.setenv("PUBLIC_DIR", str(tmp_path / "public"))
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    for k in ("BREVO_API_KEY", "SITE_BASE_URL", "SENDER_EMAIL", "SENDER_NAME"):
        monkeypatch.setenv(k, "x")
    import config
    importlib.reload(config)

    _make_post_file(tmp_path, "first-post", "---\ntitle: First Post\ndate: 2026-01-01\n---\nContent.")
    _make_post_file(tmp_path, "second-post", "---\ntitle: Second Post\ndate: 2026-02-01\n---\nContent.")

    from build import build_all
    build_all()

    index = tmp_path / "public" / "index.html"
    assert index.exists()
    html = index.read_text()
    assert "First Post" in html
    assert "Second Post" in html
