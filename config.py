from dotenv import load_dotenv
import os

load_dotenv()
LLM_API_KEY = os.getenv("GEMINI_API_KEY")

WEB_SEARCH_VALID_URLS_NUM = 3