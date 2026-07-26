import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from api.schemas import ChatRequest, ChatResponse
import time
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai import OpenAI
import logging 


env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/") + "/openai/v1"
)
api_logger = logging.getLogger("api_requests")
api_logger.setLevel(logging.INFO)
handler = logging.FileHandler("api_requests.log")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
api_logger.addHandler(handler)
def get_llm_response(question: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

def call_llm_with_retry(question: str) -> str:
    for attempt in range(3):
        try:
            return get_llm_response(question)
        except Exception as e:
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            if attempt < 2:
                time.sleep(wait_time)
    raise RuntimeError("The AI service is temporarily unavailable. Please try again later.")
            
@router.post("/api/chat", response_model=ChatResponse)
@limiter.limit("50/minute")
def chat(request: Request, chat_request: ChatRequest):
    start_time = time.time()
    try:
        answer = call_llm_with_retry(chat_request.question)
        duration = time.time() - start_time
        api_logger.info(
            f"Chat request succeeded | question: {chat_request.question} | "
            f"duration: {duration:.2f}s | tokens: N/A (pending real LLM response)"
        )
        return ChatResponse(message=answer)
    except RuntimeError as e:
        duration = time.time() - start_time
        api_logger.error(
            f"Chat request failed | question: {chat_request.question} | "
            f"duration: {duration:.2f}s | error: {e}"
        )
        return ChatResponse(message=str(e))