import streamlit as st

st.title("5.6 Consistency in Biomedical Image Analysis (Clinical)")

st.info(
    "The original embedded HTML export is not present in this repository. "
    "This page now provides a stable in-app consistency checklist instead of failing at runtime."
)

st.header("Clinical Consistency Checklist")

checks = {
    "Scanner or acquisition protocol is documented": st.checkbox("Scanner or acquisition protocol is documented"),
    "Preprocessing is applied consistently": st.checkbox("Preprocessing is applied consistently"),
    "Clinical labels use a shared definition": st.checkbox("Clinical labels use a shared definition"),
    "Evaluation includes external or site-held-out data": st.checkbox("Evaluation includes external or site-held-out data"),
}

score = sum(checks.values())
st.metric("Consistency score", f"{score}/{len(checks)}")

with st.expander("Reflection", expanded=True):
    st.text_area("Which clinical workflow step could introduce inconsistency?", key="risk_clinical_56")
    st.text_area("How would you standardize the workflow before deployment?", key="standardize_clinical_56")

with st.expander("Expected considerations"):
    st.write(
        "Strong clinical workflows define acquisition protocol, preprocessing, annotation standards, "
        "site-level validation, quality control, and escalation paths for uncertain outputs."
    )
