import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.metrics import accuracy_score, make_scorer, recall_score
import plotly.express as px
import psutil
import os

# --- MONITORING UTILITY ---
def display_performance_monitor():
    """Tracks CPU and RAM usage of the current Streamlit process."""
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.1)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Monitor")
    st.sidebar.caption("Tracks the resource usage of this app in real-time.")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("CPU Load", f"{cpu_percent}%", help="Current CPU usage of the Streamlit server.")
    c2.metric("RAM Usage", f"{mem_mb:.1f} MB", help="Current RAM memory allocated to this app.")

# ---------------------------------
# Page Config & Sidebar
# ---------------------------------
st.set_page_config(page_title="Shared Biomedical AI Vocabulary", layout="wide")

st.sidebar.markdown("### 1. Select Perspective")
perspective = st.sidebar.radio(
    "View demonstration through the lens of:",
    ["Clinical Care", "Foundational Science"],
    help="Toggle this to see how the same machine learning pipeline is interpreted differently depending on the scientific domain."
)

st.sidebar.markdown("### 2. Navigation")
activity = st.sidebar.radio(
    "Go to:",
    [
        "Activity 1 - Data Exploration",
        "Activity 2 - Data Preprocessing",
        "Activity 3 - Model Training",
        "Activity 4 - Cross-Validation"
    ],
    help="Select an activity to interact with the corresponding stage of the pipeline."
)

display_performance_monitor()

# ---------------------------------
# Context Variables
# ---------------------------------
if perspective == "Clinical Care":
    app_desc = "Interactive demonstration of a clinical analytics pipeline. Watch how a Decision Tree learns to predict in-hospital mortality using data from the eICU Collaborative Research Database."
    outcome_label = "In-Hospital Mortality (0=Survival, 1=Death)"
else:
    app_desc = "Interactive demonstration of a computational biology pipeline. Watch how a Decision Tree models pathophysiological mechanisms to discover critical thresholds in physiological biomarkers."
    outcome_label = "Systemic Failure (0=Stable, 1=Failure)"

st.title("Shared Biomedical Artificial Intelligence Vocabulary")
st.write(app_desc)

# ---------------------------------
# Load Dataset 
# ---------------------------------
@st.cache_data
def load_data():
    # Attempt to load from the local data folder as specified
    try:
        df = pd.read_csv("data/diabetes.csv")
        return df
    except FileNotFoundError:
        st.error("Error: Could not find 'data/diabetes.csv'. Please ensure the 'data' folder exists in the same directory as this script and contains the 'diabetes.csv' file.")
        st.stop()

df = load_data()

