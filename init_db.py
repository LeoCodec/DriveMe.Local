import sqlite3
import logging

DATABASE = 'database.db'
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def init_db():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Tabla de usuarios con rol y fecha de creación
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de archivos con fecha, tamaño y ruta física
        c.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                user_id INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                physical_path TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Tabla de logs
        c.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logging.info("Base de datos inicializada correctamente (database.db)")
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {e}")

if __name__ == '__main__':
    logging.info("Ejecutando script init_db.py...")
    init_db()