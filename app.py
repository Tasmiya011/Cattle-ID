import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import sqlite3
import datetime
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Cow Muzzle ID - Complete Solution", page_icon="🐄", layout="wide")

st.title("🐄 COW MUZZLE IDENTIFICATION SYSTEM")
st.markdown("*Complete Farm Management with Voice Assistant | आवाज़ संचालित पूर्ण पशु प्रबंधन*")

# ============================================
# LANGUAGE OPTIONS
# ============================================

LANGUAGES = {
    "हिंदी (Hindi)": "hi-IN",
    "English": "en-IN",
    "मराठी (Marathi)": "mr-IN",
    "தமிழ் (Tamil)": "ta-IN",
    "తెలుగు (Telugu)": "te-IN",
}

# ============================================
# DATABASE FUNCTIONS (All Features)
# ============================================

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('cows.db')

# --- BASIC CRUD ---
def get_cow_info(cow_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, breed, owner, age, health_status, last_updated FROM cows WHERE LOWER(name) = LOWER(?)', (cow_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            name, breed, owner, age, health, updated = result
            return f"{name} is a {breed} cow. Owner: {owner}. Age: {age} years. Health: {health}. Last updated: {updated}"
        return None
    except Exception as e:
        return f"Database error: {e}"

def get_vaccination_info(cow_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.vaccine_name, v.date, v.next_due
            FROM vaccinations v JOIN cows c ON c.id = v.cow_id
            WHERE LOWER(c.name) = LOWER(?)
        ''', (cow_name,))
        results = cursor.fetchall()
        conn.close()
        if results:
            info = f"Vaccination records for {cow_name}:\n"
            for vaccine, date, next_due in results:
                info += f"• {vaccine} on {date}. Next due: {next_due}\n"
            return info
        return f"No vaccination records found for {cow_name}"
    except Exception as e:
        return f"Database error: {e}"

# --- VOICE CRUD (IMPRESSIVE FEATURE 1) ---
def add_cow_by_voice(name, breed, owner, age):
    """Add new cow using voice input"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if cow already exists
        cursor.execute('SELECT id FROM cows WHERE LOWER(name) = LOWER(?)', (name,))
        if cursor.fetchone():
            conn.close()
            return f"Cow {name} already exists in database!"
        
        # Get next ID
        cursor.execute('SELECT MAX(id) FROM cows')
        max_id = cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        # Insert new cow
        cursor.execute('''
            INSERT INTO cows (id, name, breed, owner, age, health_status, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (new_id, name.title(), breed.title(), owner.title(), int(age), 'New', datetime.datetime.now().isoformat()))
        
        # Log activity
        cursor.execute('''
            INSERT INTO activities (farmer_id, action, details, timestamp, synced)
            VALUES (1, 'ADD_COW', ?, ?, 0)
        ''', (f"Added cow: {name}", datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return f"✅ Cow {name} added successfully! Breed: {breed}, Owner: {owner}, Age: {age} years"
    except Exception as e:
        return f"Error adding cow: {e}"

def update_cow_health_by_voice(cow_name, health_status):
    """Update cow health status by voice"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cows 
            SET health_status = ?, last_updated = ?
            WHERE LOWER(name) = LOWER(?)
        ''', (health_status, datetime.datetime.now().isoformat(), cow_name))
        
        if cursor.rowcount == 0:
            conn.close()
            return f"Cow {cow_name} not found!"
        
        # Log activity
        cursor.execute('''
            INSERT INTO activities (farmer_id, action, details, timestamp, synced)
            VALUES (1, 'UPDATE_HEALTH', ?, ?, 0)
        ''', (f"Updated {cow_name} health to {health_status}", datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return f"✅ {cow_name}'s health status updated to {health_status}"
    except Exception as e:
        return f"Error updating health: {e}"

def delete_cow_by_voice(cow_name):
    """Delete cow from database by voice"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute('SELECT name FROM cows WHERE LOWER(name) = LOWER(?)', (cow_name,))
        if not cursor.fetchone():
            conn.close()
            return f"Cow {cow_name} not found!"
        
        # Delete
        cursor.execute('DELETE FROM cows WHERE LOWER(name) = LOWER(?)', (cow_name,))
        
        # Log activity
        cursor.execute('''
            INSERT INTO activities (farmer_id, action, details, timestamp, synced)
            VALUES (1, 'DELETE_COW', ?, ?, 0)
        ''', (f"Deleted cow: {cow_name}", datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return f"✅ Cow {cow_name} has been removed from database"
    except Exception as e:
        return f"Error deleting cow: {e}"

# --- VOICE REPORTS (IMPRESSIVE FEATURE 2) ---
def get_vaccination_report():
    """Generate vaccination report"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.name, v.vaccine_name, v.date, v.next_due
            FROM cows c
            LEFT JOIN vaccinations v ON c.id = v.cow_id
            ORDER BY v.next_due
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "No vaccination records found."
        
        report = "📊 VACCINATION REPORT\n\n"
        report += "=" * 40 + "\n"
        
        for name, vaccine, date, next_due in results:
            if vaccine:
                report += f"🐄 {name}: {vaccine}\n"
                report += f"   Last: {date}\n"
                report += f"   Next: {next_due}\n\n"
            else:
                report += f"🐄 {name}: No vaccinations recorded\n\n"
        
        return report
    except Exception as e:
        return f"Error generating report: {e}"

def get_health_summary():
    """Get health summary of all cows"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT health_status, COUNT(*), GROUP_CONCAT(name)
            FROM cows
            GROUP BY health_status
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        summary = "🏥 HEALTH SUMMARY\n\n"
        for status, count, names in results:
            summary += f"{status}: {count} cow(s) - {names}\n"
        
        return summary
    except Exception as e:
        return f"Error: {e}"

def get_farm_statistics():
    """Get overall farm statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM cows')
        total_cows = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vaccinations WHERE next_due <= date("now", "+30 days")')
        due_vaccinations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM cows WHERE health_status = "Healthy"')
        healthy_cows = cursor.fetchone()[0]
        
        conn.close()
        
        stats = f"📈 FARM STATISTICS\n\n"
        stats += f"Total Cows: {total_cows}\n"
        stats += f"Healthy Cows: {healthy_cows}\n"
        stats += f"Vaccinations Due (30 days): {due_vaccinations}\n"
        
        return stats
    except Exception as e:
        return f"Error: {e}"

# --- HEALTH ALERTS (IMPRESSIVE FEATURE 3) ---
def check_and_generate_alerts():
    """Auto-check and generate alerts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        alerts = []
        
        # Check for upcoming vaccinations
        cursor.execute('''
            SELECT c.name, v.vaccine_name, v.next_due
            FROM vaccinations v
            JOIN cows c ON c.id = v.cow_id
            WHERE v.next_due <= date("now", "+7 days")
        ''')
        
        due_cows = cursor.fetchall()
        for name, vaccine, due_date in due_cows:
            alert = f"⚠️ ALERT: {name} needs {vaccine} vaccine on {due_date}"
            alerts.append(alert)
            
            # Save to alerts table
            cursor.execute('''
                INSERT OR IGNORE INTO alerts (cow_id, alert_type, message, date)
                SELECT id, 'Vaccination Due', ?, ?
                FROM cows WHERE name = ?
            ''', (alert, due_date, name))
        
        # Check for health issues
        cursor.execute('SELECT name, health_status FROM cows WHERE health_status != "Healthy"')
        sick_cows = cursor.fetchall()
        
        for name, status in sick_cows:
            alert = f"⚠️ HEALTH ALERT: {name} is {status}. Needs veterinary attention!"
            alerts.append(alert)
        
        conn.commit()
        conn.close()
        
        if alerts:
            return "\n".join(alerts)
        return "✅ No alerts at this time. All cows are healthy and vaccinations are up to date!"
    
    except Exception as e:
        return f"Error checking alerts: {e}"

def get_unread_alerts():
    """Get unread alerts from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.message, a.date, c.name
            FROM alerts a
            JOIN cows c ON c.id = a.cow_id
            WHERE a.is_read = 0
            ORDER BY a.date DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            alerts = "🔔 UNREAD ALERTS\n\n"
            for message, date, name in results:
                alerts += f"{message}\n   Date: {date}\n\n"
            return alerts
        return "No unread alerts"
    except Exception as e:
        return f"Error: {e}"

# --- EXPORT REPORTS (IMPRESSIVE FEATURE 4) ---
def export_to_excel():
    """Export all data to Excel"""
    try:
        conn = get_db_connection()
        
        # Read all tables
        cows_df = pd.read_sql_query("SELECT * FROM cows", conn)
        vaccines_df = pd.read_sql_query("SELECT * FROM vaccinations", conn)
        alerts_df = pd.read_sql_query("SELECT * FROM alerts", conn)
        
        conn.close()
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            cows_df.to_excel(writer, sheet_name='Cows', index=False)
            vaccines_df.to_excel(writer, sheet_name='Vaccinations', index=False)
            alerts_df.to_excel(writer, sheet_name='Alerts', index=False)
        
        return output.getvalue()
    except Exception as e:
        return None

# --- OFFLINE SYNC (IMPRESSIVE FEATURE 5) ---
def sync_offline_activities():
    """Sync offline activities when online"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM activities WHERE synced = 0')
        pending = cursor.fetchall()
        
        if pending:
            # In real implementation, this would upload to cloud
            # For demo, just mark as synced
            cursor.execute('UPDATE activities SET synced = 1 WHERE synced = 0')
            conn.commit()
            conn.close()
            return f"✅ Synced {len(pending)} offline activities"
        
        conn.close()
        return "No pending activities to sync"
    except Exception as e:
        return f"Sync error: {e}"

# ============================================
# VOICE FUNCTIONS (STT & TTS)
# ============================================

def listen_to_farmer(selected_language):
    recognizer = sr.Recognizer()
    language_code = LANGUAGES[selected_language]
    
    try:
        with sr.Microphone() as source:
            st.info(f"🎤 Listening in {selected_language}... Speak now (5 seconds)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            st.success("✅ Got it!")
            text = recognizer.recognize_google(audio, language=language_code)
            return text
    except sr.WaitTimeoutError:
        return "ERROR: No speech detected"
    except sr.UnknownValueError:
        return "ERROR: Could not understand"
    except sr.RequestError:
        return "ERROR: Need internet connection"
    except Exception as e:
        return f"ERROR: {e}"

def speak_in_background(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'hindi' in voice.name.lower() or 'indian' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech error: {e}")

def speak_to_farmer(text):
    if len(text) > 300:
        text = text[:300] + "..."
    thread = threading.Thread(target=speak_in_background, args=(text,))
    thread.daemon = True
    thread.start()

# ============================================
# INTELLIGENT VOICE COMMAND PARSER
# ============================================

def process_voice_command(command, language):
    """Parse and execute voice commands"""
    cmd = command.lower()
    
    # ADD COW command
    if any(word in cmd for word in ['add cow', 'new cow', 'नई गाय', 'जोड़ो']):
        # Parse: "add cow Lakshmi, Gir breed, Ramesh, 5 years"
        import re
        # Simple parsing - in production, use NLP
        words = cmd.split()
        return "ADD_COW_MODE"
    
    # UPDATE HEALTH command
    elif any(word in cmd for word in ['update health', 'health update', 'स्वास्थ्य अपडेट']):
        return "UPDATE_HEALTH_MODE"
    
    # DELETE COW command
    elif any(word in cmd for word in ['delete cow', 'remove cow', 'हटाओ']):
        return "DELETE_COW_MODE"
    
    # REPORT commands
    elif any(word in cmd for word in ['vaccination report', 'टीका रिपोर्ट', 'vaccine report']):
        return get_vaccination_report()
    
    elif any(word in cmd for word in ['health summary', 'स्वास्थ्य सारांश', 'health report']):
        return get_health_summary()
    
    elif any(word in cmd for word in ['farm statistics', 'statistics', 'आंकड़े', 'stat']):
        return get_farm_statistics()
    
    # ALERT commands
    elif any(word in cmd for word in ['check alerts', 'alerts', 'सूचना', 'alert check']):
        return check_and_generate_alerts()
    
    elif any(word in cmd for word in ['unread alerts', 'new alerts', 'नई सूचना']):
        return get_unread_alerts()
    
    # SYNC command
    elif any(word in cmd for word in ['sync', 'सिंक', 'offline sync']):
        return sync_offline_activities()
    
    # COW INFO (basic)
    else:
        # Check if asking about specific cow
        cow_names = ['lakshmi', 'ganga', 'kali', 'kamadhenu']
        for cow in cow_names:
            if cow in cmd:
                if any(word in cmd for word in ['vaccination', 'vaccine', 'टीका']):
                    return get_vaccination_info(cow)
                else:
                    return get_cow_info(cow)
        
        return "I can help you with: Add Cow, Update Health, Delete Cow, Vaccination Report, Health Summary, Farm Statistics, Check Alerts, or Sync. What would you like to do?"

# ============================================
# MAIN APP UI
# ============================================

# Initialize session state
if 'current_answer' not in st.session_state:
    st.session_state['current_answer'] = ""
if 'mode' not in st.session_state:
    st.session_state['mode'] = "normal"
if 'selected_language' not in st.session_state:
    st.session_state['selected_language'] = "English"

# Language selector
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    selected_lang = st.selectbox("🌍 Select Language / भाषा चुनें", options=list(LANGUAGES.keys()), index=0)
    st.session_state['selected_language'] = selected_lang

# Mode indicator
with col2:
    if st.session_state['mode'] != "normal":
        st.info(f"📝 Mode: {st.session_state['mode']}")

# Sync button
with col3:
    if st.button("🔄 Sync Offline Data", use_container_width=True):
        result = sync_offline_activities()
        st.success(result)

st.markdown("---")

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎤 Voice Assistant", 
    "➕ Add/Update Cow", 
    "📊 Reports", 
    "🔔 Alerts",
    "📁 Export Data"
])

# ============================================
# TAB 1: VOICE ASSISTANT
# ============================================
with tab1:
    st.subheader("🎤 Smart Voice Assistant")
    
    # Voice input
    if st.button("🎤 Click & Speak", use_container_width=True):
        with st.spinner("Listening..."):
            command = listen_to_farmer(selected_lang)
            
            if "ERROR" not in command:
                st.success(f"📝 You said: {command}")
                
                # Process command
                response = process_voice_command(command, selected_lang)
                
                # Handle special modes
                if response == "ADD_COW_MODE":
                    st.session_state['mode'] = "add_cow"
                    response = "Please say: cow name, breed, owner, age (example: Lakshmi, Gir, Ramesh, 5)"
                elif response == "UPDATE_HEALTH_MODE":
                    st.session_state['mode'] = "update_health"
                    response = "Please say: cow name and health status (example: Lakshmi, Healthy)"
                elif response == "DELETE_COW_MODE":
                    st.session_state['mode'] = "delete_cow"
                    response = "Please say: cow name to delete (example: delete Lakshmi)"
                
                st.info(f"🤖 {response}")
                st.session_state['current_answer'] = response
            else:
                st.error(command)
    
    # Mode-specific voice input
    if st.session_state['mode'] != "normal":
        st.subheader(f"📝 {st.session_state['mode'].replace('_', ' ').title()} Mode")
        
        if st.button("🎤 Speak Details", use_container_width=True):
            with st.spinner("Listening..."):
                details = listen_to_farmer(selected_lang)
                
                if "ERROR" not in details:
                    st.success(f"📝 You said: {details}")
                    
                    if st.session_state['mode'] == "add_cow":
                        # Parse details (simple version)
                        parts = [p.strip() for p in details.split(',')]
                        if len(parts) >= 4:
                            name, breed, owner, age = parts[0], parts[1], parts[2], parts[3]
                            response = add_cow_by_voice(name, breed, owner, age)
                        else:
                            response = "Please say: name, breed, owner, age (separated by commas)"
                    
                    elif st.session_state['mode'] == "update_health":
                        parts = [p.strip() for p in details.split(',')]
                        if len(parts) >= 2:
                            name, health = parts[0], parts[1]
                            response = update_cow_health_by_voice(name, health)
                        else:
                            response = "Please say: cow name, health status (separated by comma)"
                    
                    elif st.session_state['mode'] == "delete_cow":
                        response = delete_cow_by_voice(details)
                    
                    st.info(f"🤖 {response}")
                    st.session_state['current_answer'] = response
                    st.session_state['mode'] = "normal"
                else:
                    st.error(details)
        
        if st.button("Cancel Mode"):
            st.session_state['mode'] = "normal"
            st.rerun()
    
    # Text input fallback
    text_command = st.text_input("Or type your command:")
    if text_command:
        response = process_voice_command(text_command, selected_lang)
        st.info(f"🤖 {response}")
        st.session_state['current_answer'] = response
    
    # Voice output
    if st.button("🔊 Listen to Response", use_container_width=True):
        if st.session_state['current_answer']:
            speak_to_farmer(st.session_state['current_answer'])
            st.success("🔊 Speaking...")
        else:
            st.warning("No response to speak")

# ============================================
# TAB 2: ADD/UPDATE COW (Manual)
# ============================================
with tab2:
    st.subheader("➕ Add New Cow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Cow Name")
        breed = st.selectbox("Breed", ["Gir", "Sahiwal", "Jersey", "Holstein", "Other"])
        age = st.number_input("Age (years)", min_value=0, max_value=20, value=1)
    
    with col2:
        owner = st.text_input("Owner Name")
        health = st.selectbox("Health Status", ["Healthy", "Needs Checkup", "Sick", "Pregnant", "New"])
    
    if st.button("💾 Add Cow", use_container_width=True):
        if name and owner:
            result = add_cow_by_voice(name, breed, owner, age)
            st.success(result)
        else:
            st.warning("Please fill name and owner")
    
    st.markdown("---")
    
    st.subheader("🔄 Update Cow Health")
    cow_to_update = st.selectbox("Select Cow", ["Lakshmi", "Ganga", "Kali", "Kamadhenu"])
    new_health = st.selectbox("New Health Status", ["Healthy", "Needs Checkup", "Sick", "Pregnant", "Recovered"])
    
    if st.button("🩺 Update Health", use_container_width=True):
        result = update_cow_health_by_voice(cow_to_update, new_health)
        st.success(result)

# ============================================
# TAB 3: REPORTS
# ============================================
with tab3:
    st.subheader("📊 Farm Reports")
    
    report_type = st.radio("Select Report", ["Vaccination Report", "Health Summary", "Farm Statistics"])
    
    if st.button("📄 Generate Report", use_container_width=True):
        if report_type == "Vaccination Report":
            report = get_vaccination_report()
        elif report_type == "Health Summary":
            report = get_health_summary()
        else:
            report = get_farm_statistics()
        
        st.text_area("Report", report, height=300)
        
        if st.button("🔊 Listen to Report"):
            speak_to_farmer(report)

# ============================================
# TAB 4: ALERTS
# ============================================
with tab4:
    st.subheader("🔔 Health & Vaccination Alerts")
    
    if st.button("🔍 Check Alerts Now", use_container_width=True):
        with st.spinner("Checking..."):
            alerts = check_and_generate_alerts()
            st.info(alerts)
            if "⚠️" in alerts:
                speak_to_farmer(alerts)
    
    st.markdown("---")
    
    if st.button("📋 Show Unread Alerts"):
        unread = get_unread_alerts()
        st.info(unread)

# ============================================
# TAB 5: EXPORT DATA
# ============================================
with tab5:
    st.subheader("📁 Export Farm Data")
    
    if st.button("📊 Export to Excel", use_container_width=True):
        excel_data = export_to_excel()
        if excel_data:
            st.download_button(
                label="💾 Download Excel File",
                data=excel_data,
                file_name=f"cow_farm_data_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Excel file ready for download!")
        else:
            st.error("Error generating Excel file")
    
    if st.button("📄 Export Report as Text"):
        report = get_vaccination_report()
        st.download_button(
            label="💾 Download Report",
            data=report,
            file_name=f"vaccination_report_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("💡 Voice Commands You Can Try:")
st.caption("• 'Add cow Lakshmi, Gir, Ramesh, 5' | 'नई गाय लक्ष्मी, गिर, रमेश, 5'")
st.caption("• 'Update health Lakshmi, Healthy' | 'स्वास्थ्य अपडेट लक्ष्मी, स्वस्थ'")
st.caption("• 'Show vaccination report' | 'टीका रिपोर्ट दिखाओ'")
st.caption("• 'Check alerts' | 'सूचना देखो'")
st.caption("• 'Farm statistics' | 'फार्म के आंकड़े'")