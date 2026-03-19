import sqlite3
from werkzeug.security import generate_password_hash

# Connect to SQLite database (creates ems.db if not exists)
conn = sqlite3.connect('ems.db')
cursor = conn.cursor()

# Create users table for admin
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# Create employees table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        position TEXT NOT NULL
    )
''')

# Insert admin user (username: admin, password: admin123)
cursor.execute('''
    INSERT OR IGNORE INTO users (username, password)
    VALUES (?, ?)
''', ('admin', generate_password_hash('admin123')))

# Insert sample employees
cursor.execute('''
    INSERT OR IGNORE INTO employees (name, email, phone, position)
    VALUES
        ('Amit Sharma', 'amit@example.com', '9876543210', 'Developer'),
        ('Priya Singh', 'priya@example.com', '8765432109', 'Designer'),
        ('Rahul Verma', 'rahul@example.com', '7654321098', 'Manager')
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized successfully!")