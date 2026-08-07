import streamlit as st

st.title("1.4 Training, Validation & Generalizability (Clinical Research)")

# --- Data & Tools ---
st.markdown("""
**🗂 Datasets:**  
- [MIMIC-CXR](https://physionet.org/content/mimic-cxr/2.0.0/)  
- [NIH Chest X-ray Dataset](https://www.nih.gov/news-events/news-releases/nih-clinical-center-provides-one-largest-publicly-available-chest-x-ray-datasets-scientific-community)  

**🛠 Tools:**  
- [Keras (deep learning framework)](https://keras.io/)  
- [ML-fairness-gym (fairness experiments)](https://github.com/google/ml-fairness-gym)  
""")

st.info("This assignment will guide you step-by-step through robust validation and fairness strategies for developing deep learning models to detect pneumonia from chest X-rays.")

# Helpful navigation tip
st.caption("Click to expand each section, and interact with checkboxes, radios, and text boxes to develop your experimental design!")

st.markdown("---")

## -------- PART 1: Understanding Training & Validation Fundamentals --------
with st.expander("Part 1: Understanding Training & Validation Fundamentals", expanded=True):
    st.markdown("""
    **Clinical Track Case:**  
    Your institution collected **10,000 chest X-rays** from three hospitals over 3 years, using five X-ray machines, with a diverse, mostly urban patient population.
    """)

    st.subheader("1.1 Issues with Simple Random Train-Test Split")
    
    issues = st.multiselect(
        "Select at least three reasons why a simple random split may be problematic for this dataset:",
        [
            "Temporal leakage (data from the future in training set)",
            "Patients may appear in both train and test sets",
            "Class imbalance across hospitals or machines",
            "Ignored batch effects from different imaging equipment",
            "Incomplete representation of demographic subgroups in train/test",
            "Prevalence changes over time ignored",
        ]
    )
    st.text_area("Elaborate on the issues you selected and describe at least three risks of a simple random split.",
                 key="random_split_risks")

    st.divider()

    st.subheader("1.2 Advanced Data Splitting Strategy")
    st.markdown("Design a splitting strategy that addresses:")
    st.markdown("- Temporal factors\n- Equipment differences\n- Demographics\n- Prevalence variability")

    split_strategy = st.radio(
        "Which splitting principle do you favor?",
        [
            "Temporal split (train: first two years, test: last year)",
            "Hospital-wise split (hold out one hospital for test)",
            "Equipment-aware (stratify by X-ray machine)",
            "Hybrid (temporal + hospital + demographics)",
            "Other (describe below)"
        ]
    )
    st.text_area("Describe your proposed data splitting strategy in detail:", key="split_strategy_desc")

    st.divider()

    st.subheader("1.3 Linking Split to Identified Issues")
    st.text_area("Explain how your splitting strategy resolves the issues you chose in Task 1.1.")


## -------- PART 2: Internal Validation Techniques --------
with st.expander("Part 2: Internal Validation Techniques", expanded=False):
    st.markdown("""
    **Goal:** Evaluate your model robustly using the splits you designed.
    """)

    st.subheader("2.1 Cross-Validation Framework")
    cv_type = st.selectbox(
        "Which type of cross-validation best fits the dataset?",
        ["K-fold (random)", 
         "K-fold (hospital-stratified)", 
         "Leave-one-hospital-out", 
         "Time-series (rolling window)", 
         "Nested CV", 
         "Other"])
    n_folds = st.slider("How many folds?", 3, 10, 5)
    stratify = st.text_area(
        "How would you stratify? (e.g., by outcome label, hospital, demographic variables)",
        key="cv_stratify"
    )
    metrics = st.multiselect(
        "Which metrics would you compute for each CV fold?",
        ["AUC/ROC", "Accuracy", "F1 score", "Sensitivity", "Specificity", "Calibration", "Fairness/disparities", "Other"]
    )

    st.divider()

    st.subheader("2.2 Additional Internal Validation")
    select_val = st.multiselect(
        "Select at least two additional internal validation approaches:",
        [
            "Bootstrapping with patient-level sampling",
            "Internal holdout set (not seen in hyperparameter tuning)",
            "Permutation testing (shuffling labels)",
            "Robustness to image augmentation",
            "Patient-level cross-validation (no data leakage)",
            "Fairness audits across patient groups",
            "Other"
        ]
    )
    st.text_area("Describe the additional approaches and their benefits.", key="additional_internal_val")

    st.divider()

    st.subheader("2.3 Calibration Approach")
    st.markdown("How will you ensure your model's output probabilities are well-calibrated?")
    st.checkbox("Calibration plot (e.g., reliability curve)")
    st.checkbox("Brier score")
    st.checkbox("Expected Calibration Error (ECE)")
    st.text_area("Describe your visualization(s) and how you will quantify calibration.", key="calib_vis")
    st.selectbox("If recalibration is needed, which technique would you use?",
                ["Platt scaling", "Isotonic regression", "Temperature scaling", "Other"])
    st.text_input("Describe your recalibration approach (if needed).", key="recalib")


