"""renderers.py – Streamlit rendering helpers for citations and suggested actions."""
import streamlit as st


def render_citations(citations: list[dict]) -> None:
    """Render a collapsible citations block.

    Each citation dict may have: title, url, snippet, source.
    """
    if not citations:
        return
    with st.expander("📚 Sources", expanded=False):
        for i, c in enumerate(citations, 1):
            title = c.get("title", f"Source {i}")
            url = c.get("url")
            snippet = c.get("snippet", "")
            if url:
                st.markdown(f"**{i}. [{title}]({url})**")
            else:
                st.markdown(f"**{i}. {title}**")
            if snippet:
                st.caption(snippet)


def render_suggested_actions(actions: list[dict], on_action) -> None:
    """Render suggested-action buttons.

    ``on_action(action_dict)`` is called when the user clicks a button.
    """
    if not actions:
        return
    cols = st.columns(min(len(actions), 3))
    for col, action in zip(cols, actions):
        label = action.get("label", "Action")
        with col:
            if st.button(label, use_container_width=True, key=f"action_{label}"):
                on_action(action)
