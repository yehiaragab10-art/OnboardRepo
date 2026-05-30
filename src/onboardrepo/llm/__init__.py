from pathlib import Path
import os

from dotenv import load_dotenv


def get_gemini_api_key() -> str:
    #Load Gemini API key from environment/.env.
    
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not set. Add it to your .env file."
        )

    return api_key