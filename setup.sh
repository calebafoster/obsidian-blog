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

# Copy .env if it doesn't exist, substituting actual paths
if [ ! -f "$BLOG_DIR/.env" ]; then
    sed "s|BLOG_DIR|$BLOG_DIR|g" "$BLOG_DIR/.env.example" > "$BLOG_DIR/.env"
    echo "Created .env from .env.example — fill in BREVO_API_KEY, SITE_BASE_URL, SENDER_EMAIL, SENDER_NAME before starting services."
fi

BLOG_USER="$(whoami)"

# Install systemd services
for svc in blog-watcher blog-api; do
    sed -e "s|BLOG_DIR|$BLOG_DIR|g" -e "s|BLOG_USER|$BLOG_USER|g" \
        "$BLOG_DIR/systemd/$svc.service" | sudo tee /etc/systemd/system/$svc.service > /dev/null
done
sudo systemctl daemon-reload
sudo systemctl enable --now blog-watcher blog-api

# Allow nginx (www-data) to traverse the home directory to serve static files
chmod o+x "$HOME"

# Deploy nginx config
sed "s|BLOG_DIR|$BLOG_DIR|g" "$BLOG_DIR/nginx/blog.conf" \
    | sudo tee /etc/nginx/sites-enabled/blog.conf > /dev/null
sudo nginx -t && sudo systemctl reload nginx

echo "Done. Services enabled and started."
echo "Run: systemctl status blog-watcher blog-api"
