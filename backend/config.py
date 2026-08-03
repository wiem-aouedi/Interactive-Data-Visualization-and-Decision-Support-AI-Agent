import os
from dotenv import load_dotenv
from openai import OpenAI

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)       

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
    raise RuntimeError("Missing Azure OpenAI configuration in .env")
client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT.rstrip("/") + "/openai/v1"
)
