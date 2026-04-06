import streamlit as st
from google import genai
from google.genai.types import GenerateContentConfig

st.title("7.2 Writing Successful Biomedical AI Proposals")

st.markdown(
    """
In this activity, you will provide a short description of a hypothetical research topic that you are interested in, and will be presented with a corresponding NIH-style project summary.

"""
)

st.markdown("## :material/psychology: Try it: Generate an NIH-Style Project Summary")
st.caption(
    "**Note:** The following activity uses a generative AI model to provide suggestions and feedback. This is an educational tool, not a peer review system."
)

# LLM setup
gemini_model = "gemini-2.0-flash"
gemini_system_instruction_filepath = "assets/llm/7.2_gemini_system_instruction.txt"
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
        with st.spinner("Analyzing your research topic...", show_time=True):
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


statement = st.text_area(
    "Describe your research idea. **The more details, the better.**",
    key="experiment_input",
    height=200,
    on_change=submit,
)

if st.session_state.output != "":
    st.markdown("---")
    st.markdown("### Hypothetical Project Summary for NIH-Style Proposal:")
    st.markdown(st.session_state.output)
