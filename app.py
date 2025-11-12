from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3, os, logging

app = Flask(__name__)
app.secret_key = 'drive_me_local_key'
bcrypt = Bcrypt(app)

# Configuración de subida de archivos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configurar logs en consola
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Configuración de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---- MODELO DE USUARIO ----
class User(UserMixin):
    def __init__(self, id_, username, password):
        self.id = id_
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

# ---- RUTAS ----
@app.route('/')
def index():
    return redirect(url_for('login'))

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        try:
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            logging.info(f'Nuevo usuario creado: {username}')
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('login'))
        except:
            flash('El usuario ya existe', 'danger')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            logging.info(f'Usuario inició sesión: {username}')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("INSERT INTO files (filename, owner) VALUES (?, ?)", (filename, current_user.username))
            conn.commit()
            conn.close()
            logging.info(f'Archivo subido: {filename} por {current_user.username}')
            flash('Archivo subido correctamente', 'success')

    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM files WHERE owner=?", (current_user.username,))
    files = c.fetchall()
    conn.close()
    return render_template('dashboard.html', files=files)

# Descargar archivos
@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Logout
@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logging.info(f'Usuario cerró sesión: {username}')
    return redirect(url_for('login'))

# Ejecutar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

