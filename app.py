# Alternative app.py WITHOUT face_recognition
import streamlit as st
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import os

st.set_page_config(page_title="Cattle ID System", page_icon="🐄", layout="wide")
st.title("🐄 AI Cattle Identification System")

# Load database
df = pd.read_csv('cows.csv')

# Load and encode images using ORB (OpenCV's feature detector)
@st.cache_resource
def load_cow_features():
    orb = cv2.ORB_create(nfeatures=1000)
    cow_features = []
    cow_ids = []
    cow_names = []
    
    for cow_folder in os.listdir('known'):
        folder_path = os.path.join('known', cow_folder)
        if os.path.isdir(folder_path):
            cow_id = int(cow_folder.replace('cow', ''))
            cow_info = df[df['id'] == cow_id]
            cow_name = cow_info.iloc[0]['name'] if len(cow_info) > 0 else f"Cow {cow_id}"
            
            for img_file in os.listdir(folder_path):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(folder_path, img_file)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    kp, des = orb.detectAndCompute(img, None)
                    if des is not None:
                        cow_features.append(des)
                        cow_ids.append(cow_id)
                        cow_names.append(cow_name)
    
    return orb, cow_features, cow_ids, cow_names

# Load features
with st.spinner("Loading AI model..."):
    orb, cow_features, cow_ids, cow_names = load_cow_features()

st.success(f"✅ Ready! {len(set(cow_ids))} cows registered")

# Upload image
uploaded_file = st.file_uploader("Upload muzzle photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    # Convert to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Extract features from uploaded image
    kp_query, des_query = orb.detectAndCompute(img_gray, None)
    
    if des_query is None:
        st.error("❌ Could not detect muzzle pattern. Please take a clearer photo.")
    else:
        # Compare with known cows
        best_match = None
        best_score = 0
        best_name = None
        best_id = None
        
        # Use BFMatcher for feature matching
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        for i, train_des in enumerate(cow_features):
            matches = bf.match(des_query, train_des)
            score = len(matches)
            
            if score > best_score:
                best_score = score
                best_match = i
        
        if best_score > 10:  # Threshold for match
            cow_id = cow_ids[best_match]
            cow_name = cow_names[best_match]
            cow_info = df[df['id'] == cow_id].iloc[0]
            
            st.success(f"✅ **Identified: {cow_name}**")
            st.write(f"🐄 Owner: {cow_info['owner']}")
            st.write(f"💉 Last Vaccination: {cow_info['vaccination']}")
            st.write(f"📋 Insurance Status: {cow_info['insurance']}")
            st.write(f"🐮 Breed: {cow_info['breed']}")
        else:
            st.warning("⚠️ Cow not found in database")