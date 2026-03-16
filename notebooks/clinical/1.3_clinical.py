import streamlit as st

st.set_page_config(page_title="MS3 Biomedical AI Experiment Design Assignment", layout="wide")

st.title("1.3 Designing Biomedical Artificial Intelligence Experiments (Clinical Research)")

st.markdown(
    """
You are a clinical informatics researcher at a large academic medical center. Your hospital has higher-than-expected 30-day readmission rates for CHF patients.

**Your Task:**  
Design an AI experiment to predict readmission risk and support enhanced discharge planning.  
Follow each part, provide your responses using the inputs below. No programming required.
""")

# -- RESOURCES SECTION HERE --
st.header("Resources: Datasets & Tools")
st.markdown("""
**Datasets:**  
- [MIMIC-IV](https://physionet.org/content/mimiciv/2.2/)  
- [UK Biobank Imaging Data](https://www.ukbiobank.ac.uk/enable-your-research/about-our-data/imaging-data)  

**Tools:**  
- [Google Colab](https://colab.research.google.com/)  
- [TensorFlow](https://www.tensorflow.org/)
""")

# Session state to track progress and answers (optional, for navigation logic)

# --------------------------------------------
st.header("Part 1: Identifying Knowledge Gaps and Research Questions")

st.subheader("1.1 Review the Current Literature")
st.markdown("Identify at least **three knowledge gaps or limitations** in current AI-based readmission prediction approaches for CHF patients.")
gap1 = st.text_area("Knowledge Gap 1")
gap2 = st.text_area("Knowledge Gap 2")
gap3 = st.text_area("Knowledge Gap 3")

st.divider()

st.subheader("1.2 Research Questions (SMART Criteria)")
primary_q = st.text_area("Primary Research Question")
secondary_q1 = st.text_area("Secondary Research Question 1")
secondary_q2 = st.text_area("Secondary Research Question 2")

st.divider()

st.subheader("1.3 Relevance and Impact")
align = st.text_area("How do your research questions address the identified gaps and improve patient care?")

# --------------------------------------------
st.header("Part 2: Data Management Strategy")

st.subheader("2.1 Data Selection Approach")
data_elements = st.multiselect(
    "Which MIMIC-IV elements would you use?", [
        "Demographics", "Diagnoses (ICD codes)", "Procedures",
        "Medications", "Laboratory values", "Clinical notes", "Vitals", "Other"
    ])
other_data_elements = ""
if "Other" in data_elements:
    other_data_elements = st.text_input("Specify other data elements:")

inclusion = st.text_area("Inclusion criteria")
exclusion = st.text_area("Exclusion criteria")
missing = st.text_area("How will you handle missing data?")
bias = st.text_area("How will you address potential biases in the data?")

st.divider()

st.subheader("2.2 Data Preprocessing Pipeline")
unstructured = st.text_area("Feature extraction from unstructured clinical notes")
normalize = st.text_area("How will you normalize laboratory values?")
temporal = st.text_area("Handling of temporal data (E.g., time series, hospital stays)")
derived = st.text_area("Creation of clinically relevant derived variables")

st.divider()

st.subheader("2.3 Data Splitting Strategy")
st.markdown("How will you split your data to account for the considerations below?")
temporal_shift = st.text_area("Handling temporal shifts in clinical practice")
balancing = st.multiselect(
    "How will you handle class imbalance (readmitted vs. not)?",
    ["Oversample minority class", "Undersample majority class", "Class-weighted loss", "Other"])
if "Other" in balancing:
    balance_other = st.text_input("Specify other approach to class imbalance:")
demographics = st.text_area("How will you ensure patient demographic representation?")
generalizability = st.text_area("How will you evaluate generalizability across different hospital units?")

# --------------------------------------------
st.header("Part 3: Experimental Design")

st.subheader("3.1 Modelling Approach")
st.markdown("Briefly describe three candidate AI/ML algorithms for readmission prediction:")
algo1 = st.text_area("Algorithm 1")
algo2 = st.text_area("Algorithm 2")
algo3 = st.text_area("Algorithm 3")
chosen_algo = st.text_input("Which algorithm did you choose and why?")

address_gaps = st.text_area("How does your approach address the limitations identified in Part 1?")

st.divider()

st.subheader("3.2 Evaluation Framework")
metrics = st.multiselect(
    "Which performance metrics will you use (beyond accuracy)?",
    ["Area under ROC", "Area under PRC", "F1 Score", "Sensitivity/Recall", "Specificity", "Calibration (e.g., Brier score)", "Other"])
if "Other" in metrics:
    metric_other = st.text_input("Specify additional metrics:")
