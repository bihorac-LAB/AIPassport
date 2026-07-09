import streamlit as st

st.title("2.6 Human-AI Collaboration in Biomedicine (Basic)")

with st.container(border=True):
    st.markdown("### Question 1")
    st.markdown(
        """
    Identify and list all the human-AI collaboration tools currently at use in your lab or 
    professional organizations. How do you or your colleagues use these tools. What are their 
    benefits and drawbacks? Explain how you manage these systems, and the data created from them."""
    )

    a1 = st.text_area("Your response to Question 1", key="a1", height=200, label_visibility="collapsed")

st.markdown("---")

with st.container(border=True):
    st.markdown("### Question 2")

    st.markdown(
        """
    Consider the following case:
    
    In conducting research on the effectiveness of certain public health campaigns, the researchers 
    have decided to conduct qualitative interviews and want to use an AI transcription system. The 
    idea is that the AI tool will allow more accurate notes. After testing the tool in various voice 
    recording settings, the research study staff reviewed the transcripts and notes from the tool. 
    To their dismay, they found that although the tool transcribed the interviews, it also:

    - Made up segments of conversations that did not happen.
    - Made certain interviews appear to be being aggressive with the interviewers, when this behavior was not present; and 
    - Was not as accurate in conversations with interviewees with accents, from the around the US or otherwise.
    - Recorded personally identifiable information in the meta data of the transcripts. 

    **Should the research team use the tool considering their findings? Explain your answer 
    considering the benefits and drawbacks in going forward with using the tool.**"""
    )

    a2 = st.text_area("Your response to Question 2", key="a2", height=200, label_visibility="collapsed")
