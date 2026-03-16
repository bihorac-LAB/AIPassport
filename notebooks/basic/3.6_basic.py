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

# --- MONITORING UTILITY ---
def display_performance_monitor():
    """Tracks CPU and RAM usage of the current Streamlit process."""
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=0.1)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Health")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("CPU Load", f"{cpu_percent}%")
    c2.metric("Memory", f"{mem_mb:.1f} MB")

# --- APP CONFIG ---
st.set_page_config(page_title="Multi-Institutional Data Sharing Simulation", layout="wide")

# --- SIDEBAR & SETUP ---
st.sidebar.header("Simulation Settings")

# 1. Track Selection
track_choice = st.sidebar.radio(
    "Select Research Track:",
    ["Clinical (IC3 COVID-19)", "Basic Science (ImmPort)"],
    help="Choose the dataset scenario. Clinical simulates hospital patient records; Basic Science simulates laboratory immunology data."
)

st.sidebar.subheader("Data Parameters")

# 2. Interactive Data Controls
sample_size = st.sidebar.slider(
    "Sample Size (per Institution)", 
    min_value=50, 
    max_value=500, 
    value=200,
    step=50,
    help="Adjusting the sample size simulates larger or smaller datasets, affecting computation time and statistical significance."
)

outlier_rate = st.sidebar.slider(
    "Outlier Contamination",
    min_value=0.0,
    max_value=0.10,
    value=0.02,
    step=0.01,
    format="%f",
    help="Percentage of the dataset that contains erroneous or extreme values (outliers)."
)

display_performance_monitor()

# --- MAIN CONTENT ---

st.title("Navigating Multi-Institutional Data Sharing Challenges")
st.markdown("### Interactive Federated Learning Simulation")

# Instructions
st.info(
    "INSTRUCTIONS: This simulation guides you through the process of preparing a local dataset "
    "and collaborating with another institution without sharing raw data. "
    "Follow the numbered steps below, adjusting parameters in the sidebar and main area to observe changes."
)

if track_choice == "Clinical (IC3 COVID-19)":
    st.markdown("""
    **Current Scenario:** Harmonizing patient data from multiple hospitals (City General vs. Mountain View) to predict COVID-19 severity.
    **Challenge:** Outliers (measurement errors) and Missing Data (O2 Saturation) must be handled locally before the model can be shared.
    """)
else:
    st.markdown("""
    **Current Scenario:** Aggregating immunology data from different labs (Lab Alpha vs. Lab Beta) to analyze cytokine responses.
    **Challenge:** Outliers (equipment spikes) and Missing Data (Cell Counts) must be handled locally before the model can be shared.
    """)

st.markdown("---")

# --- DATA GENERATION ---
@st.cache_data
def generate_data(track, n_samples, contamination):
    np.random.seed(42)
    
    # Calculate number of outliers
    n_outliers = int(n_samples * contamination)
    n_regular = n_samples - n_outliers

    if track == "Clinical (IC3 COVID-19)":
        # Regular Data
        wbc_regular = np.random.normal(7000, 2000, n_regular)
        # Outlier Data (Extreme errors)
        wbc_outliers = np.random.uniform(50000, 250000, n_outliers)
        
        combined_wbc = np.append(wbc_regular, wbc_outliers)
        np.random.shuffle(combined_wbc) # Shuffle so outliers aren't all at the end

        data = {
            'ID': [f"PT-{i:03d}" for i in range(n_samples)],
            'Institution': np.random.choice(['City_General', 'Mountain_View_Clinic'], n_samples),
            'Feature_Target': combined_wbc, # WBC Count
            'Feature_Secondary': [np.nan if i % 10 == 0 else x for i, x in enumerate(np.random.normal(96, 2, n_samples))] # O2 Sat
        }
        labels = {'target': 'WBC Count', 'secondary': 'O2 Saturation'}
        
    else: # Basic Science
        # Regular Data
        il6_regular = np.random.gamma(2, 10, n_regular)
        # Outlier Data
        il6_outliers = np.random.uniform(500, 1500, n_outliers)
        
        combined_il6 = np.append(il6_regular, il6_outliers)
        np.random.shuffle(combined_il6)

        data = {
            'ID': [f"SMP-{i:03d}" for i in range(n_samples)],
            'Institution': np.random.choice(['Lab_Alpha', 'Lab_Beta'], n_samples),
            'Feature_Target': combined_il6, # Cytokine IL-6
            'Feature_Secondary': [np.nan if i % 10 == 0 else x for i, x in enumerate(np.random.normal(1200, 300, n_samples))] # T-Cell
        }
        labels = {'target': 'Cytokine IL-6', 'secondary': 'T-Cell Count'}

    return pd.DataFrame(data), labels

# Generate Data based on inputs
df_raw, col_labels = generate_data(track_choice, sample_size, outlier_rate)

# --- STEP 1: LOCAL DATA INSPECTION ---
st.header("Step 1: Local Data Inspection")
st.markdown("Before collaboration, inspect your local data for issues.")

with st.expander("View Raw Dataset", expanded=True):
    st.dataframe(df_raw.head(10), use_container_width=True)
    st.caption("Note: 'Feature_Target' contains the critical values for the model, and 'Feature_Secondary' contains missing values (NaN).")

