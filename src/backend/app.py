from flask import Flask, request, jsonify
import sqlite3
import os

# Импортируем функции из database.py
from .database import DATABASE_PATH

app = Flask(__name__)

# Вспомогательная функция для подключения к БД
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам по имени
    return conn

# Эндпоинт: GET /api/tasks — получить все задачи
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.created_at DESC
    """)
    tasks = cursor.fetchall()
    conn.close()

    # Преобразуем результат в список словарей
    tasks_list = [
        {
            "id": task["id"],
            "title": task["title"],
            "description": task["description"],
            "status": task["status"],
            "created_at": task["created_at"],
            "category": {
                "id": task["category_id"],
                "name": task["category_name"]
            } if task["category_id"] else None
        }
        for task in tasks
    ]

    return jsonify(tasks_list), 200


# Эндпоинт: POST /api/tasks — создать новую задачу
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    # Проверяем обязательные поля
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400

    title = data.get('title')
    description = data.get('description', '')
    category_id = data.get('category_id')  # Может быть None
    status = data.get('status', 'pending')

    # Валидация статуса
    valid_statuses = ['pending', 'in_progress', 'completed']
    if status not in valid_statuses:
        return jsonify({"error": f"Status must be one of: {valid_statuses}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO tasks (title, description, category_id, status)
            VALUES (?, ?, ?, ?)
        """, (title, description, category_id, status))

        task_id = cursor.lastrowid
        conn.commit()

        # Получаем созданную задачу с категорией
        cursor.execute("""
            SELECT t.id, t.title, t.description, t.status, t.created_at,
                   c.id as category_id, c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?
        """, (task_id,))
        new_task = cursor.fetchone()
        conn.close()

        if new_task:
            response = {
                "id": new_task["id"],
                "title": new_task["title"],
                "description": new_task["description"],
                "status": new_task["status"],
                "created_at": new_task["created_at"],
                "category": {
                    "id": new_task["category_id"],
                    "name": new_task["category_name"]
                } if new_task["category_id"] else None
            }
            return jsonify(response), 201
        else:
            return jsonify({"error": "Task created but not found"}), 500

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500


# Эндпоинт: GET /api/tasks/<id> — получить задачу по ID
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.title, t.description, t.status, t.created_at,
               c.id as category_id, c.name as category_name
        FROM tasks t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (task_id,))
    task = cursor.fetchone()
    conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    response = {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"],
        "category": {
            "id": task["category_id"],
            "name": task["category_name"]
        } if task["category_id"] else None
    }

    return jsonify(response), 200


# Запуск приложения (для отладки)
if __name__ == '__main__':
    from .database import init_db
    init_db()  # Убедимся, что БД инициализирована
    app.run(debug=True, host='0.0.0.0', port=5000)