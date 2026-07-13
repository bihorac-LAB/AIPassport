import streamlit as st

st.title("1.7 Mentorship and Peer Review in Biomedical AI")

st.markdown("""
**Objective:**  
Develop the skills to identify and effectively address challenges in mentoring relationships within clinical research/AI teams.

---
""")

# CASE SCENARIO
with st.expander("Read the clinical case (click to expand):", expanded=True):
    st.markdown("""
**Clinical Case:**  
Dr. Jordan, an early-career clinician-researcher, is being mentored by Dr. Martinez, a senior attending physician and clinical AI leader.  
Initially, their mentorship meetings were productive—Dr. Martinez provided guidance on integrating AI-driven risk prediction models into clinical workflows for heart failure patients.  
However, recently, Dr. Martinez has frequently rescheduled or shortened their meetings. Dr. Jordan feels increasingly unsupported, especially with a deadline approaching for a multicenter study protocol and IRB submission.

Dr. Martinez perceives Dr. Jordan as becoming overly dependent, waiting for advice instead of proactively troubleshooting workflow and data obstacles. Frustrations are mounting on both sides.

---
""")

st.markdown("----")

# PART 1: IDENTIFY THE CHALLENGES
st.header("1. Identify the Challenges")
st.markdown("""
List the problems in this clinical mentoring relationship.  
Consider issues like communication, expectations, workload, and career dynamics.
""")

user_clinical_challenges = st.text_area(
    "Write your answer here (bullet points or text):", 
    key="clinical_challenges_input"
)

if st.button("Show Example – Challenges", key="show_clinical_challenges_btn"):
    st.success(
        "Example:\n\n"
        "- **Communication breakdown:** Dr. Martinez frequently reschedules/shortens meetings, but hasn't clearly communicated new availability or reasons, leaving Dr. Jordan uncertain.\n\n"
        "- **Expectation mismatch:** Dr. Jordan expects hands-on support for urgent tasks (protocol prep, IRB submission), while Dr. Martinez expects more independent troubleshooting with less direct oversight. These clashing assumptions fuel frustration.\n\n"
        "- **Workload management/conflict:** Both are busy clinicians/researchers; rescheduling meetings may signal overcommitment or competing priorities.\n\n"
        "- **Role/career imbalance:** Dr. Jordan may feel hesitant to push for help or clarity due to career stage; Dr. Martinez may underestimate the need for guidance at critical clinical research milestones."
    )

st.markdown("----")

# PART 2: DRAFT PROFESSIONAL COMMUNICATION
st.header("2. Draft a Professional Communication")

st.markdown("""
Imagine you are **Dr. Jordan**.  
Compose a message requesting a meeting with Dr. Martinez to discuss and improve the situation:
- Clearly and professionally explain the issues.
- Show you recognize Dr. Martinez’s perspective.
- Propose concrete, actionable changes to your working relationship, tailored for busy clinical environments.
""")

user_clinical_email = st.text_area(
    "Write your email/message here:",
    value="",
    height=220, key="clinical_email_input"
)

if st.button("Show Example – Professional Communication", key="show_clinical_email_btn"):
    st.info("""\
Dear Dr. Martinez,

I hope this message finds you well. I’d like to request a meeting to discuss our current working relationship and some challenges I’ve been experiencing. Your insights on integrating AI into our heart failure protocols have been extremely valuable, and I am grateful for your mentorship.

Recently, I’ve noticed our meetings have become less frequent and are sometimes cut short. I completely appreciate your clinical and research obligations, especially as new projects arise. However, with the upcoming multicenter protocol deadline and IRB submission, I’ve felt unsure at times how to proceed when obstacles arise.

I also realize I could be more proactive in troubleshooting workflow bottlenecks before seeking your direct guidance. Would we be able to set a recurring check-in (even biweekly) and perhaps agree on short agendas to maximize our time? I’d like to become more independent but still benefit from your targeted advice during critical moments.

Thank you for considering this. I am eager to find a balance that supports both your schedule and my professional growth.

Best regards,  
Dr. Jordan
""")

st.markdown("----")

# PART 3: REFLECTION AND FEEDBACK
st.header("3. Reflection (Clinical AI Teams)")

st.markdown("""
- What aspects make mentorship relationships in clinical AI particularly challenging?
- How can you apply techniques from this activity in your own clinical or research team experience?
""")

user_clinical_reflect = st.text_area(
    "Write your reflection here (optional):",
    key="clinical_reflect_input"
)

st.success("Thank you! You have completed the clinical mentorship and peer review skills activity.")

st.markdown("""
---
**Key Takeaways for Clinical Teams:**
- Busy clinical schedules demand clear, structured, and respectful communication.
- Explicitly revisiting expectations helps prevent conflicts in high-stakes, time-pressured AI/clinical projects.
- Proactive troubleshooting empowers mentees, while “just-in-time” mentoring can make limited mentor time more effective.

**For further reading:**  
- [Effective mentoring in clinical research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4564451/)
- [Nature - How to be a good mentee](https://www.nature.com/articles/d41586-020-02927-0)
""")
