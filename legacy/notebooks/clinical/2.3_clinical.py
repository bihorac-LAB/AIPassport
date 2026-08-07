import streamlit as st

st.title("2.3 Bias, Fairness, and Societal Impact of Biomedical AI")
st.subheader("Clinical Track – Microskill 2 Interactive Assignment")

st.markdown("---")

st.header("Assignment 1: Imagine Your Ideal Clinical AI System")

st.markdown("""
> **Prompt:**  
> Imagine that you could create any AI system to assist you with your clinical practice.  
> - What would you design the system to do and why?  
> - How might you safeguard against bias and unfairness?
""")

assignment1_answer = st.text_area(
    "Write your answer here (please address usefulness, necessity, and fairness/bias):",
    height=160
)

if st.button("Reveal Example & Guidance for Assignment 1"):
    st.success("""
**Example:**

I would create a system that cycles through patient data to predict which diseases are on the rise seasonally. This would allow hospitals to prepare for an influx of sickness and for clinicians to be on the lookout for specific symptoms. It would have to take in data from surrounding hospitals and clinics to be more accurate, as some hospitals serve certain demographics and without other data, we won’t have a very generalizable picture of what’s happening in the city or surrounding areas.

**Guidance:**  
- Describe a useful, necessary AI system for your clinical setting.  
- Identify the types of data you would use and why.  
- Explicitly consider risks of bias and unfairness, and how you would attempt to mitigate or monitor them.
""")

st.markdown("---")

st.header("Assignment 2: Case Study on Algorithmic Triage in the ER")

with st.expander("Read the case (click to expand)", expanded=True):
    st.markdown("""
A large hospital is the only level one trauma center in a 100-mile radius of a small city in the Southern United States.  
Because of this, the hospital receives an abundance of patients with traumatic injuries including vehicle crashes, shootings, catastrophic injuries, along with other injuries into its Emergency Room.  
Hospital staff and administration want to find a way to best determine which patients should receive the most immediate care.  
To do this, the hospital wants to decide whether to employ an algorithm that ranks patients by the acuity of their illness as calculated using the symptoms and demographic data input by hospital staff.

> **Questions:**  
> - What are the possible vectors of bias that might impact patient care?  
> - What should the hospital consider before employing the algorithmic tool?  
> - What are the possible negative outcomes?  
> Explain your answer.
""", unsafe_allow_html=True)

assignment2_answer = st.text_area(
    "Write your answer here (please address data, bias, and practical implications):",
    height=160
)

if st.button("Reveal Example & Guidance for Assignment 2"):
    st.success("""
**Example:**

The vectors of bias for the algorithm include the data and the people who will interpret the guidance from the algorithm. As the only trauma center in a 100-mile radius, the hospital will receive all kinds of terrible injuries that other hospitals may not receive, therefore, if the data that was used to train the algorithm is not similar, the resulting guidance will be off-base. Further, although the algorithms will only be used to offer guidance, some clinicians will think that the algorithm cannot be wrong, and they won’t critically consider the results.

**Guidance:**  
- Consider how the unique patient population (regional, demographic, trauma-specific) may or may not be reflected in the data used to train the model.  
- Consider the risk that social, demographic, or subjective data could introduce or amplify bias.  
- Reflect on the consequences (e.g., inequities in care, overreliance on algorithms, errors propagating).
""")

st.markdown("---")

st.header("Reflection and Takeaways")

st.markdown("""
- Why is it important to account for societal impact and bias when designing clinical AI?
- How would you monitor or check for fairness *after* deploying such a system?
""")
reflection = st.text_area("Write your reflections here (optional):", height=100)

st.success("Thank you! Your careful thought on bias, fairness, and impact is essential for safe and effective clinical AI.")

st.markdown("""
---
**Key Points:**  
- Always consider how your data and clinical realities shape model fairness and effectiveness.
- No algorithm is objective or immune to bias.
- Both technical design and human interpretation can perpetuate or reduce inequity.

*For further learning, see: [AAMC Artificial Intelligence in Medicine Case Studies](https://www.aamc.org/contact/ai-case-studies)*
""")
