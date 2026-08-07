import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import skimage.io as io
from skimage import exposure, img_as_float

st.markdown(
    """
An image is not a picture to a model — it is a matrix of numbers. This subsection establishes where those
numbers come from and what happens when you change them.

1. **Formation.** Find structure in a real radiograph with Canny edge detection, and compare a
   CT-weighted view against an MRI-weighted one using contrast and brightness alone.
2. **Intensity operations.** Gamma, contrast rescaling, histogram equalization, and CLAHE — four ways to
   change what is *visible* without changing what was *measured*.

That distinction is the whole point of this subsection. Subsection 5.2 then handles real artefacts.
"""
)

st.warning(
    "**Privacy notice:** do not upload images containing Protected Health Information (PHI) or any "
    "sensitive personal data."
)

DEFAULT_IMAGE_PATH = "assets/images/content/Identifying Structures in X-Ray Imaging.png"


@st.cache_data
def load_default_radiograph():
    return cv2.imread(DEFAULT_IMAGE_PATH)


# ═══════════════════════════════════════════════════════════════════════════
# Part 1 — Image formation and structure
# ═══════════════════════════════════════════════════════════════════════════
st.header("1. Where Pixel Values Come From")

st.markdown(
    """
X-rays pass through the body and are absorbed — *attenuated* — to different degrees depending on tissue
density and atomic number. Bone absorbs most of the beam and reads bright; air passes it and reads dark;
soft tissue lands in between. The greyscale is a measurement, not an aesthetic choice.

Which means a **boundary** in the image is a boundary in attenuation — a place where the tissue changed.
That is what an edge detector finds.
"""
)

uploaded_file = st.file_uploader(
    "Upload a radiograph (optional)",
    type=["jpg", "jpeg", "png"],
    key="m5_form_upload",
    help="A standard JPG or PNG. Ensure no patient data is visible in the image.",
)

if uploaded_file:
    img_bgr = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
else:
    img_bgr = load_default_radiograph()

if img_bgr is None:
    st.error(
        f"Could not load the bundled radiograph at `{DEFAULT_IMAGE_PATH}`. Upload an image above to continue."
    )
else:
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    st.subheader("1.1 Finding structure: Canny edge detection")
    st.markdown(
        "Canny keeps a gradient as an edge if it exceeds the **high** threshold, and keeps weaker gradients "
        "only where they connect to a strong one. The two thresholds are the sensitivity/noise trade-off "
        "made explicit."
    )

    edge_cols = st.columns(2)
    low_threshold = edge_cols[0].slider(
        "Low threshold (sensitivity)",
        0,
        200,
        100,
        help="Gradients below this are discarded outright. Lowering it admits more noise.",
        key="m5_form_canny_low",
    )
    high_threshold = edge_cols[1].slider(
        "High threshold (edge strength)",
        0,
        255,
        150,
        help="Gradients above this are always kept as strong edges.",
        key="m5_form_canny_high",
    )

    edges = cv2.Canny(gray, low_threshold, high_threshold)

    view_cols = st.columns([1, 1, 1])
    view_cols[0].image(img_rgb, caption="Original", use_container_width=True)
    view_cols[1].image(edges, caption="Canny edges", use_container_width=True)
    with view_cols[2]:
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        fig_hist, ax_hist = plt.subplots(figsize=(4.5, 3.2))
        ax_hist.plot(hist, color="#1f77b4")
        ax_hist.set_title("Intensity histogram")
        ax_hist.set_xlabel("Pixel intensity (0–255)")
        ax_hist.set_ylabel("Pixel count")
        ax_hist.set_xlim([0, 256])
        ax_hist.grid(True, alpha=0.3)
        st.pyplot(fig_hist)
        plt.close(fig_hist)

    edge_fraction = float((edges > 0).mean())
    st.metric("Share of pixels marked as edge", f"{edge_fraction:.1%}")
    st.markdown(
        f"""
    Reading a histogram is how you diagnose an image before you diagnose a patient: intensities bunched at
    one end mean an under- or over-exposed acquisition, and no amount of modelling recovers detail that was
    never captured.

    **Consider:** why is edge detection alone insufficient for finding a fracture? Drop the low threshold and
    watch the edge fraction climb — the detector will happily outline trabecular texture, film grain, and
    soft-tissue boundaries with exactly the same confidence it gives a fracture line. It reports *where the
    gradient is*, and nothing about what the gradient means.
    """
    )

    st.subheader("1.2 The same tissue, two modalities' worth of appearance")
    st.markdown(
        "Contrast and brightness are the two knobs behind every window/level control. A high-contrast view "
        "separates dense structure the way a **CT** does; lifting brightness and moderating contrast reveals "
        "soft-tissue gradation the way an **MRI** does. Same acquired data, two different clinical questions."
    )

    mod_cols = st.columns(2)
    contrast = mod_cols[0].slider(
        "Contrast",
        1.0,
        3.0,
        1.0,
        help="Multiplies the distance between light and dark, separating tissue types. "
        "Starts at 1.0 — no change — so you can see what each step costs.",
        key="m5_form_contrast",
    )
    brightness = mod_cols[1].slider(
        "Brightness",
        -50,
        50,
        0,
        help="Shifts every value up or down, revealing detail in shadowed regions.",
        key="m5_form_brightness",
    )

    adjusted = cv2.convertScaleAbs(img_rgb, alpha=contrast, beta=brightness)

    cmp_cols = st.columns(2)
    cmp_cols[0].image(img_rgb, caption="Baseline (dense-structure focus)", use_container_width=True)
    cmp_cols[1].image(
        adjusted,
        caption=f"Adjusted (contrast {contrast}, brightness {brightness:+d})",
        use_container_width=True,
    )

    # Report the saturation this adjustment *added*. This radiograph's background is already
    # pure white, and that pre-existing 255 is not something the learner did.
    baseline_clipped = float((gray >= 255).mean())
    now_clipped = float((cv2.cvtColor(adjusted, cv2.COLOR_RGB2GRAY) >= 255).mean())
    added = max(0.0, now_clipped - baseline_clipped)

    if added > 0.10:
        st.error(
            f"**Your adjustment has pushed a further {added:.1%} of the image to pure white** "
            f"({baseline_clipped:.1%} was already background). Those values are gone with no way back. This "
            "is the failure mode that makes aggressive enhancement dangerous: the image looks more confident "
            "and contains less."
        )
    elif added > 0.02:
        st.warning(
            f"A further {added:.1%} of the image is now saturated at 255 "
            f"(background was {baseline_clipped:.1%}). You are beginning to trade real detail for apparent "
            "contrast."
        )
    else:
        st.caption(
            f"Newly saturated: {added:.2%}. Nothing meaningful has been clipped yet — "
            f"{baseline_clipped:.1%} of this image was already pure-white background."
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
def load_clinical_samples():
    """Bundled microscopy and MRI samples."""
    if_cells = io.imread("assets/datasets/images/IFCells.jpg")
    brightfield = io.imread("assets/datasets/images/BloodSmear.png")
    kidney_mri = io.imread("assets/datasets/images/kidney_mri.jpg")
    if if_cells.ndim == 3 and if_cells.shape[-1] == 4:
        if_cells = if_cells[:, :, :3]
    if brightfield.ndim == 3 and brightfield.shape[-1] == 4:
        brightfield = brightfield[:, :, :3]
    return {
        "Kidney MRI": kidney_mri,
        "Brightfield (blood smear)": brightfield,
        "Fluorescence (IF cells)": if_cells,
    }


images = load_clinical_samples()

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
            "Gamma is most useful when the interesting structure sits in the mid-tones — which, in MRI, is "
            "usually where soft-tissue contrast lives. Push it very low and the image washes out; push it "
            "high and it goes muddy. The extremes never move: gamma redistributes the middle, it does not "
            "extend the range."
        )

