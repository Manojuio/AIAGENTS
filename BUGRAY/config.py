import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

MAX_AGENT_ITERATIONS = 5 # Maximum number of iterations for the bug fixing process
MAX_FILE_READ_CHARS = 10000 # Maximum number of characters to read from a file for context
