import os
import sys
import json
import pytest

# Добавляем корень проекта в sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

# Импортируем ДО создания приложения
from backend import database

# Путь к тестовой БД
TEST_DB_PATH = "test_smart_todo.db"

# Подменяем путь к БД ГЛОБАЛЬНО в модуле database
database.DATABASE_PATH = TEST_DB_PATH

# Теперь импортируем app — он будет использовать TEST_DB_PATH
from backend.app import app

@pytest.fixture(scope="module")
def client():
    """Создаёт клиент Flask для тестирования с изолированной БД"""
    # Инициализируем тестовую БД
    database.init_db()
    database.populate_test_data()

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Очистка
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

# === Тесты ===
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
    tasks = json.loads(response.data)
    assert len(tasks) > 0
    first_task = tasks[0]
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