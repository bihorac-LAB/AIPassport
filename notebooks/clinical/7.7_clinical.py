import streamlit as st
from google import genai
from google.genai.types import GenerateContentConfig

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
gemini_model = "gemini-2.0-flash"
gemini_system_instruction_filepath = "assets/llm/7.7_gemini_system_instruction.txt"
gemini_api_key = st.secrets["GEMINI_API_KEY"]

with open(gemini_system_instruction_filepath, "r") as f:
    gemini_system_instruction = f.read()

client = genai.Client(api_key=gemini_api_key)

if "input" not in st.session_state:
    st.session_state.input = ""

if "output" not in st.session_state:
    st.session_state.output = ""

feedback_container = st.container(border=True)


from google.genai.errors import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_429(exception):
    return isinstance(exception, ClientError) and "429" in str(exception)

@retry(
    retry=retry_if_exception(is_429),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_with_retry(client, model, contents, config):
    return client.models.generate_content(model=model, contents=contents, config=config)

def submit():
    st.session_state.input = st.session_state.experiment_input
    st.session_state.experiment_input = ""

    with feedback_container:
        with st.spinner("Analyzing your response...", show_time=True):
            try:
                response = generate_with_retry(
                    client=client,
                    model=gemini_model,
                    contents=st.session_state.input,
                    config=GenerateContentConfig(
                        system_instruction=gemini_system_instruction,
                    ),
                )
                st.session_state.output = response.text
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ **Rate Limit Reached**: The Gemini API is currently receiving too many requests. Please wait a few seconds and try again.")
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
    height=200,
    on_change=submit,
)

if st.session_state.output != "":
    st.markdown("---")
    st.markdown("### Evaluation")
    st.markdown(st.session_state.output)