## -------- PART 3: External Validation and Generalizability --------
with st.expander("Part 3: External Validation & Generalizability", expanded=False):
    st.markdown("""
    **Clinical Track Case:**  
    Your model (trained internally) will be tested on the **NIH Chest X-ray dataset**.
    """)

    st.subheader("3.1 External Validation Framework")
    prep_steps = st.text_area("How will you preprocess the external dataset to ensure compatibility?")
    metrics_ext = st.multiselect(
        "Which metrics will you calculate for external validation?",
        ["AUC/ROC", "Accuracy", "F1", "Precision/Recall", "Calibration", "Fairness", "Other"])
    comp_method = st.text_area("How will you compare model performance between internal and external datasets?")
    perf_drop = st.slider("Threshold: What minimum performance drop (AUC or accuracy) would trigger model refinement?", 1, 30, 10, help="Specify as percent drop.")

    st.divider()

    st.subheader("3.2 Addressing Generalizability Gaps")
    general_gap = st.text_area(
        "Your model underperforms on pediatric patients and portable machine X-rays. Propose a strategy to improve generalizability WITHOUT overfitting to this external dataset."
    )

    st.divider()

    st.subheader("3.3 Systematic Subgroup Evaluation")
    st.markdown("How will you evaluate and address disparities?")
    st.text_area(
        "Describe how you would (i) identify & quantify subgroup performance (demographics, clinical context), (ii) test for statistical significance, and (iii) address significant disparities detected."
    )

## -------- PART 4: Addressing Model Robustness --------
with st.expander("Part 4: Addressing Model Robustness", expanded=False):
    st.markdown("""
    **Goal:** Model should remain accurate despite benign image variation.
    """)

    st.subheader("4.1 Robustness Experiments")
    st.multiselect(
        "Select which variations you would explicitly test (select all that apply):",
        [
            "Patient positioning (AP vs. PA, rotation)",
            "Varying inspiration depth",
            "Presence of medical devices",
            "Contrast, brightness or noise changes",
            "Other"
        ])
    st.text_area("For each selected variation, how would you implement and evaluate robustness?", key="robustness_steps")

    st.divider()

    st.subheader("4.2 Improving Device Robustness")
    st.text_area("Your model degrades with medical devices in images. Describe an approach to improve this (e.g., additional training, augmentations, post-processing, etc.).")

    st.divider()

    st.subheader("4.3 Continuous Model Monitoring")
    st.markdown("Develop a monitoring plan after deployment:")
    st.text_area("What continuous metrics will you track over time & how often will you evaluate robustness?")
    st.slider("What threshold (e.g. % drop in metric) will trigger a model update?", 1, 20, 5)
    st.text_area("How will you update models in production WITHOUT disrupting clinical workflow?")

## -------- PART 5: Demographic and Geographic Considerations --------

with st.expander("Part 5: Demographic & Geographic Considerations", expanded=False):
    st.markdown("""
    **Goal:** Ensure model equitability across populations.
    """)

    st.subheader("5.1 Evaluating Across Groups")
    st.multiselect(
        "Which patient groups will you explicitly compare?",
        [
            "Age (pediatric, adult, geriatric)",
            "Sex/gender",
            "Racial/ethnic groups",
            "Insurance/socioeconomic status",
            "Geographic region",
        ])
    st.text_area("Briefly describe your approach for evaluating performance in these subgroups.")

    st.divider()

    st.subheader("5.2 Common Pitfalls in Stratified Performance")
    pitfalls = st.multiselect(
        "Identify pitfalls to avoid (choose at least three):",
        [
            "Small sample size in subgroups",
            "Multiple comparison problem (statistical validity)",
            "Label leakage across groups",
            "Confounding variables not accounted for",
            "Interpreting statistical difference as clinical significance"
        ])
    st.text_area("How does your approach avoid these pitfalls?")

    st.divider()

    st.subheader("5.3 Addressing and Communicating Group Disparities")
    st.text_area("Describe your approach for (i) identifying causes of disparities, (ii) mitigating without new bias, (iii) validating mitigation, and (iv) transparent communication.")

## -------- PART 6: Reflection --------

with st.expander("Part 6: Reflection", expanded=False):
    st.subheader("6.1 Performance-Generalizability Tradeoff")
    st.text_area("How would you handle trade-offs between improving performance on one subgroup at the expense of another?")

    st.subheader("6.2 Informing Future Data Collection")
    st.text_area("Based on your validation results, how would you guide future data collection? What would you prioritize?")

    st.subheader("6.3 Communication Strategy")
    st.text_area("How would you communicate your model’s strengths and limitations to technical staff?")
    st.text_area("To clinical end users?")
    st.text_area("To hospital leadership?")

if st.button("Mark assignment as complete"):
    st.success("Assignment marked as complete! Review and save your responses as needed.")

st.caption("You can show/hide sections as needed. Use the checklists, radios, and text entry points to structure your thinking throughout the assignment.")
