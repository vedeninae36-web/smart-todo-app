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
    return max((t["id"] for t in tasks), default=0) + 1


@app.route("/")
def index():
    filter_type = request.args.get("filter", "all")
    if filter_type == "active":
        displayed_tasks = [t for t in tasks if not t["completed"]]
    elif filter_type == "completed":
        displayed_tasks = [t for t in tasks if t["completed"]]
    else:
        displayed_tasks = tasks
        filter_type = "all"

    stats = {
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t["completed"]),
        "active": len(tasks) - sum(1 for t in tasks if t["completed"]),
    }

    return render_template(
        "tasks_list.html",
        tasks=displayed_tasks,
        current_filter=filter_type,
        stats=stats,
    )


@app.route("/tasks", methods=["POST"])
def create_task():
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
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Добавляем тестовую задачу при первом запуске
    if not tasks:
        tasks.append(
            {
                "id": 1,
                "title": " Всё работает!",
                "priority": "medium",
                "completed": False,
            }
        )

    # Получаем порт из окружения (Render передаёт PORT)
    port = int(os.environ.get("PORT", 5000))
    # Отключаем debug в продакшене
    debug = os.environ.get("FLASK_ENV") != "production"

    # Запускаем с host=0.0.0.0 — ОБЯЗАТЕЛЬНО для облака
    app.run(debug=debug, host="0.0.0.0", port=port)
