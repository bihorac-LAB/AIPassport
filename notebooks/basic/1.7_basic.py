import streamlit as st

st.set_page_config(
    page_title="1.7 Mentorship and Peer Review in Biomedical AI",
    layout="centered"
)

st.title("1.7 Mentorship and Peer Review in Biomedical AI")

st.markdown("""
**Objective:**  
Develop the skills to identify and effectively address challenges in mentoring relationships.

---
""")

# CASE SCENARIO
with st.expander("Read the scenario (click to expand):", expanded=True):
    st.markdown("""
**Case:**  
Dr. Witmer, an early-career research faculty member, is mentored by Dr. Antone, a senior faculty member.  
Initially, their meetings were productive, but over time, Dr. Antone has become less available, often rescheduling or cutting meetings short.  
Dr. Witmer feels unsupported, particularly in preparing for an upcoming research grant application.  
Dr. Antone, in turn, perceives Dr. Witmer as overly reliant and not proactive in solving problems independently.  
Tensions are rising, and both parties are growing frustrated.
""")

st.markdown("----")

# PART 1: IDENTIFY THE CHALLENGES
st.header("1️⃣ Identify the Challenges")
st.markdown("""
Identify the problems in this mentoring relationship.  
Consider aspects such as communication, expectations, and role dynamics.
""")

user_challenges = st.text_area(
    "Write your answer here (bullet points or text):", 
    key="challenges_input"
)

if st.button("Show Example – Challenges", key="show_challenges_btn"):
    st.success(
        "Example:\n\n"
        "- **Communication challenges:** Dr. Antone rescheduling or shortening meetings "
        "indicates a breakdown in communication, which is essential to a healthy mentor-mentee relationship. "
        "It's possible that Dr. Antone is not discussing availability openly, and Dr. Witmer may not have communicated their needs clearly.\n\n"
        "- **Expectation challenges:** Dr. Witmer expected more consistent guidance, especially for high-stakes tasks like grant applications. "
        "Meanwhile, Dr. Antone expected Dr. Witmer to be more self-reliant. Such unspoken differences in expectations are fueling tension.\n\n"
        "- **Role dynamics:** The agreed-upon meeting schedule is not being honored, eroding trust. Dr. Witmer's reliance may also be impacting Dr. Antone's sense of effective mentoring."
    )

st.markdown("----")

# PART 2: WRITE THE RESOLUTION PLAN / PROFESSIONAL EMAIL
st.header("2️⃣ Draft a Professional Communication")

st.markdown("""
Imagine you are **Dr. Witmer**.  
Draft a message to Dr. Antone requesting a meeting to discuss and improve the situation.
- Clearly explain the issues.
- Acknowledge Dr. Antone's perspective.
- Suggest realistic, actionable improvements to your working relationship.
""")

user_email = st.text_area(
    "Write your email/message here:",
    value="",
    height=200, key="email_input"
)

if st.button("Show Example – Professional Communication", key="show_email_btn"):
    st.info("""\
Dear Dr. Antone,

I hope you're doing well. I'd like to request a meeting to discuss our working relationship and the challenges that I have been facing recently. I truly value your expertise, and I have learned a lot from you.

Over the past few months, I've noticed that our meetings have been less frequent, with some rescheduled or cut short. I understand that you have many demands on your time, but I've felt unsupported, especially as I prepare for the upcoming grant application. However, I recognize that I may have been overly reliant on you, and I want to be more proactive in problem-solving going forward. Maybe we could schedule regular check-ins, with clear agendas to make the most of our time together, and that would allow me to be more comfortable with my projects. Mainly, I want to find a way for me to be more self-reliant while benefiting from your mentorship.

I look forward to hearing your thoughts on this.

Best,  
Dr. Witmer""")

st.markdown("----")

# PART 3: REFLECTION AND FEEDBACK
st.header("3️⃣ Reflection")

st.markdown("""
- What do you think is the most important skill for maintaining a healthy mentor-mentee relationship?
- How could the approaches used in this case benefit you (as a mentor or mentee) in your own career development?
""")

user_reflect = st.text_area(
    "Write your reflection here (optional):",
    key="reflect_input"
)

st.success("Thank you! You have completed the mentorship and peer review skills activity.")

st.markdown("""
---
**Tips for Applying This:**
- Open, respectful communication and clear mutual expectations are critical.
- Regular feedback/check-ins help prevent small misalignments from growing into big ruptures.

**For further reading:**  
- [Nature - How to be a good mentee](https://www.nature.com/articles/d41586-020-02927-0)  
- [Science - How to make the most of mentoring](https://www.science.org/content/article/how-make-most-mentoring)
""")