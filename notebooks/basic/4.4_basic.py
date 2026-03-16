import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

# --- PAGE CONFIGURATION & ACCESSIBILITY ---
st.set_page_config(page_title="Choosing the Right Biomedical Deep Learning (DL) Model", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    file_path = "data/diabetes.csv"
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        return None

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Module Navigation")

st.sidebar.info("Instructions: Please use this sidebar menu below to navigate through the different phases of Activity 4. Complete each section in order before answering the final question in your Canvas submission area.")

scientific_context = st.sidebar.radio(
    "Select Learning Context:",
    ["Clinical (Patient Care)", "Foundational (Algorithmic & Basic Science)"],
    help="Toggle the interface terminology to match your specific track."
)
st.sidebar.markdown("---")

mode = st.sidebar.radio(
    "Activity 4 Phases:",
    [
        "Phase 1: Data Preprocessing", 
        "Phase 2: Model Training Structure", 
        "Phase 3: Cross-Validation & Results"
    ],
    help="Navigate through the sequential phases of Activity 4, mirroring the code cells in your Jupyter Notebook."
)

df = load_data()

# ==========================================
# PHASE 1: DATA PREPROCESSING
# ==========================================
if mode == "Phase 1: Data Preprocessing":
    st.title("Activity 4: Choosing the Right Biomedical Deep Learning Model")
    st.header("Phase 1: Data Preprocessing")
    
    with st.expander("Notebook Instructions", expanded=True):
        st.write("""
        **Notebook Directives:**
        * Complete each activity in order. Record your responses only in your Canvas submission area.
        * Open the sidebar to select the next phase in the activity.
        * **Clinical Scenario:** You are part of a hospital's clinical analytics team using a CNN model to predict in-hospital mortality.
        * **Task:** Preprocess the data before running the model.
        """)
        
    st.markdown("---")
    
    st.subheader("StandardScaler Transformation")
    st.write("In the notebook, the data is passed through `StandardScaler()` to center the mean at 0 and scale the standard deviation to 1. Toggle the scaler below to see why this is a necessary preprocessing step.")
    
    if df is not None:
        feature_cols = df.columns[:-1].tolist()
        raw_row = df.iloc[0, :-1].values
        
        apply_scaler = st.toggle(
            "Apply StandardScaler()", 
            value=False,
            help="Simulates the fit_transform() function from sklearn. This forces all features to share the same numerical scale."
        )
        
        if apply_scaler:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(df.iloc[:, :-1])
            display_data = scaled_features[0]
            st.success("Data Normalized: Notice how the massive numerical difference between 'Glucose' and 'DiabetesPedigreeFunction' has been eliminated. This prevents large numbers from artificially dominating the neural network's weights.")
        else:
            display_data = raw_row
            st.warning("Raw Data: Feeding this directly into a CNN causes the model to over-value 'Glucose' simply because the raw integer is larger than the others.")
            
        df_visual = pd.DataFrame([display_data], columns=feature_cols, index=["Patient X (Row 0)"])
        st.dataframe(df_visual.style.format("{:.3f}"), use_container_width=True)
        
        st.markdown("---")
        st.subheader("The 1D Sliding Kernel")
        st.write("After preprocessing and reshaping the input to a 1D vector, the Conv1D layer slides a kernel (size=3) across the features.")
        
        current_step = st.slider(
            "Slide the Conv1D Filter (Time Step)", 
            min_value=1, 
            max_value=len(feature_cols) - 2, 
            value=1,
            help="Move the slider to manually shift the 1D convolution filter across the array. This mimics how the Conv1D layer processes sequences."
        )
        
        display_html = "<div style='display:flex; gap:5px; flex-wrap:wrap;'>"
        for i, feat in enumerate(feature_cols):
            val = display_data[i]
            if current_step - 1 <= i < current_step - 1 + 3:
                display_html += f"<div style='background-color:#1E88E5; color:#FFFFFF; padding:10px; border-radius:5px; font-weight:bold; text-align:center;' aria-label='Active feature {feat}'>{feat}<br>{val:.2f}</div>"
            else:
                display_html += f"<div style='background-color:#E0E0E0; color:#000000; padding:10px; border-radius:5px; text-align:center;' aria-label='Inactive feature {feat}'>{feat}<br>{val:.2f}</div>"
        display_html += "</div>"
        
        st.markdown(display_html, unsafe_allow_html=True)
        st.caption("Text Description: The dark blue boxes represent the 3 adjacent features currently being multiplied by the kernel's weights to extract a latent pattern. The light gray boxes are currently inactive.")

    else:
        st.error("Dataset not found. Please ensure that 'diabetes.csv' is uploaded to a folder named 'data' inside your repository.")

# ==========================================
# PHASE 2: MODEL TRAINING STRUCTURE
# ==========================================
elif mode == "Phase 2: Model Training Structure":
    st.title("Activity 4: Choosing the Right Biomedical Deep Learning Model")
    st.header("Phase 2: Model Training Structure")
    
    with st.expander("Notebook Interpretation", expanded=True):
        st.write("""
        **Notebook Directives:**
        * Complete each activity in order. Record your responses only in your Canvas submission area.
        * Open the sidebar to select the next phase in the activity.
        * **Notebook Interpretation:**
          * There are 7 layers (1 input layer, 5 hidden layers, and 1 output layer) in the CNN model.
          * The first and second hidden layers learn the latent factors from the data using 32 and 64 nodes.
          * The Dropout layer randomly drops 30 percent of neurons during training, preventing overfitting.
        """)
        
    st.subheader("Model Architecture Breakdown")
    
    st.code("""
    model = Sequential([
        Input(shape=(X_train.shape[1], 1)),   # Input layer
        Conv1D(32, kernel_size=3, activation='relu'),
        Conv1D(64, kernel_size=3, activation='relu'),
        Flatten(),                            # Converts feature maps to 1-D vector
        Dense(32, activation='relu'),
        Dropout(0.3),                         # Prevents overfitting
        Dense(1, activation='sigmoid')        # Output layer for binary classification
    ])
    """, language="python")
    
    st.markdown("---")
    st.subheader("Interactive Mechanics: The Dropout Regularizer")
    st.write("In the Dense layer, the notebook applies `Dropout(0.3)`. This randomly turns off 30 percent of the neurons during training so the model does not become overly reliant on any single feature pathway.")
    
    dropout_rate = st.slider(
        "Adjust Dropout Rate", 
        min_value=0.0, 
        max_value=0.9, 
        value=0.3, 
        step=0.1,
        help="0.0 means all neurons are active. 0.9 means 90 percent of the network is deactivated during a training step. In Notebook 4, this is set to 0.3."
    )
    
    st.write(f"**Simulating 32 Neurons in the Dense Layer (Dropout = {dropout_rate*100:.0f} percent)**")
    
    np.random.seed(42) 
    neurons = np.ones(32)
    drop_indices = np.random.choice(32, int(32 * dropout_rate), replace=False)
    neurons[drop_indices] = 0
    
    neuron_html = "<div style='display:flex; gap:10px; flex-wrap:wrap; width: 80%;'>"
    active_count = 0
    for n in neurons:
        if n == 1:
            neuron_html += "<div style='background-color:#4CAF50; width:30px; height:30px; border-radius:15px;' title='Active Neuron' aria-label='Active Neuron'></div>"
            active_count += 1
        else:
            neuron_html += "<div style='background-color:#757575; width:30px; height:30px; border-radius:15px;' title='Dropped Neuron' aria-label='Deactivated Neuron'></div>"
    neuron_html += "</div>"
    
    st.markdown(neuron_html, unsafe_allow_html=True)
    st.caption(f"Text Description: Out of 32 total neurons, {active_count} are active (solid green) and {32-active_count} are temporarily deactivated (solid gray) for this specific training epoch.")

# ==========================================
# PHASE 3: CROSS-VALIDATION & RESULTS
# ==========================================
elif mode == "Phase 3: Cross-Validation & Results":
    st.title("Activity 4: Choosing the Right Biomedical Deep Learning Model")
    st.header("Phase 3: Cross-Validation & Results")
    
    with st.expander("Notebook Instructions", expanded=True):
        st.write("""
        **Notebook Directives:**
        * Complete each activity in order. Record your responses only in your Canvas submission area.
        * Open the sidebar to select the next phase in the activity.
        * **5-fold cross validation:** Split the data into 5 unoverlapped datasets. Instead of training on one dataset once, train and test the model five times, each time using a different part of the data as the test set.
        * **Question:** How is the performance? Is it better than the DNN that we used in Notebook 2? Why? (Record your response in Canvas).
        """)
        
    st.markdown("---")
    
    fold_data = {
        "Fold 1": {"Acc": 0.695, "Sens": 0.636, "Spec": 0.727, "Prec": 0.565},
        "Fold 2": {"Acc": 0.779, "Sens": 0.681, "Spec": 0.822, "Prec": 0.627},
        "Fold 3": {"Acc": 0.708, "Sens": 0.443, "Spec": 0.882, "Prec": 0.711},
        "Fold 4": {"Acc": 0.765, "Sens": 0.660, "Spec": 0.811, "Prec": 0.608},
        "Fold 5": {"Acc": 0.765, "Sens": 0.569, "Spec": 0.884, "Prec": 0.750}
    }
    
    st.subheader("Notebook Output Analysis")
    selected_fold = st.selectbox(
        "Select a Training Fold to View Results:", 
        ["Average (Final Output)"] + list(fold_data.keys()),
        help="Toggle between the evaluation scores of specific folds, or view the overall averaged performance."
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    if selected_fold == "Average (Final Output)":
        st.info("These are the final averaged metrics across all 5 folds, exactly as printed at the end of Activity 4.")
        acc = 0.742
        sens = 0.598
        spec = 0.825
        prec = 0.652
    else:
        st.info(f"Displaying evaluation metrics isolated to the 20 percent validation data used in {selected_fold}.")
        acc = fold_data[selected_fold]["Acc"]
        sens = fold_data[selected_fold]["Sens"]
        spec = fold_data[selected_fold]["Spec"]
        prec = fold_data[selected_fold]["Prec"]
        
    col1.metric("Accuracy", f"{acc:.3f}", help="The overall percentage of correct predictions.")
    col2.metric("Sensitivity", f"{sens:.3f}", help="The ability of the model to correctly identify positive disease cases.")
    col3.metric("Specificity", f"{spec:.3f}", help="The ability of the model to correctly identify negative cases.")
    col4.metric("Precision", f"{prec:.3f}", help="When the model predicts a positive case, this is how often it is actually correct.")
    
    st.markdown("---")
    st.subheader("Interactive Diagnosis: Evaluating Performance")
    st.write("To answer the final notebook question, notice that the **Average Sensitivity is 0.598**. This means the model is missing approximately 40 percent of the positive cases.")
    
    st.write("In the notebook, the prediction threshold is hardcoded to `0.5` (`y_pred_prob > 0.5`). Adjust the threshold slider below to simulate how performance shifts when prioritizing Sensitivity.")
    
    threshold = st.slider(
        "Prediction Probability Threshold", 
        min_value=0.1, 
        max_value=0.9, 
        value=0.5, 
        step=0.1,
        help="The cutoff point. If the model is more than X percent confident, it predicts a positive case."
    )
    
    sim_sens = max(0.1, 0.598 + ((0.5 - threshold) * 0.8))
    sim_spec = max(0.1, 0.825 - ((0.5 - threshold) * 0.5))
    
    bar_df = pd.DataFrame({
        "Metric": ["Sensitivity", "Specificity"],
        "Score": [sim_sens, sim_spec]
    })
    st.bar_chart(bar_df.set_index("Metric"), y="Score")
    st.caption("Text Description: A bar chart displaying the trade-off between Sensitivity and Specificity based on the selected probability threshold.")
    
    if threshold < 0.5:
        st.success(f"By lowering the threshold to {threshold}, Sensitivity improves to approximately {sim_sens:.2f}. The model catches more cases, but at the cost of more False Positives.")
    elif threshold > 0.5:
        st.error(f"By raising the threshold to {threshold}, Sensitivity drops to approximately {sim_sens:.2f}. The model becomes overly conservative and misses even more cases.")
