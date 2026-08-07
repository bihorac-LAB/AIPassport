# AIPassport: AI-Powered Educational Platform

AIPassport is an interactive educational platform designed to teach the fundamentals of Artificial Intelligence, from basic concepts to complex clinical applications. The platform is built with **Streamlit** and integrates **Google Gemini** to provide real-time tutoring and interactive activities.

---

## 🏗️ Architecture Overview

The project follows a **Monorepo** structure where educational content (notebooks), assets, and internal AI packages are managed in a single repository.

### 1. Global Navigation & Entry Point
- **`aipassport_notebooks.py`**: The main entry point. It handles global navigation using `st.navigation`, UI branding, and the persistent **AIP Guide** sidebar.
- **`aipassport_config.py`**: A central configuration file for managing global constants like model versions (`gemini-2.0-flash`), system prompts, and UI strings.

### 2. The AIP Guide (AI Tutor)
Instead of a complex external backend, the AI Guide is implemented as a **Direct Gemini Integration**:
- **`packages/aip_chat_simple/`**: An internal library that communicates directly with the Google GenAI API.
- **Dynamic Context Sharing**: The guide is "content-aware." It automatically detects the current page from the navigation state and can "see" live activity results (like "Fact or Fiction" verdicts) passed through `st.session_state`.

### 3. Educational Content (Notebooks)
- **`notebooks/clinical/`**: Specialized tracks for medical/clinical AI applications.
- **`notebooks/basic/`**: Core AI/ML concepts for general learners.
- Each notebook is a standalone Streamlit page that can also leverage the central AI configuration.
- **Every module presents exactly two subsections**, `{module}.1` and `{module}.2`, following an
  Understand → Apply arc. Both tracks exist for all twelve subsections. The pairing and the titles live in
  `MODULE_SUBSECTIONS` in `aipassport_notebooks.py`, which is what the registration loop walks — adding a
  subsection requires an entry there as well as a notebook file. See `docs/consolidation-plan.md` for how the
  curriculum was consolidated and `docs/deployment_doc.md` for the full path list.

### 5. Notebook Context (`assets/notebook_context/`)
One JSON per notebook, named `{module}.{subsection}_{track}.json`. The AI Guide receives it verbatim, and
reads `sections[].how_to_use` to tell learners which control to use — so it must be updated whenever a
notebook's controls change.

### 4. Assets & LLM Resources
- **`assets/llm/`**: Contains system instructions and JSON response schemas for structured AI activities.
- **`assets/images/` & `assets/widgets/`**: Static media and JSON data for interactive components like the AI Timeline.

---

## 🛠️ Setup & Local Development

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/bihorac-LAB/AIPassport.git
cd AIPassport

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Secrets Management
The app requires a `GEMINI_API_KEY` to function. Create a secrets file:
```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
```
Add your key to `.streamlit/secrets.toml`:
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your-actual-api-key-here"
```
*Note: `.streamlit/secrets.toml` is ignored by git to prevent accidental leaks.*

---

## 🚀 Running the App
```bash
streamlit run aipassport_notebooks.py
```

---

## 🎨 Branding
The platform uses the **IC3 / University of Florida** color palette:
- **Gator Blue**: `#0021A5` (Primary Navigation & Accents)
- **UF Orange**: `#FA4616` (Buttons & Interactions)
- **Background**: Modern, clean white with glassmorphic accents.
