import streamlit as st

st.set_page_config(page_title="MS2: AI Lifecycle – Basic Science Track", layout="wide")
st.title("1.2 Artificial Intelligence Lifecycle (Basic Science)")
st.header("Basic Science Track: Molecular Classification Project")

st.markdown("""
Welcome to the **AI Project Lifecycle Simulation**!

In this basic science scenario, you will step through the lifecycle of an AI project to classify molecules (e.g., for predicting protein function or drug-likeness). At each phase, you'll make choices, reflect, and see typical LLM guidance.

_There is no real molecular data required – this is a walkthrough!_
""")

st.markdown("----")

#### 1. Data Collection Step ####
st.header("Step 1: Collecting Molecular Data")
st.markdown("""
You're planning a molecular classification project.  
You need to collect a dataset of molecules and their class labels (e.g., toxic vs non-toxic, drug-like vs non-drug-like).

**What source will you use for this dataset?**  
""")
data_source = st.radio("Choose a data source below:",
                       ["Public molecular database (e.g. ChEMBL, PubChem)",
                        "In-house experimental dataset",
                        "Simulated/Generated molecules",
                        "I'm not sure / Other"])
st.write(f"**You chose**: {data_source}")

st.markdown("Why might this data source be appropriate, and what potential biases could it introduce?")
source_just = st.text_area("Reflect here:", key="data_source_reflect")

if st.button("LLM Guidance: Data Collection"):
    if data_source == "Public molecular database (e.g. ChEMBL, PubChem)":
        st.info("These offer large, diverse datasets, often with standardized structures and rich metadata. Beware of reporting/collection bias and label quality issues. Make sure your project goal matches the label definitions in these datasets.")
    elif data_source == "In-house experimental dataset":
        st.info("Such data is closer to your specific application, but could have smaller size, unstandardized formats, or local lab biases. Be transparent about experimental protocols and any missing data.")
    elif data_source == "Simulated/Generated molecules":
        st.info("Simulated datasets are helpful for data augmentation or novel compound exploration, but may not represent real-world chemistry. Validation using external sources is important.")
    else:
        st.info("Selecting the right molecular dataset is crucial; always document data provenance and consider possible biases that could affect downstream model generalizability.")

st.markdown("----")

#### 2. Preprocessing Step ####
st.header("Step 2: Preprocessing and Feature Engineering")
st.markdown("""
You have a set of molecules, each as a SMILES string (a common text-based chemical representation).

**What preprocessing steps will you take before modeling?**  
(_select all you think are important_)""")
prepro_steps = st.multiselect("Pick preprocessing steps:",
    [
        "Remove duplicate molecules",
        "Standardize chemical representations",
        "Calculate molecular descriptors/embeddings",
        "Handle missing values",
        "Scale/normalize numerical features",
        "Assign class labels",
        "None – ready to model"
    ])
st.write(f"**Your selected steps:** {', '.join(prepro_steps) if prepro_steps else 'None'}")

st.markdown("Which of these do you feel LEAST confident about, and why?")
step_reflect = st.text_area("Reflect here:", key="prepro_reflect")

if st.button("LLM Guidance: Preprocessing"):
    feedback = []
    if "Remove duplicate molecules" in prepro_steps:
        feedback.append("✔️ Removing duplicates avoids data leakage and overfitting.")
    if "Standardize chemical representations" in prepro_steps:
        feedback.append("✔️ Standardization ensures all molecules are consistently represented (e.g., tautomers, salts).")
    if "Calculate molecular descriptors/embeddings" in prepro_steps:
        feedback.append("✔️ Machine learning models can't use raw SMILES; you need to convert to descriptors or embeddings (e.g., molecular weight, fingerprints, graph embeddings).")
    if "Handle missing values" in prepro_steps:
        feedback.append("✔️ Missing data must be handled to prevent errors and bias.")
    if "Scale/normalize numerical features" in prepro_steps:
        feedback.append("✔️ Scaling helps if using models sensitive to feature scale (e.g., logistic regression).")
    if "Assign class labels" in prepro_steps:
        feedback.append("✔️ Labels are required for supervised learning.")
    if not prepro_steps or "None – ready to model" in prepro_steps:
        feedback.append("⚠️ Most raw molecular datasets need cleaning and descriptor calculation before modeling.")
    st.info("\n".join(feedback))

