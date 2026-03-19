from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'super-secret-key-123'  # Required for flash messages and sessions

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('ems.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route redirects to login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Admin login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

# Middleware to check if user is logged in
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# Dashboard (shows employee list)
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return render_template('dashboard.html', employees=employees)

# Add employee
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        if not name or not email or not phone or not position:
            flash('All fields are required', 'danger')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO employees (name, email, phone, position) VALUES (?, ?, ?, ?)',
                         (name, email, phone, position))
            conn.commit()
            conn.close()
            flash('Employee added successfully', 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_employee.html')

# Edit employee
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (id,)).fetchone()
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        if not name or not email or not phone or not position:
            flash('All fields are required', 'danger')
        else:
            conn.execute('UPDATE employees SET name = ?, email = ?, phone = ?, position = ? WHERE id = ?',
                         (name, email, phone, position, id))
            conn.commit()
            conn.close()
            flash('Employee updated successfully', 'success')
            return redirect(url_for('dashboard'))
    conn.close()
    return render_template('edit_employee.html', employee=employee)

# Delete employee
@app.route('/delete/<int:id>')
@login_required
def delete_employee(id):
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (id,)).fetchone()
    if not employee:
        flash('Employee not found', 'danger')
    else:
        conn.execute('DELETE FROM employees WHERE id = ?', (id,))
        conn.commit()
        flash('Employee deleted successfully', 'success')
    conn.close()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)