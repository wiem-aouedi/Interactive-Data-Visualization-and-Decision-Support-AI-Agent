from fastapi import APIRouter, Request
from api.schemas import ChatRequest, ChatResponse
import time
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def get_llm_response(question: str) -> str:
    return f"Mock response to: {question}"

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
    try :
        answer = call_llm_with_retry(chat_request.question)
        return ChatResponse(
            message=answer
        )
    except RuntimeError as e:
        return ChatResponse(message=str(e))
