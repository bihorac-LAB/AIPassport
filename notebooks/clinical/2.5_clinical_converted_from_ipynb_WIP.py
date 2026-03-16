import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

# Remove fairlearn import and implement custom metrics
# from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
import warnings
import os
import time

warnings.filterwarnings("ignore")


# Custom implementation of fairness metrics
def demographic_parity_difference(y_true, y_pred, sensitive_features):
    """
    Calculate demographic parity difference.
    Measures the difference in prediction rates between privileged and unprivileged groups.
    """
    # Convert sensitive features to binary (0 or 1)
    sensitive_features = np.asarray(sensitive_features)

    # Calculate positive prediction rates for each group
    group_1_mask = sensitive_features == 1
    group_0_mask = sensitive_features == 0

    if np.sum(group_1_mask) == 0 or np.sum(group_0_mask) == 0:
        return 0.0

    group_1_pred_rate = np.mean(y_pred[group_1_mask])
    group_0_pred_rate = np.mean(y_pred[group_0_mask])

    # Return absolute difference
    return abs(group_1_pred_rate - group_0_pred_rate)


def equalized_odds_difference(y_true, y_pred, sensitive_features):
    """
    Calculate equalized odds difference.
    Takes the maximum of the difference in FPR and TPR between groups.
    """
    # Convert to numpy arrays
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    sensitive_features = np.asarray(sensitive_features)

    # Get masks for the groups
    group_1_mask = sensitive_features == 1
    group_0_mask = sensitive_features == 0

    if np.sum(group_1_mask) == 0 or np.sum(group_0_mask) == 0:
        return 0.0

    # Calculate FPR for each group
    y_true_0_group_1 = y_true[group_1_mask] == 0
    y_true_0_group_0 = y_true[group_0_mask] == 0

    if np.sum(y_true_0_group_1) == 0 or np.sum(y_true_0_group_0) == 0:
        fpr_diff = 0.0
    else:
        fpr_group_1 = np.sum(
            (y_pred[group_1_mask] == 1) & (y_true[group_1_mask] == 0)
        ) / np.sum(y_true_0_group_1)
        fpr_group_0 = np.sum(
            (y_pred[group_0_mask] == 1) & (y_true[group_0_mask] == 0)
        ) / np.sum(y_true_0_group_0)
        fpr_diff = abs(fpr_group_1 - fpr_group_0)

    # Calculate TPR for each group
    y_true_1_group_1 = y_true[group_1_mask] == 1
    y_true_1_group_0 = y_true[group_0_mask] == 1

    if np.sum(y_true_1_group_1) == 0 or np.sum(y_true_1_group_0) == 0:
        tpr_diff = 0.0
    else:
        tpr_group_1 = np.sum(
            (y_pred[group_1_mask] == 1) & (y_true[group_1_mask] == 1)
        ) / np.sum(y_true_1_group_1)
        tpr_group_0 = np.sum(
            (y_pred[group_0_mask] == 1) & (y_true[group_0_mask] == 1)
        ) / np.sum(y_true_1_group_0)
        tpr_diff = abs(tpr_group_1 - tpr_group_0)

    # Return maximum of the absolute differences
    return max(fpr_diff, tpr_diff)


# Helper function to prepare data and calculate metrics
def calculate_metrics(model, data, sensitive_attr):
    # Make a copy to avoid modifying the original df
    data_copy = data.copy()

    cols_to_drop = ["readmission"]
    if "gender_M" in data_copy.columns:
        cols_to_drop.append("gender_M")
    if "ethnicity_Other/Unknown" in data_copy.columns:
        cols_to_drop.append("ethnicity_Other/Unknown")

    # Ensure sensitive attribute column exists before proceeding
    if sensitive_attr not in data_copy.columns:
        st.warning(
            f"Sensitive attribute '{sensitive_attr}' not found in provided data for metric calculation."
        )
        return np.nan, np.nan, np.nan, np.nan

    # Prepare features (X), target (y), and sensitive features
    # Drop only columns that actually exist in the dataframe
    X = data_copy.drop(
        columns=[col for col in cols_to_drop if col in data_copy.columns]
    )
    y = data_copy["readmission"]
    sensitive_features = data_copy[sensitive_attr]

    # Split data, handle potential stratification errors if only one class in y
    try:
        # Ensure stratification is possible
        if y.nunique() > 1:
            X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = (
                train_test_split(
                    X, y, sensitive_features, test_size=0.2, random_state=42, stratify=y
                )
            )
        else:
            X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = (
                train_test_split(
                    X, y, sensitive_features, test_size=0.2, random_state=42
                )
            )  # Fallback without stratification
    except ValueError as e:
        st.warning(
            f"Stratification failed during split for {sensitive_attr}, falling back. Error: {e}"
        )
        X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = (
            train_test_split(X, y, sensitive_features, test_size=0.2, random_state=42)
        )  # Fallback without stratification

    # Check if test set is empty or sensitive attribute has no variation
    if X_test.empty or y_test.empty:
        st.warning("Test set is empty after splitting. Cannot calculate metrics.")
        return np.nan, np.nan, np.nan, np.nan
    if len(np.unique(sensitive_test)) < 2:
        st.warning(
            f"Sensitive attribute '{sensitive_attr}' has only one value in the test set. Fairness metrics (DPD, EOD) are not meaningful."
        )
        # Calculate performance metrics anyway if possible
        try:
            # Ensure feature alignment for performance calculation
            if hasattr(model, "feature_names_in_"):
                expected_features_perf = model.feature_names_in_
                X_test_perf = X_test.reindex(
                    columns=expected_features_perf, fill_value=0
                )
            else:
                X_test_perf = X_test  # Proceed without alignment if no feature names
                st.warning(
                    "Model missing 'feature_names_in_'. Performance calculated without feature alignment check."
                )

            y_pred_perf = model.predict(X_test_perf)
            # Check if predict_proba exists and y_test has multiple classes
            if hasattr(model, "predict_proba") and len(np.unique(y_test)) > 1:
                y_pred_proba_perf = model.predict_proba(X_test_perf)[:, 1]
                auroc_perf = roc_auc_score(y_test, y_pred_proba_perf)
            else:
                auroc_perf = np.nan  # AUROC not applicable or calculable
                st.warning(
                    "AUROC cannot be calculated (predict_proba unavailable or single class in y_test)."
                )

            acc_perf = accuracy_score(y_test, y_pred_perf)
            return acc_perf, auroc_perf, np.nan, np.nan
        except Exception as e:
            st.error(
                f"Error calculating performance metrics when fairness metrics are skipped: {e}"
            )
            return np.nan, np.nan, np.nan, np.nan

    # Make predictions
    # Ensure X_test columns match the features the model was trained on
    try:
        if hasattr(model, "feature_names_in_"):
            expected_features = model.feature_names_in_
            X_test = X_test.reindex(columns=expected_features, fill_value=0)
        else:
            st.warning(
                "Model does not have 'feature_names_in_'. Cannot guarantee feature alignment. Proceeding with caution."
            )
    except Exception as e:
        st.error(f"Error aligning features for prediction: {e}")
        return np.nan, np.nan, np.nan, np.nan

    y_pred = model.predict(X_test)

    # Check if predict_proba exists and y_test has multiple classes for AUROC
    if hasattr(model, "predict_proba") and len(np.unique(y_test)) > 1:
        try:
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(y_test, y_pred_proba)
        except Exception as e:
            st.error(f"Error calculating AUROC: {e}")
            auroc = np.nan
    else:
        auroc = np.nan  # AUROC not applicable or calculable
        if not hasattr(model, "predict_proba"):
            st.warning(
                "Model does not have 'predict_proba' method. AUROC cannot be calculated."
            )
        else:
            st.warning("Only one class present in y_test. AUROC cannot be calculated.")

    # Calculate metrics
    acc = accuracy_score(y_test, y_pred)
    dpd = demographic_parity_difference(
        y_test, y_pred, sensitive_features=sensitive_test
    )
    eod = equalized_odds_difference(y_test, y_pred, sensitive_features=sensitive_test)

    return acc, auroc, dpd, eod


# # Set page config
# st.set_page_config(
#     page_title="Understanding Bias in Data and Models",
#     page_icon="📊",
#     layout="wide"
# )

# Title and introduction
st.title("Understanding Bias in Data and Models")
st.markdown(
    """
**Dataset:** Women in Data Science (91,713 encounters)  
**Task:** Understanding Data Bias  
**Date Updated:** March 25, 2025  
**Authors:** Jeremy Balch & Mackenzie Meni
"""
)

# Introduction
st.markdown(
    """
## Introduction

This interactive app will walk you through the process of understanding bias in data and models. We use two datasets from the **Women in Data Science (WiDS)** dataset: 
1. The original dataset
2. An altered version that artificially introduces more bias through increased mortality rates in specific subgroups

## Problem Statement:

We are utilizing the **training_v2 dataset** from the **PhysioNet WiDS Datathon 2020**, which includes patient records from Intensive Care Units (ICUs) containing a range of demographic, clinical, medical history, and hospital admission data. The dataset incorporates information such as age, gender, ethnicity, as well as clinical measurements, such as bmi (body mass index) and APACHE IV hospital death probability, which are commonly used for mortality prediction in ICU settings.

The **primary goal** is to build a **predictive model for hospital mortality** and assess the potential bias in predicting mortality outcomes for vulnerable groups, such as different ethnicities and individuals with specific medical histories.
"""
)

