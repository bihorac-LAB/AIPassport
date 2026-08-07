import streamlit as st
import pandas as pd

st.title("1.5 Leveraging Multidisciplinary Team Strengths (Clinical Research)")

# ========= HELPER (SAMPLE DATA PREVIEW): =========

@st.cache_data
def load_mimic_demo():
    # Demo: synthetic sample representing MIMIC-IV patient, diagnosis, admission structure
    return pd.DataFrame([
        {"subject_id": "10004097", "hadm_id": "28272081", "gender": "M", "age": 75, "admittime": "2021-04-03",
         "diagnosis": "Acute infarction (stroke)", "ed_outcome": "ICU", "ed_severity": 4, "ed_arrival_hour": 13,
         "ed_meds_administered": 2},
        {"subject_id": "10020701", "hadm_id": "27238410", "gender": "F", "age": 64, "admittime": "2022-11-11",
         "diagnosis": "TIA", "ed_outcome": "Floor", "ed_severity": 2, "ed_arrival_hour": 8,
         "ed_meds_administered": 1},
        {"subject_id": "10023148", "hadm_id": "29688370", "gender": "F", "age": 52, "admittime": "2020-06-18",
         "diagnosis": "Intracerebral hemorrhage", "ed_outcome": "ICU", "ed_severity": 5, "ed_arrival_hour": 20,
         "ed_meds_administered": 3},
        {"subject_id": "10029984", "hadm_id": "25409683", "gender": "M", "age": 80, "admittime": "2021-08-29",
         "diagnosis": "Thrombotic stroke", "ed_outcome": "ICU", "ed_severity": 4, "ed_arrival_hour": 15,
         "ed_meds_administered": 2},
        {"subject_id": "10033388", "hadm_id": "29938721", "gender": "F", "age": 42, "admittime": "2020-10-20",
         "diagnosis": "Migraine (stroke mimic)", "ed_outcome": "Discharge", "ed_severity": 1, "ed_arrival_hour": 17,
         "ed_meds_administered": 0},
    ])

@st.cache_data
def load_chexpert_demo():
    # Demo: sample CheXpert data (synthetic)
    return pd.DataFrame([
        {"Study": "study1/img1.png", "Sex": "Male", "Age": 69, "No Finding": 0, "Stroke": 1, "Edema": 0, "Pneumonia": 0},
        {"Study": "study2/img9.png", "Sex": "Female", "Age": 80, "No Finding": 0, "Stroke": 0, "Edema": 0, "Pneumonia": 1},
        {"Study": "study1/img3.png", "Sex": "Male", "Age": 45, "No Finding": 1, "Stroke": 0, "Edema": 0, "Pneumonia": 0},
        {"Study": "study9/img1.png", "Sex": "Female", "Age": 57, "No Finding": 0, "Stroke": 1, "Edema": 1, "Pneumonia": 0},
        {"Study": "study3/img2.png", "Sex": "Male", "Age": 74, "No Finding": 0, "Stroke": 0, "Edema": 0, "Pneumonia": 0},
    ])


with st.expander("Datasets, tools, and sample data", expanded=False):
    st.markdown("""
**Datasets**
- [MIMIC-IV](https://physionet.org/content/mimiciv/2.2/): ICU/EHR data with patient encounters, ED visits, and outcomes.
- [CheXpert](https://stanfordmlgroup.github.io/competitions/chexpert/): chest X-ray dataset with multi-label findings.

**Collaboration tools**
- [Microsoft Teams](https://www.microsoft.com/en-us/microsoft-teams/): chat, meetings, file sharing, channels.
- [Trello](https://trello.com/): tasks, boards, assigned actions.
""")

    show_mimic = st.checkbox("Show MIMIC-IV demo data")
    show_chexpert = st.checkbox("Show CheXpert demo data")
    if show_mimic:
        st.dataframe(load_mimic_demo(), use_container_width=True)
    if show_chexpert:
        st.dataframe(load_chexpert_demo(), use_container_width=True)

    st.info("Demo datasets shown are for assignment context only. Use linked resources for full data.")

# ============== MAIN NOTEBOOK / ASSIGNMENT NAVIGATION ==============

