from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_diploma'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT tasks.id, tasks.title, tasks.planned_date, tasks.status, devices.name as device_name 
        FROM tasks 
        JOIN devices ON tasks.device_id = devices.id
        ORDER BY tasks.planned_date ASC
    ''').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Неправильні дані!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/add', methods=['GET', 'POST'])
def add_task():
    if not session.get('logged_in') or session.get('role') != 'admin': return "Доступ заборонено!", 403
    conn = get_db_connection()
    if request.method == 'POST':
        device_id = request.form['device_id']
        title = request.form['title']
        planned_date = request.form['planned_date']
        checklist_raw = request.form['checklist_items']
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (device_id, title, planned_date, status) VALUES (?, ?, ?, "В очікуванні")', (device_id, title, planned_date))
        task_id = cursor.lastrowid
        items = [item.strip() for item in checklist_raw.split('\n') if item.strip()]
        for item in items: cursor.execute('INSERT INTO checklist_items (task_id, item_text, is_done) VALUES (?, ?, 0)', (task_id, item))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    devices = conn.execute('SELECT * FROM devices').fetchall()
    conn.close()
    return render_template('admin.html', devices=devices)

@app.route('/admin/add_device', methods=['POST'])
def add_device():
    if not session.get('logged_in') or session.get('role') != 'admin': return "Доступ заборонено!", 403
    device_name = request.form['device_name']
    location = request.form['location']
    if device_name and location:
        conn = get_db_connection()
        conn.execute('INSERT INTO devices (name, location) VALUES (?, ?)', (device_name, location))
        conn.commit()
        conn.close()
    return redirect(url_for('add_task'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if not session.get('logged_in') or session.get('role') != 'admin': return "Доступ заборонено!", 403
    conn = get_db_connection()
    conn.execute('DELETE FROM checklist_items WHERE task_id = ?', (task_id,))
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
def task_detail(task_id):
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('UPDATE checklist_items SET is_done = 0 WHERE task_id = ?', (task_id,))
        for item_id in request.form.getlist('checklist'):
            conn.execute('UPDATE checklist_items SET is_done = 1 WHERE id = ?', (item_id,))
        conn.execute('UPDATE tasks SET status = "Виконано" WHERE id = ?', (task_id,))
        conn.commit()
        return redirect(url_for('index'))
    task = conn.execute('SELECT tasks.*, devices.name as device_name, devices.location FROM tasks JOIN devices ON tasks.device_id = devices.id WHERE tasks.id = ?', (task_id,)).fetchone()
    items = conn.execute('SELECT * FROM checklist_items WHERE task_id = ?', (task_id,)).fetchall()
    conn.close()
    return render_template('task.html', task=task, items=items)

if __name__ == '__main__': app.run(debug=True, port=5000)