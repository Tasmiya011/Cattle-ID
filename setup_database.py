# setup_database.py
import sqlite3
import datetime

conn = sqlite3.connect('cows.db')
cursor = conn.cursor()

# Cows table (includes muzzle_encoding BLOB for Member 1's feature)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cows (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        breed TEXT,
        owner TEXT,
        age INTEGER,
        health_status TEXT,
        muzzle_encoding BLOB,      -- Store muzzle feature vector
        farmer_id INTEGER,
        last_updated TEXT
    )
''')

# Vaccinations table
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

# Health records table
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

# Farmers table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT UNIQUE,
        village TEXT,
        registered_date TEXT
    )
''')

# Activities table (for offline sync)
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

# Alerts table
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

# Insert sample cows (muzzle_encoding left as NULL for now)
cows_data = [
    (1, 'Lakshmi', 'Gir', 'Ramesh', 5, 'Healthy', None, 1, datetime.datetime.now().isoformat()),
    (2, 'Ganga', 'Sahiwal', 'Suresh', 4, 'Needs Checkup', None, 1, datetime.datetime.now().isoformat()),
    (3, 'Kali', 'Jersey', 'Mahesh', 3, 'Excellent', None, 1, datetime.datetime.now().isoformat()),
    (4, 'Kamadhenu', 'Holstein', 'Priya', 6, 'Pregnant', None, 1, datetime.datetime.now().isoformat()),
]
cursor.executemany('''
    INSERT OR REPLACE INTO cows (id, name, breed, owner, age, health_status, muzzle_encoding, farmer_id, last_updated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', cows_data)

# Sample vaccinations
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

# Sample farmer
cursor.execute('''
    INSERT OR IGNORE INTO farmers (id, name, phone, village, registered_date)
    VALUES (1, 'Ramesh', '9876543210', 'Gokul Gram', ?)
''', (datetime.datetime.now().isoformat(),))

conn.commit()
conn.close()
print("✅ Database created with muzzle_encoding column.")
print("📊 Tables: cows, vaccinations, health_records, farmers, activities, alerts")
