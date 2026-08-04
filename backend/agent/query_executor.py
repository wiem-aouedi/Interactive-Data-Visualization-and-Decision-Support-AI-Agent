from database.connections import readonly_engine
from agent.sql_validator import is_safe_query, uses_only_authorized_tables
from sqlalchemy import text
import re
import logging
 


logging.basicConfig(
    filename="query_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def add_limit_if_missing(sql_query, max_rows=1000):
    if re.search(r'\bLIMIT\b', sql_query, re.IGNORECASE):
        return sql_query  # already has one, leave it alone
    return sql_query.rstrip().rstrip(';') + f" LIMIT {max_rows};"

def execute_query(sql_query):
    try:
        sql_query = add_limit_if_missing(sql_query)
        with readonly_engine.connect().execution_options(postgresql_readonly=True) as conn:
            conn.execute(text("SET statement_timeout = 10000"))
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            logging.info(f"Query succeeded| role: readonly_user | sql: {sql_query}")
            return {"success": True, "data": rows, "error": None}
    except Exception as e:
        logging.error(f"Query failed| role: readonly_user | sql: {sql_query} | error: {e}")
        return {"success": False, "data": None, "error": str(e)}


def mock_correct_sql(broken_sql, error_message):
    # Placeholder: pretend the "corrected" query fixes the problem
    return "SELECT * FROM products LIMIT 3"


def mock_correct_sql_still_broken(broken_sql, error_message):
    # Testing-only: simulates a correction attempt that still fails
    return "SELECT still_broken_column FROM products"


def run_with_correction(sql_query, correction_function=mock_correct_sql):
    result = execute_query(sql_query)
    if result["success"]:
        return {
            "success": True,
            "data": result["data"],
            "sql_query": sql_query,
            "error": None
        }

    try:
        corrected_query = correction_function(sql_query, result["error"])
    except Exception as e:
        logging.error(f"Correction attempt raised an exception | original_sql: {sql_query} | error: {e}")
        return {
            "success": False,
            "data": None,
            "sql_query": sql_query,
            "error": "I couldn't generate a valid query for that question. Could you try rephrasing it?"
        }

    if corrected_query == "NO_QUERY" or not is_safe_query(corrected_query) or not uses_only_authorized_tables(corrected_query):
        return {
            "success": False,
            "data": None,
            "sql_query": corrected_query,
            "error": "I couldn't generate a valid query for that question. Could you try rephrasing it?"
        }

    corrected_result = execute_query(corrected_query)

    if corrected_result["success"]:
        return {
            "success": True,
            "data": corrected_result["data"],
            "sql_query": corrected_query,
            "error": None
        }

    return {
        "success": False,
        "data": None,
        "sql_query": corrected_query,
        "error": "I couldn't generate a valid query for that question. Could you try rephrasing it?"
    }

def format_result_for_user(result):
    if not result["success"]:
        return result  # already has a clear error message, nothing to add

    if len(result["data"]) == 0:
        result["message"] = "No results found for that question. Try rephrasing or asking about a different time period or category."
        return result

    return result  # has real data, nothing to change







if __name__ == "__main__":
    print("Path 1: succeeds immediately")
    print(run_with_correction("SELECT * FROM products LIMIT 3"))

    print("\nPath 2: fails, correction succeeds")
    print(run_with_correction("SELECT nonexistent_column FROM products"))

    print("\nPath 3: fails, correction also fails")
    print(run_with_correction(
        "SELECT nonexistent_column FROM products",
        correction_function=mock_correct_sql_still_broken
    ))
    print("Test: LIMIT auto-added when missing")
    print(add_limit_if_missing("SELECT * FROM sales"))

    print("\nTest: LIMIT left untouched when already present")
    print(add_limit_if_missing("SELECT * FROM products LIMIT 5"))
    print("\nTest: execute_query respects the auto-added LIMIT")
    result = execute_query("SELECT * FROM sales")
    print(f"Rows returned: {len(result['data'])}")
    print("\nTest: timeout triggers on a deliberately slow query")
    result = execute_query("SELECT pg_sleep(15)")
    print(result)
    print("\nTest: format_result_for_user with empty results")
    empty_result = run_with_correction("SELECT * FROM sales WHERE region = 'Antarctica'")
    print(format_result_for_user(empty_result))

    print("\nTest: format_result_for_user with real results")
    real_result = run_with_correction("SELECT * FROM products LIMIT 3")
    print(format_result_for_user(real_result))