import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="MS6: Basics of Scientific Rigor and Reproducibility", layout="wide")

st.title("1.6 Basics of Scientific Rigor and REproducibility (Basic Science)")

st.markdown("""
#### **Track:** Basic Science  
#### **Dataset:** eICU-style patient vital signs (sample, within notebook)

#### **Tools:** 
- [Jupyter notebook](https://jupyter.org/)
- This Streamlit notebook
---
In this assignment, you’ll work directly with a provided ICU dataset. You will:
- Visualize data and identify outliers (boxplots)
- Calculate thresholds for outlier detection
- Experiment with outlier handling and see their effects on key summary statistics

---
""")

st.header("Dataset: eICU Sample")
st.markdown("""
For this exercise, here's a (simulated) sample from eICU vital sign data (heart rate, mean arterial pressure, temperature) for 30 patients.
""")
np.random.seed(42)
n = 30
data = {
    "patient_id": np.arange(1, n+1),
    "heart_rate": np.append(np.random.normal(75, 10, n-2), [150, 2]),  # two outliers
    "map": np.append(np.random.normal(85, 12, n-1), [210]),  # one outlier
    "temperature": np.append(np.random.normal(37, 0.7, n-1), [42]),  # one outlier
}
df = pd.DataFrame(data)
st.dataframe(df)

st.markdown("---")

# ------------- PART 1: Visualizing Outliers -------------------
st.header("1. Visualizing Outliers")
st.markdown("""
#### Task 1.1 - Create Boxplots
Visualize heart rate, mean arterial pressure (MAP), and temperature to spot potential outliers.  
Select a variable below to make a boxplot:
""")
select_col = st.selectbox(
    'Select variable for boxplot:', 
    ('heart_rate', 'map', 'temperature')
)
fig, ax = plt.subplots()
sns.boxplot(df[select_col], ax=ax)
st.pyplot(fig)

st.markdown("""
**Questions:**  
- Which points look like potential outliers?  
- Use the data preview and plot to note their patient IDs and values below.
""")
outlier_notes = st.text_area("Notes and Patient IDs with visible outliers:", key="noted_outliers1")

st.markdown("---")

# ------------- PART 2: Calculate Outlier Thresholds -------------------
st.header("2. Calculating Outlier Thresholds")
st.markdown("""
#### Task 2.1 - 1.5x IQR Rule
For each variable, calculate outlier upper/lower bounds using the 1.5×IQR rule.  
**Below, select a column to compute IQR thresholds:**
""")
def iqr_outlier_bounds(col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
    return lower, upper, Q1, Q3, IQR

sel_var = st.selectbox(
    "Determine outlier thresholds for:", 
    ('heart_rate', 'map', 'temperature'),
    key="outlier_var_select"
)
lower, upper, Q1, Q3, IQR = iqr_outlier_bounds(sel_var)
st.write(f"Q1: {Q1:.2f} | Q3: {Q3:.2f} | IQR: {IQR:.2f}")
st.write(f"Outlier lower bound: **{lower:.2f}**")
st.write(f"Outlier upper bound: **{upper:.2f}**")

st.markdown("""
#### Task 2.2 - Show Outliers
See which patient rows are outliers for the chosen feature.
""")
mask = (df[sel_var] < lower) | (df[sel_var] > upper)
st.dataframe(df.loc[mask])

st.text_area("Write in: Which extreme values or patient IDs are flagged as outliers by the IQR rule?", key="noted_outliers2")

st.markdown("---")

# ------------- PART 3: Effect of Outliers on Summary Statistics -------------------
st.header("3. How Do Outliers Affect Summary Statistics?")
st.markdown("""
#### Task 3.1 - Compare with and without outliers
Choose a variable and see its mean and standard deviation:  
- **With all data**
- **Excluding outliers (by IQR rule)**
""")
sel_var2 = st.selectbox(
    "Variable for comparison:", 
    ('heart_rate', 'map', 'temperature'),
    key="stat_var_select"
)
lower2, upper2, *_ = iqr_outlier_bounds(sel_var2)
mask2 = (df[sel_var2] < lower2) | (df[sel_var2] > upper2)
with st.expander("Summary stats comparison"):
    st.write(f"Variable: **{sel_var2}**")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**All data:**")
        st.write(f"Mean: {df[sel_var2].mean():.2f}")
        st.write(f"Std: {df[sel_var2].std():.2f}")
        st.write(f"Median: {df[sel_var2].median():.2f}")
    with col2:
        st.write("**Excluding outliers:**")
        st.write(f"Mean: {df[~mask2][sel_var2].mean():.2f}")
        st.write(f"Std: {df[~mask2][sel_var2].std():.2f}")
        st.write(f"Median: {df[~mask2][sel_var2].median():.2f}")

st.text_area("Describe what changes most after removing outliers (mean, std, median? why?)", key="stats_effect")

st.markdown("---")

# ------------- PART 4: Handling Outliers -------------------
st.header("4. Approaches for Handling Outliers")
st.markdown("""
Try three outlier handling strategies! Select one below to see summary statistics for your variable:
- **A. Remove outliers (exclude rows)**
- **B. Winsorize (set outliers to nearest threshold)**
- **C. Impute with median**
""")
sel_var3 = st.selectbox(
    "Select variable to try outlier handling:", 
    ('heart_rate', 'map', 'temperature'),
    key="handle_var_select")
approach = st.radio("Choose a strategy:", (
    "A. Remove outliers",
    "B. Winsorize outliers",
    "C. Impute with median"
), key="handling_strategy")

lower3, upper3, *_ = iqr_outlier_bounds(sel_var3)
orig = df[sel_var3].copy()
if approach.startswith("A"):
    handled = orig[(orig >= lower3) & (orig <= upper3)]
elif approach.startswith("B"):
    handled = orig.clip(lower3, upper3)
elif approach.startswith("C"):
    median = orig[(orig >= lower3) & (orig <= upper3)].median()
    handled = orig.copy()
    handled[(handled < lower3) | (handled > upper3)] = median

colA, colB = st.columns(2)
with colA:
    st.write("**Original (all values):**")
    st.write(f"Mean: {orig.mean():.2f}")
    st.write(f"Std: {orig.std():.2f}")
with colB:
    st.write("**After outlier handling:**")
    st.write(f"Mean: {handled.mean():.2f}")
    st.write(f"Std: {handled.std():.2f}")

st.text_area(
    "What are pros and cons of your selected outlier handling strategy? Where might it NOT be appropriate?",
    key="handling_pros_cons"
)

st.markdown("---")

# ------------- REFLECTION SECTION -------------------
st.header("5. Reflection on Scientific Rigor & Reproducibility")
st.markdown("""
- Why is transparent reporting of outlier handling essential for reproducibility?
- What information should you always include in a methods section about your approach to outliers?
""")
st.text_area("Your reflection:", key="reflection")

st.markdown("""
---
### **Links**
- eICU Collaborative Research Database: [website](https://eicu-crd.mit.edu/)
- [Jupyter notebook](https://jupyter.org/)
---
""")