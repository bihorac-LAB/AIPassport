import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error as sklearn_mse

# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def calculate_icc(df, annotation_cols):
    """
    Calculates a basic Intraclass Correlation Coefficient (ICC).
    Higher values (closer to 1.0) indicate high agreement between researchers.
    """
    if len(annotation_cols) < 2:
        return 1.0
    
    # Variance of the mean of annotations (between-item variance)
    mean_annotations = df[annotation_cols].mean(axis=1)
    total_var = mean_annotations.var()
    
    # Average variance within the annotations (within-item/rater variance)
    rater_var = df[annotation_cols].var(axis=1).mean()
    
    icc_value = (total_var - rater_var) / total_var if total_var > 0 else 0
    return max(0, icc_value)

def train_rf_model(X_train, y_train, X_test):
    # Using RandomForest as seen in the scientific notebook
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train.ravel())
    return model.predict(X_test)

# ---------------------------------------------------------
# App layout & Security
# ---------------------------------------------------------

st.set_page_config(page_title="Genomic AI Reproducibility", layout="wide")

st.title("AI-Driven Basic Science: Genetic Mutation Analysis")
st.markdown("""
This tool simulates how **human annotation inconsistencies** in genomics (e.g., classifying protein-altering mutations) 
impact the reliability of AI models. 
""")

# Instructions Section
with st.expander("How to use this tool"):
    st.markdown("""
    1. **Select Data Source**: Use the sidebar to choose between simulating a new mutation study or uploading your own experimental CSV data.
    2. **Configure Parameters**:
        * **Number of Researchers**: Simulates how many scientists are labeling the data. More researchers often lead to a stable consensus.
        * **Annotation Variability**: Controls the 'noise' or disagreement level between researchers.
    3. **Analyze Consistency**: Look at the **Intraclass Correlation (ICC)** score. A low score means researchers disagree significantly, which risks confusing the AI.
    4. **Train AI Model**: The app automatically trains a Random Forest model on the 'Consensus' (average) label. Check the **MSE (Mean Squared Error)** to see how well the AI performs given the data quality.
    5. **Visual Inspection**: Use the tabs at the bottom to compare researcher variance and visualize the AI's prediction accuracy.
    """)

# Security and Privacy Warning
st.warning("**Data Privacy Notice:** Do not upload genetic data containing PII (Personally Identifiable Information) or sensitive patient records. This tool is for algorithmic analysis only.")

# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------

st.sidebar.header("Research Setup")
source = st.sidebar.radio(
    "Data Source", 
    ["Simulate Mutation Study", "Upload Researcher CSV"],
    help="Simulate a study where multiple researchers label the same mutations, or upload your own experimental results."
)

df = None
annotation_cols = []

if source == "Simulate Mutation Study":
    num_samples = st.sidebar.slider("Number of Mutations", 50, 500, 100)
    num_raters = st.sidebar.slider("Number of Researchers", 1, 10, 3, 
                                   help="More researchers generally lead to a more stable 'consensus' label for the AI to learn.")
    noise_level = st.sidebar.slider("Annotation Variability (Noise)", 0.0, 5.0, 1.2, 
                                    help="Simulates disagreement between scientists. High variability lowers the ICC.")
    
    # Generate ground truth mutation signal
    x = np.linspace(0, 10, num_samples)
    base_signal = 3 * x + 5 
    
    data = {"Mutation_Feature_X": x}
    annotation_cols = []
    
    # Generate columns for each researcher
    for i in range(num_raters):
        col_name = f"Researcher_{i+1}_Score"
        data[col_name] = base_signal + np.random.normal(0, noise_level, num_samples)
        annotation_cols.append(col_name)
    
    df = pd.DataFrame(data)
    # The 'Consensus' label is what the AI is actually trained on
    df["Consensus_Label"] = df[annotation_cols].mean(axis=1)

else:
    uploaded = st.file_uploader("Upload Experimental Data (CSV)", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        annotation_cols = st.multiselect("Select Researcher Annotation Columns", numeric_cols, 
                                         help="Select the columns containing scores or labels from different human annotators.")
        if annotation_cols:
            df["Consensus_Label"] = df[annotation_cols].mean(axis=1)

# ---------------------------------------------------------
# Analysis & Modeling
# ---------------------------------------------------------

if df is not None and len(annotation_cols) > 0:
    
    # 1. Reproducibility Metric
    icc_score = calculate_icc(df, annotation_cols)
    
    st.divider()
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.subheader("Annotation Consistency")
        st.metric("Intraclass Correlation (ICC)", f"{icc_score:.3f}", 
                  help="ICC measures how much researchers agree. >0.75 is considered excellent reproducibility.")
        
        if icc_score < 0.5:
            st.error("Low Agreement: High variability between researchers may lead to an unreliable AI model.")
        elif icc_score > 0.8:
            st.success("High Agreement: These annotations provide a stable foundation for AI training.")

    with m_col2:
        st.subheader("AI Model Training")
        feature_col = st.selectbox("Select Feature for AI Training", [c for c in df.columns if c not in annotation_cols and c != "Consensus_Label"])
        
        test_size = st.slider("Test Set Size (%)", 10, 50, 20)
        split = int(len(df) * (1 - test_size / 100))
        
        X = df[[feature_col]].values
        y = df["Consensus_Label"].values
        
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        y_pred = train_rf_model(X_train, y_train, X_test)
        mse = sklearn_mse(y_test, y_pred)
        
        st.metric("Model Prediction Error (MSE)", f"{mse:.4f}")

    # ---------------------------------------------------------
    # Visualizations
    # ---------------------------------------------------------
    
    st.subheader("Visual Inspection")
    tab1, tab2, tab3 = st.tabs(["Researcher Variance", "AI Predictions", "Raw Data"])
    
    with tab1:
        st.write("This chart shows the spread of labels across different researchers for each mutation sample.")
        st.line_chart(df[annotation_cols])
        
    with tab2:
        res_df = pd.DataFrame({
            "Consensus (Actual)": y_test.flatten(),
            "AI Prediction": y_pred.flatten()
        })
        st.line_chart(res_df)
        st.caption("A tight match between Consensus and Prediction indicates the AI successfully learned the researchers' combined logic.")

    with tab3:
        st.dataframe(df)

else:
    st.info("Please configure the simulation or upload a dataset to begin the reproducibility analysis.")
