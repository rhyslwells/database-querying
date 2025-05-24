import sqlite3

conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Enable foreign key support (important in SQLite)
cursor.execute("PRAGMA foreign_keys = ON;")

# Create 'users' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    city TEXT
)
''')

# Create 'products' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    price REAL NOT NULL
)
''')

# Create 'orders' table with foreign keys to users and products
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

# Insert sample data into users
cursor.executemany('''
INSERT OR IGNORE INTO users (user_id, name, email, city) VALUES (?, ?, ?, ?)
''', [
    (1, 'Alice', 'alice@example.com', 'New York'),
    (2, 'Bob', 'bob@example.com', 'Los Angeles'),
    (3, 'Charlie', 'charlie@example.com', 'Chicago'),
])

# Insert sample data into products
cursor.executemany('''
INSERT OR IGNORE INTO products (product_id, product_name, price) VALUES (?, ?, ?)
''', [
    (1, 'Laptop', 1200.00),
    (2, 'Smartphone', 800.00),
    (3, 'Headphones', 150.00),
])

# Insert sample data into orders
cursor.executemany('''
INSERT OR IGNORE INTO orders (order_id, user_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?, ?)
''', [
    (1, 1, 1, 1, '2025-05-20'),
    (2, 2, 2, 2, '2025-05-21'),
    (3, 1, 3, 1, '2025-05-22'),
    (4, 3, 1, 1, '2025-05-23'),
])

conn.commit()
conn.close()