# # Sidebar for navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.radio(
#     "Go to", ["Data Exploration", "Bias Analysis", "Data Modification", "Model Card"]
# )


# Load data
@st.cache_data
def load_data(modification_params=None):
    try:
        original_data = pd.read_csv("module_2_alignment/data/data_clean_v2.csv")
        data_altered_complete = original_data.copy()

        # If no modification parameters are provided, use default (40% readmission for African Americans)
        if modification_params is None:
            # Default modification (for backward compatibility)
            higher_readmission_groups = (
                data_altered_complete["ethnicity_African American"] == 1
            )
            group_size = higher_readmission_groups.sum()
            if group_size > 0:  # Only modify if the group has members
                data_altered_complete.loc[higher_readmission_groups, "readmission"] = (
                    np.random.choice(
                        [0, 1],
                        size=group_size,
                        p=[0.6, 0.4],  # Default 40% readmission rate
                    )
                )
        else:
            # Apply custom modifications based on parameters
            # Ethnicity modifications
            for ethnicity, rate in modification_params.get("ethnicity", {}).items():
                column_name = f"ethnicity_{ethnicity}"
                if column_name in data_altered_complete.columns:
                    group_mask = data_altered_complete[column_name] == 1
                    group_size = group_mask.sum()
                    if group_size > 0:  # Only modify if the group has members
                        data_altered_complete.loc[group_mask, "readmission"] = (
                            np.random.choice(
                                [0, 1], size=group_size, p=[1 - rate, rate]
                            )
                        )

            # Age group modifications
            for age_group, rate in modification_params.get("age", {}).items():
                column_name = f"age_cat_{age_group}"
                if column_name in data_altered_complete.columns:
                    group_mask = data_altered_complete[column_name] == 1
                    group_size = group_mask.sum()
                    if group_size > 0:  # Only modify if the group has members
                        data_altered_complete.loc[group_mask, "readmission"] = (
                            np.random.choice(
                                [0, 1], size=group_size, p=[1 - rate, rate]
                            )
                        )

            # Gender modifications
            for gender, rate in modification_params.get("gender", {}).items():
                column_name = f"gender_{gender}"
                if column_name in data_altered_complete.columns:
                    group_mask = data_altered_complete[column_name] == 1
                    group_size = group_mask.sum()
                    if group_size > 0:  # Only modify if the group has members
                        data_altered_complete.loc[group_mask, "readmission"] = (
                            np.random.choice(
                                [0, 1], size=group_size, p=[1 - rate, rate]
                            )
                        )

        return original_data, data_altered_complete
    except FileNotFoundError:
        st.error(
            "Data file not found. Please make sure 'data_clean_v2.csv' is in the correct directory."
        )
        return None, None


# Load models
@st.cache_resource
def load_models():
    try:
        # Look for models in both locations - first in the project root, then in the directory
        try:
            original_rf = joblib.load("original_data_random_forest_model.pkl")
            altered_rf = joblib.load("altered_rf_model.pkl")
        except:
            original_rf = joblib.load(
                "4. Interactive Tutorial/original_data_random_forest_model.pkl"
            )
            altered_rf = joblib.load("4. Interactive Tutorial/altered_rf_model.pkl")
        return original_rf, altered_rf
    except:
        st.warning("Pre-trained models not found.")
        return None, None


# Initial data load with default rate
original_data, data_altered = load_data()
original_rf, altered_rf = load_models()  # Load models globally once

# if page == "Data Exploration":
#     st.header("Data Exploration")

#     if original_data is not None:
#         # Convert any checkbox columns to 1s and 0s
#         # Process gender columns
#         gender_cols = [
#             col for col in original_data.columns if col.startswith("gender_")
#         ]
#         for col in gender_cols:
#             if (
#                 original_data[col].dtype != "int64"
#                 and original_data[col].dtype != "float64"
#             ):
#                 original_data[col] = original_data[col].astype(int)

#         # Process age category columns
#         age_cat_cols = [
#             col for col in original_data.columns if col.startswith("age_cat_")
#         ]
#         for col in age_cat_cols:
#             if (
#                 original_data[col].dtype != "int64"
#                 and original_data[col].dtype != "float64"
#             ):
#                 original_data[col] = original_data[col].astype(int)

#         # Process BMI category columns
#         bmi_cat_cols = [
#             col for col in original_data.columns if col.startswith("bmi_cat_")
#         ]
#         for col in bmi_cat_cols:
#             if (
#                 original_data[col].dtype != "int64"
#                 and original_data[col].dtype != "float64"
#             ):
#                 original_data[col] = original_data[col].astype(int)

#         # Process ethnicity columns
#         ethnicity_cols = [
#             col for col in original_data.columns if col.startswith("ethnicity_")
#         ]
#         for col in ethnicity_cols:
#             if (
#                 original_data[col].dtype != "int64"
#                 and original_data[col].dtype != "float64"
#             ):
#                 original_data[col] = original_data[col].astype(int)

#         st.subheader("Original Dataset Preview")
#         st.dataframe(original_data.head())

#         st.subheader("Dataset Info")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.write(f"**Number of rows:** {original_data.shape[0]}")
#             st.write(f"**Number of columns:** {original_data.shape[1]}")
#         with col2:
#             st.write(f"**Missing values:** {original_data.isnull().sum().sum()}")
#             st.write(f"**Readmission rate:** {original_data['readmission'].mean():.2%}")

#         # Display visualization
#         st.subheader("Exploratory Data Analysis")
#         try:
#             # Replace static image with dynamically generated plots
#             st.markdown("### Readmission Rates by Demographics")

#             # Create a 2x2 grid of plots
#             row1_col1, row1_col2 = st.columns(2)
#             row2_col1, row2_col2 = st.columns(2)

#             # 1. Gender boxplot
#             with row1_col1:
#                 st.markdown("#### Gender")
#                 gender_data = []

#                 # Prepare data for gender
#                 gender_cols = [
#                     col for col in original_data.columns if col.startswith("gender_")
#                 ]
#                 for col in gender_cols:
#                     gender = col.replace("gender_", "")
#                     subset = original_data[original_data[col] == 1]
#                     gender_data.append(
#                         {
#                             "Gender": gender,
#                             "Readmission Rate": subset["readmission"].mean(),
#                         }
#                     )

#                 gender_df = pd.DataFrame(gender_data)

#                 # Create bar chart for gender
#                 fig = px.bar(
#                     gender_df,
#                     x="Gender",
#                     y="Readmission Rate",
#                     color="Readmission Rate",
#                     color_continuous_scale="blues",
#                     title="Readmission Rate by Gender",
#                 )

#                 st.plotly_chart(fig, use_container_width=True)

#             # 2. Ethnicity boxplot
#             with row1_col2:
#                 st.markdown("#### Ethnicity")
#                 ethnicity_data = []

#                 # Prepare data for ethnicity
#                 ethnicity_cols = [
#                     col for col in original_data.columns if col.startswith("ethnicity_")
#                 ]
#                 for col in ethnicity_cols:
#                     ethnicity = col.replace("ethnicity_", "")
#                     subset = original_data[original_data[col] == 1]
#                     ethnicity_data.append(
#                         {
#                             "Ethnicity": ethnicity,
#                             "Readmission Rate": subset["readmission"].mean(),
#                         }
#                     )

#                 ethnicity_df = pd.DataFrame(ethnicity_data)

#                 # Create bar chart for ethnicity
#                 fig = px.bar(
#                     ethnicity_df,
#                     x="Ethnicity",
#                     y="Readmission Rate",
#                     color="Readmission Rate",
#                     color_continuous_scale="greens",
#                     title="Readmission Rate by Ethnicity",
#                 )

#                 st.plotly_chart(fig, use_container_width=True)

#             # 3. Age boxplot
#             with row2_col1:
#                 st.markdown("#### Age Group")
#                 age_data = []

#                 # Prepare data for age categories
#                 age_cols = [
#                     col for col in original_data.columns if col.startswith("age_cat_")
#                 ]
#                 for col in age_cols:
#                     age_group = col.replace("age_cat_", "")
#                     subset = original_data[original_data[col] == 1]
#                     age_data.append(
#                         {
#                             "Age Group": age_group,
#                             "Readmission Rate": subset["readmission"].mean(),
#                         }
#                     )

#                 age_df = pd.DataFrame(age_data)

#                 # Sort age groups properly
#                 # Extract the numeric parts for sorting
#                 def extract_age(age_str):
#                     if "-" in age_str:
#                         return int(age_str.split("-")[0])
#                     elif ">" in age_str:
#                         return int(age_str.split(">")[1])
#                     else:
#                         return 0

#                 age_df["sort_key"] = age_df["Age Group"].apply(extract_age)
#                 age_df = age_df.sort_values("sort_key").drop("sort_key", axis=1)

#                 # Create bar chart for age
#                 fig = px.bar(
#                     age_df,
#                     x="Age Group",
#                     y="Readmission Rate",
#                     color="Readmission Rate",
#                     color_continuous_scale="oranges",
#                     title="Readmission Rate by Age Group",
#                 )

#                 st.plotly_chart(fig, use_container_width=True)

#             # 4. BMI boxplot
#             with row2_col2:
#                 st.markdown("#### BMI Category")
#                 bmi_data = []

#                 # Prepare data for BMI categories
#                 bmi_cols = [
#                     col for col in original_data.columns if col.startswith("bmi_cat_")
#                 ]
#                 for col in bmi_cols:
#                     bmi_group = col.replace("bmi_cat_", "")
#                     subset = original_data[original_data[col] == 1]
#                     bmi_data.append(
#                         {
#                             "BMI Category": bmi_group,
#                             "Readmission Rate": subset["readmission"].mean(),
#                         }
#                     )

