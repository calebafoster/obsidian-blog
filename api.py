import secrets
from flask import Flask, request, render_template
import config
import db

app = Flask(__name__, template_folder="templates")

def _get_conn():
    conn = db.get_connection(config.DB_PATH)
    db.init_db(conn)
    return conn

@app.route("/subscribe", methods=["GET"])
def subscribe_page():
    return render_template("subscribe.html", site_name="Blog")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip().lower()
    if not email:
        return render_template("subscribe_confirm.html", site_name="Blog"), 400
    token = secrets.token_urlsafe(32)
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO subscribers (email, token) VALUES (?, ?)",
            (email, token),
        )
        conn.commit()
    finally:
        conn.close()
    return render_template("subscribe_confirm.html", site_name="Blog")

@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    token = request.args.get("token", "")
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM subscribers WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()
    return render_template("unsubscribe_confirm.html", site_name="Blog")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
