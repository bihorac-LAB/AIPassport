import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import skimage.io as io
from skimage import exposure, img_as_float

st.title("5.1 How Biomedical Images Become Data (Basic Science)")

st.markdown(
    """
An image is not a picture to a model — it is a matrix of numbers. This subsection establishes where those
numbers come from and what happens when you change them.

1. **Formation.** Build a synthetic X-ray from tissue densities and watch its histogram track your sliders.
2. **Intensity operations.** Gamma, contrast rescaling, histogram equalization, and CLAHE — four ways to
   change what is *visible* without changing what was *measured*.

That distinction is the whole point of this subsection. Subsection 5.2 then handles real artefacts.
"""
)

st.warning(
    "**Privacy notice:** this is a public educational application. Do not upload sensitive or private data."
)

# ═══════════════════════════════════════════════════════════════════════════
# Part 1 — Image formation
# ═══════════════════════════════════════════════════════════════════════════
st.header("1. Where Pixel Values Come From")

st.markdown(
    """
X-rays pass through the body and are absorbed — *attenuated* — to different degrees depending on tissue
density and atomic number. How much is absorbed decides how bright that region appears.

Set the three densities below (0 = black/air, 255 = white/bone) and watch the synthetic radiograph change.
"""
)

density_cols = st.columns(3)
air_intensity = density_cols[0].slider(
    "Lungs (air)",
    0,
    100,
    30,
    help="Air-filled spaces absorb few X-rays, so more reach the detector and the region reads darker.",
    key="m5_form_air",
)
tissue_intensity = density_cols[1].slider(
    "Soft tissue",
    50,
    150,
    100,
    help="Muscle and organs absorb a moderate amount, producing mid-greys.",
    key="m5_form_tissue",
)
bone_intensity = density_cols[2].slider(
    "Bone",
    150,
    255,
    200,
    help="Dense material absorbs most of the beam, so the region reads bright.",
    key="m5_form_bone",
)

xray = np.ones((100, 300), dtype=np.uint8) * tissue_intensity
cv2.circle(xray, (75, 50), 30, air_intensity, -1)    # left lung field
cv2.circle(xray, (225, 50), 30, air_intensity, -1)   # right lung field
cv2.rectangle(xray, (140, 20), (160, 80), bone_intensity, -1)  # central bone

form_cols = st.columns([1, 1])
with form_cols[0]:
    st.image(xray, caption="Simulated X-ray attenuation", use_container_width=True, clamp=True)
    with st.expander("Reveal: the physical interpretation"):
        st.markdown(
            """
        * **High attenuation (bone):** absorbs more X-rays, fewer reach the detector → **brighter**.
        * **Low attenuation (air in lungs):** most of the beam passes through → **darker**.
        * **Intermediate tissue (muscle, fat, organs):** moderate absorption → **shades of grey**.

        The greyscale is not an aesthetic choice. It is a measurement of how much beam survived.
        """
        )