st.header("MS5. Leveraging Multidisciplinary Team Strengths - Clinical Track")

tabs = [
    "Introduction",
    "Part 1: The Multidisciplinary Landscape",
    "Part 2: Communication Strategies",
    "Part 3: Team-Based Decision-Making",
    "Part 4: Training Opportunities",
    "Part 5: Collaboration Tools",
    "Part 6: Reflection"
]
selection = st.selectbox("Choose assignment section", tabs)

# -------------------
if selection == tabs[0]:
    st.header("Assignment Overview")
    st.markdown("""
Welcome! In this assignment, you will explore strategies and best practices for **building, managing, and optimizing multidisciplinary teams** in clinical AI projects.

**Clinical Track Focus:**  
You are leading a project to develop an AI system that assists Emergency Department (ED) physicians in triaging suspected stroke patients.

**You will:**  
- Identify key team roles and responsibilities  
- Develop team communication and problem-solving strategies  
- Apply clinical and technical datasets (MIMIC-IV, CheXpert) as context for your planning  
- Leverage modern collaboration tools  
- Address workflow integration, training, and ethical challenges

---  
_Data previews for MIMIC-IV and CheXpert are available in the dataset expander above. Leverage these real-world datasets as you respond to planning and teamwork activities below._

---
    """)

# =================== PART 1 ======================
if selection == tabs[1]:
    st.header("Part 1: Understanding the Multidisciplinary Landscape")

    st.markdown("""
**Case:**  
You're leading an AI project to develop a real-time stroke triage tool in the ED. Your resources include funding, stakeholder attention, and a 6-month timeline.
""")

    st.subheader("Task 1.1: Essential Team Roles")
    st.markdown(
        "Identify at least **five essential roles** needed for this project. For each:\n"
        "* Key responsibilities\n"
        "* The expertise they bring\n"
        "* How their contribution will impact the project outcome"
    )
    with st.form("Essential Roles"):
        roles = [f"Role {i+1}" for i in range(5)]
        for role_name in roles:
            st.text_input(f"{role_name} name", key=f"r{role_name}")
            st.text_area(f"{role_name}: Key Responsibilities", key=f"r_resp_{role_name}")
            st.text_area(f"{role_name}: Expertise", key=f"r_ex_{role_name}")
            st.text_area(f"{role_name}: Project Impact", key=f"r_imp_{role_name}")
        st.form_submit_button("Save Roles (Not persisted; for your work only)")

    st.subheader("Task 1.2: Competing Priorities")
    st.text_area("Which roles might have competing priorities or different views on goals? Where might tension arise, and why?", key="part1_2")

    st.subheader("Task 1.3: Organizational Structure")
    st.text_area("Describe (or sketch) an organizational structure for your team, with rationale.", key="part1_3")

# =================== PART 2 ======================
if selection == tabs[2]:
    st.header("Part 2: Communication Strategies")

    st.markdown("""
**Team:**  
Emergency physician, neurologist, data scientist, software engineer, nurse informaticist, hospital administrator, patient advocate.

**Challenge:**  
Diverse expertise, technical and clinical knowledge varies.
""")

    st.subheader("Task 2.1: Communication Strategy")
    st.markdown("Plan for:")
    st.markdown("""
- Meeting frequency, format, objectives
- Documentation methods/standards
- Knowledge sharing (tech & clinical)
- Progress reporting to stakeholders
        """)
    st.text_area("Your Communication Strategy", key="part2_1")

    st.subheader("Task 2.2: Shared Glossary")
    columns = st.columns(2)
    with columns[0]:
        st.markdown("**Term**")
        for i in range(10):
            st.text_input(f"Term {i+1}", key=f"glo_term_{i}")
    with columns[1]:
        st.markdown("**Definition (for clinicians & technologists)**")
        for i in range(10):
            st.text_area(f"Def {i+1}", key=f"glo_def_{i}")

    st.subheader("Task 2.3: Patient & Workflow Focus")
    st.text_area("Three strategies to ensure patient needs and clinical workflow stay central, even during technical discussions:", key="part2_3")

