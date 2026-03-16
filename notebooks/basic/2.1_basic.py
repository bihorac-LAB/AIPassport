import streamlit as st

st.set_page_config(page_title="The Fundamental Principles of Bioethics", layout="centered")
st.title("2.1 The Fundamental Principles of Bioethics")
st.subheader("Ethical Challenges in AI & Bioethics")

st.markdown("""
### **Objective**

To explore ethical challenges in using artificial intelligence (AI) in biomedical research, identify conflicting bioethical principles, and justify which principle should take precedence.
""")

st.markdown("---")

st.header("Case Study")

with st.expander("Read the Case (Click to Expand)", expanded=True):
    st.markdown("""
**Dr. Lee**, a biomedical researcher, has developed an AI model to predict disease risk based on genetic data.  
The model has the potential to identify high-risk individuals early, enabling preventive care.

**However:**  
During testing, it becomes evident that the AI algorithm disproportionately predicts higher risk for certain racial and ethnic groups due to biases in the training data. Deploying the model could benefit many patients but also risks reinforcing healthcare disparities.  
**Dr. Lee must decide** whether to launch the model while working to improve its fairness, or delay deployment entirely to refine the algorithm.
""")

st.markdown("---")

st.header("1️⃣ Which of the four principles of bioethics apply here? (Select all that apply)")

principles = [
    "Autonomy (respect for persons)",
    "Beneficence (do good)",
    "Non-maleficence (do no harm)",
    "Justice (fair and equitable treatment)"
]
selected_principles = st.multiselect("Select the principles you think are relevant:", principles)

if st.button("Show Example Principles"):
    st.success(
        "- **Autonomy**: Patients have a right to be informed and to choose how their genetic risk data are used.\n"
        "- **Beneficence**: The model could benefit many by enabling early preventive care.\n"
        "- **Non-maleficence**: There’s potential to cause harm by reinforcing disparities/faulty risk predictions.\n"
        "- **Justice**: Model bias could increase healthcare inequity for certain racial/ethnic groups."
    )

st.markdown("---")

st.header("2️⃣ Which principles are in conflict? Explain how:")

conflicts = st.text_area(
    "Describe which principles are in conflict and briefly explain why:",
    height=120
)
if st.button("Show Example Conflicts"):
    st.info(
        "- **Beneficence** (do good for many) is in tension with **Justice** (fairness) and **Non-maleficence** (avoid harm).\n"
        "The model’s deployment may help most, but also risks harming or unfairly treating minority groups."
    )

st.markdown("---")

st.header("3️⃣ Which principle should take precedence? Why?")

precedence = st.text_area(
    "Which bioethical principle do you think should guide the decision here? Justify your answer:",
    height=120
)
if st.button("Show Example Justification"):
    st.info(
        "Example: *Justice* should take precedence. If the model increases disparities or harms disadvantaged groups, this undermines the goals of medicine. A just system must assure that AI benefits are equitable, even if this requires delay and extra work."
    )

st.markdown("---")

st.header("💬 Reflection")
st.markdown("""
- If you were in Dr. Lee's position, what further steps would you consider (e.g., communicating with affected communities, auditing model bias, transparency in deployment)?
- How might regulatory bodies or IRBs guide the decision?
""")
_ = st.text_area("Write your brief reflections here (optional):", height=70)

st.success("Thank you for engaging with the ethical challenges of AI in biomedical research.")

st.markdown("""
---
**Key Reminders:**  
- **Autonomy** = patient choice
- **Beneficence** = promote well-being
- **Non-maleficence** = avoid harm
- **Justice** = treat all fairly, address disparities

**For more:**  
- [Stanford Encyclopedia of Bioethics](https://plato.stanford.edu/entries/principle-bioethics/)
- [AMA: AI and Health Equity](https://www.ama-assn.org/delivering-care/ethics/artificial-intelligence-health-care)

*Assignment auto-saves your responses if you keep the browser open.*
""")