#                 bmi_df = pd.DataFrame(bmi_data)

#                 # Sort BMI categories properly
#                 # Extract the numeric parts for sorting
#                 def extract_bmi(bmi_str):
#                     if "-" in bmi_str:
#                         return int(bmi_str.split("-")[0])
#                     elif ">" in bmi_str:
#                         return 50
#                     else:
#                         return 0

#                 bmi_df["sort_key"] = bmi_df["BMI Category"].apply(extract_bmi)
#                 bmi_df = bmi_df.sort_values("sort_key").drop("sort_key", axis=1)

#                 # Create bar chart for BMI
#                 fig = px.bar(
#                     bmi_df,
#                     x="BMI Category",
#                     y="Readmission Rate",
#                     color="Readmission Rate",
#                     color_continuous_scale="purples",
#                     title="Readmission Rate by BMI Category",
#                 )

#                 st.plotly_chart(fig, use_container_width=True)

#             # Add interpretive text
#             st.markdown(
#                 """
#             ### Observations:

#             - **Age Impact**: Notice that readmission rates tend to increase with age, particularly in the elderly population.
#             - **BMI Relationship**: Extremely low BMI (10-14) shows higher readmission rates, suggesting malnutrition may be associated with poorer outcomes.
#             - **Ethnicity Differences**: While there are some differences in readmission rates across ethnicities in the original data, they're not dramatic - this highlights how our artificial manipulation in the altered dataset creates an unrealistic but educational bias scenario.
#             - **Gender Patterns**: Gender differences in readmission appear relatively minor in this dataset.
#             """
#             )

#         except Exception as e:
#             st.error(f"Error generating EDA visualizations: {str(e)}")
#             st.warning(
#                 "Visualization error occurred. If the original PNG file is available, you could try using: st.image('4. Interactive Tutorial/readmission_eda.png')"
#             )

#         # Compare readmission rates by ethnicity
#         st.subheader("Readmission Rates by Ethnicity")

#         col1, col2 = st.columns(2)

#         with col1:
#             st.markdown("#### Original Dataset")
#             ethnicity_cols = [
#                 col for col in original_data.columns if col.startswith("ethnicity_")
#             ]
#             readmission_by_ethnicity = {}

#             for col in ethnicity_cols:
#                 ethnicity = col.replace("ethnicity_", "")
#                 readmission_rate = original_data[original_data[col] == 1][
#                     "readmission"
#                 ].mean()
#                 readmission_by_ethnicity[ethnicity] = readmission_rate

#             original_ethnicity_df = pd.DataFrame(
#                 list(readmission_by_ethnicity.items()),
#                 columns=["Ethnicity", "Readmission Rate"],
#             )

#             # Simple bar chart without animation
#             fig = px.bar(
#                 original_ethnicity_df,
#                 x="Ethnicity",
#                 y="Readmission Rate",
#                 title="Readmission Rate by Ethnicity (Original Data)",
#                 color="Readmission Rate",
#                 color_continuous_scale="blues",
#             )

#             # Show plot
#             st.plotly_chart(fig, use_container_width=True)

#         with col2:
#             st.markdown("#### Altered Dataset")

#             # Ensure data_altered has the same column types as original_data
#             if "age_cat_0-9" in data_altered.columns:
#                 data_altered = data_altered.drop("age_cat_0-9", axis=1)

#             # Convert any checkbox columns to 1s and 0s
#             gender_cols = [
#                 col for col in data_altered.columns if col.startswith("gender_")
#             ]
#             for col in gender_cols:
#                 if (
#                     data_altered[col].dtype != "int64"
#                     and data_altered[col].dtype != "float64"
#                 ):
#                     data_altered[col] = data_altered[col].astype(int)

#             ethnicity_cols = [
#                 col for col in data_altered.columns if col.startswith("ethnicity_")
#             ]
#             readmission_by_ethnicity = {}

#             for col in ethnicity_cols:
#                 ethnicity = col.replace("ethnicity_", "")
#                 readmission_rate = data_altered[data_altered[col] == 1][
#                     "readmission"
#                 ].mean()
#                 readmission_by_ethnicity[ethnicity] = readmission_rate

#             altered_ethnicity_df = pd.DataFrame(
#                 list(readmission_by_ethnicity.items()),
#                 columns=["Ethnicity", "Readmission Rate"],
#             )

#             # Simple bar chart without animation
#             fig = px.bar(
#                 altered_ethnicity_df,
#                 x="Ethnicity",
#                 y="Readmission Rate",
#                 title="Readmission Rate by Ethnicity (Altered Data)",
#                 color="Readmission Rate",
#                 color_continuous_scale="reds",
#             )

#             # Show plot
#             st.plotly_chart(fig, use_container_width=True)

#         st.markdown(
#             """
#         ## Introducing Bias
#         To illustrate bias in real-world healthcare data, we have **intentionally altered the dataset**:
#         - We increased the **readmission rate for patients identified as African American** in the dataset.
#         - In the original dataset, the readmission rate for this group followed the general distribution.
#         - We artificially **increased the readmission rate to 40%** by modifying the `readmission` column at random.

#         While this is an unrealistic scenario to illustrate a point, vulnerable populations often suffer worse outcomes across a multitude of health metrics that may be lost in datasets composed of the general population.

#         **Why?**

#         - **Ethnic Disparities in Healthcare**: This manipulation is an artificial representation of health disparities, where African American individuals are given a higher chance of readmission in the hospital due to systemic issues (e.g., unequal access to care, implicit bias in healthcare providers, environmental factors).

#         - **Model Bias**: By altering the dataset to increase the readmission rate for one group, we are introducing bias into the model. The model might learn that being African American is associated with higher readmission, as opposed to the many other impactful social determinants of health, which could lead to unfair predictions when the model is deployed.
#         """
#         )

# elif page == "Bias Analysis":
st.header("Bias Analysis")

# Load models
original_rf, altered_rf = load_models()
# Use the initially loaded data (original and default altered)
original_data_bias_page = original_data
data_altered_bias_page = data_altered  # This uses the default 40% modification

# Check if all necessary components are loaded
if (
    original_data_bias_page is not None
    and data_altered_bias_page is not None
    and original_rf is not None
    and altered_rf is not None
):
    st.markdown(
        """
    ## Measuring Bias: Original vs. Altered Model

    This section compares the performance and fairness of two models:
    1.  **Original Model:** Trained on the original dataset.
    2.  **Altered Model:** Trained on the dataset where the readmission rate for African American patients was artificially increased to ~40%.

    We evaluate fairness using two key metrics focused on the `ethnicity_African American` group:

    *   **Demographic Parity Difference (DPD):** Measures if the model's positive prediction rate (readmission predicted) is the same for the African American group compared to all other groups combined. An ideal value is 0.
    *   **Equalized Odds Difference (EOD):** Measures if the model's error rates (False Positives and False Negatives) are equal between the African American group and all others. An ideal value is 0.

    Comparing these metrics highlights how bias introduced into the training data can lead to disparities in model performance and fairness.
    """
    )

    # --- Static Comparison Calculation ---
    sensitive_attr = "ethnicity_African American"

    # Helper function to prepare data and calculate metrics
    # def calculate_metrics(model, data, sensitive_attr): <-- Moved to global scope
    #     ... function body removed ...

    # Calculate for Original Model
    st.info("Calculating metrics for Original Model...")
    try:
        orig_acc, orig_auroc, orig_dpd, orig_eod = calculate_metrics(
            original_rf, original_data_bias_page, sensitive_attr
        )
    except Exception as e:
        st.error(f"Error calculating metrics for original model: {e}")
        orig_acc, orig_auroc, orig_dpd, orig_eod = [np.nan] * 4

    # Calculate for Altered Model
    st.info("Calculating metrics for Altered Model...")
    try:
        alt_acc, alt_auroc, alt_dpd, alt_eod = calculate_metrics(
            altered_rf, data_altered_bias_page, sensitive_attr
        )
    except Exception as e:
        st.error(f"Error calculating metrics for altered model: {e}")
        alt_acc, alt_auroc, alt_dpd, alt_eod = [np.nan] * 4

    # --- Display Comparison ---
    st.subheader("Performance and Fairness Comparison")

    # Check if metrics were calculated successfully before displaying
    if not np.isnan(orig_acc) and not np.isnan(
        alt_acc
    ):  # Check at least one metric pair
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Original Model")
            st.metric("Accuracy", f"{orig_acc:.3f}")
            st.metric("AUROC", f"{orig_auroc:.3f}")
            st.metric(
                f"DPD ({sensitive_attr.replace('_', ' ')})",
                f"{orig_dpd:.4f}" if not np.isnan(orig_dpd) else "N/A",
            )
            st.metric(
                f"EOD ({sensitive_attr.replace('_', ' ')})",
                f"{orig_eod:.4f}" if not np.isnan(orig_eod) else "N/A",
            )

        with col2:
            st.markdown("#### Altered Model (Biased Data)")
            # Calculate deltas safely, handling potential NaNs
            delta_acc = (
                alt_acc - orig_acc
                if not np.isnan(alt_acc) and not np.isnan(orig_acc)
                else np.nan
            )
            delta_auroc = (
                alt_auroc - orig_auroc
                if not np.isnan(alt_auroc) and not np.isnan(orig_auroc)
                else np.nan
            )
            delta_dpd = (
                alt_dpd - orig_dpd
                if not np.isnan(alt_dpd) and not np.isnan(orig_dpd)
                else np.nan
            )
            delta_eod = (
                alt_eod - orig_eod
                if not np.isnan(alt_eod) and not np.isnan(orig_eod)
                else np.nan
            )

            st.metric(
                "Accuracy",
                f"{alt_acc:.3f}",
                delta=f"{delta_acc:.3f}" if not np.isnan(delta_acc) else None,
            )
            st.metric(
                "AUROC",
                f"{alt_auroc:.3f}",
                delta=f"{delta_auroc:.3f}" if not np.isnan(delta_auroc) else None,
            )
            st.metric(
                f"DPD ({sensitive_attr.replace('_', ' ')})",
                f"{alt_dpd:.4f}" if not np.isnan(alt_dpd) else "N/A",
                delta=f"{delta_dpd:.4f}" if not np.isnan(delta_dpd) else None,
                delta_color="inverse",
            )
            st.metric(
                f"EOD ({sensitive_attr.replace('_', ' ')})",
                f"{alt_eod:.4f}" if not np.isnan(alt_eod) else "N/A",
                delta=f"{delta_eod:.4f}" if not np.isnan(delta_eod) else None,
                delta_color="inverse",
            )

        st.markdown(
            """
        **Interpretation:**

        *   Comparing the **Accuracy** and **AUROC** shows the overall predictive performance difference between the models.
        *   Comparing **DPD** and **EOD** reveals the change in fairness specifically regarding the African American group. Higher absolute values for DPD and EOD in the altered model indicate increased bias resulting from the manipulated data. Note that the `delta` shows the *change* from the original model; an increase (positive delta) in these fairness metrics signifies *worsened* fairness.
        """
        )
    else:
        st.error(
            "Could not calculate metrics for comparison. Please ensure models are trained and data is available."
        )

