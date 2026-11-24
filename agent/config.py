import os
from dotenv import load_dotenv

load_dotenv()

SAAS_API_URL = os.getenv(
    "SAAS_API_URL",
    "http://localhost:8002"
)