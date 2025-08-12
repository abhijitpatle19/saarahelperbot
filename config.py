import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = "8475401925:AAFl1hyo1syOYfXRIVymzNg4eZEcSoBZPm8"
ADMIN_USER_ID = 8324487113  # Your Telegram user ID

# Database configuration (using simple file-based storage for this example)
DB_FILE = 'user_sessions.json' 