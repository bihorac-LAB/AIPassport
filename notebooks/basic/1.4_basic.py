import streamlit as st

st.title("1.4 Training, Validation, and Generalizability (Basic Science)")

sections = [
    "Introduction",
    "Part 1: Training & Validation Fundamentals",
    "Part 2: Internal Validation Techniques",
    "Part 3: External Validation & Generalizability",
    "Part 4: Model Robustness",
    "Part 5: Demographic & Geographic Considerations",
    "Part 6: Reflection & Communication"
]

with st.expander("Datasets and tools", expanded=False):
    st.markdown("""
**Datasets**
- [MIMIC-CXR](https://physionet.org/content/mimic-cxr/2.0.0/)
- [NIH Chest X-ray Dataset](https://nihcc.app.box.com/v/ChestXray-NIHCC)
- [NIH Chest X-ray Dataset (Kaggle mirror)](https://www.kaggle.com/datasets/nih-chest-xrays/data)

**Tools**
- [Keras](https://keras.io/)
- [ML-fairness-gym](https://github.com/google/ml-fairness-gym)
""")
    st.info("Download and inspect datasets above as needed. You can use Keras and ML-fairness-gym for modeling and evaluation.")

section = st.selectbox("Choose section", sections)


# ========== Introduction ==========
if section == sections[0]:
    st.title("MS4: Training, Validation, and Generalizability")
    st.header("Basic Science Track")
    st.markdown("""
**Assignment Overview:**

You are developing and evaluating an AI model to detect pneumonia from chest X-ray images, focusing on validation, calibration, and ensuring robust generalizability across different patient populations.

Throughout this notebook, you will:
- Develop robust training/validation strategies
- Explore internal and external validation, calibration
- Ensure model fairness and generalizability
- Design for robustness, equity, and transparency

---

**Datasets (public, user-downloadable):**
- [MIMIC-CXR (PhysioNet)](https://physionet.org/content/mimic-cxr/2.0.0/)
- [NIH Chest X-ray Dataset](https://nihcc.app.box.com/v/ChestXray-NIHCC) ([Kaggle mirror](https://www.kaggle.com/datasets/nih-chest-xrays/data))

**Tools:**
- [Keras (Deep Learning)](https://keras.io/)
- [ML-fairness-gym (Fairness Evaluation)](https://github.com/google/ml-fairness-gym)
    """)
    st.info("For all hands-on tasks, you may use summary statistics, example code snippets, diagrams, and your own reasoning.")

# ========== Part 1 ==========
if section == sections[1]:
    st.header("Part 1: Understanding Training & Validation Fundamentals")
    st.markdown("""
**Clinical Track Case:**  
You have collected 10,000 chest X-rays over the past 3 years from three hospitals (5 different X-ray machines). Patient population is diverse, predominantly urban.

---
**Task 1.1:**  
**Why would a simple random train-test split be problematic? List at least 3 issues.**
""")
    st.text_area("Your response to Task 1.1", key="task1.1")

    st.markdown("""
---
**Task 1.2:**  
**Design a more appropriate data splitting strategy that accounts for:**
- Temporal factors (e.g., changes in protocols)
- Different imaging equipment (machine/site)
- Patient demographics
- Disease prevalence
    """)
    st.text_area("Your response to Task 1.2", key="task1.2")

    st.markdown("""
---
**Task 1.3:**  
**Explain how your splitting strategy addresses the issues from Task 1.1**
    """)
    st.text_area("Your response to Task 1.3", key="task1.3")

# ========== Part 2 ==========
if section == sections[2]:
    st.header("Part 2: Internal Validation Techniques")
    st.markdown("""
---
**Task 2.1:**  
**Design a cross-validation framework for this clinical dataset. Explain:**
- What type of cross-validation?
- Number of folds?
- How to stratify?
- What metrics to use?
    """)
    st.text_area("Your response to Task 2.1", key="task2.1")

    st.markdown("""
---
**Task 2.2:**  
**Propose two additional internal validation approaches to strengthen model confidence.**
    """)
    st.text_area("Your response to Task 2.2", key="task2.2")

    st.markdown("""
---
**Task 2.3:**  
**Develop a strategy to assess your model's calibration:**
- Methods to visualize calibration
- Techniques to measure it quantitatively
- Approaches to recalibrate if needed
    """)
    st.text_area("Your response to Task 2.3", key="task2.3")


