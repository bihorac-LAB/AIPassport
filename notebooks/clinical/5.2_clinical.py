import streamlit as st
import numpy as np
from PIL import Image
from skimage import transform, img_as_ubyte
from skimage.util import random_noise
import cv2

# ==============================
# App Setup & Global Warnings
# ==============================
st.set_page_config(page_title="Image Processing Suite", layout="wide")

st.sidebar.title("Image Processing Suite")

# Data Privacy Warning
st.sidebar.warning(
    "**Privacy Notice:**\n\n"
    "This is an educational sandbox. Please **do not upload sensitive clinical data**, "
    "personally identifiable information (PII), or Protected Health Information (PHI)."
)

app_mode = st.sidebar.radio(
    "Select App Module",
    [
        "Image Processing & Augmentation",
        "Edge Detection",
        "Motion Blur Simulation",
        "Salt & Pepper Noise & Denoising"
    ],
    help="Navigate between different image preprocessing modules."
)

st.sidebar.divider()

# ==============================
# GLOBAL Image Selection
# ==============================
st.sidebar.header("Global Image Selection")
image_source = st.sidebar.radio(
    "Select Image Source:",
    ("Fluorescence (IFCells)", "Brightfield (BloodSmear)", "Upload Image"),
    help="Choose an image once. It will stay loaded as you switch between the different modules above."
)

BF_PATH = "assets/BloodSmear.png"
IF_PATH = "assets/IFCells.jpg"
uploaded_file = None

if image_source == "Upload Image":
    uploaded_file = st.sidebar.file_uploader(
        "Upload an image", type=["jpg", "png"],
        help="Supported formats: JPG, PNG. Remember: No sensitive data!"
    )

# Helper function to load images
@st.cache_data
def load_image(file_upload, choice):
    if file_upload is not None:
        return np.array(Image.open(file_upload).convert("RGB"))
    elif choice == "Fluorescence (IFCells)":
        return np.array(Image.open(IF_PATH).convert("RGB"))
    elif choice == "Brightfield (BloodSmear)":
        return np.array(Image.open(BF_PATH).convert("RGB"))
    return None

img = load_image(uploaded_file, image_source)

if img is None:
    st.info("Please select or upload an image in the sidebar to begin.")
    st.stop()

# ==============================
# 1. Image Processing & Augmentation
# ==============================
if app_mode == "Image Processing & Augmentation":
    st.title("Image Processing & Augmentation")
    st.info("**Instructions:** Adjust the sliders to scale pixel intensities (normalization) or apply spatial transformations (augmentation).")

    with st.expander("What to Expect (Click to reveal)"):
        st.write(
            "**Normalization:** Lowering the factor will uniformly darken the image. In real model training, standardizing all images to a [0, 1] range ensures stable neural network gradients.\n\n"
            "**Augmentation:** Flipping and rotating the image changes its orientation without altering the underlying cellular features. This forces machine learning models to learn the actual shape of the cells rather than memorizing their position on the slide."
        )

    normalization_factor = st.sidebar.slider("Normalization Factor", 0.0, 1.0, 1.0)
    rotation_angle = st.sidebar.slider("Rotation Angle (degrees)", -30.0, 30.0, 0.0)
    flip_horizontal = st.sidebar.checkbox("Flip Horizontal")
    flip_vertical = st.sidebar.checkbox("Flip Vertical")

    # True Normalization: Scale to [0.0, 1.0] float array
    img_processed = img.astype(np.float32) / 255.0
    img_processed = img_processed * normalization_factor
    
    # Augmentation
    img_processed = transform.rotate(img_processed, rotation_angle, mode='wrap')
    if flip_horizontal:
        img_processed = np.fliplr(img_processed)
    if flip_vertical:
        img_processed = np.flipud(img_processed)

    # Display
    col1, col2 = st.columns(2)
    col1.subheader("Original Image")
    col1.image(img, channels="RGB", use_container_width=True)
    col2.subheader("Processed Image")
    col2.image(img_processed, channels="RGB", use_container_width=True, clamp=True)

