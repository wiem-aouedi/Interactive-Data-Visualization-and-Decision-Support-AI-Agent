import re

def is_safe_query(sql_query):
    # Define a list of potentially dangerous SQL keywords
    dangerous_keywords = [
        r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bALTER\b",
        r"\bUPDATE\b", r"\bINSERT\b", r"\bEXECUTE\b", r"\bEXEC\b",
        r"\bMERGE\b", r"\bREPLACE\b", r"\bCREATE\b", r"\bGRANT\b",
        r"\bREVOKE\b", r"\bCOMMIT\b", r"\bROLLBACK\b"
    ]
    
    # Check if any dangerous keyword is present in the query
    for keyword in dangerous_keywords:
        if re.search(keyword, sql_query, re.IGNORECASE):
            return False  # Query is not safe
    
    return True  # Query is safe

test_queries = [
    ("SELECT * FROM products", True),
    ("DELETE FROM employees", False),
    ("SELECT * FROM products WHERE category = 'Deleted Items'", True),
    ("select * from clients", True),
    ("update products set stock = 0", False),
    ("SELECT updated_at FROM sales", True),
    ("SELECT * FROM products; DROP TABLE products;", False),
    ("DROP TABLE employees", False),
    ("SELECT * FROM sales JOIN products ON sales.product_id = products.id", True),
]

for query, expected in test_queries:
    result = is_safe_query(query)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status} | Expected: {expected}, Got: {result} | Query: {query}")