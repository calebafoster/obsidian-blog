import os
import re
import yaml
import markdown
from markdown import preprocessors
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension


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
