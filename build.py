import os
import re
import shutil
import yaml
import markdown
from pathlib import Path
from markdown import preprocessors
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension
from jinja2 import Environment, FileSystemLoader


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (meta_dict, body_string)."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*(?:\n|$)', content, re.DOTALL)
    if not match:
        return {}, content
    meta = yaml.safe_load(match.group(1)) or {}
    # Ensure date is always a string
    if "date" in meta:
        meta["date"] = str(meta["date"])
    body = content[match.end():]
    return meta, body


class CalloutPreprocessor(preprocessors.Preprocessor):
    """Converts Obsidian callouts to <div class="callout callout-TYPE"> blocks."""

    CALLOUT_RE = re.compile(r'^\s*>\s*\[!([\w-]+)\]\s*$')
    CONTENT_RE = re.compile(r'^\s*>\s*(.*)$')

    def run(self, lines: list[str]) -> list[str]:
        new_lines = []
        i = 0
        while i < len(lines):
            m = self.CALLOUT_RE.match(lines[i])
            if m:
                callout_type = m.group(1).lower()
                new_lines.append(f'<div class="callout callout-{callout_type}">')
                i += 1
                while i < len(lines):
                    if self.CALLOUT_RE.match(lines[i]):
                        break  # Start of a new callout — stop consuming content
                    content_match = self.CONTENT_RE.match(lines[i])
                    if content_match:
                        new_lines.append(content_match.group(1))
                        i += 1
                    else:
                        break
                new_lines.append('</div>')
            else:
                new_lines.append(lines[i])
                i += 1
        return new_lines


class CalloutExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(CalloutPreprocessor(md), 'obsidian_callout', 175)


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


class EmbedPreprocessor(preprocessors.Preprocessor):
    """Converts ![[filename]] Obsidian embeds to <img> or <a> tags."""

    EMBED_RE = re.compile(r'!\[\[([^\]]+)\]\]')

    def run(self, lines: list[str]) -> list[str]:
        new_lines = []
        for line in lines:
            def replace(m):
                filename = m.group(1).strip()
                ext = os.path.splitext(filename)[1].lower()
                url = f"/assets/{filename}"
                if ext in IMAGE_EXTENSIONS:
                    return f'<img src="{url}" alt="{filename}">'
                return f'<a href="{url}">{filename}</a>'
            new_lines.append(self.EMBED_RE.sub(replace, line))
        return new_lines


class EmbedExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(EmbedPreprocessor(md), 'obsidian_embed', 176)


def render_markdown(text: str) -> str:
    """Render Markdown string to HTML with Obsidian extensions."""
    md = markdown.Markdown(extensions=[
        TocExtension(baselevel=1),
        CalloutExtension(),
        EmbedExtension(),
        "pymdownx.superfences",
        "tables",
        "fenced_code",
    ])
    return md.convert(text)


def _get_jinja_env() -> Environment:
    templates_dir = Path(__file__).parent / "templates"
    return Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=False)


def build_post(md_path: Path, conn) -> dict:
    """Parse, render, and write a single post. Returns post metadata dict."""
    import config
    raw = md_path.read_text()
    meta, body = parse_frontmatter(raw)
    slug = md_path.stem

    md_obj = markdown.Markdown(extensions=[
        TocExtension(baselevel=1),
        CalloutExtension(),
        EmbedExtension(),
        "pymdownx.superfences",
        "tables",
        "fenced_code",
    ])
    html_content = md_obj.convert(body)
    toc = md_obj.toc

    out_dir = Path(config.PUBLIC_DIR) / "posts"
    out_dir.mkdir(parents=True, exist_ok=True)

    env = _get_jinja_env()
    tmpl = env.get_template("post.html")
    post = {
        "slug": slug,
        "title": meta.get("title", slug),
        "date": str(meta.get("date", "")),
        "toc": toc,
        "html_content": html_content,
    }
    page_html = tmpl.render(post=post, site_name="Blog")
    (out_dir / f"{slug}.html").write_text(page_html)

    try:
        conn.execute(
            "INSERT OR IGNORE INTO posts (slug, title, date) VALUES (?, ?, ?)",
            (slug, post["title"], post["date"]),
        )
        conn.commit()
    except Exception:
        pass

    return post


def build_all() -> None:
    """Build every .md in POSTS_DIR and regenerate index.html."""
    import config
    import db
    posts_dir = Path(config.POSTS_DIR)
    public_dir = Path(config.PUBLIC_DIR)
    public_dir.mkdir(parents=True, exist_ok=True)

    # Copy assets
    assets_src = posts_dir / "assets"
    assets_dst = public_dir / "assets"
    if assets_src.exists():
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)

    # Copy static assets (CSS, etc.)
    static_src = Path(__file__).parent / "static"
    static_dst = public_dir / "static"
    if static_src.exists():
        if static_dst.exists():
            shutil.rmtree(static_dst)
        shutil.copytree(static_src, static_dst)

    conn = db.get_connection(config.DB_PATH)
    db.init_db(conn)

    posts = []
    for md_file in sorted(posts_dir.glob("*.md")):
        post = build_post(md_file, conn)
        posts.append(post)

    conn.close()

    # Sort newest first
    posts.sort(key=lambda p: p["date"], reverse=True)

    env = _get_jinja_env()
    index_html = env.get_template("index.html").render(posts=posts, site_name="Blog")
    (public_dir / "index.html").write_text(index_html)


if __name__ == "__main__":
    build_all()