with op_tab2:
    st.subheader("Contrast rescaling")
    st.markdown(
        "Pick a narrow intensity window and stretch it across the full range. Everything below the minimum "
        "is crushed to black, everything above the maximum to white — and the detail in between expands to "
        "fill the space. This is precisely the window/level control on a clinical workstation."
    )
    r_cols = st.columns(2)
    in_min = r_cols[0].slider("Window minimum", 0.0, 1.0, 0.55, key="m5_rescale_min")
    in_max = r_cols[1].slider("Window maximum", 0.0, 1.0, 0.7, key="m5_rescale_max")

    if in_min >= in_max:
        st.warning("The window minimum must be below the maximum — the range would otherwise be empty.")
    else:
        adjusted_img = exposure.rescale_intensity(
            img_as_float(img), in_range=(in_min, in_max), out_range=(0, 1)
        )
        a_cols = st.columns(2)
        a_cols[0].image(img, caption="Original", use_container_width=True)
        a_cols[1].image(
            adjusted_img, caption=f"Rescaled from [{in_min}, {in_max}]", use_container_width=True
        )

    with st.expander("Reveal expected outcome"):
        st.write(
            "Hidden detail 'pops' because you gave a narrow band the whole dynamic range — but everything "
            "outside the window is now irrecoverably flat. You chose what to see, and therefore also what to "
            "discard. Two readers using different windows are looking at different images of the same patient."
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
        "tile's contrast may be amplified. Local detail improves without the noise blow-up — which is why "
        "CLAHE is the default enhancement in a great deal of medical imaging software."
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
            "you exactly where enhancement stops being information and starts being invention. An enhanced "
            "image that looks more diagnostic than the acquisition supports is a patient-safety problem."
        )

st.markdown(
    """
---
**Key takeaways**

- A pixel value is a measurement of attenuation. The histogram is the fastest way to judge whether an
  acquisition is usable at all.
- An edge detector reports where the gradient is, not what it means. Structure-finding is not diagnosis.
- Every operation here is lossy in practice: windowing discards what falls outside the window, equalization
  amplifies noise, CLAHE bounds that amplification.
- **None of these adds information.** If the structure was not captured, no transform recovers it — and any
  transform that appears to has invented it.
- Whatever you apply here must be applied identically to every image a model ever sees, at training and at
  inference. An enhancement pipeline is part of the model.

**Resources:** [scikit-image exposure](https://scikit-image.org/docs/stable/api/skimage.exposure.html) ·
[OpenCV Canny tutorial](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html)
"""
)
