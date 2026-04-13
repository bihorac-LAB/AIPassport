import streamlit as st

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
model_id = "gemma-3-27b-it"
system_instruction_filepath = "assets/llm/7.2_gemini_system_instruction.txt"
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
    st.session_state.experiment_input = ""

    with feedback_container:
        with st.spinner("Analyzing your research topic...", show_time=True):
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


statement = st.text_area(
    "Describe your research idea. **The more details, the better.**",
    key="experiment_input",
    height=200
)

if st.button("✅ Submit", type="primary", use_container_width=True):
    submit()

if st.session_state.output != "":
    st.markdown("---")
    st.markdown("### Hypothetical Project Summary for NIH-Style Proposal:")
    st.markdown(st.session_state.output)
