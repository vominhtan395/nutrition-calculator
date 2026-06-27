import os
from dotenv import load_dotenv

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")

if not USDA_API_KEY:
    raise ValueError("Thiếu USDA_API_KEY trong file .env!")