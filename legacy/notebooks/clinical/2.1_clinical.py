import streamlit as st

st.title("2.1 The Fundamental Principles of Bioethics")
st.subheader("Navigating AI and Bioethical Principles in Clinical Practice")
st.markdown("---")

st.markdown("""\
**Objective:**  
Develop the skills to navigate ethical issues arising from the use of AI using the four principles of bioethics.
""")

st.markdown("---")

with st.expander("Read the Case (click to expand)", expanded=True):
    st.markdown("""
A hospital is piloting an AI system to predict disease risks and support early diagnosis, hoping to improve patient outcomes.  
The system uses vast amounts of **de-identified patient data**, such as demographics, clinical histories, and lifestyle information.  
De-identified data means no names or addresses, but the AI still analyzes broad health trends.

**Ethical Dilemma:** For maximum accuracy, the AI benefits from detailed geographic and demographic information.  
But: such details can sometimes allow "re-identification"—figuring out who an individual is, especially in unique combinations or rare diseases.

If a patient’s health information were re-identified and accessed by third parties (employers, insurers, cybercriminals),  
it could lead to discrimination, financial harm, and loss of privacy.
""")
st.markdown("---")

st.header("1. Which of the four principles of bioethics apply here?")

bioethics_options = [
    "Autonomy (respecting patient choice and privacy)",
    "Beneficence (acting to benefit the patient and population)",
    "Non-maleficence (do no harm)",
    "Justice (fairness and equity in healthcare)"
]

bioethics_selected = st.multiselect(
    "Select all that clearly apply in this scenario:",
    bioethics_options
)

if st.button("Show Example - Principles"):
    st.success(
        "All four principles are relevant:\n"
        "- **Autonomy**: Patients expect control over their private information; re-identification risks violate their autonomy and privacy.\n"
        "- **Beneficence**: The AI could improve diagnosis and outcomes (population benefit).\n"
        "- **Non-maleficence**: Re-identification could cause real harm (discrimination, financial harm).\n"
        "- **Justice**: If certain groups are more at risk for re-identification (rare conditions, small communities), or are excluded for privacy, this raises fairness concerns."
    )

st.markdown("---")

st.header("2. Which principles are in conflict? Why?")

conflict_response = st.text_area("Explain which principles may come into conflict and describe how:", height=140)
if st.button("Show Example - Conflicts"):
    st.info(
        "- **Beneficence** (improving care via better AI) vs. **Autonomy**/**Non-maleficence** (protecting privacy, preventing harm):\n"
        "• The more detailed the data, the more AI helps patients—BUT the higher the risk of re-identification and harm.\n"
        "- **Justice** can also conflict if privacy risks are unequally distributed, or if some populations are excluded to protect privacy."
    )

st.markdown("---")

st.header("3. On your view, which principle should take precedence? Why?")

precedence_response = st.text_area("Defend your view: which principle should guide clinicians and hospital policy here, and why?", height=140)
if st.button("Show Example - Precedence"):
    st.info(
        "Example: While beneficence is important, **non-maleficence** (do no harm) and **autonomy** (patient privacy) should take precedence—especially where privacy breaches can cause irreversible harm. The hospital must put safeguards in place so that no patient can be re-identified, even if it reduces AI accuracy somewhat; otherwise, trust is lost and harm may result."
    )

st.markdown("---")

st.header("Reflection")

st.markdown("""
- What new questions do you have about the use of AI and patient data in healthcare?
- How might your thinking change if you were a member of a rare demographic group?
""")
reflection_text = st.text_area("Optional: Add your reflections here", height=100)

st.success("Thank you for your thoughtful engagement with AI and bioethics in clinical care.")

st.markdown("""
---
**Key Concepts:**  
- Autonomy = respecting patients’ wishes and privacy  
- Beneficence = doing good for the patient/population  
- Non-maleficence = avoiding harm  
- Justice = fairness in distribution of risks and benefits

**Further reading:** [Principlism in Clinical Ethics (Stanford)](https://plato.stanford.edu/entries/principle-bioethics/)
""")
