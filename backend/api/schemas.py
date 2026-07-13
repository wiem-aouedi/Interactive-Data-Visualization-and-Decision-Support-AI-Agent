from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str = Field(..., max_length=500, min_length=10)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
class ChatResponse(BaseModel):
    message: str
    sql_query: Optional[str] = None
    data: Optional[list] = None
    chart_config: Optional[dict] = None
    suggestions: Optional[list] = None