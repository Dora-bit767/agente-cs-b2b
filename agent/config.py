import os
from dotenv import load_dotenv

load_dotenv()

SAAS_API_URL = os.getenv(
    "SAAS_API_URL",
    "http://localhost:8002"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "openai/gpt-oss-120b"
)

AGENT_MAX_ITERATIONS = int(
    os.getenv("AGENT_MAX_ITERATIONS", "10")
)