with form_cols[1]:
    hist = cv2.calcHist([xray], [0], None, [256], [0, 256])
    fig_hist, ax_hist = plt.subplots(figsize=(6, 3.2))
    ax_hist.plot(hist, color="#1f77b4")
    for value, label in (
        (air_intensity, "air"),
        (tissue_intensity, "tissue"),
        (bone_intensity, "bone"),
    ):
        ax_hist.axvline(value, color="#ff7f0e", linestyle="--", linewidth=1)
        ax_hist.annotate(label, (value, ax_hist.get_ylim()[1] * 0.9), fontsize=8, rotation=90)
    ax_hist.set_title("Pixel intensity histogram")
    ax_hist.set_xlabel("Pixel intensity (0–255)")
    ax_hist.set_ylabel("Pixel count")
    ax_hist.set_xlim([0, 256])
    ax_hist.grid(True, alpha=0.3)
    st.pyplot(fig_hist)
    plt.close(fig_hist)

    st.markdown(
        f"""
    Three peaks, one per material — at **{air_intensity}** (air), **{tissue_intensity}** (soft tissue), and
    **{bone_intensity}** (bone). Move any slider and its peak moves with it.

    Reading a histogram is how you diagnose an image before you diagnose a patient: peaks bunched at one end
    mean an under- or over-exposed acquisition, and no amount of modelling recovers detail that was never
    captured.
    """
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# Part 2 — Intensity operations
# ═══════════════════════════════════════════════════════════════════════════
st.header("2. Changing What Is Visible")

st.markdown(
    """
The operations below are **display and preprocessing transforms**. They redistribute intensities to make
structure easier to see — for you or for a model. None of them adds information that was not acquired.
"""
)


@st.cache_data
def load_microscopy_images():
    """Bundled microscopy and MRI samples."""
    if_cells = io.imread("assets/datasets/images/IFCells.jpg")
    brightfield = io.imread("assets/datasets/images/BloodSmear.png")
    kidney_mri = io.imread("assets/datasets/images/kidney_mri.jpg")
    if if_cells.ndim == 3 and if_cells.shape[-1] == 4:
        if_cells = if_cells[:, :, :3]
    if brightfield.ndim == 3 and brightfield.shape[-1] == 4:
        brightfield = brightfield[:, :, :3]
    return {
        "Brightfield (blood smear)": brightfield,
        "Fluorescence (IF cells)": if_cells,
        "Kidney MRI": kidney_mri,
    }


images = load_microscopy_images()

image_choice = st.selectbox(
    "Image:", list(images), help="The same operation behaves differently on each of these.",
    key="m5_intensity_image",
)
img = images[image_choice]


def to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if image.ndim == 3 else image


op_tab1, op_tab2, op_tab3, op_tab4 = st.tabs(
    ["Gamma", "Contrast rescaling", "Histogram equalization", "CLAHE"]
)

with op_tab1:
    st.subheader("Gamma correction")
    st.markdown(
        "A power-law curve applied to every pixel. Values **below 1** brighten the image by expanding the "
        "dark end; values **above 1** darken it by compressing the bright end. Pure black and pure white "
        "stay where they are."
    )
    gamma = st.slider(
        "Gamma",
        0.1,
        3.0,
        1.0,
        step=0.05,
        help="The exponent in the power-law mapping between stored value and displayed luminance.",
        key="m5_gamma",
    )
    corrected = exposure.adjust_gamma(img, gamma=gamma, gain=1)

    g_cols = st.columns(2)
    g_cols[0].image(img, caption="Original", use_container_width=True)
    g_cols[1].image(corrected, caption=f"Gamma = {gamma}", use_container_width=True)

    with st.expander("Reveal expected outcome"):
        st.write(
            "Gamma is most useful for images whose interesting structure sits in the mid-tones. Push it very "
            "low and the image washes out; push it high and it goes muddy. Notice that the extremes never "
            "move — gamma redistributes the middle, it does not extend the range."
        )

with op_tab2:
    st.subheader("Contrast rescaling")
    st.markdown(
        "Pick a narrow intensity window and stretch it across the full range. Everything below the minimum "
        "is crushed to black, everything above the maximum to white — and the detail in between expands to "
        "fill the space."
    )
    r_cols = st.columns(2)
    in_min = r_cols[0].slider("Window minimum", 0.0, 1.0, 0.55, key="m5_rescale_min")
    in_max = r_cols[1].slider("Window maximum", 0.0, 1.0, 0.7, key="m5_rescale_max")

    if in_min >= in_max:
        st.warning("The window minimum must be below the maximum — the range would otherwise be empty.")
    else:
        adjusted = exposure.rescale_intensity(
            img_as_float(img), in_range=(in_min, in_max), out_range=(0, 1)
        )
        a_cols = st.columns(2)
        a_cols[0].image(img, caption="Original", use_container_width=True)
        a_cols[1].image(adjusted, caption=f"Rescaled from [{in_min}, {in_max}]", use_container_width=True)

    with st.expander("Reveal expected outcome"):
        st.write(
            "This is the operation behind a radiologist's window/level control. Hidden detail 'pops' because "
            "you gave a narrow band the whole dynamic range — but everything outside the window is now "
            "irrecoverably flat. You chose what to see, and therefore also what to discard."
        )

with op_tab3:
    st.subheader("Histogram equalization")
    st.markdown(
        "Rather than you choosing a window, equalization spreads the *most frequent* intensities out "
        "automatically, flattening the histogram."
    )
    num_bins = st.slider(
        "Histogram bins", 10, 256, 256, help="More bins show finer structure and look more jagged.",
        key="m5_eq_bins",
    )

    img_gray = to_gray(img)
    img_eq = cv2.equalizeHist(img_gray)

    fig_eq, ax_eq = plt.subplots(2, 2, figsize=(10, 7))
    ax_eq[0, 0].imshow(img_gray, cmap="gray")
    ax_eq[0, 0].axis("off")
    ax_eq[0, 0].set_title("Original")
    ax_eq[0, 1].hist(img_gray.ravel(), bins=num_bins, color="#1f77b4")
    ax_eq[0, 1].set_title("Original histogram")
    ax_eq[1, 0].imshow(img_eq, cmap="gray")
    ax_eq[1, 0].axis("off")
    ax_eq[1, 0].set_title("Equalized")
    ax_eq[1, 1].hist(img_eq.ravel(), bins=num_bins, color="#ff7f0e")
    ax_eq[1, 1].set_title("Equalized histogram")
    fig_eq.tight_layout()
    st.pyplot(fig_eq)
    plt.close(fig_eq)

    with st.expander("Reveal expected outcome"):
        st.write(
            "The equalized histogram is flatter and wider, and the image looks starker. The cost is that "
            "equalization is **global**: it amplifies contrast everywhere, including noise in regions that "
            "were uniform for a good reason. That is the problem CLAHE exists to solve."
        )

with op_tab4:
    st.subheader("CLAHE — contrast-limited adaptive histogram equalization")
    st.markdown(
        "Equalization applied tile by tile instead of to the whole image, with a ceiling on how much any one "
        "tile's contrast may be amplified. Local detail improves without the noise blow-up."
    )
    c_cols = st.columns(2)
    clip_limit = c_cols[0].slider(
        "Clip limit", 1.0, 10.0, 2.0, help="The ceiling on per-tile amplification.", key="m5_clahe_clip"
    )
    tile_grid_size = c_cols[1].slider(
        "Tile grid size", 2, 32, 8, help="Smaller tiles mean more local adaptation.", key="m5_clahe_tile"
    )

    img_gray = to_gray(img)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    clahe_img = clahe.apply(img_gray)

    cl_cols = st.columns(2)
    cl_cols[0].image(img_gray, caption="Original (greyscale)", use_container_width=True)
    cl_cols[1].image(
        clahe_img, caption=f"CLAHE (clip {clip_limit}, {tile_grid_size}×{tile_grid_size} tiles)",
        use_container_width=True,
    )

    with st.expander("Reveal expected outcome"):
        st.write(
            "Fine texture becomes visible across the whole field, not just in the well-exposed part. Raise "
            "the clip limit far enough and you will see the noise come back — which is the setting telling "
            "you exactly where enhancement stops being information and starts being invention."
        )

st.markdown(
    """
---
**Key takeaways**

- A pixel value is a measurement. The histogram is the fastest way to judge whether an acquisition is
  usable at all.
- Every operation here is invertible in intent but lossy in practice: windowing discards what falls outside
  the window, equalization amplifies noise, CLAHE bounds that amplification.
- **None of these adds information.** If the structure was not captured, no transform recovers it — and any
  transform that appears to has invented it.
- Whatever you apply here must be applied identically to every image a model ever sees, at training and at
  inference. An enhancement pipeline is part of the model.

**Resources:** [scikit-image exposure](https://scikit-image.org/docs/stable/api/skimage.exposure.html) ·
[OpenCV histogram equalization](https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html)
"""
)
