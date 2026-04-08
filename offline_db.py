import sqlite3
from datetime import datetime

DB_FILE = "cattle.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cows (
            id INTEGER PRIMARY KEY,
            name TEXT,
            owner TEXT,
            vaccination TEXT,
            insurance TEXT,
            breed TEXT,
            last_checkup TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS offline_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            question TEXT,
            answer TEXT,
            synced INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("Database ready")

def add_cow(cow_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO cows (id, name, owner, vaccination, insurance, breed, last_checkup)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (cow_data['id'], cow_data['name'], cow_data['owner'], cow_data['vaccination'], cow_data['insurance'], cow_data['breed'], cow_data.get('last_checkup', '')))
    conn.commit()
    conn.close()

def get_all_cows():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, owner, vaccination, insurance, breed, last_checkup FROM cows")
    rows = cursor.fetchall()
    conn.close()
    cows = []
    for row in rows:
        cows.append({'id': row[0], 'name': row[1], 'owner': row[2], 'vaccination': row[3], 'insurance': row[4], 'breed': row[5], 'last_checkup': row[6]})
    return cows

def save_offline_conversation(question, answer):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO offline_conversations (timestamp, question, answer, synced) VALUES (?, ?, ?, 0)", (datetime.now().isoformat(), question, answer))
    conn.commit()
    conn.close()

def get_unsynced_conversations():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, question, answer FROM offline_conversations WHERE synced = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_conversation_synced(conv_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE offline_conversations SET synced = 1 WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()

def is_online():
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=3)
        return True
    except:
        return False

init_db()