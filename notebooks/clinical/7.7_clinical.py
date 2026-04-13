import streamlit as st

st.title("7.7 Responsible Biomedical AI Research")

st.markdown(
    """
In this activity, you will explore a case of research misconduct, identify the ethical concerns it raises, and ways to navigate it.

"""
)

st.markdown("## :material/psychology: Try it: Navigating Research Misconduct")
st.caption(
    "**Note:** The following activity uses a generative AI model to provide suggestions and feedback. This is an educational tool, not a peer review system."
)

# LLM setup
model_id = "gemma-3-27b-it"
system_instruction_filepath = "assets/llm/7.7_gemini_system_instruction.txt"
navigator_api_key = st.secrets["NAVIGATOR_TOOLKIT_API_KEY"]

with open(system_instruction_filepath, "r") as f:
    system_instruction = f.read()

from openai import OpenAI
client = OpenAI(api_key=navigator_api_key, base_url="https://api.ai.it.ufl.edu/v1")

if "input" not in st.session_state:
    st.session_state.input = ""

if "output" not in st.session_state:
    st.session_state.output = ""

feedback_container = st.container(border=True)




def submit():
    st.session_state.input = st.session_state.experiment_input

    with feedback_container:
        with st.spinner("Analyzing your response...", show_time=True):
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": st.session_state.input}
                    ]
                )
                st.session_state.output = response.choices[0].message.content
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ **Rate Limit Reached**: The NaviGator API is receiving too many requests. Please wait a few seconds and try again.")
                else:
                    st.error(f"Error: {e}")
                st.session_state.output = ""


st.markdown("**Instructions:** Read the following case and answer the questions below.")
st.info(
    "**Case:** A clinical trial was conducted by a well-known pharmaceutical company in collaboration with the University of Oxbridge to assess the efficacy of a new cancer drug. The results of the study were published in a high-impact scientific journal and showed positive outcomes, suggesting that the drug significantly improved patient survival rates.  Dr. Smith, a postdoctoral researcher in the university's medical department, was part of the research team responsible for collecting and analyzing patient data. During a routine review of the data files, Dr. Smith noticed irregularities in the data sets, including duplicated data points and altered timestamps. After further investigation, Dr. Smith found that a significant portion of the data had been falsified to show better outcomes than observed. Dr. Smith reported these findings to the principal investigator, Dr. Johnson, who insisted that the discrepancies were due to clerical errors and urged Dr. Smith to ignore them. Feeling pressured, Dr. Smith remained silent, and the data remained in the published study."
)
st.markdown("")
st.markdown(
    "In the text box below, answer the following questions (as a single response). Personalized feedback and potential measures to prevent such future misconduct will be provided."
)
st.markdown("**Q1. What is the research misconduct in this case?**")
st.markdown("**Q2. Which of Dr. Johnson's and/or Dr. Smith's actions were unethical?**")

statement = st.text_area(
    "Provide your responses to Q1 and Q2:",
    key="experiment_input",
    height=200
)

if st.button("✅ Submit", type="primary", use_container_width=True):
    submit()

if st.session_state.output != "":
    st.markdown("---")
    st.markdown("### Evaluation")
    st.markdown(st.session_state.output)