# --- STEP 2: OUTLIER DETECTION ---
st.header("Step 2: Outlier Detection")
st.markdown(
    "Outliers can severely skew Federated Learning models. "
    "Use the Z-Score method to identify and remove data points that are statistically improbable."
)

col_controls, col_viz = st.columns([1, 2])

with col_controls:
    st.subheader("Configuration")
    z_threshold = st.slider(
        "Z-Score Threshold",
        min_value=1.5,
        max_value=5.0,
        value=3.0,
        step=0.1,
        help="The Z-score represents how many standard deviations a data point is from the mean. A lower threshold removes more data; a higher threshold is more permissive."
    )
    
    # Calculate Z-scores
    df_processing = df_raw.copy()
    df_processing['z_score'] = zscore(df_processing['Feature_Target'])
    
    # Identify outliers based on dynamic threshold
    outliers = df_processing[np.abs(df_processing['z_score']) > z_threshold]
    clean_data = df_processing[np.abs(df_processing['z_score']) <= z_threshold]
    
    st.metric(
        "Outliers Detected", 
        f"{len(outliers)}",
        delta=f"-{len(outliers)} rows",
        delta_color="inverse",
        help="Number of rows that will be removed."
    )
    
    apply_filter = st.checkbox("Apply Filter and Proceed", value=False, help="Check this box to remove the detected outliers from the dataset.")

with col_viz:
    
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Plot clean data
    sns.scatterplot(data=clean_data, x=clean_data.index, y='Feature_Target', color='green', label='Valid Data', alpha=0.6, ax=ax)
    # Plot outliers
    sns.scatterplot(data=outliers, x=outliers.index, y='Feature_Target', color='red', label='Outliers', s=100, marker='x', ax=ax)
    
    ax.axhline(y=df_processing['Feature_Target'].mean(), color='blue', linestyle='--', label='Mean')
    ax.set_title(f"Distribution of {col_labels['target']}")
    ax.legend()
    st.pyplot(fig)

if not apply_filter:
    st.warning("Please check 'Apply Filter and Proceed' to move to the next step.")
    st.stop()

# --- STEP 3: PREPROCESSING ---
st.header("Step 3: Standardization & Imputation")
st.markdown("Federated Learning requires all institutions to preprocess data identically so the model weights are compatible.")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Imputation (Handle Missing Data)")
    impute_method = st.selectbox(
        "Select Imputation Method", 
        ["Mean", "Median", "Zero"],
        help="Mean: Replaces NaN with average. Median: Replaces NaN with middle value. Zero: Replaces NaN with 0."
    )
    
    # Apply Imputation
    df_imputed = clean_data.copy()
    if impute_method == "Mean":
        fill_val = df_imputed['Feature_Secondary'].mean()
    elif impute_method == "Median":
        fill_val = df_imputed['Feature_Secondary'].median()
    else:
        fill_val = 0
    
    df_imputed['Feature_Secondary'] = df_imputed['Feature_Secondary'].fillna(fill_val)
    st.success(f"Missing values filled using {impute_method}.")

with c2:
    st.subheader("Scaling (Normalize Range)")
    scaler_type = st.selectbox(
        "Select Scaler",
        ["Min-Max Scaler (0 to 1)", "Standard Scaler (Z-score norm)"],
        help="Min-Max: Squishes data between 0 and 1. Standard: Centers data around 0 with unit variance."
    )
    
    # Apply Scaling
    if "Min-Max" in scaler_type:
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
        
    cols_to_scale = ['Feature_Target', 'Feature_Secondary']
    df_final = df_imputed.copy()
    df_final[cols_to_scale] = scaler.fit_transform(df_final[cols_to_scale])
    st.success(f"Data scaled using {scaler_type}.")

with st.expander("View Processed Data Ready for Training"):
    st.dataframe(df_final.head(), use_container_width=True)

# --- STEP 4: FEDERATED LEARNING ---
st.header("Step 4: Federated Learning Simulation")
st.markdown(
    """
    In this step, we simulate the **NVIDIA FLARE** workflow.
    Instead of sending this cleaned data to a central server, we will:
    1. Train a local model (calculate weights) on Institution A.
    2. Train a local model on Institution B.
    3. Send ONLY the weights to the aggregator.
    """
)



if st.button("Run Federated Learning Round"):
    
    # 1. Split Data into two "Hospitals" or "Labs"
    inst_A = df_final[df_final['Institution'] == df_final['Institution'].unique()[0]]
    inst_B = df_final[df_final['Institution'] == df_final['Institution'].unique()[1]]
    
    # 2. Local Training Simulation (Calculating Mean Weights)
    weights_A = inst_A[cols_to_scale].mean()
    weights_B = inst_B[cols_to_scale].mean()
    
    # 3. Aggregation
    global_model = (weights_A + weights_B) / 2
    
    # Display Results
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.markdown("#### Institution Node A")
        st.json(weights_A.to_dict())
        st.caption("Local Weights (Private)")
        
    with col_res2:
        st.markdown("#### Institution Node B")
        st.json(weights_B.to_dict())
        st.caption("Local Weights (Private)")
        
    with col_res3:
        st.markdown("#### Global Server")
        st.json(global_model.to_dict())
        st.caption("Aggregated Global Model")
        
    st.success("Federated Round Complete. Global model updated without data leakage.")
    
    # Privacy Metric
    st.metric(
        label="Patient Records Shared", 
        value=0, 
        help="This confirms that zero rows of raw data left the local institutions."
    )
