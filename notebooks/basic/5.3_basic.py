import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import psutil
import os

# --- MONITORING UTILITY ---
def get_system_usage():
    """Fetches CPU and Memory usage for the current process."""
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.1)
    return cpu_percent, mem_mb

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Biomedical Image Analysis Monitor", layout="wide")

# --- INSTRUCTIONS SECTION ---
with st.expander("📖 Instructions & Learning Objectives", expanded=True):
    st.markdown("""
    **Welcome to Microskill 3!** In this interactive module, you will:
    1. **Analyze Noise:** Observe how different algorithms react to synthetic and real-world noise.
    2. **Parameter Tuning:** Experiment with kernel sizes and thresholds to find the 'goldilocks' zone for edge detection.
    3. **Automated Segmentation:** Compare manual thresholding logic to Otsu’s automated method.
    
    **Task:** Adjust the sliders in the sidebar and use the 'Reveal Logic' buttons under each result to check your understanding against the notebook solutions.
    """)

# Sidebar for parameters
st.sidebar.header("Processing Parameters")
mode = st.sidebar.radio(
    "Choose a mode:",
    ("Synthetic Image", "Upload Image"),
    help="Select 'Synthetic' to replicate the notebook rectangle or 'Upload' to test real-world robustness."
)

noise_level = st.sidebar.slider("Noise Level", 0, 100, 50, help="Controls the random intensity variation added to the pixels.")
kernel_size = st.sidebar.slider("Sobel Kernel Size", 3, 11, 5, 2, help="Size of the derivative window. Larger kernels are smoother but less precise.")
threshold1 = st.sidebar.slider("Canny Threshold 1", 0, 255, 100, help="Lower bound for hysteresis thresholding.")
threshold2 = st.sidebar.slider("Canny Threshold 2", 0, 255, 200, help="Upper bound for hysteresis thresholding.")
blur_sigma = st.sidebar.slider("Gaussian Blur Sigma", 0.0, 5.0, 1.0, help="Standard deviation for the Gaussian filter used before Otsu.")
colormap = st.sidebar.selectbox("Colormap", ["gray", "viridis", "plasma", "magma", "inferno"], help="Visual mapping of intensity.")

# --- PERFORMANCE METRICS ---
st.sidebar.markdown("---")
st.sidebar.subheader("App Performance")
cpu, mem = get_system_usage()
col_cpu, col_mem = st.sidebar.columns(2)
col_cpu.metric("CPU Usage", f"{cpu}%")
col_mem.metric("Memory", f"{mem:.1f} MB")

# --- MAIN LOGIC ---
st.warning("Reminder: Do not upload any sensitive or personal health data (PHI).")

if mode == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img = np.array(image)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        st.info("Awaiting image upload...")
        img = None
else:
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(img, (30, 30), (70, 70), 255, -1)
    noise = np.random.randint(0, noise_level, (100, 100), dtype=np.uint8)
    img = cv2.add(img, noise)

if img is not None:
    # 1. Edge Detection Logic
    sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=kernel_size)
    sobel_edges = cv2.magnitude(sobel_x, sobel_y)
    canny_edges = cv2.Canny(img, threshold1, threshold2)
    
    # 2. Otsu's Thresholding Logic (Problem 3.2)
    blurred = cv2.GaussianBlur(img, (5, 5), blur_sigma)
    _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Normalize Sobel for display
    sobel_edges = cv2.normalize(sobel_edges, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    # Display 4-Column Layout
    st.header("Analysis Results")
    cols = st.columns(4)
    
    titles = ["Input Image", "Sobel Filter", "Canny Edge", "Otsu Threshold"]
    images = [img, sobel_edges, canny_edges, otsu_thresh]
    
    # Reveal Explanations (Aligned with Notebook Answers)
    explanations = [
        "Raw input data. In medical settings, noise can obscure critical diagnostic details.",
        "Sobel is sensitive to noise because it calculates the intensity gradient directly.",
        "Canny is more robust as it uses built-in filtering and non-maximum suppression to find clean edges.",
        "Otsu's method automatically calculates the optimal threshold to separate foreground from background."
    ]

    for i, col in enumerate(cols):
        with col:
            st.subheader(titles[i])
            fig, ax = plt.subplots()
            ax.imshow(images[i], cmap=colormap)
            ax.axis('off')
            st.pyplot(fig)
            
            # The "Reveal" Feature for Active Recall
            if st.checkbox(f"Reveal Logic {i+1}", key=f"reveal_{i}"):
                st.info(explanations[i])
