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
