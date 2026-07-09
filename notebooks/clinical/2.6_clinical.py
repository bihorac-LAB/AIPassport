import streamlit as st

st.title("2.6 Human-AI Collaboration in Biomedicine (Clinical)")

with st.container(border=True):
    st.markdown("### Question 1")
    st.markdown(
        """
    Identify and list all the human-AI collaboration tools currently at use in your clinical 
    practice. How do you or your colleagues use these tools. What are their benefits and drawbacks? 
    Explain how you manage these systems, and the data created from them. 
"""
    )

    a1 = st.text_area("Your response to Question 1", key="a1", height=200, label_visibility="collapsed")

st.markdown("---")

with st.container(border=True):
    st.markdown("### Question 2")

    st.markdown(
        """
    Consider the following case:

    A large hospital has implemented the use of an AI transcription system for hospital staff to use 
    in care settings. The idea is that the AI tool will allow more accurate notes to be input into 
    patient records. After testing the tool in various care settings for about a month, hospital 
    staff began reviewing the transcripts and notes from the tool. To their dismay, they found that 
    although the tool transcribed patient interviews, it also:
    - Made up segments of conversations that did not happen.
    - Made certain patients appear to be being aggressive with staff, when this behavior was not present; and 
    - Was not as accurate in conversations with patients with accents, from the around the US or otherwise.

    **What are the possible routes the hospital could take after reviewing the transcription data? 
    What should the hospital do?  Explain your answer.**"""
    )

    a2 = st.text_area("Your response to Question 2", key="a2", height=200, label_visibility="collapsed")
