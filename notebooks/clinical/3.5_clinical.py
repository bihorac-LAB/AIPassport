import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import psutil
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Cardiovascular Risk Data Preprocessing",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MONITORING UTILITY ---
def display_performance_monitor():
    """Tracks CPU and RAM usage of the current Streamlit process."""
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.1)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("**System Health Monitor**")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("CPU Load", f"{cpu_percent}%")
    c2.metric("RAM", f"{mem_mb:.1f} MB")

# --- DATA GENERATION (Fixed Seed for Reproducibility) ---
@st.cache_data
def load_data():
    """Generates the simulated dataset as defined in the assignment notebook."""
    np.random.seed(42)
    data = {
        'Patient_ID': np.arange(1, 101),
        'Age': np.random.randint(20, 80, 100),
        'Blood_Pressure': np.append(np.random.randint(90, 140, 95), [300, 310, 320, 330, 340]),  # Outliers
        'Cholesterol': np.append(np.random.randint(150, 250, 95), [500, 510, 520, 530, 540]),  # Outliers
        'Glucose': np.append(np.random.randint(70, 150, 95), [300, 310, 320, 330, 340]),  # Outliers
        'BMI': np.append(np.random.normal(25, 5, 95), [50, 52, 55, 60, 65]),  # Outliers
        'Missing_Feature': [np.nan if i % 10 == 0 else np.random.randint(50, 100) for i in range(100)] # Missing Data
    }
    return pd.DataFrame(data)

# Load initial data
raw_df = load_data()
df = raw_df.copy()

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Preprocessing Controls")

st.sidebar.markdown("### 1. Outlier Handling")
enable_outlier_handling = st.sidebar.checkbox(
    "Apply Winsorization", 
    value=True,
    help="Caps extreme values at specified percentiles to reduce the impact of outliers without removing data points."
)

if enable_outlier_handling:
    winsor_lower = st.sidebar.slider(
        "Lower Percentile Cap", 0, 10, 5, 
        help="Values below this percentile will be replaced with the value at this percentile."
    )
    winsor_upper = st.sidebar.slider(
        "Upper Percentile Cap", 90, 100, 95,
        help="Values above this percentile will be replaced with the value at this percentile."
    )

st.sidebar.markdown("### 2. Missing Data")
imputation_strategy = st.sidebar.radio(
    "Imputation Strategy",
    options=["Mean", "Median", "Drop Rows"],
    index=0,
    help="Choose how to handle missing values in 'Missing_Feature'. Mean is sensitive to outliers; Median is more robust."
)

st.sidebar.markdown("### 3. Feature Scaling")
scaling_method = st.sidebar.selectbox(
    "Scaling Method",
    options=["StandardScaler (Z-Score)", "MinMaxScaler (0-1)", "None"],
    index=0,
    help="StandardScaler centers data around 0 (good for outliers). MinMaxScaler squeezes data between 0 and 1."
)

display_performance_monitor()

# --- MAIN UI ---
st.title("Cardiovascular Risk: Data Preprocessing Lab")

with st.expander("**Read Case Study & Instructions**", expanded=True):
    st.markdown("""
    **The Case:** A hospital's AI model failed to predict a severe cardiac event because it was fed noisy data containing equipment errors (outliers) and missing test results.
    
    **Your Task:** Use the controls in the sidebar to clean the dataset.
    1.  **Outliers:** extreme values in Blood Pressure or Cholesterol skew the mean. Use **Winsorization** to cap them.
    2.  **Missing Data:** Some patient records have gaps. Choose an **Imputation** method to fill them.
    3.  **Scaling:** Algorithms struggle when variables have different units (e.g., Age vs. Glucose). Apply **Scaling** to normalize them.
    """)

# --- PREPROCESSING LOGIC ---

# 1. Outlier Handling (Winsorization)
if enable_outlier_handling:
    def cap_outliers(series, lower, upper):
        lower_limit, upper_limit = np.percentile(series, [lower, upper])
        return np.clip(series, lower_limit, upper_limit)
    
    cols_to_cap = ['Blood_Pressure', 'Cholesterol', 'Glucose', 'BMI']
    df[cols_to_cap] = df[cols_to_cap].apply(lambda x: cap_outliers(x, winsor_lower, winsor_upper))

# 2. Missing Data Imputation
if imputation_strategy == "Drop Rows":
    df = df.dropna()
else:
    strategy_map = {"Mean": "mean", "Median": "median"}
    imputer = SimpleImputer(strategy=strategy_map[imputation_strategy])
    # Reshape is necessary for a single feature
    df['Missing_Feature'] = imputer.fit_transform(df[['Missing_Feature']])

# 3. Scaling
# Define columns for scaling (Clinical features vs Demographic)
clinical_features = ['Blood_Pressure', 'Cholesterol', 'Glucose', 'BMI']
other_features = ['Age', 'Missing_Feature']

if scaling_method == "StandardScaler (Z-Score)":
    scaler = StandardScaler()
    df[clinical_features] = scaler.fit_transform(df[clinical_features])
    # Normalizing age and missing feature as per the notebook logic
    mm_scaler = MinMaxScaler()
    df[other_features] = mm_scaler.fit_transform(df[other_features])
    
elif scaling_method == "MinMaxScaler (0-1)":
    scaler = MinMaxScaler()
    all_numeric = clinical_features + other_features
    df[all_numeric] = scaler.fit_transform(df[all_numeric])

# --- VISUALIZATION DASHBOARD ---

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.subheader("Outlier Detection (Z-Score)")
    # Calculate Z-scores on the CURRENT df (which might already be winsorized)
    # If winsorized, Z-scores will drop below threshold, showing success
    df_zscores = df[clinical_features].apply(zscore)
    outliers_detected = ((df_zscores > 3) | (df_zscores < -3)).sum().sum()
    
    st.metric(
        label="Extreme Outliers Remaining (> 3 SD)", 
        value=outliers_detected,
        delta="- High Risk" if outliers_detected > 0 else "Clean",
        delta_color="inverse"
    )
    
    st.info(f"""
    **Current Configuration:**
    * **Winsorization:** {'On' if enable_outlier_handling else 'Off'}
    * **Imputation:** {imputation_strategy}
    * **Scaling:** {scaling_method}
    """)

with col2:
    st.subheader("Feature Distributions")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Main Boxplot
    sns.boxplot(data=df[clinical_features], ax=ax, palette="viridis")
    ax.set_title(f"Distribution of Clinical Metrics ({scaling_method})")
    ax.set_ylabel("Value (Scaled)" if scaling_method != "None" else "Value (Original Units)")
    st.pyplot(fig)
    
    st.markdown("""
    > **Observation:** > * Without **Winsorization**, notice how the box plots are "squashed" by the extreme outliers at the top.
    > * Without **Scaling**, notice how `Cholesterol` (large numbers) dominates the scale compared to `BMI`.
    """)
