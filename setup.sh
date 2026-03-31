#!/usr/bin/env bash
set -e

BLOG_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Setting up blog in $BLOG_DIR..."

# Create venv and install deps
python3 -m venv "$BLOG_DIR/.venv"
"$BLOG_DIR/.venv/bin/pip" install --upgrade pip
"$BLOG_DIR/.venv/bin/pip" install -r "$BLOG_DIR/requirements.txt"

# Create required directories
mkdir -p "$BLOG_DIR/posts/assets"
mkdir -p "$BLOG_DIR/public/assets"

# Copy .env if it doesn't exist
if [ ! -f "$BLOG_DIR/.env" ]; then
    cp "$BLOG_DIR/.env.example" "$BLOG_DIR/.env"
    echo "Created .env from .env.example — fill in your secrets before starting services."
fi

# Install and enable systemd services
sudo cp "$BLOG_DIR/systemd/blog-watcher.service" /etc/systemd/system/
sudo cp "$BLOG_DIR/systemd/blog-api.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now blog-watcher blog-api

echo "Done. Services enabled and started."
echo "Run: systemctl status blog-watcher blog-api"
