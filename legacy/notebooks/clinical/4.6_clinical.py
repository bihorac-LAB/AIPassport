import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split, KFold, cross_val_score, StratifiedKFold, LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.utils import resample
from sklearn.datasets import make_classification


def render_plotly_chart(fig, height=520):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


@st.cache_data
def load_clinical_data():
    local_path = "assets/datasets/csv/eicu_demo.csv"
    if os.path.exists(local_path):
        df = pd.read_csv(local_path)
        if "weight" in df.columns and "weight_admission" not in df.columns:
            df = df.rename(columns={"weight": "weight_admission"})
        num_feats = ["age", "lab_glucose", "lab_creatinine", "lab_potassium"]
        for col in num_feats:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df[num_feats] = df[num_feats].fillna(df[num_feats].mean())
        df = df.dropna(subset=["in_hospital_mortality"])
        return df.sample(n=min(200, len(df)), random_state=42).reset_index(drop=True), num_feats, "in_hospital_mortality"

    patient_cols = ['patientunitstayid', 'hospitalid', 'gender', 'age', 'ethnicity', 'admissionheight', 
                    'admissionweight', 'dischargeweight', 'hospitaladmitsource', 'hospitaldischargelocation', 
                    'hospitaldischargestatus', 'unittype', 'uniquepid', 'unitvisitnumber',
                    'patienthealthsystemstayid', 'hospitaldischargeyear']
    
    df = pd.read_csv('https://www.dropbox.com/scl/fi/qld4pvo6vlptm41av3y2e/patient.csv?rlkey=gry21fvb3u3dytz7i5jcujcu9&dl=1',
                     usecols=patient_cols)
    
    df['age'] = df['age'].replace({'> 89': 90})
    df = df.sort_values(by=['uniquepid', 'patienthealthsystemstayid', 'unitvisitnumber'])
    df = df.groupby('patienthealthsystemstayid').first().reset_index()
    
    hospital = pd.read_csv('https://www.dropbox.com/scl/fi/5sdjsbrjxk0hlbmpb4csi/hospital.csv?rlkey=rmlrhg3m9sm3hj2s6rykrg5w2&st=329j4gwk&dl=1')
    hospital = hospital.replace({'teachingstatus': {'f': 0, 't': 1}})
    df = df.merge(hospital, on='hospitalid', how='left')

    labnames = ['BUN', 'creatinine', 'sodium', 'Hct', 'wbc', 'glucose', 'potassium', 'Hgb', 'chloride', 'platelets',
                'RBC', 'calcium', 'MCV', 'MCHC', 'bicarbonate', 'MCH', 'RDW', 'albumin']
    labs = pd.read_csv('https://www.dropbox.com/scl/fi/qaxtx330hicc5u61siehn/lab.csv?rlkey=xs9oxpl5istkbuh5s80oyxwwi&st=ydfrjxkh&dl=1')
    labs['labname'] = labs['labname'].replace({'WBC x 1000': 'wbc', 'platelets x 1000': 'platelets'})
    labs = labs[labs['labname'].isin(labnames)]
    labs = labs.pivot_table(columns=['labname'], values=['labresult'], aggfunc='mean', index='patientunitstayid').reset_index()
    labs.columns = ['patientunitstayid'] + ['lab_' + c.lower() for c in labnames]

    df = df.merge(labs, on='patientunitstayid', how='left')
    df['in_hospital_mortality'] = df['hospitaldischargestatus'].map(lambda status: {'Alive': 0, 'Expired': 1}.get(status, np.nan))
    df = df.dropna(subset=['in_hospital_mortality'])
    
    num_feats = ['age', 'lab_glucose', 'lab_creatinine', 'lab_potassium']
    for col in num_feats: df[col] = pd.to_numeric(df[col], errors='coerce')
    df[num_feats] = df[num_feats].fillna(df[num_feats].mean())

    maj = df[df['in_hospital_mortality'] == 0]
    min_ = df[df['in_hospital_mortality'] == 1]
    min_over = resample(min_, replace=True, n_samples=len(maj), random_state=42)
    balanced = pd.concat([maj, min_over]).sample(n=200, random_state=42).reset_index(drop=True)
    
    return balanced, num_feats, 'in_hospital_mortality'

@st.cache_data
def load_foundational_data():
    X, y = make_classification(n_samples=200, n_features=4, n_informative=2, n_redundant=1, 
                               n_clusters_per_class=1, flip_y=0.1, random_state=42)
    features = ['gene_x_expression', 'protein_y_level', 'culture_ph', 'temperature_c']
    df = pd.DataFrame(X, columns=features)
    
    df['gene_x_expression'] = (df['gene_x_expression'] * 10) + 50
    df['protein_y_level'] = (df['protein_y_level'] * 5) + 20
    df['culture_ph'] = (df['culture_ph'] * 0.5) + 7.4
    df['temperature_c'] = (df['temperature_c'] * 1.5) + 37.0
    
    df['cellular_apoptosis'] = y
    return df, features, 'cellular_apoptosis'