# ========== Part 3 ==========
if section == sections[3]:
    st.header("Part 3: External Validation & Generalizability")
    st.markdown("""
**Clinical Track Case:**  
Internal validation is strong. Now test on the [NIH Chest X-ray Dataset](https://www.kaggle.com/datasets/nih-chest-xrays/data).

---
**Task 3.1:**  
**Design an external validation framework:**
- Steps to preprocess external data for compatibility
- Performance metrics
- Comparison of internal vs. external performance
- Threshold for performance drop that triggers model refinement
    """)
    st.text_area("Your response to Task 3.1", key="task3.1")

    st.markdown("""
---
**Task 3.2:**  
**Suppose model performs worse on pediatric patients & portable machines in external data. Propose a strategy to address these gaps without overfitting to external data.**
    """)
    st.text_area("Your response to Task 3.2", key="task3.2")

    st.markdown("""
---
**Task 3.3:**  
**Framework to evaluate model performance systematically across:**
- Demographic subgroups (age, sex, race/ethnicity)
- Clinical context (inpatient, ED)
- How do you: identify/quantify disparities, test their significance, and address them?
    """)
    st.text_area("Your response to Task 3.3", key="task3.3")

# ========== Part 4 ==========
if section == sections[4]:
    st.header("Part 4: Addressing Model Robustness")
    st.markdown("""
---
**Task 4.1:**  
**Design experiments to test robustness to:**
- Patient positioning
- Inspiration level
- Medical devices (tubes, lines)
- Image quality (contrast, brightness, noise)
    """)
    st.text_area("Your response to Task 4.1", key="task4.1")

    st.markdown("""
---
**Task 4.2:**  
**If performance drops for images with medical devices, propose & justify a solution to improve robustness without reducing standard image performance.**
    """)
    st.text_area("Your response to Task 4.2", key="task4.2")

    st.markdown("""
---
**Task 4.3:**  
**Develop a framework for continuous monitoring of robustness post-deployment:**
- Metrics to track
- Evaluation frequency
- Thresholds for update triggers
- Updating without workflow disruption
    """)
    st.text_area("Your response to Task 4.3", key="task4.3")


# ========== Part 5 ==========
if section == sections[5]:
    st.header("Part 5: Demographic & Geographic Considerations")
    st.markdown("""
---
**Task 5.1:**  
**Design an approach to evaluate model performance across:**
- Age groups (pediatric, adult, geriatric)
- Sex and gender
- Racial/ethnic groups
- Socioeconomic indicators
- Geographic regions
    """)
    st.text_area("Your response to Task 5.1", key="task5.1")

    st.markdown("""
---
**Task 5.2:**  
**Identify three common pitfalls in evaluating model performance across demographic groups and explain how your approach avoids them.**
    """)
    st.text_area("Your response to Task 5.2", key="task5.2")

    st.markdown("""
---
**Task 5.3:**  
**If model performs worse for certain groups, how will you:**
- Identify causes of disparity
- Mitigate disparities (without causing new biases)
- Validate mitigation effectiveness
- Communicate transparently about disparities & your actions
    """)
    st.text_area("Your response to Task 5.3", key="task5.3")


# ========== Part 6 ==========
if section == sections[6]:
    st.header("Part 6: Reflection & Communication")
    st.markdown("""
---
**Task 6.1:**  
**Reflect on the tradeoff between model performance and generalizability. How would you approach situations where improving a subgroup's performance degrades others?**
    """)
    st.text_area("Your response to Task 6.1", key="task6.1")

    st.markdown("""
---
**Task 6.2:**  
**How will your validation designs inform future data collection? What new data would be most valuable to improve generalizability?**
    """)
    st.text_area("Your response to Task 6.2", key="task6.2")

    st.markdown("""
---
**Task 6.3:**  
**How would you communicate your model's generalizability strengths/limitations to:**
- Technical team members
- Clinical end-users
- Hospital leadership
    """)
    st.text_area("Your response to Task 6.3", key="task6.3")

    st.success("Assignment Complete!\n\n(You can export, save, or print your responses at any time.)")