metrics_justification = st.text_area("Justify your choice of metrics")
validation = st.text_area("Describe your cross-validation strategy")
relevance = st.text_area("How will you assess clinical relevance, not just statistical significance?")

st.divider()

st.subheader("3.3 Addressing Challenges")
concept_drift = st.text_area("How will you handle concept drift over time?")
transparency = st.text_area("How will you ensure the model is transparent for clinical interpretation?")
fairness = st.text_area("How will you assess fairness across patient populations?")
prospective_ready = st.text_area("How will you determine if the model is ready for prospective evaluation?")

# --------------------------------------------
st.header("Part 4: Ethical Considerations and Limitations")

st.subheader("4.1 Ethical Considerations")
eth_issues = st.multiselect(
    "Select at least three ethical issues your model raises:",
    ["Privacy/confidentiality", "Informed consent", "Data security", "Algorithmic bias/fairness", "Clinical accountability", "Other"])
eth_explanation = {}
for issue in eth_issues:
    response = st.text_area(f"How will you address {issue}?")
    eth_explanation[issue] = response

st.divider()

st.subheader("4.2 Handling Incidental Findings")
incidental = st.text_area("How would you handle and report incidental findings (e.g., unexpected medication associations)?")

st.subheader("4.3 Limitations")
limitations = st.text_area("Acknowledge limitations of your approach and discuss how they may affect interpretation or application.")

# --------------------------------------------
st.header("Part 5: Reflection")

st.subheader("5.1 Iterative Design")
iteration = st.text_area("How might results from your initial experiment inform future research directions?")

st.subheader("5.2 Multidisciplinary Collaboration")
multidisciplinary = st.text_area("How does your design incorporate multidisciplinary perspectives? Where would clinical input be essential?")

st.subheader("5.3 Communicating Your Design")
st.markdown("Describe your strategy for communicating your experiment to each audience:")
ai_peer = st.text_area("AI/ML Technical Peers")
clinician = st.text_area("Clinical Providers without AI expertise")
irb = st.text_area("Institutional Review Boards/Ethics Committees")

# --------------------------------------------

st.success("You have completed all parts of the assignment! Please copy your responses to save or submit them as instructed by your course/instructor.")

st.markdown("---")

if st.button("Show Summary of My Answers"):
    st.header("Your Answers Summary")
    st.write("**Part 1: Knowledge Gaps & Research Questions**")
    st.write(f"1. {gap1}  \n2. {gap2}  \n3. {gap3}")
    st.write(f"**Primary:** {primary_q}\n**Secondary 1:** {secondary_q1}\n**Secondary 2:** {secondary_q2}")
    st.write(f"**Alignment:** {align}")

    st.write("**Part 2: Data Management**")
    st.write(f"**Data Elements:** {data_elements} {other_data_elements}")
    st.write(f"**Inclusion:** {inclusion}\n**Exclusion:** {exclusion}\n**Missing:** {missing}\n**Bias:** {bias}")
    st.write(f"**Unstructured:** {unstructured}\n**Normalize:** {normalize}\n**Temporal:** {temporal}\n**Derived:** {derived}")
    st.write(f"**Temporal Shift:** {temporal_shift}\n**Class Balancing:** {balancing}\n**Demographics:** {demographics}\n**Generalizability:** {generalizability}")

    st.write("**Part 3: Experimental Design**")
    st.write(f"**Algorithms: 1:** {algo1} **2:** {algo2} **3:** {algo3}")
    st.write(f"**Chosen Algorithm:** {chosen_algo}")
    st.write(f"**Addresses Gaps:** {address_gaps}")
    st.write(f"**Metrics:** {metrics}  \nAdditional: {metric_other if 'Other' in metrics else ''}")
    st.write(f"**Metrics Justification:** {metrics_justification}\n**Validation:** {validation}\n**Relevance:** {relevance}")
    st.write(f"**Concept Drift:** {concept_drift}  \n**Transparency:** {transparency}  \n**Fairness:** {fairness}  \n**Prospective Readiness:** {prospective_ready}")

    st.write("**Part 4: Ethics & Limitations**")
    for k, v in eth_explanation.items():
        st.write(f"**{k}:** {v}")
    st.write(f"**Incidental Findings:** {incidental}")
    st.write(f"**Limitations:** {limitations}")

    st.write("**Part 5: Reflection**")
    st.write(f"**Iterative Design:** {iteration}\n**Multidisciplinary:** {multidisciplinary}\n**AI/ML Peers:** {ai_peer}\n**Clinicians:** {clinician}\n**IRB:** {irb}")

    st.info("Copy this output as your assignment review or for archiving.")