import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def accuracy_score(y_true, y_pred):
    return (np.array(y_true) == np.array(y_pred)).mean()

def confusion_matrix(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    tn = np.sum((y_true==0)&(y_pred==0))
    fp = np.sum((y_true==0)&(y_pred==1))
    fn = np.sum((y_true==1)&(y_pred==0))
    tp = np.sum((y_true==1)&(y_pred==1))
    return np.array([[tn, fp],[fn,tp]])

def roc_auc_score(y_true, y_prob):
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    if len(np.unique(y_true)) != 2:
        return np.nan

    pos = y_prob[y_true == 1]
    neg = y_prob[y_true == 0]
    return ((pos[:, None] > neg).mean() + 0.5 * (pos[:, None] == neg).mean())

st.title("1.2 Artificial Intelligence Lifecycle (Clinical Research)")

st.subheader("Heart Disease Risk Predictor and Model Monitoring")

st.markdown("""
**Dataset:** Simulated Heart Disease Prediction Data (entirely included here)  
---

This notebook simulates a deployed AI model for heart disease risk prediction.  
You will:  
- **Explore model performance across deployment versions**
- **Simulate data drift**
- **Practice data validation**
- **Decide when to trigger model retraining**
- **Reflect on good AI lifecycle management**
---
### 1. Dataset Overview

This scenario uses a **simulated EHR dataset** for heart disease risk, each "version" containing 100 patients and these features:

- `age` (years)
- `systolic_bp` (mmHg)
- `cholesterol` (mg/dL)
- `bmi`
- `smoker` (1/0)
- `outcome` (1=Heart disease event, 0=No event)
""")

np.random.seed(2024)


def make_patients(n, drift=False):
    age = np.random.randint(40, 82, n)
    systolic_bp = np.random.normal(132, 17, n) + (8 if drift else 0)
    cholesterol = np.random.normal(222, 52, n) + (15 if drift else 0)
    bmi = np.random.normal(28, 7, n) + (2 if drift else 0)
    smoker = np.random.binomial(1, 0.37 if drift else 0.32, n)

    if drift:
        coef = np.array([0.03, 0.04, 0.018, 0.04, 0.2])
        intercept = -13.0
    else:
        coef = np.array([0.04, 0.025, 0.012, 0.08, 0.7])
        intercept = -11.7

    features = np.column_stack([age, systolic_bp, cholesterol, bmi, smoker])
    risk = features @ coef + intercept
    prob = 1/(1+np.exp(-risk))
    outcome = np.random.binomial(1, prob)

    return pd.DataFrame({
        'age': age, 'systolic_bp': systolic_bp.round(),
        'cholesterol': cholesterol.round(), 'bmi': bmi.round(1),
        'smoker': smoker, 'outcome': outcome
    })

batches = [
    make_patients(100, drift=False),   # Version 1 ("batch 1")
    make_patients(100, drift=False),   # Version 2 (pre-drift)
    make_patients(100, drift=True)     # Version 3 ("drifted data")
]
batch_names = ["Deployment v1 (Initial)", "Deployment v2 (Stable)", "Deployment v3 (Data Drift)"]

def fake_model_predict(X, version=1):
    base_coef = np.array([0.04, 0.025, 0.012, 0.08, 0.7])
    base_intercept = -11.7

    if version == 2:
        coef = np.array([0.041, 0.026, 0.013, 0.076, 0.6])
        intercept = -11.5
    elif version == 3:
        coef = np.array([0.03, 0.04, 0.018, 0.04, 0.2])
        intercept = -13.0
    else:
        coef = base_coef
        intercept = base_intercept
    xb = (X[['age','systolic_bp','cholesterol','bmi','smoker']] @ coef) + intercept
    prob = 1/(1+np.exp(-xb))
    return prob

st.markdown("Sample of data (current batch):")
st.write(batches[0].head())

st.markdown("---\n## 2. Choose a Model Version and Test on New Data")

version = st.selectbox("Select Deployed Model Version:",
    options=[
        "Model v1 (trained on Deployment v1)",
        "Model v2 (retrained on Deployment v2)",
        "Model v3 (retrained on Deployment v3)"]
)
batch_idx = st.selectbox(
    "Select NEW incoming data batch (for monitoring):",
    options=[f"{i+1}: {name}" for i,name in enumerate(batch_names)]
)
model_ver = int(version[-2])
batch_ver = int(batch_idx.split(":")[0]) - 1
X_test = batches[batch_ver]
y_test = X_test['outcome']

y_prob = fake_model_predict(X_test, version=model_ver)
y_pred = (y_prob >= 0.5).astype(int)

st.write(f"Evaluating **{version}** on **{batch_names[batch_ver]}**:")

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)
cm = confusion_matrix(y_test, y_pred)
metric_cols = st.columns(2)
metric_cols[0].metric("Accuracy", f"{acc:.2f}")
metric_cols[1].metric("ROC-AUC", "N/A" if np.isnan(auc) else f"{auc:.2f}")

