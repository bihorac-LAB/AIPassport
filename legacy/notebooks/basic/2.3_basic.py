import streamlit as st

st.title("2.3 Bias, Fairness, and Societal Impacts in Biomedical AI")
st.subheader("Basic Track – Microskill 2 Interactive Assignment")

st.markdown("---")

st.header("Assignment 1: Imagine Your Ideal AI System for Biomedical Research")
st.markdown("""
**Prompt:**  
*Imagine that you could create any AI system to assist you with your biomedical research.  
- What would you design the system to do and why?  
- How might you safeguard against bias and unfairness?*
""")

user_answer1 = st.text_area(
    "✏️ Write your answer here:",
    height=140,
    key="answer1",
)

if st.button("Reveal Example & Guidance for Assignment 1"):
    st.success(
        """
**Example:**

I would create a system that cycles through data to predict which diseases are on the rise using data from social media. This would allow preparation for illness outbreaks and for deciphering which symptoms are most predictive of an outbreak. It would have to take in data from several different social media sites to ensure that it covers many different communities and demographics.

**Guidance:**  
- Describe a system that’s helpful and necessary for your research.
- Consider bias in your design: what kinds of data would you seek, and how would you address bias or limited representation?
- Reflect on the impact of your AI, and who could be unfairly helped or harmed.
"""
    )

st.markdown("---")

st.header("Assignment 2: Public Health Crisis Algorithm Case Study")

with st.expander("Read the case (click to expand)", expanded=True):
    st.markdown(
        """
A large organization would like to develop an algorithm that assists major cities in combating public health crises.  
It will use real-time monitoring of traditional and digital media, along with search trends, to identify possible emerging disease clusters.

In creating the algorithm, the organization uses several training datasets, including those from areas where:
- The **population demographics** do **not** reflect those of most major cities.
- The **income demographics** do **not** reflect those of most major cities.

**Prompt:**  
- What are the possible vectors of bias that might impact the accuracy of the algorithm? 
- What should the organization consider before marketing the algorithmic tool?
- What are the possible negative outcomes?
- *Explain your answer.*
"""
    )

user_answer2 = st.text_area(
    "✏️ Write your answer here:",
    height=140,
    key="answer2"
)

if st.button("Reveal Example & Guidance for Assignment 2"):
    st.success(
        """
**Example:**

The vectors of bias for the algorithm include using data that does not reflect the kinds of people in the cities that will adopt the system and using income as a factor. Using this kind of data will provide resulting guidance that will be off-base. Further, although the algorithms will only be used to offer guidance, some public health officials will think that the algorithm cannot be wrong, and they won’t critically consider the results.

**Guidance:**  
- Think about whether the data “matches” the population it’s meant to serve.  
- Consider possible misrepresentations, especially if demographic and income factors are different between training and deployment.
- Reflect on the risks if policymakers rely too heavily/uncritically on algorithmic results.
"""
    )

st.markdown("---")

st.header("Reflection and Takeaways")
st.markdown("""
What are your biggest takeaways from thinking about bias and fairness in biomedical AI so far?  
How would you check for or prevent bias in your own research or collaborations?
""")
reflection = st.text_area("Your reflections here (optional):", height=100, key="reflection")

st.success("Thank you! Bias, fairness, and societal context should always be considered in biomedical AI research.")

st.markdown("""
---
**Key Points:**  
- Reflect on who benefits, who might be left out, and how your data shapes your AI’s predictions.
- Remember: No dataset is perfectly representative.
- Both data *and* human interpretation affect the impact of AI.

*For further reading:  
- [The Alan Turing Institute: Fairness in Machine Learning](https://www.turing.ac.uk/research/research-projects/fairness-machine-learning)
- [WHO Guidance: Ethics & Governance of AI for Health](https://www.who.int/publications/i/item/9789240029200)
""")
