import os
import tempfile
import sqlite3
import json
import pytest
from src.backend.app import app

# Путь к тестовой БД
TEST_DB_PATH = "test_smart_todo.db"


@pytest.fixture(scope="module")
def client():
    """Создаёт клиент Flask для тестирования"""
    # Заменяем путь к БД на тестовую
    from src.backend.database import DATABASE_PATH

    original_db_path = DATABASE_PATH
    DATABASE_PATH = TEST_DB_PATH

    # Инициализируем тестовую БД
    from src.backend.database import init_db, populate_test_data

    init_db()
    populate_test_data()

    # Создаём тестовый клиент
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Очищаем тестовую БД после всех тестов
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)


def test_get_tasks(client):
    """Тестирует GET /api/tasks — получение списка задач"""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)

    # Проверяем, что пришли задачи (из populate_test_data)
    assert len(data) >= 5  # минимум 5 задач
    for task in data:
        assert 'id' in task
        assert 'title' in task
        assert 'status' in task


def test_create_task(client):
    """Тестирует POST /api/tasks — создание новой задачи"""
    new_task = {
        "title": "Тестовая задача",
        "description": "Описание тестовой задачи",
        "category_id": 1,
        "status": "pending",
    }

    response = client.post(
        '/api/tasks', data=json.dumps(new_task), content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)

    assert data['title'] == "Тестовая задача"
    assert data['status'] == "pending"
    assert 'id' in data

    # Проверим, что задача действительно создалась
    response = client.get(f'/api/tasks/{data["id"]}')
    assert response.status_code == 200
    created_task = json.loads(response.data)
    assert created_task['title'] == "Тестовая задача"


def test_get_task_by_id(client):
    """Тестирует GET /api/tasks/<id> — получение задачи по ID"""
    # Получаем первую задачу
    response = client.get('/api/tasks')
    first_task = json.loads(response.data)[0]

    # Запрашиваем её по ID
    response = client.get(f'/api/tasks/{first_task["id"]}')
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data['id'] == first_task['id']
    assert data['title'] == first_task['title']


def test_get_task_not_found(client):
    """Тестирует GET /api/tasks/<id> — когда задача не найдена"""
    response = client.get('/api/tasks/999999')  # несуществующий ID
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


def test_create_task_invalid_status(client):
    """Тестирует POST /api/tasks — неверный статус"""
    invalid_task = {
        "title": "Задача с ошибкой",
        "status": "invalid_status",  # ❌ недопустимый статус
    }

    response = client.post(
        '/api/tasks', data=json.dumps(invalid_task), content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_create_task_missing_title(client):
    """Тестирует POST /api/tasks — отсутствие названия"""
    invalid_task = {"description": "Без названия"}

    response = client.post(
        '/api/tasks', data=json.dumps(invalid_task), content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Title is required' in data['error']
