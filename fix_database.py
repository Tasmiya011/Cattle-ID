# fix_database.py - Complete database setup

import sqlite3
import datetime

conn = sqlite3.connect('cows.db')
cursor = conn.cursor()

# 1. Create cows table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cows (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        breed TEXT,
        owner TEXT,
        age INTEGER,
        health_status TEXT,
        farmer_id INTEGER,
        last_updated TEXT
    )
''')

# 2. Create vaccinations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vaccinations (
        id INTEGER PRIMARY KEY,
        cow_id INTEGER,
        vaccine_name TEXT,
        date TEXT,
        next_due TEXT,
        FOREIGN KEY (cow_id) REFERENCES cows (id)
    )
''')

# 3. Create health_records table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY,
        cow_id INTEGER,
        date TEXT,
        condition TEXT,
        treatment TEXT,
        FOREIGN KEY (cow_id) REFERENCES cows (id)
    )
''')

# 4. Create farmers table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        village TEXT,
        registered_date TEXT
    )
''')

# 5. Create activities table
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

# 6. Create alerts table
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

# Insert sample cows
cows_data = [
    (1, 'Lakshmi', 'Gir', 'Ramesh', 5, 'Healthy', 1, datetime.datetime.now().isoformat()),
    (2, 'Ganga', 'Sahiwal', 'Suresh', 4, 'Needs Checkup', 1, datetime.datetime.now().isoformat()),
    (3, 'Kali', 'Jersey', 'Mahesh', 3, 'Excellent', 1, datetime.datetime.now().isoformat()),
    (4, 'Kamadhenu', 'Holstein', 'Priya', 6, 'Pregnant', 1, datetime.datetime.now().isoformat()),
]

cursor.executemany('''
    INSERT OR REPLACE INTO cows (id, name, breed, owner, age, health_status, farmer_id, last_updated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', cows_data)

# Insert sample vaccinations
vaccinations_data = [
    (1, 1, 'FMD Vaccine', '2026-01-10', '2026-07-10'),
    (2, 2, 'HS Vaccine', '2025-12-01', '2026-06-01'),
    (3, 3, 'FMD Vaccine', '2026-02-15', '2026-08-15'),
    (4, 4, 'BQ Vaccine', '2026-03-01', '2026-09-01'),
]

cursor.executemany('''
    INSERT OR REPLACE INTO vaccinations (id, cow_id, vaccine_name, date, next_due)
    VALUES (?, ?, ?, ?, ?)
''', vaccinations_data)

# Insert sample farmer
cursor.execute('''
    INSERT OR IGNORE INTO farmers (id, name, phone, village, registered_date)
    VALUES (1, 'Ramesh', '9876543210', 'Gokul Gram', ?)
''', (datetime.datetime.now().isoformat(),))

conn.commit()
conn.close()

print("✅ Database fixed! All tables created.")
print("📊 Tables: cows, vaccinations, health_records, farmers, activities, alerts")
print("🐄 Sample cows: Lakshmi, Ganga, Kali, Kamadhenu")