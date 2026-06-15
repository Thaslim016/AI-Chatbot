import sqlite3

conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS users")

cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# Create an admin user
cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
               ("admin", "password123", "admin"))

# You can add regular users too
cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
               ("student", "test", "user"))

conn.commit()
conn.close()
