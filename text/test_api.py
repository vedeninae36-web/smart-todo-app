import os
import sys
import tempfile
import json
import pytest

# Добавляем корень проекта в sys.path, чтобы импортировать backend
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
ROOT_DIR = os.path.abspath(ROOT_DIR)
sys.path.insert(0, ROOT_DIR)

from backend.app import app
from backend.database import init_db, populate_test_data

# Путь к тестовой БД
TEST_DB_PATH = "test_smart_todo.db"

@pytest.fixture(scope="module")
def client():
    """Создаёт клиент Flask для тестирования"""
    # Заменяем путь к БД на тестовую
    from backend.database import DATABASE_PATH
    original_db = DATABASE_PATH
    DATABASE_PATH = TEST_DB_PATH

    # Сохраняем оригинальный путь (хотя в тестах мы его перезапишем)
    # Инициализируем тестовую БД
    init_db()
    populate_test_data()

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Очистка после тестов
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

# ... остальные тесты остаются без изменений
def test_get_tasks(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 5
    for task in data:
        assert 'id' in task
        assert 'title' in task

def test_create_task(client):
    new_task = {
        "title": "Тестовая задача",
        "description": "Описание",
        "category_id": 1,
        "status": "pending"
    }
    response = client.post('/api/tasks',
                           data=json.dumps(new_task),
                           content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == "Тестовая задача"
    assert 'id' in data

def test_get_task_by_id(client):
    response = client.get('/api/tasks')
    first_task = json.loads(response.data)[0]
    response2 = client.get(f'/api/tasks/{first_task["id"]}')
    assert response2.status_code == 200
    data = json.loads(response2.data)
    assert data['id'] == first_task['id']

def test_get_task_not_found(client):
    response = client.get('/api/tasks/999999')
    assert response.status_code == 404

def test_create_task_missing_title(client):
    response = client.post('/api/tasks',
                           data=json.dumps({"description": "no title"}),
                           content_type='application/json')
    assert response.status_code == 400

def test_create_task_invalid_status(client):
    response = client.post('/api/tasks',
                           data=json.dumps({"title": "bad", "status": "invalid"}),
                           content_type='application/json')
    assert response.status_code == 400