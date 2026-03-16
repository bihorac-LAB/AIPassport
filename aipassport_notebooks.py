import streamlit as st
import os

st.set_page_config(
    page_title="AI Passport Notebooks (Dev)",
    page_icon="📚",
    layout="wide",
)

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
sidebar = {
    "Demo": [
        st.Page(
            page="reference/demos/aip_streamlit_demo.py",
            title="Streamlit Demo (3-12-25)",
            icon="📘",
        )
    ]
}

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
pg.run()
