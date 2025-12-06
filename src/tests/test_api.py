import pytest
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path


def create_app():
    base_dir = Path(__file__).parent.parent / "backend" / "templates"
    app = Flask(__name__, template_folder=str(base_dir))
    
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
        return redirect('/')

    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    def toggle_task(task_id):
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = not task['completed']
                break
        return redirect('/')

    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    def delete_task(task_id):
        # Удаляем задачу по id, изменяя список "на месте"
        for i in range(len(tasks) - 1, -1, -1):
            if tasks[i]['id'] == task_id:
                del tasks[i]
                break
        return redirect('/')

    # Инициализация
    tasks.append({"id": 1, "title": "✅ Всё работает!", "priority": "medium", "completed": False})

    return app, tasks


@pytest.fixture
def client_and_tasks():
    app, tasks = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client, tasks


# ТЕСТЫ
def test_delete_task(client_and_tasks):
    client, tasks = client_and_tasks
    assert len(tasks) == 1
    client.post('/tasks/1/delete')
    assert len(tasks) == 0


def test_filter_active(client_and_tasks):
    client, tasks = client_and_tasks
    tasks.append({"id": 2, "title": "Завершённая", "priority": "low", "completed": True})
    html = client.get('/?filter=active').get_data(as_text=True)
    assert "Всё работает!" in html
    assert "Завершённая" not in html


def test_filter_completed(client_and_tasks):
    client, tasks = client_and_tasks
    tasks.append({"id": 2, "title": "Завершённая", "priority": "low", "completed": True})
    html = client.get('/?filter=completed').get_data(as_text=True)
    assert "Завершённая" in html
    assert "Всё работает!" not in html


def test_all_endpoints_integration(client_and_tasks):
    client, tasks = client_and_tasks
    client.post('/tasks', data={'title': 'A', 'priority': 'low'})
    client.post('/tasks', data={'title': 'B', 'priority': 'high'})
    client.post('/tasks/2/toggle')      # переключаем A (id=2)
    client.post('/tasks/1/delete')      # удаляем начальную (id=1)

    assert len(tasks) == 2
    titles = {t['title'] for t in tasks}
    assert titles == {"A", "B"}
    # Проверяем, что A завершена
    a_task = next(t for t in tasks if t['title'] == 'A')
    assert a_task['completed'] is True


def test_get_root_returns_tasks(client_and_tasks):
    client, _ = client_and_tasks
    response = client.get('/')
    assert response.status_code == 200
    assert "Всё работает!" in response.get_data(as_text=True)


def test_create_task(client_and_tasks):
    client, tasks = client_and_tasks
    client.post('/tasks', data={'title': 'Тестовая задача', 'priority': 'high'})
    html = client.get('/').get_data(as_text=True)
    assert "Тестовая задача" in html
    assert "priority-high" in html


def test_toggle_task(client_and_tasks):
    client, tasks = client_and_tasks
    assert tasks[0]['completed'] is False
    client.post('/tasks/1/toggle')
    assert tasks[0]['completed'] is True


def test_empty_title_not_added(client_and_tasks):
    client, tasks = client_and_tasks
    initial = len(tasks)
    client.post('/tasks', data={'title': '', 'priority': 'low'})
    assert len(tasks) == initial