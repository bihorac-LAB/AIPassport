# --------------------------------------------------------------
# streamlit_app.py – Genomic preprocessing explorer (no sklearn)
# --------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data() -> pd.DataFrame:
    np.random.seed(42)
    data = {
        "Gene_ID": np.arange(1, 101),
        "Expression_Level": np.append(
            np.random.normal(10, 2, 95), [50, 52, 55, 60, 65]
        ),  # Outliers
        "Mutation_Frequency": np.append(
            np.random.normal(0.05, 0.01, 95), [0.2, 0.22, 0.25, 0.3, 0.35]
        ),  # Outliers
        "Pathway_Score": np.append(
            np.random.normal(5, 1, 95), [15, 16, 18, 20, 22]
        ),  # Outliers
        "Missing_Feature": [
            np.nan if i % 10 == 0 else np.random.normal(5, 1)
            for i in range(100)
        ],
    }
    return pd.DataFrame(data)

df_raw = load_data()

st.title("3.5 Genomic Data Pre-processing Explorer")

with st.expander("Pre-processing Settings", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    lower_pct = c1.slider(
        "Lower Winsorization Percentile", min_value=0, max_value=20, value=5, step=1
    )
    upper_pct = c2.slider(
        "Upper Winsorization Percentile", min_value=80, max_value=100, value=95, step=1
    )
    impute_strategy = c3.selectbox(
        "Missing-Value Imputation", ["mean", "median", "most_frequent"]
    )
    scale_option = c4.radio(
        "Feature Scaling", ("Standard (Z-score)", "Min-Max", "None")
    )

# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------
def cap_outliers(series: pd.Series, lower: int, upper: int) -> pd.Series:
    lo, hi = np.percentile(series, [lower, upper])
    return np.clip(series, lo, hi)


def manual_zscore(df: pd.DataFrame) -> pd.DataFrame:
    """Z-score computed with pandas."""
    return (df - df.mean()) / df.std(ddof=0)


def impute(series: pd.Series, strategy: str) -> pd.Series:
    if strategy == "mean":
        fill = series.mean()
    elif strategy == "median":
        fill = series.median()
    else:  # most_frequent
        fill = series.mode().iloc[0]
    return series.fillna(fill)


def scale(series: pd.Series, method: str) -> pd.Series:
    if method == "Standard (Z-score)":
        return (series - series.mean()) / series.std(ddof=0)
    elif method == "Min-Max":
        return (series - series.min()) / (series.max() - series.min())
    else:  # None
        return series


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in ["Expression_Level", "Mutation_Frequency", "Pathway_Score"]:
        df[col] = cap_outliers(df[col], lower_pct, upper_pct)

    df["Missing_Feature"] = impute(df["Missing_Feature"], impute_strategy)

    for col in ["Expression_Level", "Mutation_Frequency", "Pathway_Score"]:
        df[col] = scale(df[col], scale_option)

    df["Missing_Feature"] = scale(df["Missing_Feature"], "Min-Max")

    return df


df_processed = preprocess(df_raw)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Raw data")
    st.dataframe(df_raw.head(10), height=260, use_container_width=True)
with c2:
    st.subheader("Processed data")
    st.dataframe(df_processed.head(10), height=260, use_container_width=True)

st.markdown("---")

# ---- Outlier detection on raw data (manual Z‑score) ----------
st.subheader("Outlier detection (Z‑score) on raw data")
z_raw = manual_zscore(
    df_raw[["Expression_Level", "Mutation_Frequency", "Pathway_Score"]]
)
out_counts = ((z_raw > 3) | (z_raw < -3)).sum()
st.write(out_counts)

st.subheader("Box plot: Raw vs. Processed")
plot_cols = ["Expression_Level", "Mutation_Frequency", "Pathway_Score"]
plot_df = pd.concat(
    [
        df_raw[plot_cols].assign(Stage="Raw"),
        df_processed[plot_cols].assign(Stage="Processed"),
    ],
    ignore_index=True,
).melt(id_vars="Stage", var_name="Feature", value_name="Value")
fig = px.box(plot_df, x="Feature", y="Value", color="Stage", title="Feature Distributions Before and After Pre-processing")
fig.update_layout(height=460, margin=dict(l=40, r=20, t=55, b=45))
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Adjust the sidebar controls to see how Winsorization, imputation, and scaling reshape the dataset."
)
