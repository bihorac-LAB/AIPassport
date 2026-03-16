"""chat_widget.py – The main render_chat() entry point."""
from __future__ import annotations

from typing import Callable, Optional

import streamlit as st

from .api_client import BrainClient
from .renderers import render_citations, render_suggested_actions

_HISTORY_KEY = "aip_chat_history"
_CONV_ID_KEY = "aip_conv_id"


def _init_state(app_id: str) -> None:
    import uuid
    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []
    if _CONV_ID_KEY not in st.session_state:
        st.session_state[_CONV_ID_KEY] = str(uuid.uuid4())


def _get_client() -> BrainClient:
    return BrainClient(
        base_url=st.secrets["BRAIN_API_URL"],
        client_id=st.secrets["BRAIN_CLIENT_ID"],
        client_secret=st.secrets["BRAIN_CLIENT_SECRET"],
    )


def render_chat(
    app_id: str,
    context_fn: Optional[Callable[[], dict]] = None,
    placeholder_text: str = "Ask a question…",
    title: str = "AIP Guide",
) -> None:
    """Render the scrollable chat panel.

    The ``context_fn`` may return a dict that optionally contains:
      - ``screen_image`` (str): base64 PNG of the current chart
      - ``live_state`` (str): human-readable live widget values
      - Any other page-level metadata

    The CSS in the host app's streamlit_app.py handles viewport confinement
    and scroll — messages render flat here.
    """
    _init_state(app_id)

    if title:
        st.subheader(f"💬 {title}", divider="blue")

    # ── scrollable message history ───────────────────────────────────────────
    # Height of 70vh gives it plenty of room while leaving space for the input at the bottom
    history_box = st.container(height=650, border=False)

    with history_box:
        if not st.session_state[_HISTORY_KEY]:
            st.caption("No messages yet — ask a question below 👇")

        for msg in st.session_state[_HISTORY_KEY]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant":
                    render_citations(msg.get("citations", []))

    # Quick-action chips — always visible above the input
    cols = st.columns(2)
    if cols[0].button("🖥️ What's on my screen?", width="stretch"):
        st.session_state["_quick_action"] = "Explain what's on my screen based on the current charts and values."
        st.rerun()
    if cols[1].button("💡 How do I use this activity?", width="stretch"):
        st.session_state["_quick_action"] = "How do I use this activity and what controls are available?"
        st.rerun()

    user_input = st.chat_input(placeholder_text)
    
    # Check if a quick action button was clicked in the previous run
    if "_quick_action" in st.session_state:
        user_input = st.session_state.pop("_quick_action")

    if not user_input:
        return

    st.session_state[_HISTORY_KEY].append({"role": "user", "content": user_input})

    # Gather context — context_fn may include screen_image + live_state
    full_context = context_fn() if context_fn else {}
    screen_image = full_context.pop("screen_image", None)

    with st.spinner("Thinking…"):
        try:
            client = _get_client()
            result = client.chat(
                app_id=app_id,
                messages=st.session_state[_HISTORY_KEY],
                context=full_context,
                conversation_id=st.session_state[_CONV_ID_KEY],
                screen_image=screen_image,
            )
        except Exception as exc:
            err_str = str(exc)
            if "503" in err_str or "quota" in err_str.lower() or "over capacity" in err_str.lower():
                st.warning("⏳ The AI tutor is temporarily at capacity. Please wait a moment and try again.")
            else:
                st.error(f"Could not reach the AI backend: {exc}")
            st.session_state[_HISTORY_KEY].pop()
            return

    answer = result.get("answer_markdown", "*(no answer)*")
    citations = result.get("citations", [])

    st.session_state[_HISTORY_KEY].append(
        {"role": "assistant", "content": answer, "citations": citations}
    )
    st.rerun()
