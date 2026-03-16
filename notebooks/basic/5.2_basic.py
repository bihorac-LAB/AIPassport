import streamlit as st
import skimage.io as io
import matplotlib.pyplot as plt
import numpy as np
from skimage import img_as_float
import cv2  # Import OpenCV
from skimage import exposure
import os  # Import the os module

# --- Set page config for a modern look ---
st.set_page_config(
    page_title="Image Transformation Exercises",
    page_icon=":camera:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Images ---
@st.cache_data  # Cache the images to avoid reloading on every interaction
def load_images():
    IF_image_path = "assets/IFCells.jpg"
    mandrill_image = io.imread("http://sipi.usc.edu/database/download.php?vol=misc&img=4.2.03")
    
    # Handle local file loading safely
    try:
        IF = io.imread(IF_image_path)
        kidney_mri = io.imread("assets/kidney_mri.jpg")  
        breast_img = cv2.imread('assets/breast.png', cv2.IMREAD_GRAYSCALE)  
        I_low_contrast = io.imread("assets/low_contrast2.jpg")
    except FileNotFoundError:
        st.error("One or more local images are missing. Please ensure the 'assets' folder is populated.")
        return None, mandrill_image, None, None, None

    # Ensure images have 3 channels (RGB)
    if IF is not None and IF.shape[-1] == 4:
        IF = IF[:, :, :3]
    if mandrill_image.shape[-1] == 4:
        mandrill_image = mandrill_image[:, :, :3]

    return IF, mandrill_image, kidney_mri, breast_img, I_low_contrast

IF, mandrill_image, kidney_mri, breast_img, I_low_contrast = load_images()

# --- Disclaimer ---
st.warning("This is a public application. Please do not upload any sensitive or private data.")

# --- Sidebar for Section Selection ---
st.sidebar.title("Section Selection")
selected_section = st.sidebar.radio(
    "Choose a Section:",
    (
        "Channel Separation",
        "Gamma Correction",
        "Contrast Adjustment",
        "Negative Transformation",
        "Histogram Equalization",
        "CLAHE",
        "Non-linear Intensity Transformation",
    )
)

# --- Image Selection ---
image_choice = st.sidebar.radio(
    "Select Image:",
    ("Mandrill", "Fluorescence", "Kidney MRI")
)

if image_choice == "Mandrill":
    img = mandrill_image
elif image_choice == "Fluorescence":
    img = IF
else:
    img = kidney_mri

# --- Image Upload ---
uploaded_file = st.sidebar.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = io.imread(uploaded_file)  # Load the uploaded image
    st.sidebar.success("Image uploaded successfully!")

# --- Section Content ---

if selected_section == "Channel Separation":
    st.header("Channel Separation")
    
    st.info("""
    **Instructions:**
    1. Select an RGB image (like the Mandrill or Fluorescence image).
    2. Use the dropdown to isolate and view the Red, Green, or Blue channels independently.
    """)
    
    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("By separating the image into its RGB channels, you can analyze their individual intensity distributions. In scientific imaging (like fluorescence microscopy), specific channels often correspond to different biological markers. Visualizing them separately makes it easier to analyze specific structures without interference from other channels.")

    if img is not None and img.ndim == 3:
        R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    else:
        st.warning("Please select an RGB image for channel separation.")
        R, G, B = 0, 0, 0

    channel_choice = st.selectbox(
        "Select Channel:",
        ("Red", "Green", "Blue"),
        help="Select which color matrix to visualize."
    )

    if channel_choice == "Red":
        channel_image = R
        cmap = "Reds"
    elif channel_choice == "Green":
        channel_image = G
        cmap = "Greens"
    else:
        channel_image = B
        cmap = "Blues"

    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    ax.imshow(channel_image, cmap=cmap)
    ax.set_title(f"{channel_choice} Channel")
    ax.axis('off')
    st.pyplot(fig)

elif selected_section == "Gamma Correction":
    st.header("Gamma Correction")
    
    st.info("""
    **Instructions:**
    1. Use the slider to adjust the **Gamma** value.
    2. Observe how values **< 1** brighten the image (expanding dark regions).
    3. Observe how values **> 1** darken the image (compressing bright regions).
    """)

    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("Gamma correction adjusts the overall brightness of the image using a non-linear operation. It is particularly useful in adjusting images with low or high contrast by controlling the mid-tones. You should expect the image to appear washed out at very low gamma values and overly dark at high gamma values, while the extreme black and white pixels remain unchanged.")

    gamma_tooltip = "Gamma correction follows a power-law relationship. It adjusts the relationship between a pixel's encoded value and its actual luminance."
    gamma = st.slider("Gamma Value", 0.1, 3.0, 1.0, step=0.05, help=gamma_tooltip)

    # Apply gamma correction using skimage to match the notebook
    corrected_image = exposure.adjust_gamma(img, gamma=gamma, gain=1)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original Image", use_container_width=True)
    with col2:
        st.image(corrected_image, caption=f"Gamma Corrected (Gamma = {gamma})", use_container_width=True)

elif selected_section == "Contrast Adjustment":
    st.header("Contrast Adjustment")
    
    st.info("""
    **Instructions:**
    1. Use the sliders to define the intensity range to focus on.
    2. Pixels below 'Min' will be pushed to pure black, and pixels above 'Max' will be pushed to pure white.
    """)
    
    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("Rescaling intensities helps stretch or compress the dynamic range of the image. By isolating a specific range of pixel values and stretching them across the full 0-255 spectrum, this method modifies pixel intensity values to drastically enhance image contrast. You should see hidden details pop out, especially in medical images like MRIs.")

    min_tooltip = "Sets the lower bound of the intensity range used for rescaling."
    max_tooltip = "Sets the upper bound of the intensity range used for rescaling."

    in_range_min = st.slider("In Range Min", 0.0, 1.0, 0.55, help=min_tooltip)
    in_range_max = st.slider("In Range Max", 0.0, 1.0, 0.7, help=max_tooltip)

    adj_img = exposure.rescale_intensity(img_as_float(img), in_range=(in_range_min, in_range_max), out_range=(0, 1))

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original", use_container_width=True)
    with col2:
        # BUG FIXED HERE: Removed cmap='gray'
        st.image(adj_img, caption="Adjusted", use_container_width=True)

elif selected_section == "Negative Transformation":
    st.header("Negative Transformation")
    
    st.info("""
    **Instructions:**
    1. Observe the standard negative image where colors/intensities are inverted.
    2. Use the slider to offset the overall brightness of the inverted image.
    """)

    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("Applying a negative transformation to the image inverts each pixel intensity. This technique can highlight different features in the image by reversing the intensity mapping. In scientific imaging, it is often easier for the human eye to detect dark details on a light background than light details on a dark background.")

    inv_level_tooltip = "Adjusts the overall intensity offset of the inverted image."
    inv_level = st.slider("Inversion Level Offset", 0, 255, 127, help=inv_level_tooltip)

    inverted_image = 255 - (img * (255 / np.max(img))).astype(np.uint8)
    inverted_image = np.clip(inverted_image + inv_level, 0, 255).astype(np.uint8)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original Image", use_container_width=True)
    with col2:
        st.image(inverted_image, caption="Negative Image", use_container_width=True)

elif selected_section == "Histogram Equalization":
    st.header("Histogram Equalization")
    
    st.info("""
    **Instructions:**
    1. Adjust the number of bins to see how the histogram is constructed.
    2. Compare the original image histogram to the equalized one. 
    """)

    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("Histogram equalization enhances the overall contrast of the image by spreading out the most frequent intensity values. You should expect the equalized image to look much starker, making details prominent. The resulting histogram will look 'flatter' and more stretched out compared to the original, highly clustered histogram.")

    bins_tooltip = "Controls the number of bins used to create the histogram. Higher values provide more detail but may appear jagged."
    num_bins = st.slider("Number of Histogram Bins", 10, 256, 256, help=bins_tooltip)

    if img is not None:
        if img.ndim == 3:
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img

        fig, ax = plt.subplots(2, 2, figsize=(10, 8))
        ax[0, 0].imshow(img_gray, cmap='gray')
        ax[0, 0].axis('off')
        ax[0, 0].set_title('Original Image')

        ax[0, 1].hist(img_gray.ravel(), bins=num_bins, color='blue')
        ax[0, 1].set_title('Original Histogram')
        ax[0, 1].set_ylim(0, 4000)

        img_eq = cv2.equalizeHist(img_gray)

        ax[1, 0].imshow(img_eq, cmap='gray')
        ax[1, 0].axis('off')
        ax[1, 0].set_title('Equalized Image')

        ax[1, 1].hist(img_eq.ravel(), bins=num_bins, color='blue')
        ax[1, 1].set_title('Equalized Histogram')
        ax[1, 1].set_ylim(0, 4000)

        fig.suptitle('Histogram Equalization')
        plt.tight_layout()
        st.pyplot(fig)

elif selected_section == "CLAHE":
    st.header("Contrast Limited Adaptive Histogram Equalization (CLAHE)")
    
    st.info("""
    **Instructions:**
    1. Adjust the **Clip Limit** to control contrast enhancement limits.
    2. Adjust the **Tile Grid Size** to change the size of the local grid patches used for equalization.
    """)

    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("Unlike standard Histogram Equalization which operates globally, CLAHE operates on small local regions (tiles). This prevents the over-amplification of noise in relatively homogeneous areas of the image. You should expect an image with vastly improved local contrast, making fine textures highly visible without washing out the entire image.")

    clip_tooltip = "Limits the contrast enhancement in each tile to prevent noise amplification (overexposure)."
    tile_tooltip = "Determines the size of the tiles used for local histogram equalization. Smaller tiles provide more localized enhancement."

    clip_limit = st.slider("Clip Limit", 1.0, 10.0, 2.0, help=clip_tooltip)
    tile_grid_size = st.slider("Tile Grid Size", 2, 32, 8, help=tile_tooltip)

    if img is not None:
        if img.ndim == 3:
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
        clahe_img = clahe.apply(img_gray)

        col1, col2 = st.columns(2)
        with col1:
            st.image(img_gray, caption="Original Image", use_container_width=True)
        with col2:
            st.image(clahe_img, caption="CLAHE Image", use_container_width=True)

elif selected_section == "Non-linear Intensity Transformation":
    st.header("Non-linear Intensity Transformation")
    
    st.info("""
    **Instructions:**
    1. Adjust **m** to shift the center point of the transformation curve.
    2. Adjust **E** to control the steepness/strength of the contrast change.
    """)

    with st.expander("Reveal Expected Outcome & Analysis"):
        st.write("This transformation applies a custom mathematical curve to specifically enhance low-contrast images. By mapping a narrow range of dark input pixels to a wider range of output pixels, you should expect hidden features in very dark images to suddenly become brightly visible, acting somewhat like an extreme exposure lift.")

    m_tooltip = "Controls the threshold point of the intensity transformation curve. It dictates which intensities get enhanced."
    E_tooltip = "Determines the overall strength or steepness of the transformation slope. Higher values result in more extreme contrast separation."

    m_val = st.slider("m Value", 0.0, 5.0, 0.5, help=m_tooltip)
    E_val = st.slider("E Value", 1.0, 100.0, 100.0, help=E_tooltip)

    if img is not None:
        G = 1. / (1. + m_val / (img_as_float(img) + 1e-4)) ** E_val

        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Original Image", use_container_width=True)
        with col2:
            st.image(G, caption="Enhanced Contrast Image", use_container_width=True)
