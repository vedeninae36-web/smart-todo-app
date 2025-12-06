import os
import sys
import sqlite3
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash

# Настройка пути для импорта из backend
backend_dir = os.path.dirname(__file__)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import DATABASE_PATH, init_db, populate_test_data

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Для flash-сообщений


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    filter_param = request.args.get('filter', 'all')

    # Получаем категории
    categories = conn.execute("SELECT * FROM categories").fetchall()

    # Формируем SQL-запрос в зависимости от фильтра
    if filter_param == 'active':
        tasks = conn.execute(
            """
            SELECT t.id, t.title, t.description, t.status, t.created_at,
                   c.id as category_id, c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.status != 'completed'
            ORDER BY t.created_at DESC
        """
        ).fetchall()
    elif filter_param == 'completed':
        tasks = conn.execute(
            """
            SELECT t.id, t.title, t.description, t.status, t.created_at,
                   c.id as category_id, c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.status = 'completed'
            ORDER BY t.created_at DESC
        """
        ).fetchall()
    else:  # all
        tasks = conn.execute(
            """
            SELECT t.id, t.title, t.description, t.status, t.created_at,
                   c.id as category_id, c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            ORDER BY t.created_at DESC
        """
        ).fetchall()

    # Статистика
    total = len(tasks)
    completed = len([t for t in tasks if t['status'] == 'completed'])
    active = total - completed

    conn.close()

    return render_template(
        'tasks_list.html',
        tasks=tasks,
        categories=categories,
        total_tasks=total,
        completed_tasks=completed,
        active_tasks=active,
        filter=filter_param,
    )


@app.route('/tasks', methods=['POST'])
def create_task():
    title = request.form.get('title')
    description = request.form.get('description', '')
    category_id = request.form.get('category_id') or None

    if not title:
        flash('Название задачи обязательно!', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (title, description, category_id, status)
        VALUES (?, ?, ?, ?)
    """,
        (title, description, category_id, 'pending'),
    )
    conn.commit()
    conn.close()

    flash('Задача успешно добавлена!', 'success')
    return redirect(url_for('index'))


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        flash('Задача не найдена!', 'danger')
        conn.close()
        return redirect(url_for('index'))

    new_status = 'completed' if task['status'] != 'completed' else 'pending'
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

    flash(f'Статус задачи изменён на "{new_status}"', 'info')
    return redirect(url_for('index'))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    flash('Задача удалена!', 'warning')
    return redirect(url_for('index'))


# --- API Endpoints (оставляем для совместимости) ---
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    conn = get_db_connection()
    tasks = conn.execute(
        """
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.created_at DESC
    """
    ).fetchall()
    conn.close()

    return jsonify(
        [
            {
                "id": t["id"],
                "title": t["title"],
                "description": t["description"],
                "status": t["status"],
                "created_at": t["created_at"],
                "category": (
                    {"id": t["category_id"], "name": t["category_name"]}
                    if t["category_id"]
                    else None
                ),
            }
            for t in tasks
        ]
    )


@app.route('/api/tasks', methods=['POST'])
def api_create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400

    title = data['title']
    description = data.get('description', '')
    category_id = data.get('category_id')
    status = data.get('status', 'pending')

    if status not in ('pending', 'in_progress', 'completed'):
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (title, description, category_id, status)
        VALUES (?, ?, ?, ?)
    """,
        (title, description, category_id, status),
    )
    task_id = cursor.lastrowid
    conn.commit()

    task = conn.execute(
        """
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """,
        (task_id,),
    ).fetchone()
    conn.close()

    return (
        jsonify(
            {
                "id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "status": task["status"],
                "created_at": task["created_at"],
                "category": (
                    {"id": task["category_id"], "name": task["category_name"]}
                    if task["category_id"]
                    else None
                ),
            }
        ),
        201,
    )


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def api_get_task(task_id):
    conn = get_db_connection()
    task = conn.execute(
        """
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """,
        (task_id,),
    ).fetchone()
    conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(
        {
            "id": task["id"],
            "title": task["title"],
            "description": task["description"],
            "status": task["status"],
            "created_at": task["created_at"],
            "category": (
                {"id": task["category_id"], "name": task["category_name"]}
                if task["category_id"]
                else None
            ),
        }
    )


if __name__ == '__main__':
    init_db()
    try:
        populate_test_data()
    except Exception as e:
        print(f"⚠️  Ошибка при заполнении тестовыми данными: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
