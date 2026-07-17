# AI Passport marimo apps

The `marimo` branch is based on the consolidated `dev` branch. It contains:

- `marimo_notebooks/ai_passport.py`: a single app-mode lesson browser.
- `marimo_notebooks/lessons/*.py`: one standalone marimo notebook per
  consolidated lesson (36 lessons discovered by the `dev` navigation).
- `marimo_notebooks/lessons.json`: the extracted lesson catalog.
- `scripts/build_marimo_lessons.py`: the reproducible source-to-marimo
  content generator.

## Run the combined app locally

```bash
uvx marimo==0.17.8 run marimo_notebooks/ai_passport.py
```

The app opens in read-only app mode. To work on it in the notebook editor:

```bash
uvx marimo==0.17.8 edit marimo_notebooks/ai_passport.py
```

Run an individual lesson in app mode:

```bash
uvx marimo==0.17.8 run marimo_notebooks/lessons/4.1.py
```

## Build and serve the browser-only WASM app

```bash
bash scripts/export_marimo_wasm.sh
python3 -m http.server 8000 --directory build/marimo-wasm
```

Then open <http://localhost:8000>.

The generated page runs Python in the browser through Pyodide. It does not
require a Python notebook server after export.

## Regenerate after changing the consolidated lessons

```bash
python scripts/build_marimo_lessons.py
uvx marimo==0.17.8 check marimo_notebooks
```

The generated notebooks intentionally depend only on marimo and the browser
runtime. Server-side API keys, OpenAI/NaviGator calls, Streamlit session state,
and native-only packages are not copied into the browser apps. Written
activities remain interactive and can be downloaded as Markdown.
