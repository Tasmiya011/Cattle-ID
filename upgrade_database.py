# upgrade_database.py - Add all new tables for advanced features

import sqlite3
import datetime

conn = sqlite3.connect('cows.db')
cursor = conn.cursor()

# 1. Add farmer/user table (Multi-farmer support)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        village TEXT,
        registered_date TEXT
    )
''')

# 2. Add activity log (for sync)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY,
        farmer_id INTEGER,
        action TEXT,
        details TEXT,
        timestamp TEXT,
        synced INTEGER DEFAULT 0,
        FOREIGN KEY (farmer_id) REFERENCES farmers (id)
    )
''')

# 3. Add alerts table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY,
        cow_id INTEGER,
        alert_type TEXT,
        message TEXT,
        date TEXT,
        is_read INTEGER DEFAULT 0,
        FOREIGN KEY (cow_id) REFERENCES cows (id)
    )
''')

# 4. Add new columns to cows table
try:
    cursor.execute('ALTER TABLE cows ADD COLUMN farmer_id INTEGER')
    cursor.execute('ALTER TABLE cows ADD COLUMN last_updated TEXT')
except:
    pass  # Columns already exist

# Insert sample farmer
cursor.execute('''
    INSERT OR IGNORE INTO farmers (id, name, phone, village, registered_date)
    VALUES (1, 'Ramesh', '9876543210', 'Gokul Gram', ?)
''', (datetime.datetime.now().isoformat(),))

# Generate sample alerts
cursor.execute('''
    INSERT OR IGNORE INTO alerts (cow_id, alert_type, message, date)
    SELECT id, 'Vaccination Due', 
           name || ' needs vaccination in 7 days',
           datetime('now', '+7 days')
    FROM cows WHERE name = 'Ganga'
''')

conn.commit()
conn.close()

print("✅ Database upgraded with new features!")
print("📊 New tables: farmers, activitiepip install -r requirements.txts, alerts")
print("🔔 Sample alerts created")