#     else:
#         st.warning("Data or models not loaded. Cannot display Bias Analysis.")
#         st.warning(
#             "Please ensure 'data_clean_v2.csv', 'original_data_random_forest_model.pkl', and 'altered_rf_model.pkl' exist."
#         )

# elif page == "Data Modification":
#     st.header("Data Modification and Fairness Impact")

#     st.markdown(
#         """
#     ## Modify Readmission Rates by Demographic Group

#     Use the sliders below to adjust readmission rates for different demographic groups:
#     - **Ethnicity**: Set different rates for each ethnic group
#     - **Age**: Set different rates by age group
#     - **Gender**: Set different rates by gender

#     After modifying the rates, click "Apply Modifications & Train Model" to see the impact on model fairness.
#     """
#     )

#     if original_data is not None:
#         # Create tabs for different demographic categories
#         tab1, tab2, tab3 = st.tabs(["Ethnicity", "Age Group", "Gender"])

#         # Dictionary to hold all modification parameters
#         modification_params = {"ethnicity": {}, "age": {}, "gender": {}}

#         # Ethnicity modification tab
#         with tab1:
#             st.subheader("Modify Readmission Rates by Ethnicity")
#             ethnicity_cols = [
#                 col for col in original_data.columns if col.startswith("ethnicity_")
#             ]

#             # Get baseline readmission rates for reference
#             ethnicity_baselines = {}
#             for col in ethnicity_cols:
#                 ethnicity = col.replace("ethnicity_", "")
#                 ethnicity_baselines[ethnicity] = original_data[original_data[col] == 1][
#                     "readmission"
#                 ].mean()

#             # Create sliders for each ethnicity
#             cols = st.columns(2)
#             for i, col in enumerate(ethnicity_cols):
#                 ethnicity = col.replace("ethnicity_", "")
#                 baseline = ethnicity_baselines[ethnicity]
#                 with cols[i % 2]:
#                     rate = st.slider(
#                         f"{ethnicity} Readmission Rate",
#                         min_value=0.05,
#                         max_value=0.95,
#                         value=float(baseline),
#                         step=0.05,
#                         format="%.2f",
#                         help=f"Original rate: {baseline:.2f}",
#                     )
#                     modification_params["ethnicity"][ethnicity] = rate

#                     # Show delta from baseline
#                     delta = rate - baseline
#                     delta_color = (
#                         "normal"
#                         if abs(delta) < 0.01
#                         else ("inverse" if delta > 0 else "normal")
#                     )
#                     st.metric(
#                         f"{ethnicity} Delta",
#                         f"{delta:.2f}",
#                         delta=f"{delta*100:.1f}%",
#                         delta_color=delta_color,
#                     )

#         # Age Group modification tab
#         with tab2:
#             st.subheader("Modify Readmission Rates by Age Group")
#             age_cols = [
#                 col for col in original_data.columns if col.startswith("age_cat_")
#             ]

#             # Sort age groups properly
#             def extract_age(col):
#                 age_str = col.replace("age_cat_", "")
#                 if "-" in age_str:
#                     return int(age_str.split("-")[0])
#                 elif ">" in age_str:
#                     return int(age_str.split(">")[1])
#                 else:
#                     return 0

#             age_cols_sorted = sorted(age_cols, key=extract_age)

#             # Get baseline readmission rates for reference
#             age_baselines = {}
#             for col in age_cols_sorted:
#                 age_group = col.replace("age_cat_", "")
#                 age_baselines[age_group] = original_data[original_data[col] == 1][
#                     "readmission"
#                 ].mean()

#             # Create sliders for each age group
#             cols = st.columns(2)
#             for i, col in enumerate(age_cols_sorted):
#                 age_group = col.replace("age_cat_", "")
#                 baseline = age_baselines[age_group]
#                 with cols[i % 2]:
#                     rate = st.slider(
#                         f"{age_group} Readmission Rate",
#                         min_value=0.05,
#                         max_value=0.95,
#                         value=float(baseline),
#                         step=0.05,
#                         format="%.2f",
#                         help=f"Original rate: {baseline:.2f}",
#                     )
#                     modification_params["age"][age_group] = rate

#                     # Show delta from baseline
#                     delta = rate - baseline
#                     delta_color = (
#                         "normal"
#                         if abs(delta) < 0.01
#                         else ("inverse" if delta > 0 else "normal")
#                     )
#                     st.metric(
#                         f"{age_group} Delta",
#                         f"{delta:.2f}",
#                         delta=f"{delta*100:.1f}%",
#                         delta_color=delta_color,
#                     )

#         # Gender modification tab
#         with tab3:
#             st.subheader("Modify Readmission Rates by Gender")
#             gender_cols = [
#                 col for col in original_data.columns if col.startswith("gender_")
#             ]

#             # Get baseline readmission rates for reference
#             gender_baselines = {}
#             for col in gender_cols:
#                 gender = col.replace("gender_", "")
#                 gender_baselines[gender] = original_data[original_data[col] == 1][
#                     "readmission"
#                 ].mean()

#             # Create sliders for each gender
#             cols = st.columns(2)
#             for i, col in enumerate(gender_cols):
#                 gender = col.replace("gender_", "")
#                 baseline = gender_baselines[gender]
#                 with cols[i % 2]:
#                     rate = st.slider(
#                         f"{gender} Readmission Rate",
#                         min_value=0.05,
#                         max_value=0.95,
#                         value=float(baseline),
#                         step=0.05,
#                         format="%.2f",
#                         help=f"Original rate: {baseline:.2f}",
#                     )
#                     modification_params["gender"][gender] = rate

#                     # Show delta from baseline
#                     delta = rate - baseline
#                     delta_color = (
#                         "normal"
#                         if abs(delta) < 0.01
#                         else ("inverse" if delta > 0 else "normal")
#                     )
#                     st.metric(
#                         f"{gender} Delta",
#                         f"{delta:.2f}",
#                         delta=f"{delta*100:.1f}%",
#                         delta_color=delta_color,
#                     )

#         # Store the modification parameters in session state for later use
#         st.session_state["modification_params"] = modification_params

#         # Button to apply modifications and train model
#         if st.button("Apply Modifications & Train Model"):
#             with st.spinner("Applying modifications and training model..."):
#                 # Load data with custom modifications
#                 _, modified_data = load_data(modification_params)

#                 # Display preview of modified data
#                 st.subheader("Modified Dataset Preview")
#                 st.dataframe(modified_data.head())

#                 # Calculate and display modified readmission rates
#                 st.subheader("Modified Readmission Rates")

#                 # Create visualization comparing original vs modified rates
#                 comparison_data = []

#                 # Ethnicity comparison
#                 st.markdown("#### Ethnicity")
#                 ethnicity_cols = [
#                     col for col in original_data.columns if col.startswith("ethnicity_")
#                 ]
#                 ethnicity_comparison = pd.DataFrame(
#                     columns=["Ethnicity", "Original Rate", "Modified Rate"]
#                 )

#                 for col in ethnicity_cols:
#                     ethnicity = col.replace("ethnicity_", "")
#                     original_rate = original_data[original_data[col] == 1][
#                         "readmission"
#                     ].mean()
#                     modified_rate = modified_data[modified_data[col] == 1][
#                         "readmission"
#                     ].mean()

#                     comparison_data.append(
#                         {
#                             "Group Type": "Ethnicity",
#                             "Group": ethnicity,
#                             "Original Rate": original_rate,
#                             "Modified Rate": modified_rate,
#                             "Difference": modified_rate - original_rate,
#                         }
#                     )

