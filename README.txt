# 📝 Smart Todo App

Простое веб-приложение для управления задачами с приоритетами, фильтрацией и статистикой.  
Реализовано на Flask + Bootstrap, контейнеризировано через Docker, автоматизировано через GitHub Actions.

🔗 **Демо**: https://smart-todo-app.onrender.com
📦 **GitHub**: https://github.com/vedeninae36-web/smart-todo-app

---

## 🚀 Установка и запуск

### 1. Клонируйте репозиторий

git clone https://github.com/vedeninae36-web/smart-todo-app.git
cd smart-todo-app

### 2. Создайте и активируйте виртуальное окружение

python -m venv venv
venv\Scripts\activate

### 3. Установите зависимости

pip install -r requirements.txt

### 4. Запустите приложение

python src/backend/app.py

👉 Откройте: http://localhost:5000

---

## 🐳 Запуск в Docker

docker compose up --build

👉 Доступно по: http://localhost:5000

---

## 🧪 Тестирование

python -m pytest src/tests/ -v

✅ Все тесты должны пройти (8 из 8).

---

## 📡 API документация

Приложение использует следующие эндпоинты:

### GET /
Возвращает главную страницу со списком задач.

### POST /tasks
Создаёт новую задачу.
{
  "title": "Название задачи",
  "priority": "low|medium|high"
}

### POST /tasks/<id>/toggle
Переключает статус выполнения задачи.

### POST /tasks/<id>/delete
Удаляет задачу.

---

## 🧩 CI/CD

Проект автоматически тестируется и деплоится через GitHub Actions.

![CI Status](https://img.shields.io/github/actions/workflow/status/vedeninae36-web/smart-todo-app/ci.yml?branch=main&label=CI&logo=github)

---

## 🛠 Требования

- Python 3.14+
- Docker (опционально)
- Git

---

## 📄 Лицензия

MIT — см. файл LICENSE.

---

## 🙏 Благодарности

Спасибо за использование!  
Если есть вопросы или предложения — создавайте issue.