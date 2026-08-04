import time
import logging
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.schemas import ChatRequest, ChatResponse
from agent.text_to_sql import generate_sql, generate_corrected_sql
from agent.sql_validator import is_safe_query, contains_prompt_injection
from agent.query_executor import run_with_correction

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

api_logger = logging.getLogger("api_requests")
api_logger.setLevel(logging.INFO)
handler = logging.FileHandler("api_requests.log")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
api_logger.addHandler(handler)


def call_with_retry(fn, *args, retries=3):
    for attempt in range(retries):
        try:
            return fn(*args)
        except Exception as e:
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            if attempt < retries - 1:
                time.sleep(wait_time)
    raise RuntimeError("The AI service is temporarily unavailable. Please try again later.")


@router.post("/api/chat", response_model=ChatResponse)
@limiter.limit("50/minute")
def chat(request: Request, chat_request: ChatRequest):
    start_time = time.time()
    question = chat_request.question

    if contains_prompt_injection(question):
        api_logger.warning(f"Blocked question (prompt injection) | question: {question}")
        return ChatResponse(message="I can't process that question. Please rephrase it.")

    try:
        sql_query = call_with_retry(generate_sql, question)

        if sql_query == "NO_QUERY":
            duration = time.time() - start_time
            api_logger.info(f"No query generated | question: {question} | duration: {duration:.2f}s")
            return ChatResponse(message="I couldn't answer that from the available data. Could you rephrase your question?")

        if not is_safe_query(sql_query):
            api_logger.warning(f"Blocked unsafe SQL | question: {question} | sql: {sql_query}")
            return ChatResponse(message="I can't run that query for safety reasons. Please rephrase your question.")

        result = run_with_correction(sql_query, correction_function=generate_corrected_sql)
        duration = time.time() - start_time

        if not result["success"]:
            api_logger.error(
                f"Query failed (including after auto-correction) | question: {question} | "
                f"original_sql: {sql_query} | attempted_sql: {result['sql_query']} | "
                f"duration: {duration:.2f}s | error: {result['error']}"
            )
            return ChatResponse(message=result["error"], sql_query=result["sql_query"])

        if result["sql_query"] != sql_query:
            api_logger.info(
                f"Chat request succeeded after auto-correction | question: {question} | "
                f"original_sql: {sql_query} | corrected_sql: {result['sql_query']} | duration: {duration:.2f}s"
            )
        else:
            api_logger.info(f"Chat request succeeded | question: {question} | sql: {sql_query} | duration: {duration:.2f}s")

        return ChatResponse(
            message="Here's what I found.",
            sql_query=result["sql_query"],
            data=[dict(row._mapping) for row in result["data"]]
        )

    except RuntimeError as e:
        duration = time.time() - start_time
        api_logger.error(f"Chat request failed | question: {question} | duration: {duration:.2f}s | error: {e}")
        return ChatResponse(message=str(e))