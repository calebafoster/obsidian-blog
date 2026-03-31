import os
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.environ["BREVO_API_KEY"]
SITE_BASE_URL = os.environ["SITE_BASE_URL"].rstrip("/")
SENDER_EMAIL  = os.environ["SENDER_EMAIL"]
SENDER_NAME   = os.environ["SENDER_NAME"]
POSTS_DIR     = os.environ["POSTS_DIR"]
PUBLIC_DIR    = os.environ["PUBLIC_DIR"]
DB_PATH       = os.environ["DB_PATH"]
