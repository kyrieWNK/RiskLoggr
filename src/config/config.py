import os
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path=env_path)

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise ValueError("❌ OPENAI_API_KEY not set properly in .env file!")

if not settings.OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables or .env file.")