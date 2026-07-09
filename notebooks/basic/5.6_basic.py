import streamlit as st

st.title("5.6 Consistency in Biomedical Image Analysis (Basic)")

st.info(
    "The original embedded HTML export is not present in this repository. "
    "This page now provides a stable in-app consistency checklist instead of failing at runtime."
)

st.header("Consistency Checklist")

checks = {
    "Acquisition settings are documented": st.checkbox("Acquisition settings are documented"),
    "Preprocessing is applied consistently": st.checkbox("Preprocessing is applied consistently"),
    "Labels use a shared definition": st.checkbox("Labels use a shared definition"),
    "Evaluation includes a held-out set": st.checkbox("Evaluation includes a held-out set"),
}

score = sum(checks.values())
st.metric("Consistency score", f"{score}/{len(checks)}")

with st.expander("Reflection", expanded=True):
    st.text_area("Which step is most likely to introduce inconsistency?", key="risk_basic_56")
    st.text_area("How would you standardize the workflow?", key="standardize_basic_56")

with st.expander("Expected considerations"):
    st.write(
        "Strong workflows define acquisition settings, preprocessing steps, label definitions, "
        "quality control rules, and validation splits before model training."
    )