st.title("Module Navigation")
scientific_context = st.radio(
    "Select Learning Context:", 
    ["Clinical (eICU)", "Foundational Science"],
    help="Toggle the terminology and dataset to match your specific field of study."
)

st.markdown("---")

st.title("Learning Activities")
st.info("Use the menu below to navigate between the three different activities in this module.")

mode = st.radio(
    "Select an Activity:",
    [
        "Activity 1: Overfitting and Underfitting", 
        "Activity 2: Hyperparameter Tuning",
        "Activity 3: Cross-Validation Strategies"
    ],
    help="Navigate through the interactive activities to explore model generalizability."
)

if scientific_context == "Clinical (eICU)":
    df, features, target = load_clinical_data()
    context_desc = "Predicting in-hospital mortality using the eICU Database."
else:
    df, features, target = load_foundational_data()
    context_desc = "Predicting cellular apoptosis using a simulated foundational science dataset."

if 'current_context' not in st.session_state or st.session_state.current_context != scientific_context:
    st.session_state.current_context = scientific_context
    st.session_state.selected_features = features

X = df[st.session_state.selected_features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ==========================================
# ACTIVITY 1: OVERFITTING AND UNDERFITTING
# ==========================================
if mode == "Activity 1: Overfitting and Underfitting":
    st.title("Activity 1: Overfitting vs. Underfitting")
    
    with st.expander("Activity Instructions", expanded=True):
        st.write("""
        1. Compare a 'Complex' model (Low k) to a 'Simple' model (High k) using the inputs below.
        2. Observe how the complex model attempts to draw boundaries around every single outlier, while the simple model draws a generalized regional boundary.
        3. Use the sidebar on the left to navigate to Activity 2 when you are ready.
        """)
    
    st.subheader("Visualizing Decision Boundaries (Top 2 Features)")
    
    c1, c2 = st.columns(2)
    k_low = c1.number_input("Complex Model (k)", 1, 50, 1, help="A low k value makes the model highly sensitive to noise.")
    k_high = c2.number_input("Simple Model (k)", 1, 50, 15, help="A high k value smooths out the boundaries.")

    def boundary_data(k_val):
        X_2d = X_train_s[:, :2] 
        knn = KNeighborsClassifier(n_neighbors=k_val).fit(X_2d, y_train)
        x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
        y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1), np.arange(y_min, y_max, 0.1))
        Z = knn.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        return X_2d, xx, yy, Z

    X_2d_low, xx_low, yy_low, z_low = boundary_data(k_low)
    X_2d_high, xx_high, yy_high, z_high = boundary_data(k_high)
    fig_b = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(f"Overfitting (k={k_low})", f"Underfitting (k={k_high})"),
        horizontal_spacing=0.08,
    )
    for col, x_2d, xx, yy, z in (
        (1, X_2d_low, xx_low, yy_low, z_low),
        (2, X_2d_high, xx_high, yy_high, z_high),
    ):
        fig_b.add_trace(
            go.Contour(
                x=xx[0],
                y=yy[:, 0],
                z=z,
                colorscale="Cividis",
                opacity=0.75,
                showscale=False,
                hoverinfo="skip",
            ),
            row=1,
            col=col,
        )
        fig_b.add_trace(
            go.Scatter(
                x=x_2d[:, 0],
                y=x_2d[:, 1],
                mode="markers",
                marker=dict(
                    color=y_train,
                    colorscale="Cividis",
                    size=7,
                    line=dict(color="white", width=1),
                ),
                showlegend=False,
                hovertemplate=(
                    f"{st.session_state.selected_features[0]}: %{{x:.2f}}<br>"
                    f"{st.session_state.selected_features[1]}: %{{y:.2f}}<extra></extra>"
                ),
            ),
            row=1,
            col=col,
        )
        fig_b.update_xaxes(title_text=st.session_state.selected_features[0], row=1, col=col)
        fig_b.update_yaxes(title_text=st.session_state.selected_features[1], row=1, col=col)
    render_plotly_chart(fig_b, height=620)
    st.caption("Colorblind-accessible contour plot displaying model decision boundaries. Yellow regions predict one class outcome, while dark blue regions predict the other. White-outlined dots represent individual patient or cell sample data points.")

    with st.expander("Reveal Concept Summary"):
        st.write("Models with low k values create highly jagged decision boundaries, essentially memorizing the training data (overfitting). Models with high k values create smooth, broad boundaries, which may miss critical patterns (underfitting).")

