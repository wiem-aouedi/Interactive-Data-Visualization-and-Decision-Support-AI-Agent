from database.connections import readonly_engine
from sqlalchemy import text


def execute_query(sql_query):
    try:
        with readonly_engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            return {"success": True, "data": rows, "error": None}
    except Exception as e:
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

    corrected_query = correction_function(sql_query, result["error"])
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