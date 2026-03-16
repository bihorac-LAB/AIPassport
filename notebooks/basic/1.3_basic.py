import streamlit as st

st.set_page_config(page_title="MS3 Biomedical AI Experiment Design (Basic Science Track)", layout="centered")

st.title("1.3 Designing Biomedical Artificial Intelligence Experiments (Basic Science Track)")

# ======= Datasets & Tools: Real Assignment-Only =======
st.markdown("""
**🗂 Datasets:**
- [Cell Painting Dataset](https://broad.io/CellPainting)
- [Allen Brain Atlas](https://portal.brain-map.org/)

**🛠 Tools:**
- [PyTorch](https://pytorch.org/)
- [scikit-learn](https://scikit-learn.org/stable/)
""")

st.markdown("---")

# ---------------- PART 1 -----------------
with st.expander("Part 1: Identifying Knowledge Gaps and Research Questions", expanded=True):
    st.markdown("""
    *You are a computational biologist in a lab studying how cells respond to drug compounds.  
    Your images capture subtle cell changes that traditional methods miss.  
    Leverage AI to classify phenotypes and uncover novel responses!*
    """)

    st.subheader("1.1 Literature Knowledge Gaps (pick AND elaborate)")
    gaps = st.multiselect(
        "Select at least three gaps or challenges commonly found in current literature:",
        [
            "Small labeled datasets limit model generalizability",
            "Models don’t detect subtle phenotype changes",
            "Lack of interpretability/biological insight",
            "Batch effects and imaging artifacts",
            "Difficulty applying across cell lines/treatments",
            "Limited validation for novel phenotypes"
        ])
    gap_details = st.text_area("Describe or elaborate on the selected knowledge gaps:")

    st.subheader("1.2 Research Questions (SMART)")
    st.caption("Brainstorm and clearly state one primary and two secondary research questions using SMART criteria.")
    primary_q = st.text_input("Primary research question:")
    secondary_q1 = st.text_input("Secondary research question 1:")
    secondary_q2 = st.text_input("Secondary research question 2:")

    st.subheader("1.3 Alignment and Advancement")
    st.text_area("How will your research questions address these gaps? What impact will this have for basic science?",
                 key="align")

# ---------------- PART 2 -----------------
with st.expander("Part 2: Data Management Strategy", expanded=False):
    st.markdown("""
    *Imagine you have full access to the [Cell Painting Dataset](https://broad.io/CellPainting).  
    Decide how you'll select, clean, process, and split images to create a robust AI experiment.*
    """)

    st.subheader("2.1 Data Selection")
    st.info("Select which image/staining types are MOST relevant for phenotype discovery.\nYou may select more than one.")
    image_types = st.multiselect(
        "Which staining channels or compartments will you include?",
        ["DNA", "Mitochondria", "Endoplasmic Reticulum", "Golgi", "Cytoskeleton", "Other (specify below)"])
    image_types_other = st.text_input("If 'Other,' specify here:")

    st.markdown("**Criteria:**")
    inclusions = st.text_area("Inclusion criteria for images (e.g., cell type, focus quality, treatment)")
    exclusions = st.text_area("Exclusion criteria for images")
    st.radio("How will you handle poor quality images?", ["Manual review/removal", "Automated quality scoring", "Both", "Other"], index=2)
    st.text_area("How will you address possible biases in image acquisition (batch effects, experimental conditions)?", key="biases")

    st.subheader("2.2 Data Preprocessing Pipeline")
    st.info("Consider aspects such as normalization, feature extraction, reducing dimensionality, and creating derived features.")
    norm = st.checkbox("Will you apply normalization and standardization?")
    normalize_what = st.text_input("If yes, what aspects? (e.g., intensity, background):", disabled=not norm)
    feature_method = st.radio(
        "Preferred feature extraction method?",
        ["Pretrained CNN", "Custom CNN", "Classical image features (e.g., shape, texture)", "Hybrid/Other"])
    feature_details = st.text_input("If hybrid/other, describe here:", disabled=feature_method not in ["Hybrid/Other"])
    dim_reduce = st.selectbox(
        "Will you use dimensionality reduction techniques?",
        ["None", "PCA", "UMAP", "t-SNE", "Autoencoder"])
    derived_feat = st.text_area("Suggest at least one biologically relevant derived feature (e.g., nuclear/cytoplasmic ratio):")

    st.subheader("2.3 Splitting/Generalization")
    st.markdown("Design your data splits and generalization strategy.")
    batch_effects = st.radio(
        "How will you handle batch effects during splitting?",
        ["Stratified by batch", "Hold out batches for test only", "Random split", "Other (describe below)"])
    batch_other = st.text_input("Describe if 'Other' for batches:", disabled=batch_effects != "Other (describe below)")
    st.checkbox("Will you use class balancing (oversample/undersample) to handle rare phenotypes?")
    st.selectbox("How will you represent distinct cell lines or treatment conditions?",
                 ["Include as features", "Stratified sampling", "Both", "Other"])
    st.text_area("How will you assess if your model generalizes to different imaging platforms or datasets?")

