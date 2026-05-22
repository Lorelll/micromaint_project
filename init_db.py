import sqlite3

def init_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Таблиця користувачів (для Адміна)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Таблиця пристроїв
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')

    # Таблиця завдань
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            title TEXT NOT NULL,
            planned_date TEXT NOT NULL,
            status TEXT DEFAULT 'В очікуванні',
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )
    ''')

    # Таблиця пунктів чек-ліста
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            item_text TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        )
    ''')

    # Очищення для демо
    cursor.execute("DELETE FROM checklist_items")
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM devices")
    cursor.execute("DELETE FROM users")

    # Створюємо тестового адміна (Пароль: admin123)
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

    # Тестові пристрої
    cursor.execute("INSERT INTO devices (id, name, location) VALUES (1, 'Банкомат #402', 'вул. Хрещатик, 19')")
    cursor.execute("INSERT INTO devices (id, name, location) VALUES (2, 'Термінал самообслуговування #12', 'пр. Науки, 5')")

    # Тестові завдання
    cursor.execute("INSERT INTO tasks (id, device_id, title, planned_date, status) VALUES (1, 1, 'Планове щомісячне ТО', '2026-05-18', 'В очікуванні')")
    cursor.execute("INSERT INTO tasks (id, device_id, title, planned_date, status) VALUES (2, 2, 'Перевірка купюроприймача', '2026-05-18', 'Виконано')")

    cursor.execute("INSERT INTO checklist_items (task_id, item_text, is_done) VALUES (1, 'Зовнішній огляд та очищення від пилу', 0)")
    cursor.execute("INSERT INTO checklist_items (task_id, item_text, is_done) VALUES (1, 'Тестування модуля видачі готівки', 0)")

    conn.commit()
    conn.close()
    print("Базу даних успішно оновлено!")

if __name__ == '__main__':
    init_database()