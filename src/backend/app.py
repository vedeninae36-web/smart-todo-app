import os
import sys
from flask import Flask, render_template, request, redirect, url_for

# Явное указание пути к шаблонам — решает проблему с кириллицей в Windows
if sys.platform == "win32":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    template_dir = os.path.normpath(template_dir)
else:
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Отладочный вывод (можно удалить после проверки)
print(">>> Путь к шаблонам:", template_dir)
print(">>> tasks_list.html существует?", os.path.isfile(os.path.join(template_dir, 'tasks_list.html')))

# Создаём приложение с явным указанием папки шаблонов
app = Flask(__name__, template_folder=template_dir)

# Временное хранилище задач
tasks = []

def get_next_id():
    return max((t["id"] for t in tasks), default=0) + 1

@app.route('/')
def index():
    filter_type = request.args.get('filter', 'all')
    if filter_type == 'active':
        displayed_tasks = [t for t in tasks if not t['completed']]
    elif filter_type == 'completed':
        displayed_tasks = [t for t in tasks if t['completed']]
    else:
        displayed_tasks = tasks
        filter_type = 'all'

    stats = {
        'total': len(tasks),
        'completed': sum(1 for t in tasks if t['completed']),
        'active': len(tasks) - sum(1 for t in tasks if t['completed'])
    }

    return render_template(
        'tasks_list.html',
        tasks=displayed_tasks,
        current_filter=filter_type,
        stats=stats
    )

@app.route('/tasks', methods=['POST'])
def create_task():
    title = request.form.get('title', '').strip()
    priority = request.form.get('priority', 'low')
    if title:
        tasks.append({
            "id": get_next_id(),
            "title": title,
            "priority": priority,
            "completed": False
        })
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Добавляем тестовую задачу
    if not tasks:
        tasks.append({"id": 1, "title": "✅ Всё работает! Можно добавлять свои задачи.", "priority": "medium", "completed": False})
    app.run(debug=True, host='0.0.0.0', port=5000)