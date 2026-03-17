import streamlit as st
import os
import sys
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Allow internal access to aip-streamlit-chatui
# ---------------------------------------------------------------------------
_chatui_pkg = os.path.join(os.path.dirname(__file__), "packages")
if os.path.isdir(_chatui_pkg):
    sys.path.insert(0, _chatui_pkg)

from aip_chat_simple import render_ai_guide

st.set_page_config(
    page_title="AI Passport Notebooks (Dev)",
    page_icon="📚",
    layout="wide",
)

# ── CSS: right chat column is sticky and stays in view ─────────
st.markdown("""
<style>
/* IC3 / UF Brand Variables */
:root {
    --gator-blue: #0021A5;
    --uf-orange: #FA4616;
    --dark-blue: #001A57;
    --light-blue: #E8EEF7;
}

/* Base Primary Buttons - UF Orange */
button[kind="primary"] {
    background-color: var(--uf-orange) !important;
    color: white !important;
    border-color: var(--uf-orange) !important;
}
button[kind="primary"]:hover {
    background-color: #D6390E !important;
    border-color: #D6390E !important;
}

/* Chat Input styling */
[data-testid="stChatInput"] {
    border-color: rgba(128,128,128,0.2) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--uf-orange) !important;
}

#aip-toggle-tab {
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    z-index: 999999;
    width: 32px;
    height: 64px;
    background-color: var(--gator-blue, #0021A5);
    border: none;
    border-radius: 8px 0 0 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 1.3rem;
    box-shadow: -4px 0 8px rgba(0,0,0,0.15);
    transition: right 0.3s ease, background-color 0.2s;
}
#aip-toggle-tab:hover {
    background-color: var(--dark-blue, #001A57);
}

/* Hide the underlying Streamlit button but keep it clickable for JS */
#toggle-btn-container {
    position: fixed;
    top: -9999px;
    left: -9999px;
    width: 1px;
    height: 1px;
    overflow: hidden;
    opacity: 0;
}
</style>
""", unsafe_allow_html=True)

N_MICROSKILLS_PER_MODULE = 7

MODULE_NAMES = [
    "Module 1 - Fundamentals",
    "Module 2 - Alignment",
    "Module 3 - Data",
    "Module 4 - Machine Learning",
    "Module 5 - Images",
    "Module 6 - Generative AI",
    "Module 7 - Impact Project",
]

# Streamlit demo showed during 3-12-25 Co-I meeting
sidebar = {}

demo_path = "reference/demos/aip_streamlit_demo.py"
if os.path.exists(demo_path):
    sidebar["Demo"] = [
        st.Page(
            page=demo_path,
            title="Streamlit Demo (3-12-25)",
            icon="📘",
        )
    ]

for module_idx, module_name in enumerate(MODULE_NAMES):
    sidebar[module_name] = []

    for microskill_idx in range(N_MICROSKILLS_PER_MODULE):
        for track in ["clinical", "basic"]:
            microskill_path = (
                f"notebooks/{track}/{module_idx + 1}.{microskill_idx + 1}_{track}.py"
            )

            if os.path.exists(microskill_path):
                page = st.Page(
                    page=microskill_path,
                    title=f"Microskill {module_idx + 1}.{microskill_idx + 1} - {track.capitalize()}",
                    icon="📝",
                    url_path=f"{module_idx + 1}.{microskill_idx + 1}_{track}",
                )
                sidebar[module_name].append(page)

pg = st.navigation(sidebar)

# ── Chat Toggle State & Logic ────────────────────────────────────────────────
if "_chat_open" not in st.session_state:
    st.session_state["_chat_open"] = False

chat_open = st.session_state["_chat_open"]
right_pos = "450px" if chat_open else "0px"
arrow_char = "〉" if chat_open else "〈"
padding_right = "480px" if chat_open else "0px"

# Inject dynamic positioning CSS
st.markdown(f"""
<style>
.block-container {{
    padding-right: {padding_right} !important;
    transition: padding-right 0.3s ease;
}}

[data-testid="stColumn"]:has(#aip-chat-panel-marker) {{
    position: fixed !important;
    top: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 450px !important;
    min-width: 450px !important;
    max-width: 450px !important;
    flex: none !important;
    height: 100vh !important;
    background-color: #F8F9FA !important;
    padding: 2rem 1.25rem 1rem 1.25rem !important;
    border-left: 3px solid #0021A5 !important;
    box-shadow: -6px 0 20px rgba(0,0,0,0.08) !important;
    z-index: 999990 !important;
    overflow-y: auto !important;
}}

#aip-toggle-tab {{
    right: {right_pos};
}}
</style>
<div id="aip-toggle-tab" title="Toggle AI Guide">{arrow_char}</div>
""", unsafe_allow_html=True)

# JS to wire the custom toggle tab
components.html(f"""
<script>
(function() {{
    var parentDoc = window.parent.document;
    var oldTab = parentDoc.getElementById('aip-toggle-tab');
    if (!oldTab) return;
    var newTab = oldTab.cloneNode(true);
    oldTab.parentNode.replaceChild(newTab, oldTab);

    function findAndClick() {{
        var container = parentDoc.getElementById('toggle-btn-container');
        if (!container) return;
        var buttons = container.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {{
            buttons[i].click();
            return;
        }}
    }}

    newTab.addEventListener('click', function(e) {{
        e.preventDefault();
        e.stopPropagation();
        findAndClick();
    }});
}})();
</script>
""", height=0, width=0)

# Hidden Streamlit toggle button
with st.container():
    st.markdown('<div id="toggle-btn-container">', unsafe_allow_html=True)
    if st.button("Toggle Chat", key="__aip_toggle__"):
        st.session_state["_chat_open"] = not st.session_state["_chat_open"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Context function ─────────────────────────────────────────────────────────
def _context_fn() -> dict:
    # 'pg' is the StreamlitPage object returned by st.navigation
    # It has attributes like title, icon, url_path
    ctx = {
        "current_page": getattr(pg, "title", "AIPassport Home"),
        "url_path": getattr(pg, "url_path", ""),
        "platform": "AI Passport",
        "description": "Educational platform for AI basics and clinical applications.",
    }
    return ctx

# ── Layout: Main Content + Chat ──────────────────────────────────────────────
if st.session_state["_chat_open"]:
    col_main, col_chat = st.columns([7, 1])
    with col_chat:
        st.markdown('<div id="aip-chat-panel-marker"></div>', unsafe_allow_html=True)
        render_ai_guide(
            gemini_api_key=st.secrets.get("GEMINI_API_KEY"),
            context_fn=_context_fn,
        )
else:
    col_main = st.container()

with col_main:
    pg.run()
