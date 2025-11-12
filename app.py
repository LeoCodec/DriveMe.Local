from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3, os, logging

# ------------------ CONFIGURACIÓN GENERAL ------------------
app = Flask(__name__)
app.secret_key = 'drive_me_local_key'
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# ------------------ LOGIN MANAGER ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------ MODELO DE USUARIO ------------------
class User(UserMixin):
    def __init__(self, id_, username, password, role='user'):
        self.id = id_
        self.username = username
        self.password = password
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password, role FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

# ------------------ RUTAS ------------------

@app.route('/')
def index():
    return redirect(url_for('login'))

# ---------- REGISTRO ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Evita duplicados
        c.execute("SELECT id FROM users WHERE username=?", (username,))
        if c.fetchone():
            flash('El usuario ya existe', 'danger')
            conn.close()
            return redirect(url_for('register'))

        # Inserta usuario normal por defecto
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'user'))
        conn.commit()
        conn.close()

        logging.info(f'Nuevo usuario creado: {username}')
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):
            user_obj = User(*user)
            login_user(user_obj)
            logging.info(f'Usuario inició sesión: {username}')

            if user_obj.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')

    return render_template('login.html')

# ---------- DASHBOARD USUARIO ----------
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO files (filename, user_id) VALUES (?, ?)", (filename, current_user.id))
            conn.commit()
            conn.close()
            logging.info(f'Archivo subido: {filename} por {current_user.username}')
            flash('Archivo subido correctamente', 'success')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM files WHERE user_id=?", (current_user.id,))
    files = c.fetchall()
    conn.close()

    return render_template('dashboard.html', files=files)

# ---------- PANEL ADMIN ----------
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Acceso denegado. No tienes permisos de administrador.', 'danger')
        return redirect(url_for('dashboard'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Totales
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM files")
    total_files = c.fetchone()[0]

    # Listado de usuarios
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()

    # Listado de archivos
    c.execute("""
        SELECT f.id, f.filename, u.username 
        FROM files f 
        JOIN users u ON f.user_id = u.id
    """)
    files = c.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_files=total_files,
        users=users,
        files=files
    )

# ---------- DESCARGAR ARCHIVO ----------
@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ---------- LOGOUT ----------
@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logging.info(f'Usuario cerró sesión: {username}')
    return redirect(url_for('login'))

# ------------------ MAIN ------------------
if __name__ == '__main__':
    # Asegura que la base de datos exista con columnas necesarias
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000, debug=True)
class User(UserMixin):
    def __init__(self, id_, username, password, role='user'):
        self.id = id_
        self.username = username
        self.password = password
        self.role = role