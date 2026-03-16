import streamlit as st
import numpy as np
from skimage.morphology import closing, disk
from skimage.feature import graycomatrix, graycoprops
from PIL import Image
import matplotlib.pyplot as plt
import os

# ------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------
st.set_page_config(page_title="Biomedical Toolkit", layout="wide")

st.sidebar.warning("⚠️ **Confidentiality:** Do not upload patient-identifiable images.")

# ------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------
st.sidebar.title("Toolkit Controls")
tool_choice = st.sidebar.radio("Active Tool", ["Texture Analysis", "Morphological Closing"])

st.sidebar.subheader("Preprocessing")
use_norm = st.sidebar.toggle("Standardize Intensity", value=True, help="Normalizes image to 0-255 range.")

# ------------------------------------------------------------
# TOOL 1: TEXTURE ANALYSIS
# ------------------------------------------------------------
if tool_choice == "Texture Analysis":
    st.title("Pathology Texture Analysis")
    st.sidebar.subheader("Texture Settings")
    dist = st.sidebar.slider("Pixel Distance", 1, 10, 1)
    
    # Selection for sample or upload
    data_mode = st.sidebar.selectbox("Data Source", ["Sample: Malignant", "Sample: Benign", "Upload Custom"])
    
    img_path = None
    if data_mode == "Sample: Malignant":
        img_path = "./data/small_slide_BC.png"
    elif data_mode == "Sample: Benign":
        img_path = "./data/small_slide_noBC.png"
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Pathology Slide", type=["png", "jpg"])

    # Load logic
    image_to_process = None
    if img_path and os.path.exists(img_path):
        image_to_process = Image.open(img_path).convert("L")
    elif 'uploaded_file' in locals() and uploaded_file:
        image_to_process = Image.open(uploaded_file).convert("L")
    elif img_path:
        st.error(f"Sample file not found at {img_path}. Please upload an image.")

    if image_to_process:
        img_array = np.array(image_to_process)
        if use_norm:
            img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min() + 1e-5) * 255).astype(np.uint8)

        glcm = graycomatrix(img_array, distances=[dist], angles=[0], levels=256, symmetric=True, normed=True)
        contrast = graycoprops(glcm, 'contrast')[0, 0]
        correlation = graycoprops(glcm, 'correlation')[0, 0]

        col1, col2 = st.columns([2, 1])
        col1.image(img_array, caption=f"Analyzing: {data_mode}", use_container_width=True)
        with col2:
            st.metric("Contrast", f"{contrast:.2f}")
            st.metric("Correlation", f"{correlation:.4f}")

# ------------------------------------------------------------
# TOOL 2: MORPHOLOGICAL CLOSING
# ------------------------------------------------------------
else:
    st.title("Morphological Enhancement")
    
    st.sidebar.subheader("Morphology Settings")
    radius = st.sidebar.slider("Disk Radius", 1, 15, 5)
    
    # Toggle between sample and upload
    use_sample = st.sidebar.checkbox("Use Sample Ultrasound", value=True)
    
    img = None
    if use_sample:
        sample_path = "./data/breast_US.png"
        if os.path.exists(sample_path):
            img = np.array(Image.open(sample_path).convert("L"))
        else:
            # FALLBACK: Generate a synthetic ultrasound 'phantom' if file is missing
            st.sidebar.info("Sample file not found. Generating synthetic phantom...")
            img = np.zeros((300, 300), dtype=np.uint8)
            # Create a 'lesion' with some noise/gaps
            rr, cc = np.ogrid[:300, :300]
            mask = (rr - 150)**2 + (cc - 150)**2 < 80**2
            img[mask] = 180
            # Introduce 'gaps' (noise) to show how closing works
            noise = np.random.choice([0, 1], size=img.shape, p=[0.05, 0.95])
            img = (img * noise).astype(np.uint8)
    else:
        uploaded_us = st.sidebar.file_uploader("Upload Ultrasound", type=["png", "jpg"])
        if uploaded_us:
            img = np.array(Image.open(uploaded_us).convert("L"))

    if img is not None:
        if use_norm:
            img = ((img - img.min()) / (img.max() - img.min() + 1e-5) * 255).astype(np.uint8)
            
        closed_img = closing(img, disk(radius))
        
        col1, col2 = st.columns(2)
        col1.image(img, caption="Original (with noise/gaps)", use_container_width=True)
        col2.image(closed_img, caption=f"Closed (Radius {radius})", use_container_width=True)
        
        

        st.subheader("Action Map (What changed?)")
        fig, ax = plt.subplots()
        diff = closed_img.astype(float) - img.astype(float)
        im = ax.imshow(diff, cmap="magma")
        plt.colorbar(im)
        ax.axis('off')
        st.pyplot(fig)
        st.caption("The bright areas indicate where the Closing operation filled in dark holes.")
    else:
        st.info("Please upload an ultrasound scan to begin.")