# =================== PART 3 ======================
if selection == tabs[3]:
    st.header("Part 3: Team-Based Decision-Making")
    st.markdown("""
Your team faces a choice:

**Approach A:** Deep learning; higher accuracy (92%) but low explainability.  
**Approach B:** More explainable; lower accuracy (88%) but can give reasons.

Team is divided.  
""")

    st.subheader("Task 3.1: Decision-Making Framework")
    st.markdown("Design a process to fairly weigh both approaches, address all viewpoints, reach consensus, and document with rationale.")
    st.text_area("Decision-making framework", key="part3_1")

    st.subheader("Task 3.2: Cognitive Biases")
    st.markdown("Identify three biases that might affect the process and propose mitigations.")
    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            st.text_input(f"Bias {i+1}", key=f"bias{i+1}")
            st.text_area(f"Mitigation {i+1}", key=f"mitg{i+1}")

    st.subheader("Task 3.3: Decision Documentation Template")
    st.markdown("Template should include all perspectives, rationale, decision, and contingencies.")
    st.text_area("Decision documentation template", key="part3_3")

# =================== PART 4 ======================
if selection == tabs[4]:
    st.header("Part 4: Training Opportunities")
    st.markdown("""
Progress check:  
- Clinical team struggles with model validation  
- Technical team unsure about stroke protocols  
- Divergent expectations for 'success'
""")

    st.subheader("Task 4.1: Cross-Training Plan")
    st.markdown("- List specific topics for training\n- Who leads which part?\n- Format/duration\n- Effectiveness assessment")
    st.text_area("Cross-training plan", key="part4_1")

    st.subheader("Task 4.2: Shadowing Schedule")
    st.markdown("Design a 'Day in the Life' schedule. What should each group focus on during observation?")
    st.text_area("Shadowing schedule and focus points", key="part4_2")

    st.subheader("Task 4.3: External Resources")
    st.markdown("Identify three external resources (courses, workshops, key articles), and for each, what gap it will address.")
    for i in range(3):
        st.text_input(f"Resource {i+1}", key=f"extres{i+1}")
        st.text_area(f"How it helps", key=f"extreshow{i+1}")

# =================== PART 5 ======================
if selection == tabs[5]:
    st.header("Part 5: Collaboration Tools")

    st.markdown("""
Team is cross-departmental, some remote, some onsite, confidentiality critical.
""")

    st.subheader("Task 5.1: Digital Tool Selection")
    st.markdown("Pick three digital tools; for each, briefly justify:")
    for i in range(3):
        st.text_input(f"Tool {i+1}", key=f"collabtool{i+1}")
        st.text_area(f"Purpose & Features", key=f"collpurp{i+1}")
        st.text_area(f"Limitations/Concerns", key=f"colllim{i+1}")

    st.subheader("Task 5.2: Secure Sharing Protocol")
    st.markdown("- Sharing/document control for: docs, clinical data, code/specs, meeting notes")
    st.text_area("Protocol for secure sharing", key="part5_2")

    st.subheader("Task 5.3: Weekly Progress Dashboard")
    st.markdown("Template should show milestones, challenges, deadlines, achievements")
    st.text_area("Weekly dashboard template/design", key="part5_3")

# =================== PART 6 ======================
if selection == tabs[6]:
    st.header("Part 6: Reflection")

    st.subheader("Task 6.1: Integrating AI into Clinical Workflows")
    st.markdown("What challenges might you encounter, and how can a multidisciplinary team reduce resistance to change?")
    st.text_area("Integration reflection", key="part6_1")

    st.subheader("Task 6.2: Team Effectiveness Metrics")
    st.markdown("Suggest three ways to evaluate successful collaboration in your team.")
    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            st.text_input(f"Metric {i+1}", key=f"teameff{i+1}")

    st.subheader("Task 6.3: Addressing Ethics")
    st.markdown("Describe a process to identify, discuss, and resolve ethical issues as a multidisciplinary team.")
    st.text_area("Ethical issue resolution process", key="part6_3")

st.info("For more on the real-world data: [MIMIC-IV documentation](https://physionet.org/content/mimiciv/2.2/) | [CheXpert docs](https://stanfordmlgroup.github.io/competitions/chexpert/).")
