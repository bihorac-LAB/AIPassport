import streamlit as st
import pandas as pd

st.set_page_config(page_title="MS5: Leveraging Multidisciplinary Team Strengths (Basic Science)", layout="wide")

st.title("1.5 Leveraging Multidisciplinary Team Strengths (Basic Science)")

st.markdown("""
**Datasets:**
- [Single Cell Portal](https://singlecell.broadinstitute.org/single_cell)
- [Human Protein Atlas](https://www.proteinatlas.org/)

**Tools:** 
- [Slack](https://slack.com/) | [GitHub](https://github.com/)
""")

st.markdown("""
### Case Context
You lead a project to develop an AI system that analyzes single-cell RNA-seq data, identifying novel cellular subtypes in brain tissue from both healthy controls and those with neurodegenerative disease. You have funding to build a multidisciplinary team and one year to deliver a working prototype.
---
""")

#### ---- PART 1 ----
st.header("Part 1: Understanding the Multidisciplinary Landscape")
st.markdown("""
#### You are forming your team. Interact with the fields below:
""")

with st.expander("Sample Data Table: Brain Single-Cell Expression"):
    df_example = pd.DataFrame({
        "Cell_ID": ["cell_1", "cell_2", "cell_3", "cell_4"],
        "Gene_A": [3.2, 0.0, 2.3, 7.1],
        "Gene_B": [0.0, 5.1, 1.2, 4.3],
        "Disease_Status": ["Control", "Disease", "Control", "Disease"]
    })
    st.dataframe(df_example)

st.subheader("Task 1.1: Essential Team Roles")
for i in range(1, 6):
    with st.form(key=f"role_{i}"):
        st.markdown(f"**Role #{i}:**")
        role = st.text_input(f"Role Name (#{i})", key=f"role_name_{i}")
        resp = st.text_area("Key Responsibilities", key=f"resp_{i}")
        exp = st.text_area("Expertise/Background", key=f"exp_{i}")
        impact = st.text_area("Contribution/Impact on Research", key=f"impact_{i}")
        st.form_submit_button("Save Role")

st.subheader("Task 1.2: Potential Tensions")
st.text_area("Which roles may have competing priorities and why? Where might tensions arise?", key="tensions")

st.subheader("Task 1.3: Organizational Structure")
st.text_area("Create a simple organizational structure and explain your rationale (e.g., org chart, lines of reporting, interface roles)", key="org_structure")

st.markdown("---")

#### ---- PART 2 ----
st.header("Part 2: Communication Strategies")

st.subheader("Task 2.1: Team Communication Plan")
st.text_area("How will you structure meetings, documentation, and progress reporting? Specify meeting types, docs, and methods of sharing knowledge.", key="comm_plan")

st.subheader("Task 2.2: Glossary of Key Terms")
terms = [
    "Dimensionality reduction", "Clustering", "Batch effect", "Cell heterogeneity", 
    "RNA-seq", "Feature selection", "Normalization", "Marker gene",
    "Dropout (in ML)", "Overfitting"
]
with st.form("glossary"):
    for term in terms:
        st.text_input(f"{term} (definition)", key=f"gloss_{term}")
    st.form_submit_button("Save Glossary")

st.subheader("Task 2.3: Ensuring Biological Relevance and Rigor")
st.text_area("List three strategies to keep biology/scientific rigor central during technical work.", key="relevance_rigor")

st.markdown("---")

#### ---- PART 3 ----
st.header("Part 3: Team-Based Decision-Making")

st.markdown("""
The team faces a key choice:
- **Approach A**: Unsupervised clustering for discovering new subtypes.
- **Approach B**: Supervised classification using prior cell-type markers.
""")
if st.checkbox("Show example marker gene table"):
    df_markers = pd.DataFrame({
        "Cell Type": ["Neuron", "Astrocyte", "Microglia", "Oligodendrocyte"],
        "Key Marker": ["MAP2", "GFAP", "IBA1", "MBP"]
    })
    st.dataframe(df_markers)

