
-- Drop old tables (dependent table first, since sales references products and employees)
DROP TABLE IF EXISTS ventes;
DROP TABLE IF EXISTS produits;
DROP TABLE IF EXISTS employes;
DROP TABLE IF EXISTS clients;

-- Recreate with English names
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    price_per_unit NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    department VARCHAR(64) NOT NULL,
    hire_date DATE NOT NULL,
    salary NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    segment VARCHAR(64) NOT NULL,
    city VARCHAR(64) NOT NULL,
    country VARCHAR(64) NOT NULL,
    registration_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    product_id INTEGER REFERENCES products(id) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    region VARCHAR(64) NOT NULL,
    employee_id INTEGER REFERENCES employees(id) NOT NULL
);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_sales_employee_id ON sales(employee_id);