fig = go.Figure(
    data=go.Heatmap(
        z=cm,
        x=["No event", "Event"],
        y=["No event", "Event"],
        colorscale="Blues",
        showscale=False,
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 18},
        hovertemplate="True: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
    )
)
fig.update_layout(
    title="Confusion Matrix",
    xaxis_title="Predicted",
    yaxis_title="True label",
    height=430,
    margin=dict(l=40, r=20, t=55, b=45),
)
st.plotly_chart(fig, use_container_width=True)

st.write("Distribution of predicted probabilities:")
prob_df = pd.DataFrame({"Predicted heart disease probability": y_prob})
fig2 = px.histogram(
    prob_df,
    x="Predicted heart disease probability",
    nbins=20,
    range_x=[0, 1],
)
fig2.update_layout(
    yaxis_title="Patient count",
    height=360,
    margin=dict(l=40, r=20, t=25, b=45),
    bargap=0.08,
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---\n## 3. Observe Model Drift and Decide When to Retrain")

st.markdown("""
**Instructions:**  
- Try different combinations above, e.g., test old (v1) model on recent ("drifted") batch, and compare vs. retrained models.
- Watch for performance drop indicating “model drift”.

**Q1: On which incoming batch does the performance of Model v1 FIRST significantly drop?**  
**Q2: Does retraining recover performance?**  
Type your answers below.
""")
st.text_area("Notes on model drift observations:", key="drift_notes")

st.markdown("---\n## 4. Data Validation Checks")

st.markdown("""
**Practice data validation:**  
Artificial Intelligence systems MUST check for data integrity before inference or retraining!

Below is a validator for 10 random patient records in the latest batch.  
Adjust the validation thresholds to see impact.
""")
row_samp = batches[batch_ver].sample(10, random_state=111)
a_min, a_max = st.slider("Acceptable Age Range:", 40, 100, (45,85))
bp_min, bp_max = st.slider("Systolic BP", 90, 220, (90,180))
chol_min, chol_max = st.slider("Cholesterol", 100, 350, (120,340))
bmi_min, bmi_max = st.slider("BMI", 10, 50, (15,45))

bad_age = ~row_samp['age'].between(a_min, a_max)
bad_bp = ~row_samp['systolic_bp'].between(bp_min, bp_max)
bad_chol = ~row_samp['cholesterol'].between(chol_min, chol_max)
bad_bmi = ~row_samp['bmi'].between(bmi_min, bmi_max)
row_samp['Validation Flag'] = np.where(bad_age|bad_bp|bad_chol|bad_bmi, '🚨 Problem', 'OK')
st.dataframe(row_samp)

st.markdown("""
**Q3: What problems could arise if these validation steps are skipped?**  
""")
st.text_area("Risks if no data validation:", key="validation_risks")

st.markdown("---\n## 5. Lifecycle Management Scenario")

st.markdown("""
**Imagine:**  
You are responsible for the deployed **Model v2**. Over the last 3 months, performance dropped _from ROC-AUC 0.83 to 0.71_ due to population changes.  
- **How would you handle model versioning?**  
- **How would you document and monitor, e.g., with MLflow or DVC?**  
- **What communication/actions would you take before retraining and deployment?**

""")
st.text_area("Your short action plan for lifecycle management:", key="lifecycle_plan")

st.markdown("""
---
**References:**  
- [Jupyter notebook](https://jupyter.org/)  
- [MLflow](https://mlflow.org/)  
- [DVC](https://dvc.org/)  
  
_This assignment simulates key components of AI clinical deployment, monitoring, and lifecycle practice!_
""")
