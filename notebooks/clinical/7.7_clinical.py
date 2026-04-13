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

if "_pending" not in st.session_state:
    st.session_state._pending = False

statement = st.text_area(
    "Provide your responses to Q1 and Q2:",
    key="experiment_input",
    height=200
)

if st.button("✅ Submit", type="primary", use_container_width=True):
    st.session_state.input = st.session_state.experiment_input
    st.session_state._pending = True
    st.rerun()

if st.session_state._pending:
    st.session_state._pending = False
    with st.container(border=True):
        placeholder = st.empty()
        try:
            with st.spinner("⏳ Generating response...", show_time=True):
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": st.session_state.input}
                    ]
                )
            full_response = response.choices[0].message.content
            curr = ""
            for line in full_response.split("\n"):
                curr += line + "\n"
                placeholder.markdown(curr + "▌")
                import time; time.sleep(0.04)
            placeholder.markdown(full_response)
            st.session_state.output = full_response
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.output = ""

if st.session_state.output:
    st.markdown("---")
    st.markdown("### Evaluation")
    st.markdown(st.session_state.output)
