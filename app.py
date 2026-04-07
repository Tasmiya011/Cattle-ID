import streamlit as st
import pandas as pd
import threading
import time
from offline_db import get_all_cows, add_cow, is_online, save_offline_conversation, get_unsynced_conversations, mark_conversation_synced

# Inject IndexedDB JavaScript
def inject_js():
    with open("static/offline_cache.js", "r") as f:
        js_code = f.read()
    st.components.v1.html(f"<script>{js_code}</script>", height=0)

inject_js()

st.title("🐄 Cattle ID - Offline Test with Auto-Sync")

# Load cows from CSV into offline database (only once)
if 'loaded' not in st.session_state:
    df = pd.read_csv('cows.csv')
    for _, row in df.iterrows():
        add_cow(row.to_dict())
    st.session_state.loaded = True
    st.success("Cows loaded into offline DB")

# Background sync thread
def background_sync():
    while True:
        if is_online():
            unsynced = get_unsynced_conversations()
            if unsynced:
                for conv_id, ts, q, a in unsynced:
                    # Here you would send to cloud/Gemini API
                    print(f"Syncing: {q} -> {a}")
                    mark_conversation_synced(conv_id)
                st.toast(f"Synced {len(unsynced)} offline conversations", icon="☁️")
        time.sleep(30)

if 'sync_started' not in st.session_state:
    thread = threading.Thread(target=background_sync, daemon=True)
    thread.start()
    st.session_state.sync_started = True

# Show cows
cows = get_all_cows()
st.write(f"Total cows: {len(cows)}")
st.dataframe(pd.DataFrame(cows))

# Internet status
if is_online():
    st.success("✅ You are ONLINE")
else:
    st.warning("⚠️ You are OFFLINE")

# Show pending sync count
unsynced_count = len(get_unsynced_conversations())
if unsynced_count > 0:
    st.info(f"📤 {unsynced_count} offline conversations waiting to sync")

# Question box
question = st.text_input("Ask a question:")
if question:
    if is_online():
        answer = f"Online reply to: {question}"
    else:
        answer = "Offline mode: I saved your question. It will sync when internet returns."
        save_offline_conversation(question, answer)
    st.write(f"Answer: {answer}")