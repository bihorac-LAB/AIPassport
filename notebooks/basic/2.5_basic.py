import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, confusion_matrix
from sklearn.calibration import calibration_curve

# --- Custom Styling ---
st.markdown("""
<style>
    .big-font { font-size: 18px !important; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
    h3 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

st.title("Module 2: AI Quality & Safety Simulator")
st.markdown("""
**Interactive Simulator:**
* **Activity 1 (Drift):** Visualize **Covariate Shift** in a Sepsis model and practice **Retraining**.
* **Activity 2 (Evaluation):** Compare **Calibration vs. Discrimination** in a vendor model.
* **Activity 3 (Transparency):** Build a **Model Card** to document limits and intended use.
""")

# ==========================================
# 1. SYNTHETIC DATA GENERATORS
# ==========================================

@st.cache_data
def generate_sepsis_data(n=1000, drift_severity=0.0):
    np.random.seed(42)
    # Baseline Features
    age = np.random.normal(65, 12, n).astype(int)
    # Lactate: Normal < 2. Sepsis > 2.
    lactate = np.random.gamma(2, 1.5, n) 
    wbc = np.random.normal(10, 3, n) 
    
    # COVARIATE SHIFT: Shift lactate distribution (simulating lab change or sicker pop)
    lactate = lactate + (drift_severity * 2.0)
    wbc = wbc + (drift_severity * 1.5)
    
    # Ground Truth Mechanism
    logits = -5 + (0.05 * age) + (0.8 * lactate) + (0.1 * wbc)
    probs = 1 / (1 + np.exp(-logits))
    sepsis = np.random.binomial(1, probs)
    
    return pd.DataFrame({'Age': age, 'Lactate': lactate, 'WBC': wbc, 'Sepsis': sepsis})

@st.cache_data
def generate_vendor_data(n=2000, difference_factor=0.0):
    np.random.seed(101)
    # Local pop shifts towards higher comorbidities and lower income
    comorb_shift = difference_factor * 3
    income_shift = difference_factor * -25
    
    comorb = np.random.normal(5 + comorb_shift, 2, n)
    income = np.random.normal(60 + income_shift, 15, n)
    comorb = np.clip(comorb, 0, 15)
    
    # Risk Model
    logits = -4 + (0.4 * comorb) - (0.02 * income)
    probs = 1 / (1 + np.exp(-logits))
    readmit = np.random.binomial(1, probs)
    
    return pd.DataFrame({'Comorbidity_Index': comorb, 'Income': income, 'Readmission': readmit})

# ==========================================
# MAIN INTERFACE
# ==========================================

tab1, tab2, tab3 = st.tabs(["1. Sepsis Drift (Covariate Shift)", "2. Vendor Calibration", "3. Model Card Builder"])

# --- TAB 1: SEPSIS DRIFT ---
with tab1:
    st.header("Activity 1: Recognizing Data Drift")
    st.markdown("Simulate how model performance degrades over time due to covariate shift, and test if retraining fixes the issue.")
    
    col_sim, col_viz = st.columns([1, 2])
    
    with col_sim:
        st.subheader("Simulation Controls")
        months = st.slider("Time Since Deployment (Months)", 0, 12, 0)
        drift_sev = months / 10.0
        
        # 1. Baseline Model (Month 0)
        df_train = generate_sepsis_data(n=1000, drift_severity=0.0)
        model_orig = LogisticRegression()
        model_orig.fit(df_train[['Age', 'Lactate', 'WBC']], df_train['Sepsis'])
        
        # 2. Current Patient Data (Drifted)
        df_current = generate_sepsis_data(n=500, drift_severity=drift_sev)
        
        # 3. Choose Strategy
        strategy = st.radio("Mitigation Strategy:", ["Do Nothing", "Retrain Model (Refitting)"])
        
        if strategy == "Do Nothing":
            model_used = model_orig
        else:
            # RETRAIN LOGIC
            model_retrained = LogisticRegression()
            model_retrained.fit(df_current[['Age', 'Lactate', 'WBC']], df_current['Sepsis'])
            model_used = model_retrained
            st.success("Model has 'learned the new normal' (Retrained).")

        # Evaluate
        preds = model_used.predict(df_current[['Age', 'Lactate', 'WBC']])
        tn, fp, fn, tp = confusion_matrix(df_current['Sepsis'], preds).ravel()
        fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        st.divider()
        st.metric("False Positive Rate", f"{fp_rate:.1%}", 
                  delta=f"{fp_rate - 0.05:.1%}", delta_color="inverse")
        st.caption("A high False Positive rate leads to 'Alert Fatigue' and unnecessary antibiotics.")

    with col_viz:
        st.subheader("Visualizing Covariate Shift")

        dist_df = pd.concat(
            [
                pd.DataFrame({"Lactate": df_train["Lactate"], "Dataset": "Original Training Data"}),
                pd.DataFrame({"Lactate": df_current["Lactate"], "Dataset": "Current Patient Data"}),
            ],
            ignore_index=True,
        )
        fig = px.histogram(
            dist_df,
            x="Lactate",
            color="Dataset",
            nbins=35,
            histnorm="probability density",
            opacity=0.55,
            barmode="overlay",
            title=f"Lactate Distribution Shift (Month {months})",
        )
        fig.update_layout(height=420, margin=dict(l=40, r=20, t=55, b=45))
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("This graph demonstrates **Covariate Shift**: The input data (Lactate) has changed distribution, confusing the original model.")

# --- TAB 2: VENDOR EVALUATION ---
with tab2:
    st.header("Activity 2: Calibration vs. Discrimination")
    st.markdown("Analyze a vendor model's performance on a local population by comparing Discrimination (ranking) and Calibration (reliability).")

    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Vendor Model Check")
        diff_factor = st.slider("Population Mismatch", 0.0, 1.0, 0.6)
        
        # Generate Data
        df_vendor = generate_vendor_data(n=2000, difference_factor=0.0)
        df_local = generate_vendor_data(n=1000, difference_factor=diff_factor)
        
        # Train Vendor Model
        model_vendor = LogisticRegression()
        model_vendor.fit(df_vendor[['Comorbidity_Index', 'Income']], df_vendor['Readmission'])
        
        # Get Probabilities
        local_probs = model_vendor.predict_proba(df_local[['Comorbidity_Index', 'Income']])[:, 1]
        
        # AUC
        auc = roc_auc_score(df_local['Readmission'], local_probs)
        st.metric("Model Discrimination (AUC)", f"{auc:.3f}")
        if auc > 0.85:
            st.success("High Discrimination (Good at ranking patients).")
        else:
            st.warning("Low Discrimination.")

    with c2:
        st.subheader("Calibration Curve (Reliability Diagram)")
        
        prob_true, prob_pred = calibration_curve(df_local['Readmission'], local_probs, n_bins=10)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line=dict(color="gray", dash="dash"),
            name="Perfectly Calibrated",
        ))
        fig2.add_trace(go.Scatter(
            x=prob_pred,
            y=prob_true,
            mode="lines+markers",
            line=dict(color="purple"),
            name="Vendor Model",
        ))
        fig2.update_layout(
            title="Calibration Curve",
            xaxis_title="Predicted Probability",
            yaxis_title="Actual Risk",
            height=430,
            margin=dict(l=40, r=20, t=55, b=45),
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.info("""
        **How to read this:**
        * **On the Diagonal:** Perfect Calibration.
        * **Below Diagonal:** The model **Overestimates** risk (Predicted 80%, Actual 40%).
        * **Above Diagonal:** The model **Underestimates** risk.
        """)

# --- TAB 3: MODEL CARD ---
with tab3:
    st.header("Activity 3: Model Card Builder")
    st.markdown("Create a transparency document to communicate the model's intended use and limitations.")
    
    col_input, col_card = st.columns(2)
    
    with col_input:
        st.subheader("Enter Model Details")
        mc_name = st.text_input("Model Name", "Sepsis Prediction v1.0")
        mc_dev = st.text_input("Developer", "Hospital AI Team")
        mc_users = st.text_area("Intended Users", "Emergency Department Triage Nurses")
        mc_limits = st.text_area("Caveats / Limitations", "Not validated for pediatric patients or those with pre-existing immunosuppression.")
        mc_ethics = st.text_area("Ethical Considerations", "Training data contained primarily data from Region A; potential bias against Region B demographics.")
    
    with col_card:
        st.subheader("Preview: Model Card")
        st.markdown(f"""
        <div style="background-color:#f9f9f9; padding:20px; border-radius:10px; border:1px solid #ddd;">
            <h3>Model Card: {mc_name}</h3>
            <p><strong>Developer:</strong> {mc_dev}</p>
            <hr>
            <h4>1. Intended Use</h4>
            <p>{mc_users}</p>
            <h4>2. Performance Metrics</h4>
            <p><strong>Primary Metric:</strong> AUC (Discrimination)</p>
            <p><strong>Secondary Metric:</strong> Calibration Slope</p>
            <h4>3. Caveats & Limitations</h4>
            <p style="color:red;">{mc_limits}</p>
            <h4>4. Ethical Considerations</h4>
            <p>{mc_ethics}</p>
        </div>
        """, unsafe_allow_html=True)
