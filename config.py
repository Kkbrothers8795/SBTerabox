import os

# Load configuration values from Docker environment variables
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Parse OWNER_ID and ADMINS safely
OWNER_ID = [int(i) for i in os.environ.get("OWNER_ID", "").split(",") if i.strip().isdigit()]
ADMINS = [int(i) for i in os.environ.get("ADMINS", "").split(",") if i.strip().isdigit()]

# Redis configuration
HOST = os.environ.get("HOST", "")
PORT = os.environ.get("PORT", "")
PASSWORD = os.environ.get("PASSWORD", "")

CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "")   ## add without using "@"
START_IMAGE = os.environ.get("START_IMAGE", "https://i.ibb.co/d28yPfL/960389-original-4320x7680.jpg")
VERIFY_IMAGE = os.environ.get("VERIFY_IMAGE", "https://i.ibb.co/jw8zc5h/t3-1866t0y.jpg")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")   ## add without using "@"
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")  ## With @
TUTORAL_VID_URL = os.environ.get("TUTORAL_VID_URL", "https://t.me/Muthal_Gang_Reunite/42")

MONGO_DB_URL = os.environ.get("MONGO_DB_URL", "")
DB_NAME = os.environ.get("DB_NAME", "")

PRIVATE_CHAT_ID = int(os.environ.get("PRIVATE_CHAT_ID", "0"))  ## CHAT WHERE YOU WANT TO STORE VIDEOS

COOKIE = os.environ.get("COOKIE", "")

SHORTNER_URL = os.environ.get("SHORTNER_URL", "")
SHORTNER_API = os.environ.get("SHORTNER_API", "")
