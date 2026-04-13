import streamlit as st
import time

st.title("7.1 Designing Biomedical AI Experiments (Basic)")

header_cols = st.columns(3)
with header_cols[1]:
    st.image("assets/images/headers/7.1_header.png")

st.markdown(
    """
Biomedical researchers are increasingly looking to incorporate artificial intelligence into their research programs.
But designing a strong AI-enabled experiment requires more than just selecting a model — it means establishing clear
hypotheses, understanding data limitations, selecting appropriate AI techniques, and planning for baseline and
comparative evaluations.

In this activity, you'll receive personalized, automated feedback on your **experiment design ideas**. Whether you have
a specific project in mind or are brainstorming how to integrate AI into your existing work, this tool will help you
refine your thinking and increase the feasibility and clarity of your approach.

"""
)

st.markdown("## :material/psychology: Try it: Describe your Biomedical AI Experiment Idea")
st.caption(
    "**Note:** The following activity uses a generative AI model to provide suggestions and feedback. This is an educational tool, not a peer review system."
)

# LLM setup
model_id = "gemma-3-27b-it"
system_instruction_filepath = "assets/llm/7.1_gemini_system_instruction.txt"
navigator_api_key = st.secrets["NAVIGATOR_TOOLKIT_API_KEY"]

with open(system_instruction_filepath, "r") as f:
    base_instruction = f.read()

system_instruction = """Respond in clear, readable markdown. Do NOT return JSON or code blocks.
Use headers (###), bullet points, and bold text to organize your feedback.\n\n""" + base_instruction

from openai import OpenAI
client = OpenAI(api_key=navigator_api_key, base_url="https://api.ai.it.ufl.edu/v1")

if "experiment_idea" not in st.session_state:
    st.session_state.experiment_idea = ""

if "experiment_feedback" not in st.session_state:
    st.session_state.experiment_feedback = ""

if "_pending" not in st.session_state:
    st.session_state._pending = False

statement = st.text_area(
    "Describe your idea for a biomedical research experiment involving AI. **The more details, the better.**",
    placeholder="e.g., I want to use deep learning to predict postoperative complications based on EHR data and imaging...",
    key="experiment_input",
    height=200
)

if st.button("✅ Submit", type="primary", use_container_width=True):
    st.session_state.experiment_idea = st.session_state.experiment_input
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
                        {"role": "user", "content": st.session_state.experiment_idea}
                    ]
                )
            full_response = response.choices[0].message.content
            curr = ""
            for line in full_response.split("\n"):
                curr += line + "\n"
                placeholder.markdown(curr + "▌")
                time.sleep(0.04)
            placeholder.markdown(full_response)
            st.session_state.experiment_feedback = full_response
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.experiment_feedback = ""

if st.session_state.experiment_feedback:
    st.markdown("---")
    st.markdown("# :material/lightbulb: AI Feedback on Your Experimental Design")
    st.markdown(st.session_state.experiment_feedback)