#                 # Age comparison
#                 st.markdown("#### Age Group")
#                 age_cols = [
#                     col for col in original_data.columns if col.startswith("age_cat_")
#                 ]

#                 for col in age_cols:
#                     age_group = col.replace("age_cat_", "")
#                     original_rate = original_data[original_data[col] == 1][
#                         "readmission"
#                     ].mean()
#                     modified_rate = modified_data[modified_data[col] == 1][
#                         "readmission"
#                     ].mean()

#                     comparison_data.append(
#                         {
#                             "Group Type": "Age",
#                             "Group": age_group,
#                             "Original Rate": original_rate,
#                             "Modified Rate": modified_rate,
#                             "Difference": modified_rate - original_rate,
#                         }
#                     )

#                 # Gender comparison
#                 st.markdown("#### Gender")
#                 gender_cols = [
#                     col for col in original_data.columns if col.startswith("gender_")
#                 ]

#                 for col in gender_cols:
#                     gender = col.replace("gender_", "")
#                     original_rate = original_data[original_data[col] == 1][
#                         "readmission"
#                     ].mean()
#                     modified_rate = modified_data[modified_data[col] == 1][
#                         "readmission"
#                     ].mean()

#                     comparison_data.append(
#                         {
#                             "Group Type": "Gender",
#                             "Group": gender,
#                             "Original Rate": original_rate,
#                             "Modified Rate": modified_rate,
#                             "Difference": modified_rate - original_rate,
#                         }
#                     )

#                 # Create a dataframe with the comparison data
#                 comparison_df = pd.DataFrame(comparison_data)

#                 # Visualization: Separate plots for each group type
#                 st.subheader("Comparison: Original vs Modified Rates")

#                 # Define helper locally for sorting age groups if needed
#                 def extract_age_local(col):
#                     if isinstance(col, str) and col.startswith(
#                         "age_cat_"
#                     ):  # Handle if column name is passed
#                         age_str = col.replace("age_cat_", "")
#                     elif isinstance(col, str):  # Handle if group name is passed
#                         age_str = col
#                     else:
#                         return 0  # Default case

#                     if "-" in age_str:
#                         return int(age_str.split("-")[0])
#                     if ">" in age_str:
#                         return int(age_str.split(">")[1])
#                     return 0

#                 group_types = comparison_df["Group Type"].unique()
#                 color_schemes = {
#                     "Ethnicity": px.colors.qualitative.Plotly,  # Using qualitative palette
#                     "Age": px.colors.sequential.Greens,
#                     "Gender": px.colors.sequential.Purples,
#                 }

#                 # Use more distinct colors for the two bars
#                 bar_colors = ["#1f77b4", "#ff7f0e"]  # Default Plotly blue and orange

#                 for group_type in group_types:
#                     st.markdown(f"#### {group_type}")
#                     df_group = comparison_df[comparison_df["Group Type"] == group_type]

#                     # Sort age and BMI groups if applicable
#                     if group_type == "Age":
#                         df_group["sort_key"] = df_group["Group"].apply(
#                             extract_age_local
#                         )
#                         df_group = df_group.sort_values("sort_key").drop(
#                             "sort_key", axis=1
#                         )
#                     # Add sorting for BMI if needed later

#                     fig = px.bar(
#                         df_group,
#                         x="Group",
#                         y=["Original Rate", "Modified Rate"],
#                         # Use fixed colors for Original vs Modified
#                         color_discrete_map={
#                             "Original Rate": bar_colors[0],
#                             "Modified Rate": bar_colors[1],
#                         },
#                         barmode="group",
#                         title=f"{group_type}: Original vs Modified Readmission Rates",
#                         labels={
#                             "value": "Readmission Rate",
#                             "variable": "Dataset",
#                             "Group": group_type,
#                         },
#                     )
#                     fig.update_layout(legend_title_text="Dataset")  # Add legend title
#                     st.plotly_chart(fig, use_container_width=True)

#                 # Train model on modified data
#                 st.subheader("Training Model on Modified Data")

#                 # Prepare modified data for modeling (ensure age_cat_0-9 is also dropped here if somehow missed earlier)
#                 cols_to_drop_model = ["readmission"]
#                 if "gender_M" in modified_data.columns:
#                     cols_to_drop_model.append("gender_M")
#                 if "ethnicity_Other/Unknown" in modified_data.columns:
#                     cols_to_drop_model.append("ethnicity_Other/Unknown")

#                 modified_data_model_ready = modified_data.drop(
#                     columns=list(set(cols_to_drop_model) & set(modified_data.columns))
#                 )
#                 X = modified_data_model_ready
#                 y = modified_data["readmission"]

#                 # Split data
#                 X_train, X_test, y_train, y_test = train_test_split(
#                     X, y, test_size=0.2, random_state=42
#                 )

#                 # Train model
#                 modified_model = RandomForestClassifier(
#                     n_estimators=100, random_state=42
#                 )
#                 modified_model.fit(X_train, y_train)

#                 # Save model
#                 joblib.dump(modified_model, "modified_rf_model.pkl")

#                 # Evaluate
#                 y_pred = modified_model.predict(X_test)
#                 y_pred_proba = modified_model.predict_proba(X_test)[:, 1]

#                 # Display metrics
#                 accuracy = accuracy_score(y_test, y_pred)
#                 auroc = roc_auc_score(y_test, y_pred_proba)

#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.metric("Accuracy", f"{accuracy:.2f}")
#                 with col2:
#                     st.metric("AUROC", f"{auroc:.2f}")

#                 # Fairness analysis on modified model
#                 st.subheader("Fairness Analysis on Modified Data")

#                 # Tabs for different sensitive attributes
#                 fairness_tab1, fairness_tab2, fairness_tab3 = st.tabs(
#                     ["Ethnicity Fairness", "Age Fairness", "Gender Fairness"]
#                 )

#                 # Function to analyze fairness for a given sensitive attribute
#                 def analyze_fairness(sensitive_attr, attribute_type, model, base_data):
#                     # Filter out 'Other/Unknown' ethnicity for Age/Gender analysis
#                     data_to_analyze = base_data.copy()
#                     if (
#                         attribute_type in ["Age", "Gender"]
#                         and "ethnicity_Other/Unknown" in data_to_analyze.columns
#                     ):
#                         st.info(
#                             f"Filtering out 'Other/Unknown' ethnicity for {attribute_type} analysis."
#                         )
#                         data_to_analyze = data_to_analyze[
#                             data_to_analyze["ethnicity_Other/Unknown"] == 0
#                         ]

#                     # Prepare data (drop potentially missing columns like gender_M, ethnicity_Other/Unknown for modeling)
#                     cols_to_drop = ["readmission"]
#                     if "gender_M" in data_to_analyze.columns:
#                         cols_to_drop.append("gender_M")
#                     # Note: ethnicity_Other/Unknown might already be filtered out above for Age/Gender
#                     if "ethnicity_Other/Unknown" in data_to_analyze.columns:
#                         cols_to_drop.append("ethnicity_Other/Unknown")

#                     # Ensure sensitive_attr exists after filtering and potential drops
#                     if sensitive_attr not in data_to_analyze.columns:
#                         st.warning(
#                             f"Sensitive attribute '{sensitive_attr}' not found in the data for analysis. Skipping."
#                         )
#                         return

#                     # Check if data is empty before preparing features
#                     if data_to_analyze.empty:
#                         st.warning(
#                             f"No data remaining for analysis after filtering for {attribute_type} and sensitive attribute {sensitive_attr}."
#                         )
#                         return

#                     # Check if sensitive attribute column exists before accessing
#                     if sensitive_attr not in data_to_analyze.columns:
#                         st.warning(
#                             f"Sensitive attribute column '{sensitive_attr}' does not exist in the dataframe being analyzed. Skipping."
#                         )
#                         return

#                     X = data_to_analyze.drop(
#                         columns=list(set(cols_to_drop) & set(data_to_analyze.columns))
#                     )  # Drop only existing columns
#                     y = data_to_analyze["readmission"]
#                     sensitive_features = data_to_analyze[sensitive_attr]

#                     # Check if data is empty after preparing features
#                     if X.empty or y.empty:
#                         st.warning(
#                             f"Feature set or target is empty after preparation for {attribute_type} and sensitive attribute {sensitive_attr}."
#                         )
#                         return

#                     # Split data
#                     try:
#                         # Use stratify if target has multiple classes
#                         stratify_target = y if y.nunique() > 1 else None
#                         (
#                             X_train,
#                             X_test,
#                             y_train,
#                             y_test,
#                             sensitive_train,
#                             sensitive_test,
#                         ) = train_test_split(
#                             X,
#                             y,
#                             sensitive_features,
#                             test_size=0.2,
#                             random_state=42,
#                             stratify=stratify_target,
#                         )
#                     except ValueError as e:
#                         st.warning(
#                             f"Could not split data for {sensitive_attr} (Attribute Type: {attribute_type}): {e}"
#                         )
#                         return

#                     # Check if split resulted in empty test set
#                     if X_test.empty or y_test.empty:
#                         st.warning(
#                             f"Test set is empty after splitting for {sensitive_attr}. Skipping fairness calculation."
#                         )
#                         return

#                     # Make predictions
#                     y_pred = model.predict(X_test)

