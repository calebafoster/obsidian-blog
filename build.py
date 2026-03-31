import re
import yaml
import markdown
from markdown.extensions.toc import TocExtension

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (meta_dict, body_string)."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}, content
    meta = yaml.safe_load(match.group(1)) or {}

    # Convert date values to strings to ensure consistent string representation
    if "date" in meta and meta["date"] is not None:
        meta["date"] = str(meta["date"])

    body = content[match.end():]
    return meta, body

def render_markdown(text: str) -> str:
    """Render Markdown string to HTML."""
    md = markdown.Markdown(extensions=[
        TocExtension(baselevel=1),
        "pymdownx.superfences",
        "tables",
        "fenced_code",
    ])
    return md.convert(text)
