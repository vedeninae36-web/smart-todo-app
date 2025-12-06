import os
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path

# Настройка приложения
base_dir = Path(__file__).parent.resolve()
template_dir = base_dir / "templates"

app = Flask(__name__, template_folder=str(template_dir))

# Глобальное хранилище задач
tasks = []


def get_next_id():
    """Возвращает следующий уникальный ID для задачи"""
    return max((t["id"] for t in tasks), default=0) + 1


def find_task_by_id(task_id):
    """Находит задачу по ID или возвращает None"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def get_filtered_tasks(filter_type):
    """Возвращает список задач в зависимости от фильтра"""
    if filter_type == "active":
        return [t for t in tasks if not t["completed"]]
    elif filter_type == "completed":
        return [t for t in tasks if t["completed"]]
    else:
        return tasks


def get_stats():
    """Возвращает статистику по задачам"""
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    active = total - completed
    return {"total": total, "completed": completed, "active": active}


@app.route("/")
def index():
    """Главная страница — отображает список задач"""
    filter_type = request.args.get("filter", "all")
    displayed_tasks = get_filtered_tasks(filter_type)
    stats = get_stats()
    return render_template(
        "tasks_list.html",
        tasks=displayed_tasks,
        current_filter=filter_type,
        stats=stats,
    )


@app.route("/tasks", methods=["POST"])
def create_task():
    """Создаёт новую задачу"""
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "low")
    if title:
        tasks.append(
            {
                "id": get_next_id(),
                "title": title,
                "priority": priority,
                "completed": False,
            }
        )
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """Переключает статус задачи (выполнено/активно)"""
    task = find_task_by_id(task_id)
    if task:
        task["completed"] = not task["completed"]
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    """Удаляет задачу по ID"""
    task = find_task_by_id(task_id)
    if task:
        tasks.remove(task)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Инициализация тестовой задачи
    if not tasks:
        tasks.append(
            {
                "id": 1,
                "title": "✅ Всё работает!",
                "priority": "medium",
                "completed": False,
            }
        )
    
    # Получаем порт от Render (или 5000 локально)
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_ENV") == "production"
    
    # Запускаем приложение
    app.run(debug=debug, host="0.0.0.0", port=port)