#                     # Calculate bias metrics
#                     # Check if sensitive_test has variation needed for metrics
#                     if len(np.unique(sensitive_test)) < 2:
#                         st.warning(
#                             f"Sensitive attribute '{sensitive_attr}' has only one value in the test set. Fairness metrics are not meaningful."
#                         )
#                         dpd = np.nan
#                         eod = np.nan
#                     else:
#                         try:
#                             dpd = demographic_parity_difference(
#                                 y_test, y_pred, sensitive_features=sensitive_test
#                             )
#                             eod = equalized_odds_difference(
#                                 y_test, y_pred, sensitive_features=sensitive_test
#                             )
#                         except Exception as e:
#                             st.error(
#                                 f"Error calculating fairness metrics for {sensitive_attr}: {e}"
#                             )
#                             dpd, eod = np.nan, np.nan

#                     # Display metrics
#                     cols = st.columns(2)
#                     with cols[0]:
#                         st.metric(
#                             "Demographic Parity Difference",
#                             f"{dpd:.4f}" if not np.isnan(dpd) else "N/A",
#                             delta_color="inverse",
#                             help="Ideal value is 0. Higher values indicate more disparity in predictions between groups.",
#                         )
#                     with cols[1]:
#                         st.metric(
#                             "Equalized Odds Difference",
#                             f"{eod:.4f}" if not np.isnan(eod) else "N/A",
#                             delta_color="inverse",
#                             help="Ideal value is 0. Higher values indicate more disparity in error rates between groups.",
#                         )

#                     # Group-specific metrics
#                     group1_idx = sensitive_test == 1
#                     group0_idx = sensitive_test == 0

#                     # Check if both groups exist in the test set
#                     if group1_idx.sum() > 0 and group0_idx.sum() > 0:
#                         # Safely calculate group metrics
#                         def safe_division(numerator, denominator):
#                             return numerator / denominator if denominator > 0 else 0

#                         # Group 1 calculations
#                         y_test_g1 = y_test[group1_idx]
#                         y_pred_g1 = y_pred[group1_idx]
#                         acc_g1 = accuracy_score(y_test_g1, y_pred_g1)
#                         pr_g1 = y_pred_g1.mean()
#                         fpr_g1 = safe_division(
#                             np.sum((y_pred_g1 == 1) & (y_test_g1 == 0)),
#                             np.sum(y_test_g1 == 0),
#                         )
#                         fnr_g1 = safe_division(
#                             np.sum((y_pred_g1 == 0) & (y_test_g1 == 1)),
#                             np.sum(y_test_g1 == 1),
#                         )

#                         # Group 0 calculations
#                         y_test_g0 = y_test[group0_idx]
#                         y_pred_g0 = y_pred[group0_idx]
#                         acc_g0 = accuracy_score(y_test_g0, y_pred_g0)
#                         pr_g0 = y_pred_g0.mean()
#                         fpr_g0 = safe_division(
#                             np.sum((y_pred_g0 == 1) & (y_test_g0 == 0)),
#                             np.sum(y_test_g0 == 0),
#                         )
#                         fnr_g0 = safe_division(
#                             np.sum((y_pred_g0 == 0) & (y_test_g0 == 1)),
#                             np.sum(y_test_g0 == 1),
#                         )

#                         metrics = pd.DataFrame(
#                             {
#                                 "Metric": [
#                                     "Accuracy",
#                                     "Positive Rate",
#                                     "False Positive Rate",
#                                     "False Negative Rate",
#                                 ],
#                                 f"{sensitive_attr} = 1": [
#                                     acc_g1,
#                                     pr_g1,
#                                     fpr_g1,
#                                     fnr_g1,
#                                 ],
#                                 f"{sensitive_attr} = 0": [
#                                     acc_g0,
#                                     pr_g0,
#                                     fpr_g0,
#                                     fnr_g0,
#                                 ],
#                                 "Difference": [
#                                     abs(acc_g1 - acc_g0),
#                                     abs(pr_g1 - pr_g0),
#                                     abs(fpr_g1 - fpr_g0),
#                                     abs(fnr_g1 - fnr_g0),
#                                 ],
#                             }
#                         )

#                         # Format as percentages
#                         for col in metrics.columns[1:]:
#                             metrics[col] = metrics[col].apply(lambda x: f"{x:.2%}")

#                         st.dataframe(metrics)  # Keep the table for all types

#                         # --- PERFORMANCE METRIC PLOTS REMOVED FOR ALL TYPES ---
#                     else:
#                         st.warning(
#                             f"Not enough samples in one or both groups for {sensitive_attr} in the test set."
#                         )

#                 # Define column lists based on the modified_data dataframe
#                 ethnicity_cols_analysis = [
#                     col
#                     for col in modified_data.columns
#                     if col.startswith("ethnicity_") and col != "ethnicity_Other/Unknown"
#                 ]  # Exclude Other/Unknown ethnicity itself
#                 age_cols_analysis = [
#                     col for col in modified_data.columns if col.startswith("age_cat_")
#                 ]

#                 # Need extract_age function definition available here or redefine sorting key logic
#                 def extract_age_local(col):  # Define helper locally if needed
#                     age_str = col.replace("age_cat_", "")
#                     if "-" in age_str:
#                         return int(age_str.split("-")[0])
#                     if ">" in age_str:
#                         return int(age_str.split(">")[1])
#                     return 0

#                 age_cols_analysis_sorted = sorted(
#                     age_cols_analysis, key=extract_age_local
#                 )
#                 gender_cols_analysis = [
#                     col
#                     for col in modified_data.columns
#                     if col.startswith("gender_") and col != "gender_M"
#                 ]  # Exclude gender_M if it's dropped

#                 # Analyze fairness for ethnicities
#                 with fairness_tab1:
#                     if not ethnicity_cols_analysis:
#                         st.warning(
#                             "No ethnicity columns found for analysis in modified data."
#                         )
#                     for col in ethnicity_cols_analysis:
#                         ethnicity = col.replace("ethnicity_", "")
#                         st.markdown(f"#### {ethnicity}")
#                         analyze_fairness(
#                             col, "Ethnicity", modified_model, modified_data
#                         )  # Pass modified_data

#                 # Analyze fairness for age groups
#                 with fairness_tab2:
#                     if not age_cols_analysis_sorted:
#                         st.warning(
#                             "No age columns found for analysis in modified data."
#                         )
#                     for col in age_cols_analysis_sorted:
#                         age_group = col.replace("age_cat_", "")
#                         st.markdown(f"#### {age_group}")
#                         analyze_fairness(
#                             col, "Age", modified_model, modified_data
#                         )  # Pass modified_data

#                 # Analyze fairness for genders
#                 with fairness_tab3:
#                     if not gender_cols_analysis:
#                         st.warning(
#                             "No gender columns found for analysis in modified data."
#                         )
#                     for col in gender_cols_analysis:
#                         gender = col.replace("gender_", "")
#                         st.markdown(f"#### {gender}")
#                         analyze_fairness(
#                             col, "Gender", modified_model, modified_data
#                         )  # Pass modified_data

#                 # Add summary and interpretation
#                 st.markdown(
#                     """
#                 ## Interpretation of Fairness Metrics

#                 - **Demographic Parity Difference**: Measures if the prediction rates are equal across different demographic groups.
#                   - Lower values (closer to 0) indicate more fairness.

#                 - **Equalized Odds Difference**: Measures if error rates (both false positives and false negatives) are equal across groups.
#                   - Lower values indicate more fairness in how errors are distributed.

#                 By modifying the readmission rates for different demographic groups, you can observe how these changes affect model fairness.

#                 ### Tips for Exploration:

#                 1. Try increasing the disparity between groups to see how it affects fairness metrics.
#                 2. Try equalizing rates across all groups to see if it improves fairness.
#                 3. Observe which demographic attributes have the largest impact on fairness when modified.
#                 """
#                 )
#     else:
#         st.error(
#             "Data not available. Please check if the dataset file exists in the correct location."
#         )

# elif page == "Model Card":
#     st.header("Model Card: Hospital Readmission Prediction")

#     st.markdown(
#         """
#     This model card provides comprehensive information about the hospital readmission prediction model,
#     trained on the Women in Data Science (WiDS) dataset. The card follows best practices for transparency
#     in machine learning by documenting details about the model, its performance, fairness considerations,
#     and limitations.
#     """
#     )

#     # Ensure the original model and data are loaded
#     if original_rf is not None and original_data is not None:
#         # Create tabs for different sections of the model card
#         model_tab1, model_tab2, model_tab3, model_tab4, model_tab5 = st.tabs(
#             [
#                 "Model Details",
#                 "Dataset Analysis",
#                 "Quantitative Analysis",
#                 "Fairness Evaluation",
#                 "Limitations & Considerations",
#             ]
#         )

#         with model_tab1:
#             st.subheader("Model Specifications")

#             # Two columns for model details
#             col1, col2 = st.columns(2)

#             with col1:
#                 st.markdown(
#                     """
#                 ### Base Model
#                 - **Model Type:** Random Forest Classifier
#                 - **Implementation:** scikit-learn 1.0+
#                 - **Parameters:**
#                   - n_estimators: 100
#                   - criterion: gini
#                   - max_depth: None (unlimited)
#                   - min_samples_split: 2
#                   - min_samples_leaf: 1
#                   - random_state: 42

#                 ### Training Process
#                 - **Validation Strategy:** 80/20 train/test split
#                 - **Training Date:** March 2025
#                 - **Training Hardware:** CPU-based training
#                 """
#                 )

#             with col2:
#                 st.markdown(
#                     """
#                 ### Input Features
#                 - **Demographics:** Age, Gender, Ethnicity
#                 - **Clinical Measurements:** BMI, vital signs
#                 - **Medical History:** Prior conditions, interventions
#                 - **Hospital Metrics:** APACHE score, ICU type

