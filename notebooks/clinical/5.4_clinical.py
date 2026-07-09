import streamlit as st

st.title("5.4 Biomedical Computer Vision Applications (Clinical)")

st.info(
    "The original embedded HTML export is not present in this repository. "
    "This page now provides a stable in-app review activity instead of failing at runtime."
)

st.header("Clinical Computer Vision Application Review")
application = st.selectbox(
    "Choose an application area",
    [
        "Fracture screening",
        "Pathology slide triage",
        "Ultrasound lesion assessment",
    ],
)

st.markdown(
    """
    Use this page to reason about how a clinical computer vision workflow should be selected,
    validated, and monitored before use in care settings.
    """
)

cols = st.columns(3)
cols[0].metric("Input", "Clinical images")
cols[1].metric("Model task", "Vision pipeline")
cols[2].metric("Output", "Decision support")

with st.expander("Review prompts", expanded=True):
    st.write(f"Application selected: **{application}**")
    st.text_area("What clinical feature should the model learn?", key="feature_goal_clinical_54")
    st.text_area("What patient-safety risk could appear if the model fails?", key="failure_modes_clinical_54")
    st.text_area("What validation evidence would be needed before deployment?", key="evidence_clinical_54")

with st.expander("Expected considerations"):
    st.write(
        "Good answers should mention image quality, subgroup performance, external validation, "
        "clinical workflow fit, and human review."
    )