st.subheader("Task 3.1: Decision-Making Framework")
st.text_area("Design a framework for evaluating both options, addressing stakeholder concerns, and documenting decisions.", key="decision_framework")

st.subheader("Task 3.2: Cognitive Biases & Mitigation")
st.text_area("Identify three cognitive biases and propose mitigation strategies.", key="cog_biases")

st.subheader("Task 3.3: Decision Documentation Template")
doc_template = st.text_area("Create a template that records the final choice, rationale, dissenting opinions, and contingency plans.", key="decision_template", value=
"""Decision Summary:
Reasons for Selected Approach:
Stakeholder Concerns Raised:
How Concerns Were Addressed:
Contingency Plan if Chosen Approach Fails:
""")

st.markdown("---")

#### ---- PART 4 ----
st.header("Part 4: Training Opportunities")

st.subheader("Task 4.1: Cross-Training Plan")
st.text_area("Plan trainings to cover concepts (e.g., PCA, t-SNE, cell heterogeneity, validation). Who leads, duration, format, assessment?", key="cross_train")

st.subheader("Task 4.2: 'Day in the Lab' Shadowing Schedule")
st.text_area("Outline a mutual shadowing plan. What should computational folks focus on in the lab? What about biologists in the dry lab?", key="shadowing")

st.subheader("Task 4.3: External Learning Resources")
st.text_area(
    "Suggest three external resources (courses, workshops, articles), stating which gap each will address.",
    key="external_resources"
)

st.markdown("---")

#### ---- PART 5 ----
st.header("Part 5: Collaboration Tools")

st.subheader("Task 5.1: Tool Selection")
tools = ["Slack", "GitHub", "Google Drive", "Notion", "Dropbox", "JupyterHub", "Confluence"]
for i in range(1, 4):
    st.selectbox(f"Tool #{i}", options=tools, key=f"tool_{i}")
    st.text_area(f"Purpose, features, limitations for Tool #{i}", key=f"tool_{i}_desc")

st.subheader("Task 5.2: Sharing Protocols and Data")
st.text_area(
    "Describe your protocol for sharing research docs, data (raw/processed), code, and notes among the team.",
    key="sharing_protocol"
)

st.subheader("Task 5.3: Weekly Project Dashboard Template")
project_dashboard = st.text_area("Draft a dashboard template summarizing progress, issues, deadlines, and highlights.", value=
"""## Project Dashboard (Week of: [Date])

### Milestone Progress
- [ ] Milestone 1
- [ ] Milestone 2

### Analytical Challenges
- Issue: [Description]
- Input Requested from: [Team/Role]

### Upcoming Deadlines
1. [Deadline/Task]

### Recent Findings or Achievements
- [Description]
""", key="dashboard_template")

st.markdown("---")

#### ---- PART 6 ----
st.header("Part 6: Reflection")

st.subheader("Task 6.1: Integrating AI into Traditional Biology")
st.text_area(
    "Reflect on possible challenges in integrating AI into biology. How can a multidisciplinary approach overcome resistance?",
    key="ai_integration"
)

st.subheader("Task 6.2: Evaluating Team Effectiveness")
st.text_area(
    "Propose three concrete metrics or indicators of collaboration and team success.",
    key="effectiveness_metrics"
)

st.subheader("Task 6.3: Addressing Reproducibility Issues")
st.text_area(
    "Design a process for addressing reproducibility or methodological issues, leveraging the team's diverse expertise.",
    key="reproducibility_process"
)

st.markdown("""
---
### 🎓 **Links**
- [Single Cell Portal](https://singlecell.broadinstitute.org/single_cell)
- [Human Protein Atlas](https://www.proteinatlas.org/)
- [Slack](https://slack.com/)
- [GitHub](https://github.com/)

---  
*Fill in your answers throughout, download as PDF, or export notes as needed.*
""")