#!/bin/bash

# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Виртуальное окружение настроено. Активируйте его командой: source venv/bin/activate"