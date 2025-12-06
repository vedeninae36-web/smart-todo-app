import sqlite3

DATABASE_PATH = "smart_todo.db"


def init_db():
    """Инициализация базы данных: создание таблиц, если они не существуют"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ База данных и таблицы успешно созданы.")


def populate_test_data():
    """Заполнение базы данных тестовыми данными, если таблицы пусты"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Проверим, есть ли уже данные
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Не добавляем, если уже есть задачи

    categories = [("Работа",), ("Учёба",), ("Личное",)]
    cursor.executemany("INSERT OR IGNORE INTO categories (name) VALUES (?)", categories)

    cursor.execute("SELECT id, name FROM categories")
    category_map = {name: id for id, name in cursor.fetchall()}

    tasks = [
        ("Подготовить презентацию", "Крайний срок — завтра", category_map["Работа"], "pending"),
        ("Прочитать главу 5", "По курсу Python", category_map["Учёба"], "in_progress"),
        ("Позвонить маме", "Обсудить выходные", category_map["Личное"], "pending"),
        ("Написать отчёт по проекту", "Отправить руководителю", category_map["Работа"], "completed"),
        ("Сделать домашнее задание", "По алгоритмам", category_map["Учёба"], "pending"),
    ]

    cursor.executemany("""
        INSERT INTO tasks (title, description, category_id, status)
        VALUES (?, ?, ?, ?)
    """, tasks)

    conn.commit()
    conn.close()
    print(" Тестовые данные успешно добавлены.")