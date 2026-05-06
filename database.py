import sqlite3
import uuid

def init_db():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            sender TEXT,
            message TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        )
    ''')
    conn.commit()
    conn.close()

def create_session():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    session_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO sessions (session_id) VALUES (?)", (session_id,))
    conn.commit()
    conn.close()
    return session_id


def add_message_to_db(session_id, sender, message):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, sender, message) VALUES (?, ?, ?)",
                   (session_id, sender, message))
    conn.commit()
    conn.close()


def get_history(session_id):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM messages WHERE session_id = ? ORDER BY id", (session_id,))
    history = cursor.fetchall()
    conn.close()
    return history