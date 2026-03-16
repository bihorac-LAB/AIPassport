import streamlit as st
import pandas as pd
import random
from faker import Faker
from datetime import datetime

# ------------------------------
# Page Configuration & Instructions
# ------------------------------
st.set_page_config(page_title="OMOP ETL Simulator", layout="wide")

st.title("Clinical Data Simulation: EHR to OMOP CDM")

with st.expander("How to use this app & Educational Context"):
    st.markdown("""
    ### Project Goal
    This app demonstrates the **ETL (Extract, Transform, Load)** process of moving raw EHR data into the **OMOP Common Data Model (CDM)**.
    
    1. **Step 1: Raw Data Generation**: We use the `Faker` library to create synthetic patients.
    2. **Step 2: Person Mapping**: We map source values (like 'Male') to standardized **Concept IDs** (like `8507`).
    3. **Step 3: Condition Simulation**: We map ICD-10 codes to OMOP Standard Concepts for conditions.
    
    *Source: [OHDSI OMOP CDM Documentation](https://www.ohdsi.org/web/wiki/doku.php?id=documentation:cdm:person)*
    """)

# ------------------------------
# Sidebar - Interactivity & Instructions
# ------------------------------
st.sidebar.header("Simulation Settings")
st.sidebar.info("Adjust the parameters below to re-generate the synthetic cohort.")

num_patients = st.sidebar.slider(
    "Number of patients", 
    min_value=5, 
    max_value=100, 
    value=10,
    help="Determines how many unique patient rows are generated in the source data and person table."
)

seed_value = st.sidebar.number_input(
    "Random Seed", 
    value=123,
    help="Ensures reproducibility. Using 123 matches the original notebook's output."
)

# Initialize Faker with seed
fake = Faker()
Faker.seed(seed_value)
random.seed(seed_value)

# ------------------------------
# Step 1: Generate Fake Patients
# ------------------------------
def generate_fake_patients(n):
    races = ['White', 'Black', 'Asian', 'Other']
    ethnicities = ['Not Hispanic or Latino', 'Hispanic or Latino']
    data = []
    for i in range(n):
        gender = random.choice(['Male', 'Female'])
        data.append({
            "person_source_value": fake.unique.uuid4(),
            "full_name": fake.name_male() if gender == 'Male' else fake.name_female(),
            "gender": gender,
            "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=90),
            "address": fake.address(),
            "race": random.choice(races),
            "ethnicity": random.choice(ethnicities)
        })
    df = pd.DataFrame(data)
    df["birthdate"] = pd.to_datetime(df["birthdate"])
    return df

original_data = generate_fake_patients(num_patients)

st.header("Step 1: Raw Source Data")
st.markdown("This represents messy, non-standardized data exported from a hospital's local database.")
st.dataframe(original_data, use_container_width=True)

# ------------------------------
# Step 2: Mapping & Person Table
# ------------------------------
def map_gender(gender):
    return {'Male': 8507, 'Female': 8532}.get(gender, 0)

def map_race(race):
    return {'White': 8527, 'Black': 8516, 'Asian': 8515, 'Other': 8529}.get(race, 0)

def map_ethnicity(ethnicity):
    return {'Not Hispanic or Latino': 38070399, 'Hispanic or Latino': 38003563}.get(ethnicity, 0)

def convert_to_omop_person(df):
    return pd.DataFrame({
        "person_id": range(1, len(df) + 1),
        "gender_concept_id": df["gender"].map(map_gender),
        "year_of_birth": df["birthdate"].dt.year,
        "month_of_birth": df["birthdate"].dt.month,
        "day_of_birth": df["birthdate"].dt.day,
        "birth_datetime": df["birthdate"],
        "race_concept_id": df["race"].map(map_race),
        "ethnicity_concept_id": df["ethnicity"].map(map_ethnicity),
        "person_source_value": df["person_source_value"],
        "gender_source_value": df["gender"],
        "race_source_value": df["race"],
        "ethnicity_source_value": df["ethnicity"]
    })

omop_person = convert_to_omop_person(original_data)

st.header("Step 2: Standardized OMOP Person Table")
st.markdown("Notice how names and addresses are removed, and demographics are replaced with **Concept IDs**.")

# Interactive Tooltip simulation for columns
st.info("**Pro-tip:** Hover over the table to see data, or check the 'Concept Map' below.")
st.dataframe(omop_person, use_container_width=True)

# ------------------------------
# Step 3: Condition Occurrence
# ------------------------------
st.header("Step 3: Condition Occurrence")
st.markdown("We simulate diagnoses by mapping ICD-10 source codes to OMOP Standard Concepts.")

icd_to_omop = {"E11.9": 201826, "I10": 320128, "J45.909": 317009, "F32.9": 440383}

def generate_full_condition_occurrence(person_df):
    conditions = []
    icd_codes = list(icd_to_omop.keys())
    for i, person in person_df.iterrows():
        for _ in range(random.randint(1, 3)):
            icd = random.choice(icd_codes)
            start_date = fake.date_between(start_date='-5y', end_date='-6m')
            conditions.append({
                "condition_occurrence_id": len(conditions) + 1,
                "person_id": person['person_id'],
                "condition_concept_id": icd_to_omop[icd],
                "condition_start_date": start_date,
                "condition_type_concept_id": 32020, # EHR Problem List
                "condition_source_value": icd
            })
    return pd.DataFrame(conditions)

condition_occurrence = generate_full_condition_occurrence(omop_person)
st.dataframe(condition_occurrence, use_container_width=True)

# ------------------------------
# Discussion Section (From Notebook)
# ------------------------------
st.divider()
st.header("Knowledge Check")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Why use Concept IDs?")
    st.write("Concept IDs allow researchers to run the same query across different hospitals, even if one uses ICD-10 and another uses SNOMED.")

with col2:
    st.markdown("### ETL Challenges")
    st.write("In the real world, source data is often 'messy' (e.g., misspelled genders or missing birthdates), requiring significant cleaning before mapping.")
