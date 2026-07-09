import streamlit as st

st.title("5.4 Biomedical Computer Vision Applications (Basic)")

st.info(
    "The original embedded HTML export is not present in this repository. "
    "This page now provides a stable in-app review activity instead of failing at runtime."
)

st.header("Computer Vision Application Review")
application = st.selectbox(
    "Choose an application area",
    [
        "Microscopy cell analysis",
        "Tissue slide quality control",
        "Image-based phenotype screening",
    ],
)

st.markdown(
    """
    Use this page to reason about how a computer vision workflow should be selected and evaluated.
    Focus on whether the task needs classification, segmentation, detection, or image enhancement.
    """
)

cols = st.columns(3)
cols[0].metric("Input", "Biomedical images")
cols[1].metric("Model task", "Vision pipeline")
cols[2].metric("Output", "Decision support")

with st.expander("Review prompts", expanded=True):
    st.write(f"Application selected: **{application}**")
    st.text_area("What visual feature should the model learn?", key="feature_goal_basic_54")
    st.text_area("What could make this model fail on new images?", key="failure_modes_basic_54")
    st.text_area("What evidence would show the model is useful?", key="evidence_basic_54")

with st.expander("Expected considerations"):
    st.write(
        "Good answers should mention image quality, labeling consistency, external validation, "
        "and whether the output can be checked by a domain expert."
    )
