import requests
import config
import db

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"

def notify_post(slug: str) -> None:
    """Send email notifications for a post to all subscribers, if not already sent."""
    conn = db.get_connection(config.DB_PATH)
    db.init_db(conn)

    try:
        post = conn.execute(
            "SELECT title, date, notified FROM posts WHERE slug = ?", (slug,)
        ).fetchone()

        if post is None or post["notified"]:
            return

        subscribers = conn.execute("SELECT email, token FROM subscribers").fetchall()
        post_url = f"{config.SITE_BASE_URL}/posts/{slug}"

        all_sent = True
        for sub in subscribers:
            unsubscribe_url = f"{config.SITE_BASE_URL}/unsubscribe?token={sub['token']}"
            html_body = f"""
<p>A new post has been published: <strong>{post['title']}</strong></p>
<p><a href="{post_url}">Read the post →</a></p>
<hr>
<p style="font-size:0.8em;color:#888;">
  <a href="{unsubscribe_url}">Unsubscribe</a>
</p>
"""
            payload = {
                "sender": {"name": config.SENDER_NAME, "email": config.SENDER_EMAIL},
                "to": [{"email": sub["email"]}],
                "subject": f"New post: {post['title']}",
                "htmlContent": html_body,
            }
            resp = requests.post(
                BREVO_SEND_URL,
                headers={"api-key": config.BREVO_API_KEY, "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )
            if resp.status_code not in (200, 201, 202):
                print(f"[notifier] Warning: Brevo error for {sub['email']}: {resp.status_code} {resp.text}", flush=True)
                all_sent = False

        if all_sent:
            conn.execute("UPDATE posts SET notified = 1 WHERE slug = ?", (slug,))
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python notifier.py <slug>")
        sys.exit(1)
    notify_post(sys.argv[1])