# ==============================
# 2. Edge Detection
# ==============================
elif app_mode == "Edge Detection":
    st.title("Edge Detection with Filters")
    st.info("**Instructions:** Apply spatial filters to extract structural features like cell walls.")

    with st.expander("What to Expect (Click to reveal)"):
        st.write(
            "**Directional Edges:** The horizontal filter will highlight the top and bottom boundaries of the cells, while the vertical filter will highlight the left and right boundaries.\n\n"
            "**Magnitude & Sobel:** These combine the horizontal and vertical gradients into a single image, creating a bright, continuous outline around the cellular structures. This is a critical first step for automated cell counting or segmentation algorithms."
        )
        st.write("")

    st.sidebar.header("Filter Settings")
    horiz_strength = st.sidebar.slider("Horizontal Filter Strength", 0.5, 5.0, 1.0)
    vert_strength = st.sidebar.slider("Vertical Filter Strength", 0.5, 5.0, 1.0)
    sobel_strength = st.sidebar.slider("Sobel Filter Strength", 0.5, 5.0, 1.0)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    base_horiz = np.array([[1,1,1],[0,0,0],[-1,-1,-1]], np.float32)
    base_vert = np.array([[1,0,-1],[1,0,-1],[1,0,-1]], np.float32)
    
    img_horiz = cv2.filter2D(gray, cv2.CV_64F, horiz_strength * base_horiz)
    img_vert = cv2.filter2D(gray, cv2.CV_64F, vert_strength * base_vert)
    
    E_custom = np.sqrt(img_horiz**2 + img_vert**2)
    E_custom = cv2.normalize(E_custom, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = np.sqrt(sobelx**2 + sobely**2)
    sobel = cv2.normalize(sobel, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    sobel = cv2.convertScaleAbs(sobel * sobel_strength)

    display_horiz = cv2.convertScaleAbs(img_horiz)
    display_vert = cv2.convertScaleAbs(img_vert)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.image(gray, caption="Original Grayscale", use_container_width=True)
    col2.image(display_horiz, caption="Horizontal Edges", use_container_width=True)
    col3.image(display_vert, caption="Vertical Edges", use_container_width=True)
    col4.image(E_custom, caption="Edge Magnitude", use_container_width=True)
    col5.image(sobel, caption="Sobel Edges", use_container_width=True)

# ==============================
# 3. Motion Blur Simulation
# ==============================
elif app_mode == "Motion Blur Simulation":
    st.title("Motion Blur Simulation")
    st.info("**Instructions:** Use this tool to simulate imaging artifacts caused by camera shake or stage movement.")

    with st.expander("What to Expect (Click to reveal)"):
        st.write(
            "You should expect the image to look 'smeared'. Increasing the **Blur Length** makes the smear stretch further, simulating a faster or longer physical movement during image capture. "
            "Changing the **Blur Angle** will alter the exact trajectory (e.g., diagonal, horizontal, or vertical) of that smear."
        )

    st.sidebar.header("Motion Blur Settings")
    blur_length = st.sidebar.slider("Blur Length", 3, 50, 20)
    blur_angle = st.sidebar.slider("Blur Angle (degrees)", 0, 180, 45)

    kernel = np.zeros((blur_length, blur_length))
    kernel[int((blur_length-1)/2), :] = np.ones(blur_length)
    M = cv2.getRotationMatrix2D((blur_length/2-0.5, blur_length/2-0.5), blur_angle, 1)
    kernel = cv2.warpAffine(kernel, M, (blur_length, blur_length))
    kernel /= blur_length

    img_motion = cv2.filter2D(img, -1, kernel)
    
    col1, col2 = st.columns(2)
    col1.image(img, caption="Original Image", use_container_width=True)
    col2.image(img_motion, caption="With Motion Blur", use_container_width=True)

# ==============================
# 4. Salt & Pepper Noise & Denoising
# ==============================
elif app_mode == "Salt & Pepper Noise & Denoising":
    st.title("Salt & Pepper Noise and Denoising")
    st.info("**Instructions:** Introduce random sensor noise and attempt to clean it up using different filtering algorithms.")

    with st.expander("What to Expect (Click to reveal)"):
        st.write(
            "**The Noise:** You will see random pure black and pure white pixels scattered across the image, common in faulty imaging sensors.\n\n"
            "**The Fix:** You should expect the **Median filter** to clean this up beautifully, as it replaces the extreme noise pixels with the middle value of their neighbors, keeping the cell edges sharp. "
            "Conversely, the **Gaussian filter** will likely just blur the noise into the surrounding pixels, making the image look muddy. This demonstrates why Median filters are strictly preferred for this specific artifact."
        )
        st.write("")

    st.sidebar.header("Noise Settings")
    noise_amount = st.sidebar.slider("Noise Amount", 0.0, 0.2, 0.05)
    
    st.sidebar.header("Denoising Filter")
    filter_type = st.sidebar.radio("Filter Type", ["Median", "Gaussian"])
    
    if filter_type == "Median":
        filter_strength = st.sidebar.slider("Kernel Size (odd only)", 3, 11, 3, step=2)
    else:
        filter_strength = st.sidebar.slider("Gaussian Sigma", 0.5, 5.0, 1.0, step=0.5)

    noisy = random_noise(img, mode="s&p", amount=noise_amount)
    noisy_u8 = img_as_ubyte(noisy)
    
    if filter_type == "Median":
        denoised = cv2.medianBlur(noisy_u8, filter_strength)
    else:
        denoised = cv2.GaussianBlur(noisy_u8, (5,5), filter_strength)

    col1, col2, col3 = st.columns(3)
    col1.image(img, caption="Original", use_container_width=True)
    col2.image(noisy, caption="With Salt & Pepper Noise", use_container_width=True, clamp=True)
    col3.image(denoised, caption=f"Denoised ({filter_type})", use_container_width=True)
