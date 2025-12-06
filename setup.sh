#!/bin/bash

# Название виртуального окружения
VENV_DIR="venv"

# Проверяем, существует ли уже виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
    echo "Создаём виртуальное окружение..."
    python3 -m venv "$VENV_DIR"
else
    echo "Виртуальное окружение уже существует."
fi

# Активируем окружение
source "$VENV_DIR/bin/activate"

# Устанавливаем зависимости
echo "Устанавливаем зависимости из requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Настройка завершена! Активируйте окружение командой: source venv/bin/activate"