# --------------------
# Activity 1 - Data Exploration
# --------------------
if activity == "Activity 1 - Data Exploration":
    st.header("Activity 1: Exploring Data Types")
    
    st.markdown("### Instructions")
    st.write("Before training a model, data scientists must inspect the raw data to understand feature distributions and identify correlations with the outcome variable. Use the controls below to preview the dataset and inspect the data types.")
    
    st.subheader("Data Preview")
    n_rows = st.slider(
        "Number of records to display", 
        min_value=1, max_value=20, value=5,
        help="Drag the slider to increase or decrease the number of rows visible in the table below."
    )
    st.dataframe(df.head(n_rows), use_container_width=True)
    
    with st.expander("View Data Types (.dtypes)"):
        st.write("These are the variable types the computer recognizes for each column:")
        st.write(df.dtypes)
    
    st.subheader("Feature Distributions")
    feature_to_plot = st.selectbox(
        "Select a feature to visualize:", 
        df.columns[:-1],
        help="Choose a specific metric to see a histogram of its distribution."
    )
    
    # ADA COMPLIANCE: Colorblind safe colors (Blue & Orange)
    fig = px.histogram(
        df, x=feature_to_plot, color="Outcome", barmode="overlay",
        title=f"Distribution of {feature_to_plot} grouped by Outcome",
        color_discrete_sequence=["#1f77b4", "#ff7f0e"] 
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View chart data as text (Accessible Alternative)"):
        st.dataframe(df.groupby("Outcome")[feature_to_plot].describe())

    st.markdown("---")
    with st.expander("Reveal Expected Insights for Data Exploration"):
        st.write("By inspecting the dataset, you should notice there are 8 input features (predictors) containing numerical data (integers and floats), and 1 binary outcome variable containing integers (0 or 1).")

# --------------------
# Activity 2 - Preprocessing
# --------------------
elif activity == "Activity 2 - Data Preprocessing":
    st.header("Activity 2: Data Preprocessing and Splitting")
    
    st.markdown("### Instructions")
    st.write("Before a model can learn, the data must be partitioned into a Training Set and a Testing Set. Use the slider below to adjust the ratio of this split and observe how the data is divided.")

    X = df.iloc[:, :-1].copy()
    y = df.iloc[:, -1].copy()

    test_size = st.slider(
        "Test set size (default is 0.2)", 
        min_value=0.1, max_value=0.5, value=0.2, step=0.05,
        help="The proportion of the dataset to reserve for testing. The notebook uses 0.2 (20%)."
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    
    split_df = pd.DataFrame({
        "Set": ["Training Data", "Testing Data"],
        "Count": [len(X_train), len(X_test)]
    })
    
    fig = px.pie(
        split_df, values="Count", names="Set", title="Train/Test Split Proportions", hole=0.4,
        color_discrete_sequence=["#1f77b4", "#ff7f0e"]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View split proportions as text (Accessible Alternative)"):
        st.dataframe(split_df)

    st.markdown("---")
    with st.expander("Reveal Expected Insights for Preprocessing"):
        st.write("When following the notebook's default setting of 0.2, you should expect 80% of the patient records to be used for training the model, and 20% to be held back for testing.")
        st.write("This separation is critical. If we evaluated the model on the exact same data it was trained on, it would likely memorize the answers (overfitting), resulting in falsely high performance metrics that would fail in real-world scenarios.")

# --------------------
# Activity 3 - Train & Predict
# --------------------
elif activity == "Activity 3 - Model Training":
    st.header("Activity 3: Model Training and Interactive Prediction")
    
    st.markdown("### Instructions")
    st.write("With the data prepared, we can train the Decision Tree Classifier. Adjust the 'Max Depth' parameter to control how complex the model's rules can become. Then, explore the Decision Tree Visualization to trace the mathematical logic the model uses to make a prediction. Finally, test the model yourself using the live simulator.")
    
    max_depth = st.slider(
        "Max Depth", 
        min_value=1, max_value=15, value=4, 
        help="Controls how deep the tree can grow. Deeper trees capture more complex patterns but risk overfitting. The notebook defaults to 4."
    )
    dt = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    st.metric(
        "Accuracy (acc = accuracy_score)", 
        f"{acc:.4f}",
        help="The proportion of correct predictions made by the model on the unseen test dataset. Note how this matches your notebook output."
    )
    
    st.divider()
    st.subheader("Decision Tree Visualization")
    st.write("This graphic maps out the exact mathematical thresholds the algorithm uses to sort data and make decisions.")
    
    
    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(dt, feature_names=df.columns[:-1], class_names=["0", "1"], filled=True, rounded=True, fontsize=10)
    st.pyplot(fig)
    
    with st.expander("View Decision Tree rules as text (Accessible Alternative)"):
        st.text(export_text(dt, feature_names=list(df.columns[:-1])))

    st.divider()
    st.subheader("Live Interactive Simulator")
    st.write("Adjust the metrics below. The Decision Tree will process the inputs through the visual rules above and output a live prediction.")
    
    input_data = {}
    input_cols = st.columns(4)
    for idx, col in enumerate(df.columns[:-1]):
        with input_cols[idx % 4]:
            input_data[col] = st.slider(
                col, 
                float(df[col].min()), float(df[col].max()), float(df[col].median()),
                help=f"Adjust the {col} value to see how the model reacts."
            )

    user_df = pd.DataFrame([input_data])
    prediction = dt.predict(user_df)[0]
    prob = dt.predict_proba(user_df)[0]
    
    if prediction == 1:
        st.error("Model Prediction: Outcome Detected (Class 1)")
    else:
        st.success("Model Prediction: Outcome Not Detected (Class 0)")
    st.progress(prob[1], text=f"Calculated Probability: {prob[1]*100:.1f}%")

    st.markdown("---")
    with st.expander("Reveal Expected Insights for Model Training"):
        st.write("Using the notebook's default Max Depth of 4, you should observe an accuracy of approximately 0.6948.")
        st.write("Looking at the Decision Tree Visualization, you should expect to see the model heavily prioritizing features like Glucose and BMI near the top of the tree. These primary splits indicate the strongest predictors of the outcome variable within this dataset.")

# --------------------
# Activity 4 - Cross-Validation
# --------------------
elif activity == "Activity 4 - Cross-Validation":
    st.header("Activity 4: Cross-Validation")
    
    st.markdown("### Instructions")
    st.write("A single Train/Test split can be sensitive to exactly how the data was randomly divided. Cross-validation provides a more robust evaluation by dividing the dataset into multiple 'folds'. The model is trained and tested on every fold. Adjust the number of folds below to see how the average metrics stabilize.")
    

    cv_folds = st.slider(
        "Folds (cv)", 
        min_value=2, max_value=10, value=5,
        help="How many pieces to divide the dataset into for cross-validation. The notebook defaults to 5."
    )
    dt = DecisionTreeClassifier(max_depth=4, random_state=42)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    
    scoring = {
        "accuracy": "accuracy",
        "sensitivity": "recall",                  
        "precision": "precision",
        "specificity": make_scorer(recall_score, pos_label=0)  
    }
    
    with st.spinner('Running cross-validation...'):
        cv_results = cross_validate(dt, X, y, cv=cv_folds, scoring=scoring)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Accuracy", f"{np.mean(cv_results['test_accuracy']):.4f}", help="Overall proportion of correct predictions across all folds.")
    col2.metric("Average Sensitivity", f"{np.mean(cv_results['test_sensitivity']):.4f}", help="True Positive Rate across all folds.")
    col3.metric("Average Specificity", f"{np.mean(cv_results['test_specificity']):.4f}", help="True Negative Rate across all folds.")
    col4.metric("Average Precision", f"{np.mean(cv_results['test_precision']):.4f}", help="Positive Predictive Value across all folds.")

    cv_df = pd.DataFrame({
        "Fold": [f"Fold {i+1}" for i in range(cv_folds)], 
        "Accuracy": cv_results['test_accuracy']
    })
    
    fig = px.bar(
        cv_df, x="Fold", y="Accuracy", title="Accuracy per Fold", 
        text_auto=".3f", range_y=[0, 1], color_discrete_sequence=["#1f77b4"]
    )
    fig.add_hline(y=np.mean(cv_results['test_accuracy']), line_dash="dash", line_color="#ff7f0e", annotation_text="Mean")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View fold metrics as text (Accessible Alternative)"):
        st.dataframe(cv_df)

    st.markdown("---")
    with st.expander("Reveal Expected Insights for Cross-Validation"):
        st.write("Using the default 5 folds, you should expect the Average Accuracy to rise slightly to approximately 0.7305 compared to the single Train/Test split.")
        st.write("You should also expect to see a higher Specificity (~0.7540) than Sensitivity (~0.6871). This reveals an important insight about the model: it is currently slightly better at correctly identifying stable patients (True Negatives) than it is at catching patients who experience failure/mortality (True Positives).")
