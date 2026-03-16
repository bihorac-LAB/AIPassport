import streamlit as st
import cv2
import numpy as np

# --- PAGE CONFIG & PRIVACY WARNING ---
st.set_page_config(page_title="AI Passport: Clinical Demo", layout="wide")

st.sidebar.warning("PRIVACY NOTICE: Please do not upload any images containing Protected Health Information (PHI) or sensitive personal data.")

st.sidebar.title("AI Passport: Clinical Assignment")
activity = st.sidebar.radio(
    "Select Activity:", 
    ["Activity 1: X-ray Edge Detection", "Activity 2: CT vs MRI Analysis"],
    help="Use this menu to navigate between the different parts of your clinical assignment."
)

st.sidebar.divider()

# --- SHARED FUNCTIONS & CONSTANTS ---
def apply_edge_detection(image, low, high):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, low, high)

def adjust_contrast_brightness(image, contrast, brightness):
    # contrast: 1.0-3.0, brightness: -50 to 50
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

# Using the exact same image path for both activities
DEFAULT_IMAGE_PATH = "assets/images/content/Identifying Structures in X-Ray Imaging.png"

# --- ACTIVITY 1: X-RAY ---
if activity == "Activity 1: X-ray Edge Detection":
    st.title("Activity 1: Identifying Structures in X-Ray Imaging")
    
    with st.expander("Instructions", expanded=True):
        st.markdown("""
        1. Observe the default image below or upload your own sample image using the sidebar.
        2. Adjust the **Low Threshold** and **High Threshold** sliders in the sidebar.
        3. Observe how the edge detection algorithm highlights different structures and noise within the image.
        4. Return to Canvas to answer the question: *Why might edge detection alone be insufficient for detecting fractures in an X-ray image?*
        """)
    
    st.sidebar.markdown("### Activity 1 Controls")
    uploaded_file = st.sidebar.file_uploader(
        "Upload an X-ray (Optional)", 
        type=["jpg", "jpeg", "png"], 
        key="xray_up",
        help="Upload a standard image file (JPG or PNG). Ensure no patient data is visible."
    )

    if uploaded_file:
        img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(DEFAULT_IMAGE_PATH)
        if img is None:
            st.error("Please upload an image to begin, or ensure the default image is placed in the correct directory.")
            st.stop()

    low_threshold = st.sidebar.slider(
        "Low Threshold (Sensitivity)", 
        0, 200, 100,
        help="Pixels with an intensity gradient below this value will be discarded. Lowering this increases the noise detected."
    )
    high_threshold = st.sidebar.slider(
        "High Threshold (Edge Strength)", 
        0, 255, 150,
        help="Pixels with an intensity gradient above this value are marked as strong edges. Adjust this to isolate distinct boundaries."
    )
    
    edges = apply_edge_detection(img, low_threshold, high_threshold)

    col1, col2 = st.columns(2)
    col1.image(img, caption="Original Image", use_container_width=True)
    col2.image(edges, caption="Edge Detection Output", use_container_width=True)

# --- ACTIVITY 2: CT vs MRI ---
elif activity == "Activity 2: CT vs MRI Analysis":
    st.title("Activity 2: Comparing CT and MRI for Brain Imaging")
    
    with st.expander("Instructions", expanded=True):
        st.markdown("""
        1. Observe the side-by-side medical scans provided below.
        2. Use the **Contrast** and **Brightness** sliders in the sidebar to adjust the right-hand image.
        3. Notice how adjusting these settings impacts the visibility of dense structures versus soft tissues, simulating the visual difference between a CT scan and an MRI.
        4. Return to Canvas to list the key differences between the modalities and explain their preferred clinical scenarios.
        """)
    
    st.sidebar.markdown("### Activity 2 Controls")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a Scan (Optional)", 
        type=["jpg", "jpeg", "png"], 
        key="brain_up",
        help="Upload a standard image file (JPG or PNG). Ensure no patient data is visible."
    )

    if uploaded_file:
        img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(DEFAULT_IMAGE_PATH)
        if img is None:
            st.error("Please upload a scan to begin, or ensure the default image is in the correct directory.")
            st.stop()

    contrast = st.sidebar.slider(
        "Increase Contrast (Intensity)", 
        1.0, 3.0, 1.2,
        help="Increases the visual difference between the light and dark areas of the scan, helping to distinguish between tissue types."
    )
    brightness = st.sidebar.slider(
        "Brightness", 
        -50, 50, 0,
        help="Adjusts the overall lightness or darkness of the image to reveal hidden details in shadowed areas."
    )

    adjusted_img = adjust_contrast_brightness(img, contrast, brightness)

    col1, col2 = st.columns(2)
    col1.image(img, caption="Baseline Scan (Simulated CT Focus)", use_container_width=True)
    col2.image(adjusted_img, caption="Adjusted Scan (Simulated MRI Focus)", use_container_width=True)
    
    st.info("Observation Tip for Canvas: Compare the baseline image on the left with your adjusted image on the right. High contrast highlights dense bone (typical of a CT), while adjusting brightness and contrast together can reveal variations in soft tissue layers (typical of an MRI).")
