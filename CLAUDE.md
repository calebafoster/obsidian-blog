# CLAUDE.md - obsidian blog

## Overview
A self-hosted blog site to host written posts previously on Substack. Drop a `.md` file into the `posts/` folder on the home server and it automatically builds the site, publishes the post, and notifies subscribers by email.

## Hosting
- Home server: Orange Pi, user `orangepi`
- Deploy path: `/home/orangepi/blog-app/obsidian-blog/`
- Domain: `blog.tesselis.org` (HTTPS via `/etc/ssl/tesselis/cert.pem` — same wildcard cert as other tesselis.org services)
- Nginx serves static files from `public/`, proxies `/subscribe` and `/unsubscribe` to Flask on `127.0.0.1:5000`
- Other services on same Pi: `budget.tesselis.org` (port 9901), `jellyfin.tesselis.org` (port 8096)
- systemd manages all background services

## Tech Stack
- **Python** — all scripting and services
- **SQLite** — subscriber storage (`subscribers.db`)
- **python-markdown** + Jinja2 — Markdown rendering and HTML templating
- **watchdog** — file watcher daemon (monitors `posts/` for new `.md` files)
- **Flask** — minimal subscriber API (`/subscribe`, `/unsubscribe` only)
- **Brevo** — transactional email (free tier, 300/day) for subscriber notifications
- **Nginx** — static file serving + reverse proxy to Flask API

## Architecture (Approach B: pre-rendered static site)
1. Drop `.md` into `posts/` — this is the entire publish action
2. watchdog daemon detects new file → triggers build script → sends email notifications
3. Build script parses frontmatter, renders Markdown → HTML, writes to `public/`
4. Nginx serves `public/` directly (no Python on request path for readers)
5. Flask API handles only `/subscribe` and `/unsubscribe`, proxied through nginx

## Visual Design
- Theme: **AnuPpuccin** with **Rosé Pine** color scheme (dark)
- Key colors: base `#191724`, surface `#1f1d2e`, text `#e0def4`, iris `#c4a7e7`, pine `#31748f`, foam `#9ccfd8`, gold `#f6c177`, love `#eb6f92`, rose `#ebbcba`
- Layout: centered reading column with floating table of contents on the right
- Nav: top bar with site name + links (posts, subscribe)

## Post Format
Markdown files with YAML frontmatter:
```markdown
---
title: Post Title
date: 2026-03-28
tags: [optional, tags]
---
Content here...
```
- `title` and `date` are required
- Filename becomes the URL slug (e.g. `my-post.md` → `/posts/my-post`)
- Embeds/assets live in `posts/assets/`, copied to `public/assets/` on build

## Markdown Rendering
- Standard Markdown (headings, bold, lists, code blocks, images)
- Callouts: Obsidian syntax (`> [!note]`, `> [!warning]`, etc.) via custom preprocessor → `<div class="callout callout-note">`. Styled with Rose Pine colors per type (note → iris, warning → gold, danger → love)
- Embeds/transclusions: `![[filename]]` → `<img>` or `<a>` depending on file type, resolved from `posts/assets/`
- TOC: auto-generated from headings, rendered in right-side panel
- Syntax highlighting for code blocks

## Database Schema
- `subscribers` table: `email`, `token` (unique unsubscribe token), `created_at`
- `posts` table: `slug`, `title`, `date`, `notified` (bool — tracks whether notification emails have been sent)

## Subscription Flow
- Simple email form on site → `POST /subscribe` → stored in SQLite (no double opt-in)
- Each subscriber gets a unique unsubscribe token; unsubscribe link included in every email
- `GET /unsubscribe?token=…` removes the subscriber

## Theme Files
- `AnuPpuccin/theme.css` — source theme CSS (reference for color variables and styling conventions)
- `AnuPpuccin/manifest.json` — theme metadata
