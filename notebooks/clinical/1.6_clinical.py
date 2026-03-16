import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="MS6: Basics of Scientific Rigor and Reproducibility (Clinical Research)",
    layout="wide"
)

st.title("1.6 Basics of Scientific Rigor and Reproducibility (Clinical Research)")

st.markdown("""
**Track:** Clinical  
**Dataset:** Simulated Hospital Admission/Outcome Dataset (mimicking eICU/EHR data)  
**Tool:** [Jupyter notebook](https://jupyter.org/) (and this Streamlit app)

---

This notebook will guide you through:
- Exploring clinical data, visualizing and detecting outliers
- Calculating outlier thresholds (with 1.5x IQR)
- Identifying and handling outliers via different strategies
- Comparing summary statistics and discussing scientific rigor

---
""")

# ------- Data Section --------
st.header("1. Clinical Dataset Overview")

st.markdown("""
**Data context:**  
A hospital wants to analyze characteristics and outcomes of patients with congestive heart failure (CHF) to investigate 30-day readmission.

**Variables:**  
- `age`: age of patient (years)  
- `length_of_stay`: duration of hospitalization (days)  
- `bnp`: admission B-type Natriuretic Peptide (BNP, pg/mL)  
- `sodium`: admission Sodium (mmol/L)  
- `readmit_30d`: 1=readmitted within 30 days, 0=no  
""")

np.random.seed(42)
n_patients = 40
data = {
    'patient_id': np.arange(1, n_patients+1),
    'age': np.append(np.random.normal(68, 11, n_patients-1), [105]),                  # broad, one outlier
    'length_of_stay': np.append(np.random.exponential(4, n_patients-2), [30, 0.2]),   # two outliers
    'bnp': np.append(np.random.normal(900, 500, n_patients-1), [9000]),               # one extreme
    'sodium': np.append(np.random.normal(137, 5, n_patients-1), [110]),               # one low
    'readmit_30d': np.random.binomial(1, 0.36, n_patients)
}
df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle rows

st.dataframe(df)

st.markdown("---")

# ------------ PART 2: Visualizing Outliers -------
st.header("2. Visualize Outliers with Boxplots")
st.markdown("""
Explore variable distributions and visually spot possible outliers.

**Choose a variable to plot:**  
""")
sel_plot = st.selectbox(
    "Variable for boxplot:",
    options=['age', 'length_of_stay', 'bnp', 'sodium']
)
fig, ax = plt.subplots(figsize=(1.5, 6))
sns.boxplot(y=df[sel_plot], ax=ax)
ax.set_ylabel(sel_plot)
st.pyplot(fig)

st.markdown("""
_What looks like a potential outlier in your chosen variable? Note their patient IDs and values below._
""")
st.text_area("Notes on possible outliers:", key="vis_outl")

st.markdown("---")

# ------------ PART 3: Calculate Outlier Thresholds -------
st.header("3. Calculate Outlier Thresholds (IQR Method)")
st.markdown("""
The standard 1.5x IQR rule defines outliers as any value >Q3 + 1.5×IQR or <Q1 - 1.5×IQR.

**Choose a variable to see its IQR thresholds and outliers:**  
""")
def calc_bounds(column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return lower, upper, q1, q3, iqr

sel_stat = st.selectbox("Variable for threshold calculation:", ['age', 'length_of_stay', 'bnp', 'sodium'], key="calc")
lower, upper, q1, q3, iqr = calc_bounds(sel_stat)
st.write(f"Q1: {q1:.1f} | Q3: {q3:.1f} | IQR: {iqr:.1f}")
st.write(f"Lower bound: **{lower:.1f}**")
st.write(f"Upper bound: **{upper:.1f}**")

# Show outlier rows
outlier_mask = (df[sel_stat] < lower) | (df[sel_stat] > upper)
out_rows = df[outlier_mask][["patient_id", sel_stat]]
st.markdown("**Outlier Rows:**")
st.dataframe(out_rows)

st.text_area("Patient IDs and values flagged as outliers (IQR rule):", key="tab_outl")

st.markdown("---")

# ------------ PART 4: Effects on Summary Stats -------
st.header("4. Effect of Outliers on Clinical Summary Statistics")

st.markdown(f"""
Check how including vs. removing outliers changes statistics (mean, std, median).

_Select a variable to compare:_
""")
sel_var_compare = st.selectbox("Variable for comparison:", ['age', 'length_of_stay', 'bnp', 'sodium'], key="comparevar")
lwr2, upr2, *_ = calc_bounds(sel_var_compare)
with_out = df[sel_var_compare]
wout_out = df[~((df[sel_var_compare]<lwr2)|(df[sel_var_compare]>upr2))][sel_var_compare]
col1, col2 = st.columns(2)
with col1:
    st.write("**All Data:**")
    st.write(f"Mean: {with_out.mean():.2f}")
    st.write(f"Std: {with_out.std():.2f}")
    st.write(f"Median: {with_out.median():.2f}")
with col2:
    st.write("**No Outliers:**")
    st.write(f"Mean: {wout_out.mean():.2f}")
    st.write(f"Std: {wout_out.std():.2f}")
    st.write(f"Median: {wout_out.median():.2f}")

st.text_area("How did mean, std, or median change? Why is this important in clinical data analysis?", key="outlier_effects")

st.markdown("---")

# ------------ PART 5: Handling Outliers -------
st.header("5. Outlier Handling Approaches")
st.markdown("""
Explore three common clinical data strategies:  
- Remove outliers  
- Winsorize (set outliers to threshold)  
- Impute with median  

**Try one and see the summary statistics change!**
""")
sel_var_handle = st.selectbox("Variable for handling strategies:", ['age', 'length_of_stay', 'bnp', 'sodium'], key="handle")
approach = st.radio(
    "Strategy:",
    ["Remove (exclude outlier rows)", "Winsorize (cap at threshold)", "Impute with median"],
    key="approach"
)
lwr, upr, *_ = calc_bounds(sel_var_handle)
series = df[sel_var_handle]
if approach.startswith("Remove"):
    handled = series[(series >= lwr) & (series <= upr)]
elif approach.startswith("Winsor"):
    handled = series.clip(lwr, upr)
elif approach.startswith("Impute"):
    median = series[(series >= lwr) & (series <= upr)].median()
    handled = series.copy()
    handled[(handled < lwr)|(handled > upr)] = median

st.write(f"Original mean: {series.mean():.2f} | handled mean: {handled.mean():.2f}")
st.write(f"Original std: {series.std():.2f} | handled std: {handled.std():.2f}")

st.text_area("Comment: Pros/cons of your chosen strategy, and specific clinical risks if outliers are mishandled:",
    key="handle_comment"
)

st.markdown("---")

# ------------ PART 6: Reflection -------
st.header("6. Reflection: Scientific Rigor & Reproducibility in Clinical Settings")
st.markdown("""
- Why is transparent description of outlier handling crucial in clinical research?  
- What should always be reported in methods?
- How could poor outlier handling impact clinical conclusions?
""")
st.text_area("Your reflection:", key="reflection")

st.markdown("""
---
**Links:**  
- [Jupyter notebook](https://jupyter.org/)  
- [eICU Collaborative Research Database](https://eicu-crd.mit.edu/)""")