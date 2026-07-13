import streamlit as st
import os
import sys
import json
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
    background-color: var(--gator-blue) !important;
    color: white !important;
    border-color: var(--gator-blue) !important;
}
button[kind="primary"]:hover {
    background-color: #D6390E !important;
    border-color: #D6390E !important;
}

/* Chat Input border styling */
[data-testid="stChatInput"] {
    border-color: rgba(128,128,128,0.2) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--uf-orange) !important;
}

/* Toggle tab button */
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

/* Hide the underlying Streamlit toggle button */
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

N_LESSONS_PER_MODULE = 7

MODULE_NAMES = [
    "Module 1 - Fundamentals",
    "Module 2 - Alignment",
    "Module 3 - Data",
    "Module 4 - Machine Learning",
    "Module 5 - Images",
    "Module 6 - Generative AI",
    "Module 7 - Impact Project",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_notebook_path(lesson_id):
    return os.path.join(
        BASE_DIR,
        "notebooks",
        "clinical",
        f"{lesson_id}_clinical.py",
    )


def get_module_lessons(module_number):
    return [
        f"{module_number}.{lesson_number}"
        for lesson_number in range(1, N_LESSONS_PER_MODULE + 1)
        if os.path.exists(get_notebook_path(f"{module_number}.{lesson_number}"))
    ]


def load_notebook_context(lesson_id):
    if not lesson_id:
        return None

    context_path = os.path.join(
        BASE_DIR,
        "assets",
        "notebook_context",
        f"{lesson_id}_clinical.json",
    )

    if not os.path.exists(context_path):
        return None

    try:
        with open(context_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"context_error": f"Could not load notebook context: {e}"}

sidebar = {}

# ── Notebook Wrapping & Rendering Logic ────────────────────────────────━━━━
def render_home_page():
    st.title("📚 AI Passport: Module Index")
    st.info("Choose a module to open its lessons and activities.")

    cols = st.columns(2)
    for index, page in enumerate(module_pages):
        with cols[index % 2]:
            if st.button(
                page.title,
                key=f"btn_{page.url_path}",
                type="primary",
                use_container_width=True,
            ):
                st.switch_page(page)

def get_module_number(url_path):
    if not url_path or not url_path.startswith("module-"):
        return None

    try:
        return int(url_path.removeprefix("module-"))
    except ValueError:
        return None


def get_active_lesson(url_path):
    module_number = get_module_number(url_path)
    if module_number is None:
        return None

    lessons = get_module_lessons(module_number)
    if not lessons:
        return None

    selected_lesson = st.session_state.get(f"module_{module_number}_lesson")
    return selected_lesson if selected_lesson in lessons else lessons[0]


def get_lesson_label(lesson_id):
    context = load_notebook_context(lesson_id)
    if context and context.get("title"):
        return f"{lesson_id} — {context['title']}"
    return f"Lesson {lesson_id}"


def render_module_page():
    current_url_path = getattr(pg, "url_path", "")
    module_number = get_module_number(current_url_path)

    if module_number is None or not 1 <= module_number <= len(MODULE_NAMES):
        st.error("Module not found.")
        return

    if st.button("← All modules", key=f"home_from_module_{module_number}"):
        st.switch_page(home_page)

    st.title(MODULE_NAMES[module_number - 1])
    lessons = get_module_lessons(module_number)

    if not lessons:
        st.info("Lessons for this module are coming soon.")
        return

    selected_lesson = st.selectbox(
        "Choose a lesson",
        options=lessons,
        format_func=get_lesson_label,
        key=f"module_{module_number}_lesson",
    )
    st.divider()

    # Load and run the selected lesson content.
    if selected_lesson:
        nb_path = get_notebook_path(selected_lesson)
        
        if os.path.exists(nb_path):
            with open(nb_path, "r", encoding="utf-8") as f:
                code = f.read()
                
                # Compatibility layer for Jupyter/IPython functions
                def display(*args, **kwargs):
                    for arg in args:
                        st.write(arg)
                
                class ImageCompatibility:
                    def __init__(self, filename=None, data=None, width=None, height=None, **kwargs):
                        self.filename = filename
                        self.data = data
                        self.width = width
                    def _repr_png_(self): return self.data

                # Create isolated global namespace for the notebook execution
                exec_globals = globals().copy()
                exec_globals.update({
                    "display": display,
                    "Image": ImageCompatibility,
                })
                
                try:
                    exec(code, exec_globals)
                except (ImportError, ModuleNotFoundError) as e:
                    missing_lib = e.name if hasattr(e, "name") else str(e)
                    st.warning(f"⚠️ **Requirement Missing**: This lab requires `{missing_lib}`, which is not installed in the cloud environment.")
                    st.info("Some libraries (like TensorFlow) are only supported on specific Python versions. We recommend running this lab locally using an environment with the correct dependencies.")
                    st.code(f"pip install {missing_lib}", language="bash")
                except Exception as e:
                    st.error(f"Error executing notebook: {e}")
                    st.exception(e)
        else:
            st.warning(f"Notebook not found!")
            st.info(f"Looking for: `{nb_path}`")
            st.caption("Please ensure lesson files follow the `{module}.{lesson}_clinical.py` pattern.")

# ── Multipage Registration ──────────────────────────────────────────────────
home_page = st.Page(page=render_home_page, title="Home", icon="🏠", default=True)
module_pages = [
    st.Page(
        page=render_module_page,
        title=module_name,
        icon="📝",
        url_path=f"module-{module_idx + 1}",
    )
    for module_idx, module_name in enumerate(MODULE_NAMES)
]

sidebar["Home"] = [home_page]
sidebar["Modules"] = module_pages

pg = st.navigation(sidebar, position="hidden")

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

/* Fixed chat panel: scrollable, with sticky input at bottom */
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
    padding: 1rem 1.25rem 0 1.25rem !important;
    border-left: 3px solid #0021A5 !important;
    box-shadow: -6px 0 20px rgba(0,0,0,0.08) !important;
    z-index: 999990 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}}

