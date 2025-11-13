from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3

# Creamos el blueprint
admin_bp = Blueprint('admin', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Acceso denegado. No tienes permisos de administrador.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
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
        files=files,
        title="Panel de Administración",
        page="admin"
    )
