import os
import sys
import sqlite3
from flask import Flask, request, jsonify

# Добавляем папку backend в путь, чтобы импортировать database.py
backend_dir = os.path.dirname(__file__)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Теперь импортируем без точки
from database import DATABASE_PATH

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute("""
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.created_at DESC
    """).fetchall()
    conn.close()

    return jsonify([
        {
            "id": t["id"],
            "title": t["title"],
            "description": t["description"],
            "status": t["status"],
            "created_at": t["created_at"],
            "category": {"id": t["category_id"], "name": t["category_name"]} if t["category_id"] else None
        }
        for t in tasks
    ])

@app.route('/api/tasks', methods=['POST'])
def create_task():
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
    cursor.execute("""
        INSERT INTO tasks (title, description, category_id, status)
        VALUES (?, ?, ?, ?)
    """, (title, description, category_id, status))
    task_id = cursor.lastrowid
    conn.commit()

    # Получаем созданную задачу
    task = conn.execute("""
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (task_id,)).fetchone()
    conn.close()

    return jsonify({
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"],
        "category": {"id": task["category_id"], "name": task["category_name"]} if task["category_id"] else None
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    task = conn.execute("""
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (task_id,)).fetchone()
    conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"],
        "category": {"id": task["category_id"], "name": task["category_name"]} if task["category_id"] else None
    })

if __name__ == '__main__':
    # Инициализация БД при запуске
    from database import init_db, populate_test_data
    init_db()
    # Заполним тестовыми данными один раз
    try:
        populate_test_data()
    except:
        pass  # игнорируем, если данные уже есть

    app.run(debug=True, host='0.0.0.0', port=5000)