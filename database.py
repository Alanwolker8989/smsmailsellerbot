import sqlite3
from datetime import datetime

DB_NAME = "mail_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            gmail_email TEXT,
            gmail_password TEXT,
            limit_count INTEGER DEFAULT 5,
            last_reset_date TEXT DEFAULT '2024-01-01 00:00:00'  -- Константа
        )
    """)

    # Проверим, есть ли нужные столбцы, и добавим их, если нет
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'last_reset_date' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_reset_date TEXT DEFAULT '2024-01-01 00:00:00'")

    conn.commit()
    conn.close()
    
def save_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, limit_count, last_reset_date)
        VALUES (?, ?, 5, ?)
    """, (user_id, username, str(datetime.now())))

    conn.commit()
    conn.close()

def get_user_limit_and_reset_date(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT limit_count, last_reset_date FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1]
    return 0, str(datetime.now())  # Если нет — лимит 0 и дата сейчас

def update_user_limit_and_reset_date(user_id: int, new_limit: int):
    reset_date = str(datetime.now())
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET limit_count = ?, last_reset_date = ? WHERE user_id = ?", (new_limit, reset_date, user_id))
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

def delete_user_gmail(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET gmail_email = NULL, gmail_password = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_total_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    conn.close()
    return result[0]