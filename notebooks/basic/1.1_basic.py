import streamlit as st
from streamlit_timeline import timeline
import json

st.title("1.1 Demystifying Artificial Intelligence (Clinical)")

header_cols = st.columns(3)
with header_cols[1]:
    st.image("assets/images/headers/1.1_header.png", width=300)

st.markdown(
    """
Artificial intelligence can often seem mysterious, complex, or even magical—but at its core, AI is a 
            tool built by humans to solve specific problems. This assignment is designed to help 
            demystify AI by grounding it in history and critical thinking. 
            
First, you’ll explore an **Interactive AI Timeline** that highlights major milestones in the 
development of AI, providing a sense of how the field has evolved over time. 

Next, you will test your assumptions and beliefs about AI with **AI: Fact or Fiction?**, an 
interactive activity that provides immediate feedback to separate myth from the reality

Together, these activities aim to build your foundational understanding and make AI feel a little 
less like science fiction and a little more like science.
"""
)


# @st.cache_data
def load_timeline_data():
    timeline_data = None
    with open("assets/widgets/1.1_ai_timeline.json", "r") as f:
        timeline_data = f.read()
    return timeline_data


timeline_data = load_timeline_data()


with st.container(border=True):
    "## :material/touch_app: Interactive AI Timeline",

    st.markdown(
        """
    **Artificial Intelligence (AI)** has evolved from a bold academic concept into a transformative
    force reshaping science, medicine, industry, and everyday life. This interactive timeline 
    explores key milestones in the history of AI—from the theoretical groundwork laid by Alan Turing 
    in the 1950s, to the explosive rise of generative models and multimodal agents in the 2020s.
    
    As you scroll through the AI timeline, consider how each technological breakthrough not only 
    eflects the state of computing at the time but also contributes to a larger story of increasing 
    intelligence, autonomy, and impact.
"""
    )

    with st.container(border=True):
        timeline(timeline_data, height=600)


def get_property(property):
    try:
        return property
    except KeyError:
        return None


with st.container(border=True):
    st.markdown("## :material/gavel: AI: Fact or Fiction?")
    st.caption(
        "**Note:** The following activity uses generative AI to automatically provide feedback. Accuracy and appropriateness of responses is not guaranteed."
    )

    st.markdown(
        """
    Artificial Intelligence can often feel like a mysterious black box—surrounded by hype, myths, and 
    sometimes even fear. While some statements about AI reflect real technical capabilities and 
    limitations, others are based on outdated ideas or science fiction. As AI continues to grow more 
    powerful and visible in our lives, it becomes increasingly important to distinguish fact from 
    fiction.

    This interactive tool invites you to put your assumptions to the test. Enter any statement you’ve 
    heard or believed about AI—whether technical or philosophical—and our built-in AI assistant will 
    help you evaluate whether it’s accurate, misleading, or just plain wrong.

    """
    )

    # LLM configuration
    model_id = "gemma-3-27b-it"
    system_instruction_filepath = "assets/llm/1.1_gemini_system_instruction.txt"
    gemini_response_schema_filepath = "assets/llm/1.1_gemini_response_schema.json"
    navigator_api_key = st.secrets["NAVIGATOR_TOOLKIT_API_KEY"]

    with open(system_instruction_filepath, "r") as f:
        system_instruction = f.read()

    with open(gemini_response_schema_filepath, "r") as f:
        gemini_response_schema = json.load(f)

    def init_session():
        if "statement" not in st.session_state:
            st.session_state.statement = ""

        if "verdict" not in st.session_state:
            st.session_state.verdict = ""

    def submit():
        st.session_state.statement = st.session_state.text_input
        st.session_state.text_input = ""

        with llm_container:
            with st.spinner("Thinking...", show_time=True):
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": st.session_state.statement}
                    ],
                    response_format={"type": "json_object"}
                )

        st.session_state.verdict = json.loads(response.choices[0].message.content)

    init_session()
    from openai import OpenAI
    client = OpenAI(api_key=navigator_api_key, base_url="https://api.ai.it.ufl.edu/v1")

    llm_container = st.container(border=True)
    with llm_container:

        statement = st.text_input(
            "Enter any statement about AI you'd like to evaluate.",
            placeholder="e.g., AI can think like a human.",
            key="text_input",
            on_change=submit,
        )

        if st.session_state.verdict != "":
            V = st.session_state.verdict

            verdict = get_property(V["verdict"])
            explanation = get_property(
                V["verdict_explanation"]["verdict_explanation_summary"]
            )
            changes = get_property(V["verdict_explanation"]["potential_future_changes"])
            limitations = get_property(V["verdict_explanation"]["limitations"])
            challenges = get_property(V["verdict_explanation"]["challenges"])
            requirements = get_property(V["verdict_explanation"]["future_requirements"])

            real_world_examples = get_property(V["real_world_examples"])
            research_examples = get_property(V["research_papers"])
            ml_concepts = get_property(V["high_level_machine_learning_concepts"])
            datasets = get_property(V["relevant_public_datasets"])
            research_directions = get_property(V["potential_research_directions"])

            st.markdown(f'Is "**{st.session_state.statement}**" fact or fiction?')

            fn, icon = None, None
            if verdict in ["FACT", "MOSTLY FACT", "CURRENTLY FACT"]:
                icon = ":material/thumb_up:"
                fn = st.success
            elif verdict in ["FICTION", "MOSTLY FICTION", "CURRENTLY FICTION"]:
                icon = ":material/thumb_down:"
                fn = st.error
            elif verdict in ["MISLEADING", "NOT A STATEMENT", "MALICIOUS"]:
                icon = ":material/report:"
                fn = st.warning
            else:
                icon = ":material/question_mark:"
                fn = st.info

            # verdict_text = f"# {icon} {verdict}\n\n{explanation}"
            ai_concept_str = ", ".join(ml_concepts)

            verdict_text = f"""
                **Statement:** {st.session_state.statement} \n\n
                **Related AI concepts:** {ai_concept_str} \n\n
                # {icon} {verdict} 
                {explanation}
            """

            fn(verdict_text)

            # st.markdown(f"**Related AI/ML Concepts:** {ai_concept_str}\n\n")

            st.info("Click the tabs below for more information about your statement.")

            with st.expander(
                "Real-World Biomedical Applications", icon=":material/build:"
            ):
                for i, example in enumerate(real_world_examples):
                    st.markdown(f"{i+1}. {example}")

            with st.expander(
                "Limitations, Challenges, and Future Requirements ",
                icon=":material/build:",
            ):
                st.markdown(limitations)
                st.markdown(challenges)
                st.markdown(requirements)

            with st.expander("Research Opportunities", icon=":material/build:"):
                cols_ro = st.columns(len(research_directions), border=False)
                for i, example in enumerate(research_directions):
                    with cols_ro[i]:
                        st.markdown(f"{example}")

            with st.expander("AI Concepts", icon=":material/build:"):
                cols_ac = st.columns(len(ml_concepts), border=False)
                for i, example in enumerate(ml_concepts):
                    with cols_ac[i]:
                        st.markdown(f"**{example}**")

            with st.expander("Datasets", icon=":material/build:"):
                cols_d = st.columns(len(datasets), border=False)
                for i, example in enumerate(datasets):
                    with cols_d[i]:
                        st.markdown(f"{example}")

            with st.expander("Further Reading", icon=":material/build:"):
                for i, example in enumerate(research_examples):
                    st.markdown(f"{i+1}. {example}")
