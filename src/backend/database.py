# src/backend/database.py

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "smart_tasks.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#CCCCCC'
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high'))
                NOT NULL DEFAULT 'medium',
            category_id INTEGER,
            deadline DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
        """
    )

    # Индексы
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tasks_status_priority "
        "ON tasks(is_completed, priority)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title)",
    ]
    for idx in indexes:
        cursor.execute(idx)

    conn.commit()
    conn.close()


def fill_test_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    categories = [("Work", "#FF5733"), ("Personal", "#33FF57"), ("Study", "#3357FF")]
    for name, color in categories:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)",
            (name, color),
        )

    cursor.execute("SELECT id, name FROM categories")
    category_map = {name: id for id, name in cursor.fetchall()}

    cursor.execute("DELETE FROM tasks WHERE title LIKE 'Test Task %'")

    now = datetime.now()
    tasks = [
        (
            "Test Task 1: Complete report",
            "Finish quarterly report",
            "high",
            category_map["Work"],
            now + timedelta(days=2),
        ),
        (
            "Test Task 2: Buy groceries",
            "Milk, bread, eggs",
            "medium",
            category_map["Personal"],
            now + timedelta(hours=12),
        ),
        (
            "Test Task 3: Read chapter",
            "Read Chapter 5",
            "low",
            category_map["Study"],
            now + timedelta(days=5),
        ),
        (
            "Test Task 4: Team meeting",
            "Discuss project roadmap",
            "high",
            category_map["Work"],
            now + timedelta(hours=24),
        ),
        (
            "Test Task 5: Gym session",
            "Workout at 6 PM",
            "medium",
            category_map["Personal"],
            now + timedelta(days=1),
        ),
    ]

    for title, desc, prio, cat_id, ddl in tasks:
        cursor.execute(
            """
            INSERT INTO tasks (
                title, description, priority, category_id, deadline
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (title, desc, prio, cat_id, ddl),
        )

    conn.commit()
    conn.close()
    print(
        "✅ База данных инициализирована. " "Добавлено 3 категории и 5 тестовых задач."
    )


if __name__ == "__main__":
    init_db()
    fill_test_data()
