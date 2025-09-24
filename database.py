import sqlite3
from datetime import date

DB_NAME = "mail_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            gmail_email TEXT,
            gmail_password TEXT,
            limit_count INTEGER DEFAULT 5
        )
    """)

    conn.commit()
    conn.close()

def save_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, limit_count)
        VALUES (?, ?, 5)
    """, (user_id, username))

    conn.commit()
    conn.close()

def get_user_limit(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT limit_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_user_limit(user_id: int, new_limit: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET limit_count = ? WHERE user_id = ?", (new_limit, user_id))
    conn.commit()
    conn.close()

def update_user_gmail_password(user_id: int, email: str, password: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET gmail_email = ?, gmail_password = ? WHERE user_id = ?", (email, password, user_id))
    conn.commit()
    conn.close()

def get_user_gmail_password(user_id: int) -> tuple:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT gmail_email, gmail_password FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            limit_count INTEGER DEFAULT 5
        )
    """)

    # Проверим, есть ли нужные столбцы, и добавим их, если нет
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'gmail_email' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN gmail_email TEXT")
    if 'gmail_password' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN gmail_password TEXT")

    conn.commit()
    conn.close()