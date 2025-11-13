from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
import sqlite3, os, logging
from datetime import datetime


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

# ------------------ FORMULARIO DE SUBIDA ------------------
class UploadForm(FlaskForm):
    file = FileField("Selecciona un archivo", validators=[DataRequired()])
    submit = SubmitField("Subir Archivo")

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

        c.execute("SELECT id FROM users WHERE username=?", (username,))
        if c.fetchone():
            flash('El usuario ya existe', 'danger')
            conn.close()
            return redirect(url_for('register'))

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
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')

    return render_template('login.html')

# ---------- DASHBOARD USUARIO ----------
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UploadForm()

    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("""
                INSERT INTO files (filename, user_id, uploaded_by, uploaded_at)
                VALUES (?, ?, ?, ?)
            """, (filename, current_user.id, current_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()

            logging.info(f'Archivo subido: {filename} por {current_user.username}')
            flash('Archivo subido correctamente', 'success')
            return redirect(url_for('dashboard'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT filename, uploaded_at FROM files WHERE user_id=?", (current_user.id,))
    files = c.fetchall()
    conn.close()

    return render_template('dashboard.html', files=files, form=form, title="Mi Unidad", page="inicio")

# ---------- PANEL ADMIN ----------
@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Acceso denegado. No tienes permisos de administrador.', 'danger')
        return redirect(url_for('dashboard'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Totales
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM files")
    total_files = c.fetchone()[0]

    # Si tienes logs, puedes contar, si no pon en 0
    total_logs = 0

    # Usuarios
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()

    # Archivos
    c.execute("""
        SELECT filename AS name, uploaded_by AS user, uploaded_at AS date
        FROM files
        ORDER BY uploaded_at DESC
    """)
    files = c.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_files=total_files,
        total_logs=total_logs,
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

# ------------------ CREAR BASE DE DATOS ------------------
def init_db():
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
            uploaded_by TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

# ------------------ MAIN ------------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
