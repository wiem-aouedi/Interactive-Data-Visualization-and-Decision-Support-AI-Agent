from connections import engine
from faker import Faker
from sqlalchemy import text
import random

faker = Faker()

# Reset everything to a clean state before generating
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE sales, employees, products, clients RESTART IDENTITY"))
    conn.commit()

# --- EMPLOYEES ---
departments = ["Sales", "Marketing", "IT", "HR", "Finance"]
employees_ids = []
with engine.connect() as conn:
    for _ in range(100):
        result = conn.execute(text("""
            INSERT INTO employees (name, department, hire_date, salary)
            VALUES (:name, :department, :hire_date, :salary)
            RETURNING id
        """), {
            "name": faker.name(),
            "department": random.choice(departments),
            "hire_date": faker.date_between(start_date="-10y", end_date="today"),
            "salary": round(random.uniform(2500, 8000), 2)
        })
        employees_ids.append(result.scalar())
    conn.commit()
    print(f"{len(employees_ids)} employees created")

# --- PRODUCTS ---
categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
products_ids = []
with engine.connect() as conn:
    for _ in range(400):
        category = random.choice(categories)
        result = conn.execute(text("""
            INSERT INTO products (name, category, price_per_unit, stock)
            VALUES (:name, :category, :price_per_unit, :stock)
            RETURNING id
        """), {
            "name": f"{faker.word().capitalize()} {category}",
            "category": category,
            "price_per_unit": round(random.uniform(10, 500), 2),
            "stock": random.randint(1, 200)
        })
        products_ids.append(result.scalar())
    conn.commit()
    print(f"{len(products_ids)} products created")

# --- CLIENTS ---
segments = ["Retail", "Wholesale", "Enterprise", "SMB"]
clients_ids = []
with engine.connect() as conn:
    for _ in range(6000):
        result = conn.execute(text("""
            INSERT INTO clients (name, segment, city, country, registration_date)
            VALUES (:name, :segment, :city, :country, :registration_date)
            RETURNING id
        """), {
            "name": faker.name(),
            "segment": random.choice(segments),
            "city": faker.city(),
            "country": faker.country(),
            "registration_date": faker.date_between(start_date="-8y", end_date="today")
        })
        clients_ids.append(result.scalar())
    conn.commit()
    print(f"{len(clients_ids)} clients created")

# --- SALES ---
regions = ["North", "South", "East", "West", "Central"]
sales_ids = []
with engine.connect() as conn:
    for _ in range(35000):
        result = conn.execute(text("""
            INSERT INTO sales (sale_date, product_id, amount, quantity, region, employee_id)
            VALUES (:sale_date, :product_id, :amount, :quantity, :region, :employee_id)
            RETURNING id
        """), {
            "sale_date": faker.date_between(start_date="-3y", end_date="today"),
            "product_id": random.choice(products_ids),
            "amount": round(random.uniform(20, 5000), 2),
            "quantity": random.randint(1, 20),
            "region": random.choice(regions),
            "employee_id": random.choice(employees_ids)
        })
        sales_ids.append(result.scalar())
    conn.commit()
    print(f"{len(sales_ids)} sales created")