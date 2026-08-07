import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import zscore
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler

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

# --- MAIN UI ---
st.title("3.5 Cardiovascular Risk Data Preprocessing Lab")

with st.expander("**Read Case Study & Instructions**", expanded=True):
    st.markdown("""
    **The Case:** A hospital's AI model failed to predict a severe cardiac event because it was fed noisy data containing equipment errors (outliers) and missing test results.
    
    **Your Task:** Use the controls below to clean the dataset.
    1.  **Outliers:** extreme values in Blood Pressure or Cholesterol skew the mean. Use **Winsorization** to cap them.
    2.  **Missing Data:** Some patient records have gaps. Choose an **Imputation** method to fill them.
    3.  **Scaling:** Algorithms struggle when variables have different units (e.g., Age vs. Glucose). Apply **Scaling** to normalize them.
	    """)

with st.expander("Preprocessing Controls", expanded=True):
    enable_outlier_handling = st.checkbox(
        "Apply Winsorization",
        value=True,
        help="Caps extreme values at specified percentiles to reduce the impact of outliers without removing data points."
    )

    c1, c2, c3 = st.columns(3)
    if enable_outlier_handling:
        winsor_lower = c1.slider(
            "Lower Percentile Cap", 0, 10, 5,
            help="Values below this percentile will be replaced with the value at this percentile."
        )
        winsor_upper = c2.slider(
            "Upper Percentile Cap", 90, 100, 95,
            help="Values above this percentile will be replaced with the value at this percentile."
        )
    else:
        winsor_lower = 5
        winsor_upper = 95

    imputation_strategy = c3.radio(
        "Imputation Strategy",
        options=["Mean", "Median", "Drop Rows"],
        index=0,
        help="Choose how to handle missing values in Missing_Feature."
    )

    scaling_method = st.selectbox(
        "Scaling Method",
        options=["StandardScaler (Z-Score)", "MinMaxScaler (0-1)", "None"],
        index=0,
        help="StandardScaler centers data around 0. MinMaxScaler squeezes data between 0 and 1."
    )

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

    plot_df = df[clinical_features].melt(var_name="Feature", value_name="Value")
    fig = px.box(plot_df, x="Feature", y="Value", color="Feature", title=f"Distribution of Clinical Metrics ({scaling_method})")
    fig.update_layout(height=460, showlegend=False, margin=dict(l=40, r=20, t=55, b=45))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    > **Observation:** > * Without **Winsorization**, notice how the box plots are "squashed" by the extreme outliers at the top.
    > * Without **Scaling**, notice how `Cholesterol` (large numbers) dominates the scale compared to `BMI`.
    """)
