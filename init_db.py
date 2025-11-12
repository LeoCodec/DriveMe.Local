import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Crear usuario admin
admin_username = "admin"
admin_password = "admin123"
hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')

cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (admin_username, hashed_pw, "admin"))
    print("✅ Usuario administrador creado: admin / admin123")
else:
    print("ℹ️ El usuario admin ya existe.")

# Crear usuario Leo Cruz
user_username = "Leo Cruz"
user_password = "leocruz123"
hashed_user_pw = bcrypt.generate_password_hash(user_password).decode('utf-8')

cursor.execute("SELECT * FROM users WHERE username = ?", (user_username,))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (user_username, hashed_user_pw, "user"))
    print("✅ Usuario creado: Leo Cruz / leocruz123")
else:
    print("ℹ️ El usuario Leo Cruz ya existe.")

conn.commit()
conn.close()