#                 ### Output
#                 - **Target Variable:** Hospital Readmission (binary)
#                 - **Output Type:** Probability scores + binary classification
#                 - **Threshold:** 0.5 (default)
#                 """
#                 )

#             st.subheader("Intended Use")
#             st.markdown(
#                 """
#             - **Primary Use Case:** Predict hospital readmission risk for ICU patients
#             - **Intended Users:** Healthcare researchers, hospital administrators
#             - **Out-of-scope Uses:**
#               - Individual treatment decisions without clinical oversight
#               - Deployment in settings with different demographics than training data
#               - Risk scoring for insurance or coverage decisions
#             """
#             )

#         with model_tab2:
#             st.subheader("Dataset Analysis")

#             st.markdown(
#                 """
#             ### Data Source
#             The WiDS Datathon 2020 dataset includes de-identified data from hospital ICUs, with information
#             on demographics, vitals, lab values, medications, and outcomes.
#             """
#             )

#             # Dataset Demographics
#             st.subheader("Dataset Demographics")

#             # Create visualizations for demographics
#             col1, col2 = st.columns(2)

#             with col1:
#                 # Gender distribution
#                 gender_cols = [
#                     col for col in original_data.columns if col.startswith("gender_")
#                 ]
#                 gender_counts = {}

#                 for col in gender_cols:
#                     gender = col.replace("gender_", "")
#                     count = original_data[original_data[col] == 1].shape[0]
#                     gender_counts[gender] = count

#                 gender_df = pd.DataFrame(
#                     list(gender_counts.items()), columns=["Gender", "Count"]
#                 )

#                 fig = px.pie(
#                     gender_df,
#                     values="Count",
#                     names="Gender",
#                     title="Gender Distribution",
#                     color_discrete_sequence=px.colors.qualitative.Pastel,
#                 )
#                 st.plotly_chart(fig, use_container_width=True)

#             with col2:
#                 # Ethnicity distribution
#                 ethnicity_cols = [
#                     col for col in original_data.columns if col.startswith("ethnicity_")
#                 ]
#                 ethnicity_counts = {}

#                 for col in ethnicity_cols:
#                     ethnicity = col.replace("ethnicity_", "")
#                     count = original_data[original_data[col] == 1].shape[0]
#                     ethnicity_counts[ethnicity] = count

#                 ethnicity_df = pd.DataFrame(
#                     list(ethnicity_counts.items()), columns=["Ethnicity", "Count"]
#                 )

#                 fig = px.pie(
#                     ethnicity_df,
#                     values="Count",
#                     names="Ethnicity",
#                     title="Ethnicity Distribution",
#                     color_discrete_sequence=px.colors.qualitative.Pastel,
#                 )
#                 st.plotly_chart(fig, use_container_width=True)

#             # Age distribution
#             st.subheader("Age Distribution")
#             age_cols = [
#                 col for col in original_data.columns if col.startswith("age_cat_")
#             ]
#             age_counts = {}

#             for col in age_cols:
#                 age_group = col.replace("age_cat_", "")
#                 count = original_data[original_data[col] == 1].shape[0]
#                 age_counts[age_group] = count

#             age_df = pd.DataFrame(
#                 list(age_counts.items()), columns=["Age Group", "Count"]
#             )

#             # Sort age groups properly
#             def extract_age(age_str):
#                 if "-" in age_str:
#                     return int(age_str.split("-")[0])
#                 elif ">" in age_str:
#                     return int(age_str.split(">")[1])
#                 else:
#                     return 0

#             age_df["sort_key"] = age_df["Age Group"].apply(extract_age)
#             age_df = age_df.sort_values("sort_key").drop("sort_key", axis=1)

#             fig = px.bar(
#                 age_df,
#                 x="Age Group",
#                 y="Count",
#                 title="Age Distribution",
#                 color="Count",
#                 color_continuous_scale="blues",
#             )
#             st.plotly_chart(fig, use_container_width=True)

#             # Target distribution
#             st.subheader("Target Variable: Hospital Readmission")

#             readmission_counts = (
#                 original_data["readmission"].value_counts().reset_index()
#             )
#             readmission_counts.columns = ["Readmission", "Count"]
#             readmission_counts["Readmission"] = readmission_counts["Readmission"].map(
#                 {0: "No Readmission", 1: "Readmission"}
#             )

#             fig = px.pie(
#                 readmission_counts,
#                 values="Count",
#                 names="Readmission",
#                 title="Readmission Distribution",
#                 color_discrete_sequence=["#2ECC71", "#E74C3C"],
#             )
#             st.plotly_chart(fig, use_container_width=True)

#         with model_tab3:
#             st.subheader("Quantitative Analysis")

#             sensitive_attr = "ethnicity_African American"

#             # Calculate metrics for the original model
#             try:
#                 orig_acc, orig_auroc, orig_dpd, orig_eod = calculate_metrics(
#                     original_rf, original_data, sensitive_attr
#                 )
#             except Exception as e:
#                 st.error(f"Error calculating metrics: {e}")
#                 orig_acc, orig_auroc, orig_dpd, orig_eod = [np.nan] * 4

#             # Overall model performance metrics
#             st.markdown("### Performance Metrics")

#             col1, col2 = st.columns(2)

#             with col1:
#                 st.metric(
#                     "Accuracy", f"{orig_acc:.3f}" if not np.isnan(orig_acc) else "N/A"
#                 )
#                 st.markdown(
#                     """
#                 **Accuracy** is the proportion of correct predictions (both true positives and true negatives)
#                 among the total number of predictions.
#                 """
#                 )

#             with col2:
#                 st.metric(
#                     "AUROC", f"{orig_auroc:.3f}" if not np.isnan(orig_auroc) else "N/A"
#                 )
#                 st.markdown(
#                     """
#                 **Area Under ROC Curve (AUROC)** measures the model's ability to discriminate between positive
#                 and negative classes. Values close to 1 indicate better discrimination.
#                 """
#                 )

#             # Feature importance
#             st.subheader("Feature Importance")

#             if hasattr(original_rf, "feature_names_in_") and hasattr(
#                 original_rf, "feature_importances_"
#             ):
#                 # Get feature importances
#                 feature_importance = pd.DataFrame(
#                     {
#                         "Feature": original_rf.feature_names_in_,
#                         "Importance": original_rf.feature_importances_,
#                     }
#                 ).sort_values("Importance", ascending=False)

#                 # Display top 15 features
#                 top_features = feature_importance.head(15)

#                 fig = px.bar(
#                     top_features,
#                     x="Importance",
#                     y="Feature",
#                     orientation="h",
#                     title="Top 15 Feature Importances",
#                     color="Importance",
#                     color_continuous_scale="viridis",
#                 )
#                 fig.update_layout(yaxis={"categoryorder": "total ascending"})
#                 st.plotly_chart(fig, use_container_width=True)

#                 st.markdown(
#                     """
#                 **Feature importance** indicates how useful each feature was in building the random forest model.
#                 Higher importance suggests the feature had a greater impact on predictions.
#                 """
#                 )
#             else:
#                 st.warning("Feature importance information not available in the model.")

#             # Confusion Matrix
#             st.subheader("Confusion Matrix")

#             # Get a subset of data for confusion matrix visualization
#             X_subset = original_data.drop(columns=["readmission"])
#             if "gender_M" in X_subset.columns:
#                 X_subset = X_subset.drop(columns=["gender_M"])
#             if "ethnicity_Other/Unknown" in X_subset.columns:
#                 X_subset = X_subset.drop(columns=["ethnicity_Other/Unknown"])

#             y_subset = original_data["readmission"]

#             # Split the data
#             X_train, X_test, y_train, y_test = train_test_split(
#                 X_subset, y_subset, test_size=0.2, random_state=42
#             )

#             # Ensure feature alignment
#             if hasattr(original_rf, "feature_names_in_"):
#                 X_test_aligned = X_test.reindex(
#                     columns=original_rf.feature_names_in_, fill_value=0
#                 )
#             else:
#                 X_test_aligned = X_test

#             # Make predictions
#             try:
#                 y_pred = original_rf.predict(X_test_aligned)

#                 # Create confusion matrix
#                 cm = confusion_matrix(y_test, y_pred)

#                 # Normalize confusion matrix
#                 cm_normalized = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

#                 # Create heatmap with plotly
#                 labels = ["No Readmission", "Readmission"]

#                 # Create annotation text
#                 annotations = [
#                     [
#                         f"{cm[i, j]}<br>({cm_normalized[i, j]:.1%})"
#                         for j in range(len(cm[i]))
#                     ]
#                     for i in range(len(cm))
#                 ]

#                 fig = go.Figure(
#                     data=go.Heatmap(
#                         z=cm, x=labels, y=labels, colorscale="blues", showscale=False
#                     )
#                 )

#                 # Add annotations
#                 for i in range(len(cm)):
#                     for j in range(len(cm[i])):
#                         fig.add_annotation(
#                             x=labels[j],
#                             y=labels[i],
#                             text=annotations[i][j],
#                             showarrow=False,
#                             font=dict(
#                                 color="white" if cm[i, j] > cm.max() / 2 else "black"
#                             ),
#                         )

#                 fig.update_layout(
#                     title="Confusion Matrix",
#                     xaxis_title="Predicted",
#                     yaxis_title="Actual",
#                     xaxis=dict(side="top"),
#                 )
#                 st.plotly_chart(fig, use_container_width=True)

