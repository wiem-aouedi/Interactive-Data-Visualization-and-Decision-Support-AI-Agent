from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
from database.connections import readonly_engine

# LangChain's SQLDatabase wraps the SQLAlchemy engine and reflects
# the real schema (tables, columns, foreign keys) into a description
# string. This is the CDC-required mechanism for providing schema
# context to the LLM. sample_rows_in_table_info=0 keeps actual row
# data out of the prompt, so it's just structure.
db = SQLDatabase(engine=readonly_engine, sample_rows_in_table_info=0)

# Computed once at import — static prefix, good for prompt caching.
SCHEMA_DESCRIPTION = db.get_table_info()

llm = ChatOpenAI(
    model=AZURE_OPENAI_DEPLOYMENT,
    api_key=AZURE_OPENAI_API_KEY,
    base_url=AZURE_OPENAI_ENDPOINT.rstrip("/") + "/openai/v1",
    model_kwargs={"max_completion_tokens": 500},
)

SYSTEM_PROMPT = """You are a PostgreSQL expert. Convert the user's question into a single, valid, read-only SQL query.

Database schema:
{schema}

Rules:
- Only generate SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, ALTER, or any other data-modifying statement.
- Only use the tables and columns listed in the schema above. Never invent column or table names.
- Only join tables using the exact foreign key relationships listed in the schema above. Never join two tables that have no listed foreign key relationship, even if their column names seem related.
- Return ONLY the raw SQL query. No explanations, no markdown formatting, no code fences.
- If the question cannot be answered with the given schema, respond with exactly: NO_QUERY

Example:
Question: "What are the top 5 clients by total sales?"
The sales table has no foreign key to clients (only to employees and products), so this cannot be answered.
Correct response: NO_QUERY
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

chain = prompt_template | llm


def clean_sql_response(raw_sql: str) -> str:
    cleaned = raw_sql.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("sql"):
            cleaned = cleaned[3:].strip()
    if cleaned.upper().rstrip(";") == "NO_QUERY":
        return "NO_QUERY"
    return cleaned.rstrip(";") + ";"


def generate_sql(question: str) -> str:
    response = chain.invoke({
        "schema": SCHEMA_DESCRIPTION,
        "question": question
    })
    return clean_sql_response(response.content)