import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ethical Data Acquisition Audit", layout="wide")

st.markdown("""
<style>
    .narrator-box {
        background-color: #f4f6f7; 
        border-left: 5px solid #2c3e50; 
        padding: 20px; 
        border-radius: 4px; 
        font-style: italic; 
        font-family: 'Georgia', serif;
        margin-bottom: 25px;
        color: #333;
    }
    .instruction-box {
        background-color: #e8f6f3;
        border: 1px solid #a2d9ce;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        color: #0e6655;
    }
    .header-box {
        background-color: #eaf2f8; 
        border: 1px solid #d5d8dc; 
        padding: 15px; 
        border-radius: 5px; 
        margin-bottom: 20px;
    }
    .toolkit-step {
        background-color: #fdfefe;
        border: 1px solid #eaecee;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    h2 { color: #1a5276; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    h4 { color: #2c3e50; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR: TRACK & CONFIGURATION ---
st.sidebar.title("Audit Configuration")

track = st.sidebar.radio(
    "Select Research Track:",
    ["Clinical Track (IC3 COVID-19)", "Basic Science Track (ImmPort)"],
    help="Select the dataset context for this audit session."
)

# Set Variables based on Track
if "Clinical" in track:
    dataset_name = "IC3 UF Public COVID-19 Dataset"
    dataset_link = "https://ic3.center.ufl.edu/research/resources/datasets/"
    subject_term = "Patient"
    sample_term = "Electronic Health Record (EHR)"
    underserved_example = "Rural populations with limited hospital access"
else:
    dataset_name = "ImmPort (Immunology Database)"
    dataset_link = "https://www.immport.org/shared/home"
    subject_term = "Donor"
    sample_term = "Biological Specimen"
    underserved_example = "Donors of non-European ancestry"

st.sidebar.markdown("---")
st.sidebar.info(f"**Current Context**\n\nDataset: {dataset_name}\nSubject: {subject_term}")

# Navigation
section = st.sidebar.radio(
    "Select Audit Activity:",
    [
        "1. Intro: The Four Pillars",
        "2. Autonomy: Consent Audit",
        "3. Justice: Representation Audit",
        "4. Privacy: Security Audit",
        "5. Beneficence: Impact Audit"
    ]
)

# --- 3. HELPER FUNCTIONS ---
def narrator(text):
    st.markdown(f'<div class="narrator-box"><b>Narrator:</b> "{text}"</div>', unsafe_allow_html=True)

def instruction(text):
    st.markdown(f'<div class="instruction-box"><b>Activity Instructions:</b> {text}</div>', unsafe_allow_html=True)

# --- 4. APP CONTENT ---

# === SECTION 1: INTRO ===
if section == "1. Intro: The Four Pillars":
    st.title("Module MS2: Acquiring Ethically Sourced Biomedical Data")
    
    narrator(
        "Welcome to this educational journey. Today, we embark on an exploration of practices that honor patient autonomy, "
        "ensure societal justice, and promote the beneficence of improving human health. Our journey will focus on four key pillars."
    )
    
    st.markdown(f"""
    <div class="header-box">
        <h4>Audit Target: {dataset_name}</h4>
        <p><b>Source:</b> <a href="{dataset_link}" target="_blank">Link to Dataset</a></p>
        <p><b>Role:</b> You are acting as the Ethical Compliance Officer. Your goal is to review the proposed study protocol 
        and identify failures in consent, representation, and security.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.info("**1. Autonomy**\n\nInformed Consent & Control")
    with col2: st.info("**2. Justice**\n\nEquitable Representation")
    with col3: st.info("**3. Privacy**\n\nData Security & Encryption")
    with col4: st.info("**4. Beneficence**\n\nReturning Value to Society")

# === SECTION 2: AUTONOMY ===
elif section == "2. Autonomy: Consent Audit":
    st.header("Activity 1: The 'Fine Print' Audit (Autonomy)")
    
    narrator(
        "Informed consent is a critical component of respecting patient autonomy. It transcends a simple signature on a document; "
        "it is a dynamic, ongoing dialogue. Simplifying complex medical jargon is crucial."
    )
    
    instruction(
        f"The current protocol uses standard legal text for {subject_term} consent. "
        "Use the tool below to revise the language and observe the impact on participant comprehension."
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Current Protocol (Legal Standard)")
        st.warning(
            f"The undersigned {subject_term} hereby grants permissions for the indefinite utilization of "
            f"{sample_term}s and associated metadata, waiving all rights to pecuniary gain..."
        )
        st.write("**Audit Finding:** Low comprehension. Participants may feel alienated or coerced.")

    with col2:
        st.markdown("#### Revision Tool")
        literacy = st.select_slider(
            "Select Language Complexity Level:", 
            options=["Medical Jargon", "Standard", "Simplified & Empowering"], 
            value="Medical Jargon",
            help="Adjusting this slider changes the phrasing of the consent form."
        )
        
        if literacy == "Medical Jargon":
            st.info("Status: No changes made. (See warning on left)")
        elif literacy == "Standard":
            st.info("Status: Improved, but still transactional.")
        elif literacy == "Simplified & Empowering":
            st.success(
                f"**Revised Text:** 'We are asking for your permission to use your {sample_term} to help researchers understand disease. "
                "You can say no without affecting your care. You can also withdraw later. We want you to be a partner in this science.'"
            )
            st.write("**Audit Result:** Compliant. The participant is empowered to make an informed choice.")

# === SECTION 3: JUSTICE (REP-EQUITY TOOLKIT) ===
elif section == "3. Justice: Representation Audit":
    st.header("Activity 2: The 'Hidden Population' Audit (Justice)")
    
    narrator(
        "Societal justice requires a commitment to equitable practices. This means diversifying the recruitment for studies. "
        "Achieving health equity demands robust community engagement."
    )
    
    instruction(
        "The current recruitment plan is passive (email only). Use the REP-EQUITY Toolkit below to identify the missing group "
        "and select active strategies to close the representation gap."
    )

    # --- REP-EQUITY SIMULATION ---
    st.markdown("#### REP-EQUITY Toolkit Configuration")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown('<div class="toolkit-step"><b>Step 1: Define Underserved Groups</b></div>', unsafe_allow_html=True)
        st.text_input(
            f"Identify the group missing from {dataset_name}:", 
            value=underserved_example,
            help="This group will be the focus of your recruitment efforts."
        )

        st.markdown('<div class="toolkit-step"><b>Steps 3 & 4: Set Recruitment Goal</b></div>', unsafe_allow_html=True)
        goal = st.slider(
            f"Target Proportion for Underserved {subject_term}s (%):", 
            0, 100, 30,
            help="The percentage of the total sample that should come from the underserved group to ensure statistical power."
        )
        baseline = 5 # Fixed baseline for demo
        
    with c2:
        st.markdown('<div class="toolkit-step"><b>Step 5: Manage External Factors (Select Strategies)</b></div>', unsafe_allow_html=True)
        s1 = st.checkbox("Community Liaisons (+10%)", help="Hire trusted community members to facilitate recruitment.")
        s2 = st.checkbox("Translated Materials (+5%)", help="Provide consent forms in the native language of the target group.")
        s3 = st.checkbox("Logistical Support (+10%)", help="Provide transportation or mobile clinics to reduce access barriers.")
        
        # Calculate Logic
        current = baseline + (10 if s1 else 0) + (5 if s2 else 0) + (10 if s3 else 0)
        
        st.markdown('<div class="toolkit-step"><b>Step 6: Evaluate Representation</b></div>', unsafe_allow_html=True)
        
        df = pd.DataFrame({
            "Stage": ["Baseline (Passive)", "With Selected Strategies", "Target Goal"],
            "Percentage": [baseline, current, goal]
        })
        fig = px.bar(df, x="Stage", y="Percentage", color="Stage", 
                     color_discrete_map={"Baseline (Passive)":"#95a5a6", "With Selected Strategies":"#27ae60", "Target Goal":"#2c3e50"})
        fig.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    if current >= goal:
        st.success(f"**Audit Result:** PASS. The selected strategies are sufficient to achieve a representative sample in the {dataset_name}.")
    else:
        st.warning("**Audit Result:** FAIL. Additional strategies are needed to reach the target goal.")

# === SECTION 4: PRIVACY ===
elif section == "4. Privacy: Security Audit":
    st.header("Activity 3: The 'Data Fortress' Audit (Privacy)")
    
    narrator(
        "Protecting patient privacy is not merely a legal obligation, it is a moral imperative. "
        "Employ multi-layered security protocols, including state-of-the-art encryption and routine security audits."
    )
    
    instruction(
        f"The protocol currently lacks depth. Select the necessary security layers below to protect the {sample_term} data. "
        "You must achieve a 'Secure' rating to pass the audit."
    )
    
    st.subheader("Security Protocol Checklist")

    c1, c2, c3, c4 = st.columns(4)
    l1 = c1.checkbox("End-to-End Encryption", help="Data is encoded so only authorized parties can read it.")
    l2 = c2.checkbox("Role-Based Access Control", help="Restricts system access to authorized users based on their role.")
    l3 = c3.checkbox("De-identification", help="Removes personal identifiers (Name, ID) from the dataset.")
    l4 = c4.checkbox("Regular Audits", help="Routine checks to identify and patch vulnerabilities.")
    
    score = sum([l1, l2, l3, l4])
    
    st.markdown("---")
    st.markdown("#### Simulation Results")
    
    if score == 4:
        st.success("🛡️ **Status: SECURE.** Multi-layered protocols are active. Compliance verified.")
    elif score >= 2:
        st.warning("⚠️ **Status: VULNERABLE.** Some protections are in place, but gaps remain. High risk of breach.")
    else:
        st.error("🚨 **Status: CRITICAL RISK.** Data is effectively unprotected. Protocol rejected.")

# === SECTION 5: BENEFICENCE ===
elif section == "5. Beneficence: Impact Audit":
    st.header("Activity 4: Closing the Loop (Beneficence)")
    
    narrator(
        "To maximize beneficence, researchers must cultivate an ethical framework that integrates continuous patient feedback. "
        "Outcomes from research should be made accessible to the contributing communities."
    )
    
    instruction(
        "The current protocol ends at 'Research Analysis'. Click the button below to mandate the 'Return of Value' phase "
        "and complete the ethical cycle."
    )
    
    st.subheader("The Ethical Data Cycle")
    
    col1, col2, col3 = st.columns(3)
    col1.info(f"1. Acquisition\n\n({subject_term} provides data)")
    col2.info("2. Research\n\n(Analysis of patterns)")
    
    if col3.button("Execute 'Return of Value' Phase", help="Distribute findings and health insights back to the participants."):
        col3.success("3. Beneficence\n\n(Findings returned)")
        st.markdown(f"""
        **Impact Report:**
        * **For {subject_term}s:** Received actionable health insights.
        * **For Community:** Trust restored; willing to participate in future studies.
        * **For {dataset_name}:** Validated as a tool for public good.
        """)
    else:
        col3.warning("3. [Pending Action]\n\n(Cycle incomplete)")

# --- FOOTER ---
st.markdown("---")
st.caption("Module MS2 | Course Materials | Based on REP-EQUITY Toolkit & IC3/ImmPort Datasets")
