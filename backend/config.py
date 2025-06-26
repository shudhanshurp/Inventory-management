# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    DEBUG = True
    PORT = 5001
    CORS_ORIGINS = ["http://localhost:3000", "https://ordersense.vercel.app"]
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-1.5-flash"
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required") 