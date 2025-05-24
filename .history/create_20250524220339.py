import streamlit as st
import sqlite3
import pandas as pd

st.title("SQLite Database Builder & Query Interface")

@st.cache_resource
def get_connection():
    conn = sqlite3.connect('my_database.db', check_same_thread=False)
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_and_seed_db(conn):
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
    )
    ''')

    # Check if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO users (user_id, name, email, city) VALUES (?, ?, ?, ?)
        ''', [
            (1, 'Alice', 'alice@example.com', 'New York'),
            (2, 'Bob', 'bob@example.com', 'Los Angeles'),
            (3, 'Charlie', 'charlie@example.com', 'Chicago'),
        ])

    # Check if products table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO products (product_id, product_name, price) VALUES (?, ?, ?)
        ''', [
            (1, 'Laptop', 1200.00),
            (2, 'Smartphone', 800.00),
            (3, 'Headphones', 150.00),
        ])

    # Check if orders table is empty
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO orders (order_id, user_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 1, 1, 1, '2025-05-20'),
            (2, 2, 2, 2, '2025-05-21'),
            (3, 1, 3, 1, '2025-05-22'),
            (4, 3, 1, 1, '2025-05-23'),
        ])

    conn.commit()


conn = get_connection()
create_and_seed_db(conn)

# Default example query using JOIN across tables
default_query = '''
SELECT o.order_id, u.name AS user_name, p.product_name, o.quantity, o.order_date
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN products p ON o.product_id = p.product_id
LIMIT 10
'''

query = st.text_area("Enter your SQL query:", default_query)

if st.button("Run Query"):
    try:
        df = pd.read_sql_query(query, conn)
        st.dataframe(df)
        st.success(f"Query executed successfully, {len(df)} rows returned.")
    except Exception as e:
        st.error(f"Error executing query: {e}")
