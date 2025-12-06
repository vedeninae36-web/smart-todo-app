


Студент: Элеонора
GitHub: https://github.com/vedeninae36-web/smart-todo-app
Демо: https://smart-todo-app.onrender.com

🔧 Подготовка окружения
Установка Python и Git
Установите Python 3.14+ с официального сайта, обязательно с галочкой Add Python to PATH.
Установите Git с git-scm.com.
Проверьте установку:
cmd
12
⚠️ Ошибка: python не распознаётся → перезапустите терминал или установите Python заново с Add to PATH.

✅ Задание 8: Веб-интерфейс (Flask + Bootstrap)
Структура проекта
1234567
Команды
cmd
12
Основные файлы
app.py — Flask-приложение с маршрутами GET /, POST /tasks, POST /tasks/<id>/toggle, POST /tasks/<id>/delete
templates/base.html — базовый шаблон с Bootstrap
templates/tasks_list.html — наследует base.html, отображает задачи, форму, статистику и фильтры
Запуск
cmd
12345
cd src\backend
python -m venv venv
venv\Scripts\activate
pip install Flask
python app.py
→ Открыть http://localhost:5000

⚠️ Ошибка TemplateNotFound → убедитесь, что папка templates рядом с app.py и файлы не .html.txt.

✅ Задание 9: Модульное тестирование (pytest)
Файл: src/tests/test_api.py
Написано 8 тестов на все эндпоинты
Используется @pytest.fixture для изоляции состояния
Проверка фильтров, CRUD, статистики
Команды
cmd
12
pip install pytest
python -m pytest src/tests/ -v
⚠️ Ошибка ModuleNotFoundError: No module named 'backend' → тесты не должны импортировать app.py напрямую. Используется локальное копирование логики или sys.path.insert (в итоге использован self-contained тест без импорта).

✅ Задание 10: Линтер и форматтер (flake8 + black)
Установка
cmd
1
pip install flake8 black
Конфигурационные файлы
.flake8:
ini
1234
pyproject.toml:
toml
123
Команды
cmd
123
black src/                  # форматирование
black --check src/          # проверка
flake8 src/                 # линтер
⚠️ Ошибка W292 no newline at end of file → добавьте пустую строку в конец файла.
⚠️ Ошибка E501 line too long → разбейте длинные строки в database.py.
⚠️ Ошибка F401 unused import → удалите неиспользуемый url_for.

✅ Задание 12: Контейнеризация (Docker)
Файлы
requirements.txt:
txt
1
Dockerfile:
dockerfile
1234567
docker-compose.yml:
yaml
12345
Установка Docker
Скачайте и установите Docker Desktop.
Перезагрузите компьютер.
Проверьте:
cmd
12
Команды
cmd
12
docker compose build
docker compose up
⚠️ Ошибка docker-compose not found → используйте docker compose (без дефиса).
⚠️ Ошибка no configuration file → убедитесь, что вы в папке smart-todo-app.

✅ Задание 13: CI/CD и деплой
GitHub Actions (ci.yml)
Тесты → линтер → сборка Docker → пуш в GHCR
Используется github.actor для избежания ошибки denied: installation not allowed
Render (деплой в облако)
Зарегистрируйтесь на render.com
Создайте Web Service → выберите репозиторий
Укажите порт 5000
Добавьте в app.py:
python
12
Финальный .github/workflows/ci.yml
yaml
12345678910111213141516171819202122
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test-and-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14" }
      - run: pip install flake8 black pytest Flask

⚠️ Ошибка denied: installation not allowed → замените github.repository_owner на github.actor.

📤 Финальные шаги
Закоммитьте всё:
cmd
123
Убедитесь, что:
В GitHub Actions — все шаги зелёные ✅
В Render — приложение доступно по HTTPS
В GitHub Packages — есть Docker-образ
🎯 Заключение
Все задания выполнены:

✅ Задание 8: веб-интерфейс
✅ Задание 9: тесты
✅ Задание 10: качество кода
✅ Задание 12: Docker
✅ Задание 13: CI/CD + деплой
Проект полностью автоматизирован, соответствует industry standards и готов к использованию.