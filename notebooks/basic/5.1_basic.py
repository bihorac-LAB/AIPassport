import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt

# =====================================================================
# PAGE CONFIGURATION
# =====================================================================
st.set_page_config(page_title="Biomedical Imaging Demo", layout="wide")

st.title("Landscape of Biomedical Imaging")

# Explicit instructions for the students
st.info("**Instructions:** Use the controls in the sidebar to adjust the simulated tissue densities. Observe how these changes affect the X-ray image below, and then generate a histogram to mathematically analyze the resulting pixel intensities.")

# =====================================================================
# INTERACTIVE CONTROLS (SIDEBAR)
# =====================================================================
st.sidebar.header("Tissue Density Controls")
st.sidebar.write("Adjust the simulated density (0 = Black/Air, 255 = White/Bone)")

# Tooltips using the `help` parameter
air_intensity = st.sidebar.slider(
    "Lungs (Air)", 0, 100, 30,
    help="Simulates the radiodensity of air-filled spaces. Lower values absorb fewer X-rays and appear darker."
)
tissue_intensity = st.sidebar.slider(
    "Soft Tissue", 50, 150, 100,
    help="Simulates the radiodensity of soft tissues like muscle or organs. Intermediate values appear as shades of gray."
)
bone_intensity = st.sidebar.slider(
    "Bone", 150, 255, 200,
    help="Simulates the radiodensity of dense materials. Higher values absorb more X-rays and appear brighter."
)


# =====================================================================
# SECTION 1: SIMULATED X-RAY
# =====================================================================
st.header("1. Simulated X-ray Attenuation")

# Generate the image using the dynamic slider values
image = np.ones((100, 300), dtype=np.uint8) * tissue_intensity

# Two circular, dark spots (Lungs/Air)
cv2.circle(image, (75, 50), 30, air_intensity, -1)  
cv2.circle(image, (225, 50), 30, air_intensity, -1)

# White rectangle in center (Bone)
cv2.rectangle(image, (140, 20), (160, 80), bone_intensity, -1)

# Save the generated image to Streamlit's session state
st.session_state['xray_image'] = image

# Display the image
st.image(image, caption="Simulated X-ray Attenuation", use_container_width=True, clamp=True)

# The "Reveal" 
with st.expander("Reveal: Biological Interpretation"):
    st.write("""
    X-rays pass through the body and are absorbed (or attenuated) by different tissues depending on their density and atomic number. The amount of attenuation determines how bright or dark a region appears on the X-ray image.
    
    * **High attenuation materials (e.g., Bone):** Absorb more X-rays and allow fewer to reach the detector. They appear brighter (white) on the image.
    * **Low attenuation materials (e.g., Air in lungs):** Allow most X-rays to pass through. They appear darker (black) on the image.
    * **Intermediate tissues (e.g., Muscle, fat, organs):** Absorb X-rays to a moderate degree. They appear in shades of gray.
    """)
    # Note: To add a real image here later, use: st.image("your_image.png")


# =====================================================================
# SECTION 2: INTENSITY HISTOGRAM
# =====================================================================
st.divider()
st.header("2. Pixel Intensity Histogram")
st.write("Understanding the histogram of an image is critical for interpreting brightness and contrast.")

# Interactive button with a tooltip
if st.button("Generate Histogram from Image above", help="Click to calculate and plot the frequency of pixel intensities from the current simulated X-ray."):
    
    # Calculate real histogram using cv2
    hist = cv2.calcHist([st.session_state['xray_image']], [0], None, [256], [0, 256])
    
    # Plot using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(hist, color='blue')
    ax.set_title("Pixel Intensity Histogram")
    ax.set_xlabel("Pixel Intensity (0-255)")
    ax.set_ylabel("Frequency (Number of Pixels)")
    ax.grid(True)
    ax.set_xlim([0, 256])
    
    # Display the plot in Streamlit
    st.pyplot(fig)
    
    # The "Reveal" 
    with st.expander("Reveal: Histogram Analysis"):
        st.write(f"""
        The three distinct peaks in this histogram correspond directly to the materials in our simulated image. Because you can adjust the sliders, these peaks will move!
        
        Currently, the peaks represent:
        * **Intensity {air_intensity}:** Air (Lungs)
        * **Intensity {tissue_intensity}:** Soft Tissue (Background)
        * **Intensity {bone_intensity}:** Bone (Center structure)
        """)