# ---------------- PART 3 -----------------
with st.expander("Part 3: Experimental Design", expanded=False):

    st.markdown("""
    *Now design the actual AI experiment for classification/discovery!*
    """)
    st.subheader("3.1 Model Selection")
    st.markdown("Below, pick **three** candidate AI algorithms (you can select and elaborate on a favorite).")
    algo = st.multiselect(
        "Choose at least three AI models to consider for this image classification task:",
        [
            "Convolutional Neural Network (PyTorch)",
            "Random Forest (scikit-learn)",
            "Gradient Boosted Trees",
            "Transfer learning with pretrained model",
            "Support Vector Machine",
            "Autoencoder + clustering",
            "Other"
        ])
    st.text_area("For each, what are their potential strengths/weaknesses with your dataset?")

    selected_algo = st.radio("Which approach will you use for your main experiment?",
                             algo)
    st.text_area("Justify your choice—why does it address your research questions and the knowledge gaps earlier?")

    st.subheader("3.2 Evaluation Framework")
    st.markdown("Select which **evaluation metrics** you will use. You may select more than one.")
    metrics = st.multiselect("Metrics:",
        ["Accuracy", "F1 Score", "Precision/Recall", "AUC/ROC", "Confusion Matrix", "Biological enrichment (GO, pathways)", "Cluster purity/silhouette", "Cross-dataset transfer", "Other"])
    st.text_area("Justify your metrics (how do they reflect **biological AND technical** success?)")
    st.radio("Cross-validation type for model validation?",
             ["K-fold (random)", "K-fold (by cell line)", "Leave-one-batch-out", "Other"])
    st.text_area("How will you determine if coverage/generalizability is adequate?")

    st.text_area("How will you make sure model findings are **biologically meaningful**? (e.g., expert review, linking features to cellular pathways)")

    st.subheader("3.3 Addressing AI for Science Challenges")
    st.markdown("Briefly explain how you'll tackle these common obstacles:")
    st.text_area("How to handle heterogeneity in cellular responses?")
    st.text_area("How to ensure the model captures **biologically interpretable** features?")
    st.text_area("How to interpret/model which image features drive a particular phenotype?", key="interpret")
    st.text_area("If you discover novel or ambiguous phenotypes, how will you experimentally or computationally validate them?")

# ---------------- PART 4 -----------------
with st.expander("Part 4: Ethical Considerations and Limitations", expanded=False):

    st.markdown("*Reflect on why basic research AI also requires strong ethical thinking and limits awareness.*")
    st.subheader("4.1 Ethical Considerations")
    st.markdown("Pick and explain at least three ethical issues relevant to this cellular imaging project.")
    eth_choices = st.multiselect(
        "Ethical issues:",
        [
            "Data privacy/confidentiality",
            "Data ownership/credit for image contributors",
            "Bias in cell lines, compounds, or imaging hardware",
            "Potential misinterpretation of AI-driven results",
            "Responsible reporting of surprising or ambiguous findings",
            "Transparency and reproducibility",
            "Other"
        ])
    st.text_area("How will you address/mitigate the ethical issues you selected above?")

    st.subheader("4.2 Handling Unexpected Discoveries")
    st.text_area("If your model finds results that contradict established biology, how will you verify, communicate, or respond?")

    st.subheader("4.3 Limitations")
    st.text_area("Identify the main limitations of your approach AND how these might affect interpretation or next steps in science.")

# ---------------- PART 5 -----------------
with st.expander("Part 5: Reflection", expanded=False):

    st.markdown("Scientific AI design is iterative and multidisciplinary!")
    st.subheader("5.1 Iterative Experimental Design")
    st.text_area("If your experiment suggests new questions or findings, how would you adapt for future research?")
    st.subheader("5.2 Multidisciplinary Collaboration")
    st.checkbox("Will you seek input from domain-expert biologists?")
    st.text_area("Where would direct feedback from biological scientists be essential in this workflow?")
    st.subheader("5.3 Communication Strategies")
    st.markdown("How would you communicate your design/results to each audience?")
    st.text_area("AI/ML technical peers")
    st.text_area("Biological scientists without AI expertise")
    st.text_area("Institutional review boards or ethics committees")

# Optional: Submission "toast"
if st.button("✅ Mark assignment as complete"):
    st.success("Assignment marked as complete! Review your responses and save for your reference.")

st.caption("Tip: You can expand/collapse each section as you work—and come back to change your answers anytime while the app runs.")