-- =========================================
-- 🗃️ Base de Datos: DriveMe.Local
-- =========================================

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS logs;

-- =========================================
-- 👤 Tabla de usuarios
-- =========================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',      -- Puede ser 'user' o 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usuario administrador inicial
INSERT INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin');

-- =========================================
-- 📁 Archivos subidos por los usuarios
-- =========================================
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    user_id INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =========================================
-- 🧾 Registros de actividad
-- =========================================
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