#                 # Explanation
#                 st.markdown(
#                     """
#                 The **confusion matrix** shows:
#                 - **True Negatives (top-left)**: Correctly predicted no readmission
#                 - **False Positives (top-right)**: Incorrectly predicted readmission
#                 - **False Negatives (bottom-left)**: Incorrectly predicted no readmission
#                 - **True Positives (bottom-right)**: Correctly predicted readmission

#                 Each cell shows the count and percentage of the actual class.
#                 """
#                 )
#             except Exception as e:
#                 st.error(f"Error generating confusion matrix: {e}")

#         with model_tab4:
#             st.subheader("Fairness Evaluation")

#             st.markdown(
#                 """
#             ### Fairness Metrics

#             We evaluate the model's fairness across different demographic groups. The fairness metrics help identify
#             if the model exhibits biased behavior toward certain populations.
#             """
#             )

#             # Define the key sensitive attributes to analyze
#             sensitive_attrs = {
#                 "ethnicity_African American": "African American",
#                 "ethnicity_Caucasian": "Caucasian",
#                 "gender_F": "Female",
#             }

#             # Create a fairness metrics comparison
#             fairness_data = []

#             for attr_col, attr_name in sensitive_attrs.items():
#                 try:
#                     _, _, dpd, eod = calculate_metrics(
#                         original_rf, original_data, attr_col
#                     )

#                     fairness_data.append(
#                         {
#                             "Sensitive Attribute": attr_name,
#                             "Demographic Parity Difference": (
#                                 dpd if not np.isnan(dpd) else 0
#                             ),
#                             "Equalized Odds Difference": (
#                                 eod if not np.isnan(eod) else 0
#                             ),
#                         }
#                     )
#                 except Exception as e:
#                     st.error(f"Error calculating fairness metrics for {attr_name}: {e}")

#             if fairness_data:
#                 fairness_df = pd.DataFrame(fairness_data)

#                 # Create DPD chart
#                 fig1 = px.bar(
#                     fairness_df,
#                     x="Sensitive Attribute",
#                     y="Demographic Parity Difference",
#                     title="Demographic Parity Difference by Group",
#                     color="Demographic Parity Difference",
#                     color_continuous_scale="RdBu_r",
#                     range_color=[
#                         0,
#                         fairness_df["Demographic Parity Difference"].max() * 1.1,
#                     ],
#                 )
#                 fig1.update_layout(yaxis_title="DPD (Lower is better)")
#                 st.plotly_chart(fig1, use_container_width=True)

#                 # Create EOD chart
#                 fig2 = px.bar(
#                     fairness_df,
#                     x="Sensitive Attribute",
#                     y="Equalized Odds Difference",
#                     title="Equalized Odds Difference by Group",
#                     color="Equalized Odds Difference",
#                     color_continuous_scale="RdBu_r",
#                     range_color=[
#                         0,
#                         fairness_df["Equalized Odds Difference"].max() * 1.1,
#                     ],
#                 )
#                 fig2.update_layout(yaxis_title="EOD (Lower is better)")
#                 st.plotly_chart(fig2, use_container_width=True)
#             else:
#                 st.warning("Could not calculate fairness metrics for comparison.")

#             st.markdown(
#                 """
#             ### Fairness Metrics Explained

#             - **Demographic Parity Difference (DPD)**: Measures the difference in prediction rates between the sensitive group and others. Ideal value is 0.

#             - **Equalized Odds Difference (EOD)**: Measures the maximum difference in false positive rates and true positive rates between groups. Ideal value is 0.

#             Higher values indicate more disparity between groups and potential unfairness in the model.
#             """
#             )

#             # Prediction rate comparison across demographic groups
#             st.subheader("Prediction Rates by Demographic Group")

#             # Get predictions for different demographic groups
#             try:
#                 # Prepare features
#                 X = original_data.drop(columns=["readmission"])
#                 if "gender_M" in X.columns:
#                     X = X.drop(columns=["gender_M"])
#                 if "ethnicity_Other/Unknown" in X.columns:
#                     X = X.drop(columns=["ethnicity_Other/Unknown"])

#                 # Ensure feature alignment
#                 if hasattr(original_rf, "feature_names_in_"):
#                     X_aligned = X.reindex(
#                         columns=original_rf.feature_names_in_, fill_value=0
#                     )
#                 else:
#                     X_aligned = X

#                 # Make predictions
#                 y_pred = original_rf.predict(X_aligned)

#                 # Calculate prediction rates for different groups
#                 prediction_rates = []

#                 # For ethnicities
#                 ethnicity_cols = [
#                     col for col in original_data.columns if col.startswith("ethnicity_")
#                 ]
#                 for col in ethnicity_cols:
#                     ethnicity = col.replace("ethnicity_", "")
#                     group_mask = original_data[col] == 1
#                     if group_mask.sum() > 0:  # Ensure group has members
#                         pred_rate = y_pred[group_mask].mean()
#                         actual_rate = original_data.loc[
#                             group_mask, "readmission"
#                         ].mean()

#                         prediction_rates.append(
#                             {
#                                 "Group Type": "Ethnicity",
#                                 "Group": ethnicity,
#                                 "Predicted Rate": pred_rate,
#                                 "Actual Rate": actual_rate,
#                                 "Difference": pred_rate - actual_rate,
#                             }
#                         )

#                 # For genders
#                 gender_cols = [
#                     col for col in original_data.columns if col.startswith("gender_")
#                 ]
#                 for col in gender_cols:
#                     gender = col.replace("gender_", "")
#                     group_mask = original_data[col] == 1
#                     if group_mask.sum() > 0:  # Ensure group has members
#                         pred_rate = y_pred[group_mask].mean()
#                         actual_rate = original_data.loc[
#                             group_mask, "readmission"
#                         ].mean()

#                         prediction_rates.append(
#                             {
#                                 "Group Type": "Gender",
#                                 "Group": gender,
#                                 "Predicted Rate": pred_rate,
#                                 "Actual Rate": actual_rate,
#                                 "Difference": pred_rate - actual_rate,
#                             }
#                         )

#                 # Convert to DataFrame
#                 pred_rate_df = pd.DataFrame(prediction_rates)

#                 # Create visualization
#                 for group_type in pred_rate_df["Group Type"].unique():
#                     group_data = pred_rate_df[pred_rate_df["Group Type"] == group_type]

#                     fig = go.Figure()

#                     # Add bars for predicted rates
#                     fig.add_trace(
#                         go.Bar(
#                             x=group_data["Group"],
#                             y=group_data["Predicted Rate"],
#                             name="Predicted Rate",
#                             marker_color="royalblue",
#                         )
#                     )

#                     # Add bars for actual rates
#                     fig.add_trace(
#                         go.Bar(
#                             x=group_data["Group"],
#                             y=group_data["Actual Rate"],
#                             name="Actual Rate",
#                             marker_color="lightcoral",
#                         )
#                     )

#                     fig.update_layout(
#                         title=f"Predicted vs. Actual Readmission Rates by {group_type}",
#                         xaxis_title=group_type,
#                         yaxis_title="Rate",
#                         barmode="group",
#                         yaxis=dict(
#                             range=[
#                                 0,
#                                 max(
#                                     group_data["Predicted Rate"].max(),
#                                     group_data["Actual Rate"].max(),
#                                 )
#                                 * 1.1,
#                             ]
#                         ),
#                     )

#                     st.plotly_chart(fig, use_container_width=True)

#                 st.markdown(
#                     """
#                 These charts compare the predicted readmission rates with the actual rates for different demographic groups.
#                 Significant differences between predicted and actual rates for specific groups may indicate biased model behavior.
#                 """
#                 )
#             except Exception as e:
#                 st.error(f"Error generating prediction rate comparison: {e}")

#         with model_tab5:
#             st.subheader("Limitations & Ethical Considerations")

#             st.markdown(
#                 """
#             ### Known Limitations

#             - **Data Representativeness**: The WiDS dataset may not be representative of all hospital populations globally.

#             - **Feature Coverage**: The model uses a subset of available features and may not capture all relevant factors for readmission.

#             - **Temporal Validity**: Healthcare practices and patient demographics change over time, potentially limiting the model's future validity.

#             - **Causality**: The model identifies correlations but does not establish causal relationships.

#             ### Ethical Considerations

#             - **Fairness Across Groups**: While we've measured fairness metrics, using this model in production requires ongoing monitoring for bias.

#             - **Human Oversight**: This model should supplement, not replace, clinical judgment.

#             - **Transparency**: Decision-makers should understand how model predictions are generated and their limitations.

#             - **Privacy**: All deployments must ensure patient data privacy and comply with relevant regulations (e.g., HIPAA).

#             ### Recommendations for Use

#             - **Monitoring**: Regularly evaluate the model's performance and fairness on new data.

#             - **Feedback Loop**: Establish a process to incorporate feedback from healthcare providers.

#             - **Threshold Adjustment**: Consider adjusting decision thresholds to balance performance across different groups.

#             - **Domain Expertise**: Involve healthcare professionals in interpretation and application of the model's predictions.
#             """
#             )

#             st.info(
#                 "This model card follows recommendations from the [Model Cards for Model Reporting paper](https://arxiv.org/abs/1810.03993) (Mitchell et al., 2019)."
#             )

#     else:
#         st.warning(
#             "Original model or data could not be loaded. Cannot display Model Card details."
#         )
#         st.warning(
#             "Please ensure 'data_clean_v2.csv' and 'original_data_random_forest_model.pkl' exist."
#         )
