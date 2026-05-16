import os
from dotenv import load_dotenv

# Load the environment variables from the root .env file
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    PAYMONGO_SECRET_KEY: str = os.getenv("PAYMONGO_SECRET_KEY")
    PAYMONGO_WEBHOOK_SECRET: str = os.getenv("PAYMONGO_WEBHOOK_SECRET")
    
    # This will be your Cloudflare domain later (e.g., https://kiosk.yourdomain.com)
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

# Create a settings object we can import anywhere
settings = Settings()