/* Pin the stBottom (chat input wrapper) to the bottom of the scroll container */
[data-testid="stColumn"]:has(#aip-chat-panel-marker) [data-testid="stBottom"] {{
    position: sticky !important;
    bottom: 0 !important;
    z-index: 10 !important;
    background-color: #F8F9FA !important;
    padding: 0.5rem 0 0.75rem 0 !important;
}}

#aip-toggle-tab {{
    right: {right_pos};
}}

</style>
<div id="aip-toggle-tab" title="Toggle AI Guide">{arrow_char}</div>
""", unsafe_allow_html=True)

# JS for sidebar toggle - robust version with retry
components.html(f"""
<script>
(function() {{
    var parentDoc = window.parent.document;

    function attachToggle() {{
        var oldTab = parentDoc.getElementById('aip-toggle-tab');
        if (!oldTab) {{ setTimeout(attachToggle, 200); return; }}

        // Clone to remove stale listeners
        var newTab = oldTab.cloneNode(true);
        oldTab.parentNode.replaceChild(newTab, oldTab);

        newTab.addEventListener('click', function(e) {{
            e.preventDefault();
            e.stopPropagation();
            clickToggleBtn();
        }});
    }}

    function clickToggleBtn() {{
        // Find by aria-label or by searching inside toggle-btn-container
        var container = parentDoc.getElementById('toggle-btn-container');
        if (container) {{
            var btn = container.querySelector('button');
            if (btn) {{ btn.click(); return; }}
        }}
        // Fallback: find any button whose text includes 'Toggle'
        var allBtns = parentDoc.querySelectorAll('button');
        for (var i = 0; i < allBtns.length; i++) {{
            if (allBtns[i].innerText.indexOf('Toggle') !== -1) {{
                allBtns[i].click();
                return;
            }}
        }}
    }}

    // Run after a short delay to ensure DOM is ready
    setTimeout(attachToggle, 300);
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

# ── Layout: Main Content + Chat ──────────────────────────────────────────────
if st.session_state["_chat_open"]:
    col_main, col_chat = st.columns([7, 1])
    with col_chat:
        st.markdown('<div id="aip-chat-panel-marker"></div>', unsafe_allow_html=True)
        render_ai_guide(
            navigator_api_key=st.secrets.get("NAVIGATOR_TOOLKIT_API_KEY"),
            context_fn=lambda: {
                "current_page": getattr(pg, "title", "AIPassport Home"),
                "url_path": getattr(pg, "url_path", ""),
                "active_lesson": get_active_lesson(getattr(pg, "url_path", "")),
                "platform": "AI Passport",
                "notebook_context": load_notebook_context(
                    get_active_lesson(getattr(pg, "url_path", "")),
                ),
            },
        )
else:
    col_main = st.container()

with col_main:
    pg.run()
