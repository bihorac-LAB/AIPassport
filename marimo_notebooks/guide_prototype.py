# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
#     "openai>=1.0",
# ]
# ///
"""AIP Guide chatbot prototype (marimo app mode).

A minimal, standalone proof-of-concept for putting the AIP Guide into a marimo
app using `mo.ui.chat`. It talks to UF's NaviGator gateway (OpenAI-compatible),
exactly like the Streamlit app does today.

Run it:

    export NAVIGATOR_TOOLKIT_API_KEY=...        # never commit this
    uvx marimo==0.17.8 run marimo_notebooks/guide_prototype.py   # app mode
    uvx marimo==0.17.8 edit marimo_notebooks/guide_prototype.py  # editor

The key is read from the environment, so this runs locally now and drops onto a
server (`marimo run` / FastAPI mount) unchanged. Do NOT bake the key into a
static WASM export -- it would be publicly readable.
"""

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import os

    import marimo as mo

    return mo, os


@app.cell
def _():
    # These mirror aipassport_config.py (the Streamlit app's single source of
    # truth). On a server this notebook could import that module directly; they
    # are inlined here so the prototype runs standalone from any directory.
    DEFAULT_MODEL = "gemma-4-31b-it"
    NAVIGATOR_TOOLKIT_BASE_URL = "https://api.ai.it.ufl.edu/v1"
    AI_GUIDE_SYSTEM_PROMPT = (
        "You are the AIP Guide, a helpful AI tutor for the AIPassport "
        "educational platform. Be concise, encouraging, and accurate."
    )
    AI_GUIDE_PLACEHOLDER = "Ask the AIP Guide anything..."
    GATOR_BLUE = "#0021A5"
    UF_ORANGE = "#FA4616"
    return (
        AI_GUIDE_PLACEHOLDER,
        AI_GUIDE_SYSTEM_PROMPT,
        DEFAULT_MODEL,
        GATOR_BLUE,
        NAVIGATOR_TOOLKIT_BASE_URL,
        UF_ORANGE,
    )


@app.cell
def _(os):
    import tomllib
    from pathlib import Path

    def read_navigator_key():
        # 1) environment variable -- works locally and drops onto a server.
        #    LITELLM_API_KEY is the gateway key; NAVIGATOR_TOOLKIT_API_KEY is
        #    kept as a fallback name for the same secret.
        for env_name in ("LITELLM_API_KEY", "NAVIGATOR_TOOLKIT_API_KEY"):
            key = os.environ.get(env_name)
            if key:
                return key
        # 2) .streamlit/secrets.toml -- the same gitignored secret file the
        #    Streamlit app already uses, so the key is stored in one place.
        candidates = [Path.cwd() / ".streamlit" / "secrets.toml"]
        if "__file__" in globals():
            candidates.append(
                Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
            )
        for secrets_path in candidates:
            if secrets_path.is_file():
                data = tomllib.loads(secrets_path.read_text())
                for key_name in ("LITELLM_API_KEY", "NAVIGATOR_TOOLKIT_API_KEY"):
                    if data.get(key_name):
                        return data[key_name]
        return None

    api_key = read_navigator_key()
    guide_available = bool(api_key)
    return api_key, guide_available


@app.cell
def _(GATOR_BLUE, UF_ORANGE, mo):
    header = mo.md(
        f"""
        <div style="border-left:6px solid {UF_ORANGE};padding:.5rem 1rem;">
          <h1 style="color:{GATOR_BLUE};margin:.1rem 0;">AIP Guide</h1>
          <p style="margin:.1rem 0;color:#555;">
            Your AI tutor for the AI Passport course &mdash; ask about any lesson.
            &nbsp;<a href="./" target="_blank" rel="noopener"
                    style="color:{GATOR_BLUE};font-weight:600;">Open full screen &#8599;</a>
          </p>
        </div>
        """
    )
    header
    return


@app.cell
def _(guide_available, mo):
    # Show clearly whether a live key is wired up, without crashing when it isn't.
    status = (
        mo.callout(
            mo.md("**NaviGator connected.** The Guide is answering live."),
            kind="success",
        )
        if guide_available
        else mo.callout(
            mo.md(
                "**Offline preview.** `NAVIGATOR_TOOLKIT_API_KEY` is not set, so "
                "the Guide echoes a placeholder instead of calling NaviGator.\n\n"
                "Set the key in your environment to enable live answers:\n\n"
                "```bash\nexport NAVIGATOR_TOOLKIT_API_KEY=...\n```"
            ),
            kind="warn",
        )
    )
    status
    return


@app.cell
def _(
    AI_GUIDE_SYSTEM_PROMPT,
    DEFAULT_MODEL,
    NAVIGATOR_TOOLKIT_BASE_URL,
    api_key,
    guide_available,
    mo,
):
    if guide_available:
        # NaviGator is OpenAI-compatible, so mo.ai.llm.openai points straight at it.
        guide_model = mo.ai.llm.openai(
            DEFAULT_MODEL,
            system_message=AI_GUIDE_SYSTEM_PROMPT,
            api_key=api_key,
            base_url=NAVIGATOR_TOOLKIT_BASE_URL,
        )
    else:
        # Offline stub so the chat still renders and "responds" without a key.
        def guide_model(messages, config):
            last = messages[-1].content if messages else ""
            return (
                "The AIP Guide is in offline preview. Set "
                "`NAVIGATOR_TOOLKIT_API_KEY` to get real answers.\n\n"
                f"> You asked: {last}"
            )

    return (guide_model,)


@app.cell
def _(GATOR_BLUE, mo):
    # mo.ui.chat always opens with an empty transcript, so we render the Guide's
    # opening message as a bubble just above it to give the chat a starting point.
    greeting = mo.md(
        f"""
        <div style="background:#eef2ff;border-left:4px solid {GATOR_BLUE};
                    border-radius:.5rem;padding:.75rem 1rem;margin:.25rem 0 .75rem;">
          <strong style="color:{GATOR_BLUE};">AIP Guide</strong><br/>
          Hi! I'm your AI Passport tutor. Ask me to explain a concept, walk through
          a lesson activity, or check your understanding. Pick a starter question
          below, or just type your own.
        </div>
        """
    )
    greeting
    return


@app.cell
def _(guide_model, mo):
    chat = mo.ui.chat(
        guide_model,
        prompts=[
            "What is the difference between AI and machine learning?",
            "Explain overfitting in simple terms.",
            "How do I read a confusion matrix?",
            "Quiz me on this lesson.",
        ],
        config={"max_tokens": 800, "temperature": 0.5},
        max_height=520,
    )
    chat
    return (chat,)


if __name__ == "__main__":
    app.run()