# ==========================================
# ACTIVITY 2: HYPERPARAMETER TUNING
# ==========================================
elif mode == "Activity 2: Hyperparameter Tuning":
    st.title("Activity 2: Hyperparameter Tuning")
    
    with st.expander("Activity Instructions", expanded=True):
        st.write("""
        1. Adjust the 'maximum k' slider to generate the Accuracy Curve.
        2. Observe where the Train and Test accuracy lines begin to separate. This divergence indicates the exact point where the model stops learning general rules and starts memorizing the training data.
        3. Use the sidebar on the left to navigate to Activity 3 when you are ready.
        """)

    st.subheader("Accuracy Curve")
    k_max = st.slider("Select maximum k to test", 5, 50, 20, help="Expanding the maximum k allows you to see where the model begins to underfit the data.")
    
    ks = range(1, k_max + 1)
    train_acc, test_acc = [], []
    for k in ks:
        knn = KNeighborsClassifier(n_neighbors=k).fit(X_train_s, y_train)
        train_acc.append(accuracy_score(y_train, knn.predict(X_train_s)))
        test_acc.append(accuracy_score(y_test, knn.predict(X_test_s)))

    fig_acc = go.Figure()
    fig_acc.add_trace(go.Scatter(x=list(ks), y=train_acc, mode="lines+markers", name="Train Accuracy", line=dict(color="#00204c")))
    fig_acc.add_trace(go.Scatter(x=list(ks), y=test_acc, mode="lines+markers", name="Test Accuracy", line=dict(color="#d6b800")))
    fig_acc.update_xaxes(title_text="Number of Neighbors (k)")
    fig_acc.update_yaxes(title_text="Accuracy", range=[0, 1.05])
    render_plotly_chart(fig_acc, height=500)
    st.caption("Line graph comparing model accuracy on training data versus testing data across different values of k. The dark blue line represents training accuracy, and the yellow line represents testing accuracy.")

    with st.expander("Reveal Concept Summary"):
        st.write("The optimal hyperparameter is found just before the training and testing curves diverge significantly. A large gap between high training accuracy and low testing accuracy is the mathematical signature of overfitting.")

# ==========================================
# ACTIVITY 3: CROSS-VALIDATION STRATEGIES
# ==========================================
elif mode == "Activity 3: Cross-Validation Strategies":
    st.title("Activity 3: Cross-Validation Strategies")
    
    with st.expander("Activity Instructions", expanded=True):
        st.write("""
        1. Adjust the 'Number of Folds' slider to see how stable the model performance is.
        2. Observe the variance in the boxplot. A wide box indicates the model is highly sensitive to how the data is split.
        3. Compare the mean accuracies and standard deviations of K-Fold, Stratified K-Fold, and LOO-CV.
        """)
        
    col_cv1, col_cv2 = st.columns(2)
    n_f = col_cv1.slider("Number of Folds", 2, 10, 5, help="Controls how many subsets the data is split into during validation.")
    k_cv = col_cv2.slider("Model Complexity (k)", 1, 20, 5, help="Sets the neighbor count for the model being validated.")

    knn_cv = KNeighborsClassifier(n_neighbors=k_cv)
    kf = KFold(n_splits=n_f, shuffle=True, random_state=42)
    X_s = StandardScaler().fit_transform(X) 
    scores = cross_val_score(knn_cv, X_s, y, cv=kf)

    fig_cv = go.Figure()
    fig_cv.add_trace(
        go.Box(
            x=scores,
            name=f"{n_f} Folds",
            boxpoints="all",
            jitter=0.35,
            pointpos=0,
            marker_color="#d6b800",
            line_color="#00204c",
        )
    )
    fig_cv.update_xaxes(title_text="Accuracy", range=[0, 1.05])
    fig_cv.update_layout(title=f"Accuracy Distribution ({n_f} Folds)")
    render_plotly_chart(fig_cv, height=430)
    st.caption("Boxplot displaying the spread of accuracy scores across multiple data folds. Wider boxes indicate greater instability in the model's performance.")

    st.subheader("Comparing Validation Strategies")
    skf = StratifiedKFold(n_splits=n_f, shuffle=True, random_state=42)
    loo = LeaveOneOut()
    
    with st.spinner("Calculating metrics..."):
        skf_s = cross_val_score(knn_cv, X_s, y, cv=skf)
        loo_s = cross_val_score(knn_cv, X_s, y, cv=loo)

    methods = ["K-Fold", "Stratified K-Fold", "LOO-CV"]
    means = [scores.mean(), skf_s.mean(), loo_s.mean()]
    sterr = [scores.std(), skf_s.std(), loo_s.std()]

    fig_bar = go.Figure(
        go.Bar(
            x=methods,
            y=means,
            error_y=dict(type="data", array=sterr, visible=True),
            marker_color=["#00204c", "#575c6d", "#d6b800"],
        )
    )
    fig_bar.update_yaxes(title_text="Mean Accuracy", range=[0, 1.1])
    render_plotly_chart(fig_bar, height=500)
    st.caption("Bar chart comparing the mean accuracy of K-Fold, Stratified K-Fold, and Leave-One-Out cross-validation. Error bars represent the standard deviation of scores.")

    with st.expander("Reveal Concept Summary"):
        st.write("Stratified K-Fold is generally preferred for biomedical datasets as it ensures the ratio of positive to negative outcomes remains consistent across all test folds. LOO-CV provides an unbiased estimate but at a high computational cost and potentially high variance.")