st.markdown("----")

#### 3. Modeling Step ####
st.header("Step 3: Model Selection")
st.markdown("""
Suppose your goal is to classify molecules as 'active' or 'inactive' against a protein.  
You have typical molecular fingerprints (binary vectors) as features.
""")
model_choice = st.radio(
    "Choose a modeling approach:",
    [
        "Logistic regression",
        "Random forest",
        "Neural network",
        "Support vector machine",
        "Other (add below)"
    ]
)
other_model = ""
if model_choice == "Other (add below)":
    other_model = st.text_input("Specify model:")

st.markdown("Why did you pick this model?")
model_reflect = st.text_area("Your reasoning:", key="modelwhy")

if st.button("LLM Guidance: Model choice"):
    if model_choice == "Logistic regression":
        st.info("Logistic regression works well for linearly separable binary tasks, fast to train, and its results are interpretable. If you have high-dimensional binary descriptors, regularization is important.")
    elif model_choice == "Random forest":
        st.info("Random forests handle high-dimensional molecular fingerprints well, resist overfitting, and offer feature importance interpretation. Good baseline for many cheminformatics tasks.")
    elif model_choice == "Neural network":
        st.info("Neural networks can capture nonlinear features, especially if using graph-based or sequential models (e.g., graph neural networks). But they require larger datasets and careful hyperparameter selection.")
    elif model_choice == "Support vector machine":
        st.info("SVMs are strong with high-dimensional data and can model nonlinearity with kernels, but need tuning and may struggle with very large datasets.")
    elif model_choice == "Other (add below)":
        st.info(f"You chose: {other_model.strip() or '(unspecified)'} -- always explain how the inductive bias and requirements match your problem/data.")

st.markdown("----")

#### 4. Validation ####
st.header("Step 4: Model Validation")
st.markdown("""
You have trained your classifier.

**How will you validate performance?**  
(_select all that apply_) 
""")
validation = st.multiselect(
    "Pick your validation approach(es):",
    [
        "Simple train/test split",
        "Cross-validation",
        "External test set (different source)",
        "Leave-cluster-out validation (e.g., by scaffold or class)",
        "Other (add below)"
    ])
other_val = ""
if "Other (add below)" in validation:
    other_val = st.text_input("Describe other validation:")

st.markdown("Which approach would best test generalizability?")
gen_reflect = st.text_area("Your thoughts on generalizability:", key="valgeneral")

if st.button("LLM Guidance: Validation"):
    lines = []
    if "Cross-validation" in validation:
        lines.append("✔️ Cross-validation (e.g., K-fold) is a robust internal check on generalization within your data.")
    if "External test set (different source)" in validation:
        lines.append("✔️ An external test set best measures generalizability to unseen chemical space/labs.")
    if "Leave-cluster-out validation (e.g., by scaffold or class)" in validation:
        lines.append("✔️ Scaffold-split validation is crucial to test how well the model extrapolates to novel molecule types, not just close analogs.")
    if "Simple train/test split" in validation:
        lines.append("⚠️ Single splits might not fully capture model stability, especially for clustered molecular data.")
    if "Other (add below)" in validation:
        lines.append(f"Other: {other_val.strip() or '(unspecified)'} -- justify your approach!")
    if not lines:
        lines.append("Validation is critical for trustworthy molecular ML. Use multiple strategies!")
    st.info("\n".join(lines))

st.markdown("----")
st.header("Summary & Reflection")

st.markdown("""
**Assignment Reflection:**  
- What do you see as the most important/least obvious challenge in the molecular AI lifecycle?
- What would you like to learn next?
""")

st.text_area("Freeform reflection:", key="final_reflect")

st.success("Thank you for completing the simulation! You have stepped through core lifecycle decisions for a molecular AI project. Remember: proper documentation and justification at each stage builds trust and rigor in your science.")

st.markdown("""
---
References:
- [ChEMBL](https://www.ebi.ac.uk/chembl/), [PubChem](https://pubchem.ncbi.nlm.nih.gov/)
- [rdkit](https://www.rdkit.org/)
- [DeepChem](https://deepchem.io/)
- [OpenAI](https://platform.openai.com/docs/guides/chat)

*(If you want to expand the notebook with real data or OpenAI API calls, let your instructor know!)*
""")