import streamlit as st
import json

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

In this activity, you’ll receive personalized, automated feedback on your **experiment design ideas**. Whether you have
a specific project in mind or are brainstorming how to integrate AI into your existing work, this tool will help you
refine your thinking and increase the feasibility and clarity of your approach.

"""
)

st.markdown(
    "## :material/psychology: Try it: Describe your Biomedical AI Experiment Idea"
)
st.caption(
    "**Note:** The following activity uses a generative AI model to provide suggestions and feedback. This is an educational tool, not a peer review system."
)

# LLM setup
model_id = "gemma-3-27b-it"
system_instruction_filepath = "assets/llm/7.1_gemini_system_instruction.txt"
gemini_response_schema_filepath = "assets/llm/7.1_gemini_response_schema.json"
navigator_api_key = st.secrets["NAVIGATOR_TOOLKIT_API_KEY"]

with open(system_instruction_filepath, "r") as f:
    system_instruction = f.read()

with open(gemini_response_schema_filepath, "r") as f:
    gemini_response_schema = json.load(f)

from openai import OpenAI
client = OpenAI(api_key=navigator_api_key, base_url="https://api.ai.it.ufl.edu/v1")

if "experiment_idea" not in st.session_state:
    st.session_state.experiment_idea = ""

if "experiment_feedback" not in st.session_state:
    st.session_state.experiment_feedback = ""

feedback_container = st.container(border=True)


def submit():
    st.session_state.experiment_idea = st.session_state.experiment_input
    st.session_state.experiment_input = ""

    with feedback_container:
        with st.spinner("Analyzing your experiment design...", show_time=True):
            response = client.models.generate_content(
                model=model_id,
                contents=st.session_state.experiment_idea,
                config=GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_schema=gemini_response_schema,
                    response_mime_type="application/json",
                ),
            )
        st.session_state.experiment_feedback = json.loads(
            json.dumps(json.loads(response.text))
        )


statement = st.text_area(
    "Describe your idea for a biomedical research experiment involving AI. **The more details, the better.**",
    placeholder="e.g., I want to use deep learning to predict postoperative complications based on EHR data and imaging...",
    key="experiment_input",
    height=200,
    on_change=submit,
)

if st.session_state.experiment_feedback != "":
    F = st.session_state.experiment_feedback

    st.markdown("---")
    st.markdown("# :material/lightbulb: AI Feedback on Your Experimental Design")

    if F["summary_sentiment"] == "positive":
        st.success(F["summary"])
    elif F["summary_sentiment"] == "neutral":
        st.warning(F["summary"])
    elif F["summary_sentiment"] == "negative":
        st.error(F["summary"])
    else:
        st.info(F["summary"])

    st.markdown("### Hypothesis")
    st.markdown(F["hypothesis"])
    st.markdown("### AI Techniques")
    st.markdown(F["ai_methods"])
    st.markdown("### Evaluation Plan")
    st.markdown(F["baselines"])
    st.markdown("### Feasibility")
    st.markdown(F["feasibility"])
    st.markdown("### Suggested Improvements")
    st.markdown(F["suggestions"])
    st.markdown("### Potential Pitfalls")
    st.markdown(F["pitfalls"])
    st.markdown("### Relevant Datasets")
    st.markdown(F["datasets"])
    st.markdown("### Related Work")
    st.markdown(F["related_work"])
