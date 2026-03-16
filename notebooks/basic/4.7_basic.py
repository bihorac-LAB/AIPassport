import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import psutil
import os
import shap
import lime
import lime.lime_tabular
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, confusion_matrix, roc_auc_score

# --- VERSION COMPATIBILITY CHECK ---
def check_compatibility():
    major_version = int(np.__version__.split('.')[0])
    if major_version >= 2:
        st.error(f"Incompatibility Detected: Current NumPy version is {np.__version__}.")
        st.warning("The SHAP library requires NumPy < 2.0.0. Please update your requirements.txt.")
        st.stop()

# --- MONITORING UTILITY ---
def display_performance_monitor():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.1)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sandbox Performance")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("CPU Load", f"{cpu_percent}%")
    c2.metric("RAM Usage", f"{mem_mb:.1f} MB")

# --- Page Configuration ---
st.set_page_config(page_title="Healthcare AI Fairness Sandbox", layout="wide")

# --- Data Loading & Model Training ---
@st.cache_resource
def load_and_train():
    file_path = os.path.join("assets", "diabetes.csv")
    if not os.path.exists(file_path):
        st.error(f"File Not Found: Ensure 'diabetes.csv' is in the 'assets' directory.")
        st.stop()
        
    df = pd.read_csv(file_path)
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(solver='lbfgs', max_iter=1000)
    model.fit(X_train, y_train)
    
    return df, X_train, X_test, y_train, y_test, model

# Initialize
check_compatibility()
df, X_train, X_test, y_train, y_test, model = load_and_train()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
activity = st.sidebar.radio(
    "Select an Activity:",
    [
        "Activity 1: Data & Fairness Metrics", 
        "Activity 2: Global Explainability (SHAP)", 
        "Activity 3: Local Explainability (LIME)",
        "Activity 4: The 'What-If' Simulation"
    ],
    help="Navigate through the stages of algorithmic accountability."
)

display_performance_monitor()

# ==========================================
# ACTIVITY 1: DATA & FAIRNESS
# ==========================================
if activity == "Activity 1: Data & Fairness Metrics":
    st.title("Activity 1: Data Preview and Fairness Metrics")
    
    with st.expander("Instructions", expanded=True):
        st.write("""
        1. Review the raw data and overall performance metrics.
        2. Use the slider to adjust age group bins and observe how demographic segmentation impacts model sensitivity.
        """)

    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown("---")
    st.subheader("Fairness Analysis")
    
    # User-defined age groups for interactivity
    age_split = st.slider("Select Middle-Aged Threshold", 30, 60, 45, help="Adjust the age boundaries to see how group performance changes.")
    
    X_test_age = X_test.copy()
    X_test_age['Age_Group'] = pd.cut(
        X_test_age['Age'],
        bins=[0, 30, age_split, 100],
        labels=['Young Adults', 'Middle-Aged', 'Older Adults']
    )

    metrics_list = []
    for group in ['Young Adults', 'Middle-Aged', 'Older Adults']:
        idx = X_test_age['Age_Group'] == group
        if idx.any():
            g_pred = model.predict(X_test[idx])
            g_true = y_test[idx]
            tn, fp, fn, tp = confusion_matrix(g_true, g_pred, labels=[0, 1]).ravel()
            metrics_list.append({
                "Age Group": group,
                "Samples": len(g_true),
                "Accuracy": accuracy_score(g_true, g_pred),
                "Sensitivity": recall_score(g_true, g_pred),
                "Specificity": tn / (tn + fp) if (tn + fp) > 0 else 0
            })
    
    fair_df = pd.DataFrame(metrics_list)
    
    col_a, col_b = st.columns([1, 2])
    col_a.dataframe(fair_df, use_container_width=True)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=fair_df.melt(id_vars="Age Group", value_vars=["Accuracy", "Sensitivity", "Specificity"]), 
                x="Age Group", y="value", hue="variable", ax=ax, palette="viridis")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Metric Score")
    col_b.pyplot(fig)

# ==========================================
# ACTIVITY 2: GLOBAL SHAP
# ==========================================
elif activity == "Activity 2: Global Explainability (SHAP)":
    st.title("Activity 2: Global Explainability with SHAP")
    
    with st.expander("Instructions", expanded=True):
        st.write("""
        1. Adjust the feature count to see the most influential clinical factors.
        2. SHAP values indicate how much each feature pushes the model's prediction higher or lower.
        """)

    max_display = st.slider("Features to Display", 1, 8, 5)
    
    explainer = shap.Explainer(model, X_test)
    shap_values = explainer(X_test)
    
    st.subheader("SHAP Summary Plot")
    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, X_test, max_display=max_display, show=False)
    st.pyplot(plt.gcf())

# ==========================================
# ACTIVITY 3: LOCAL LIME
# ==========================================
elif activity == "Activity 3: Local Explainability (LIME)":
    st.title("Activity 3: Local Explainability with LIME")
    
    with st.expander("Instructions", expanded=True):
        st.write("""
        1. Select a patient from the test set to analyze their specific prediction.
        2. Identify which clinical factors contributed most to that individual's classification.
        """)

    patient_idx = st.number_input("Patient Index", 0, len(X_test)-1, 0)
    
    lime_explainer = lime.lime_tabular.LimeTabularExplainer(
        training_data=np.array(X_train),
        feature_names=X_train.columns,
        class_names=['Healthy', 'Diabetes'],
        mode='classification'
    )

    exp = lime_explainer.explain_instance(X_test.iloc[patient_idx], model.predict_proba, num_features=5)
    
    st.subheader(f"Explanation for Patient #{patient_idx}")
    st.pyplot(exp.as_pyplot_figure())

# ==========================================
# ACTIVITY 4: WHAT-IF SIMULATOR
# ==========================================
elif activity == "Activity 4: The 'What-If' Simulation":
    st.title("Activity 4: The 'What-If' Simulation")
    
    with st.expander("Instructions", expanded=True):
        st.write("""
        1. Manually adjust the clinical parameters below to create a synthetic patient profile.
        2. Observe the model's real-time prediction and confidence level.
        """)

    cols = st.columns(4)
    profile = {}
    for i, col in enumerate(X_train.columns):
        with cols[i % 4]:
            profile[col] = st.slider(col, float(df[col].min()), float(df[col].max()), float(df[col].mean()))
    
    input_df = pd.DataFrame([profile])
    prediction = model.predict(input_df)[0]
    prob = model.predict_proba(input_df)[0][1]

    st.markdown("---")
    label = "Positive (Diabetes)" if prediction == 1 else "Negative (Healthy)"
    color = "#d9534f" if prediction == 1 else "#5cb85c"
    
    st.markdown(f"<h2 style='text-align: center; color: {color};'>Prediction: {label}</h2>", unsafe_allow_html=True)
    st.progress(prob)
    st.markdown(f"<h4 style='text-align: center;'>Confidence Level: {prob:.1%}</h4>", unsafe_allow_html=True)
