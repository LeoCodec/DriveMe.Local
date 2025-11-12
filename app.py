from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import sqlite3, os, logging, datetime

# ------------------ CONFIGURACIÓN GENERAL ------------------
app = Flask(__name__)
app.secret_key = 'drive_me_local_key'
bcrypt = Bcrypt(app)

# Carpetas de subida
UPLOAD_FOLDER_USER = 'uploads'
UPLOAD_FOLDER_ADMIN = 'uploads_admin'
os.makedirs(UPLOAD_FOLDER_USER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_ADMIN, exist_ok=True)

app.config['UPLOAD_FOLDER_USER'] = UPLOAD_FOLDER_USER
app.config['UPLOAD_FOLDER_ADMIN'] = UPLOAD_FOLDER_ADMIN

# Logs
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

# ------------------ CONEXIÓN BASE DE DATOS ------------------
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ REGISTRO ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (username,))
        if c.fetchone():
            flash('El usuario ya existe', 'danger')
            conn.close()
            return redirect(url_for('register'))

        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'user'))
        conn.commit()
        c.execute("INSERT INTO logs (event, timestamp) VALUES (?, ?)", 
                  (f'Nuevo usuario creado: {username}', datetime.datetime.now()))
        conn.commit()
        conn.close()

        logging.info(f'Nuevo usuario creado: {username}')
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ------------------ LOGIN ------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['password'], user['role'])
            login_user(user_obj)

            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO logs (event, timestamp) VALUES (?, ?)", 
                      (f'Usuario inició sesión: {username}', datetime.datetime.now()))
            conn.commit()
            conn.close()

            if user_obj.role == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')

    return render_template('login.html')

# ------------------ DASHBOARD (USUARIO NORMAL) ------------------
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_USER'], filename))

            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO files (filename, uploaded_by, uploaded_at) VALUES (?, ?, ?)",
                      (filename, current_user.username, datetime.datetime.now()))
            c.execute("INSERT INTO logs (event, timestamp) VALUES (?, ?)",
                      (f'Archivo subido: {filename} por {current_user.username}', datetime.datetime.now()))
            conn.commit()
            conn.close()

            flash('Archivo subido correctamente', 'success')

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT filename, uploaded_at FROM files WHERE uploaded_by=?", (current_user.username,))
    files = c.fetchall()
    conn.close()

    return render_template('dashboard.html', files=files)

# ------------------ PANEL ADMIN ------------------
@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Acceso denegado. No tienes permisos de administrador.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM files")
    total_files = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs")
    total_logs = cursor.fetchone()[0]

    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT filename, uploaded_by, uploaded_at FROM files")
    files = cursor.fetchall()

    cursor.execute("SELECT event, timestamp FROM logs ORDER BY id DESC LIMIT 20")
    logs = cursor.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_files=total_files,
        total_logs=total_logs,
        users=users,
        files=files,
        logs=logs
    )

# ------------------ SUBIDA ARCHIVOS ADMIN ------------------
@app.route("/admin/upload", methods=["POST"])
@login_required
def admin_upload():
    if current_user.role != "admin":
        flash("Acceso denegado", "danger")
        return redirect(url_for("dashboard"))

    file = request.files.get("file")
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER_ADMIN"], filename))

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO logs (event, timestamp) VALUES (?, ?)", 
                  (f'Archivo de admin subido: {filename}', datetime.datetime.now()))
        conn.commit()
        conn.close()

    return redirect(url_for("admin_panel"))

# ------------------ DESCARGAR ARCHIVO ------------------
@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_USER'], filename, as_attachment=True)

# ------------------ LOGOUT ------------------
@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO logs (event, timestamp) VALUES (?, ?)",
              (f'Usuario cerró sesión: {username}', datetime.datetime.now()))
    conn.commit()
    conn.close()

    logging.info(f'Usuario cerró sesión: {username}')
    return redirect(url_for('login'))

# ------------------ MAIN ------------------
if __name__ == '__main__':
    conn = get_db()
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
            uploaded_by TEXT,
            uploaded_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000, debug=True)
# ------------------ FIN DEL CÓDIGO ------------------