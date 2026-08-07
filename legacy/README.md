# Legacy Streamlit implementation

This is the original AIPassport application, preserved unchanged as the functional reference for the
React + FastAPI rebuild. See `../docs/legacy-audit.md` for what it contained and how its content was
reorganized.

It uses repo-relative asset paths, so run it from **inside this directory**:

```bash
cd legacy
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# .streamlit/secrets.toml needs NAVIGATOR_TOOLKIT_API_KEY for the 1.1 and 7.x AI activities
streamlit run aipassport_notebooks.py
```

Notes:

- Without an API key the 1.1 and 7.x activities render an "AI feedback is unavailable" notice; the
  rest of the app works.
- Microskills 5.1–5.3 additionally require the `libgl1` system package for OpenCV.
- `keep_alive.yml.disabled` was the GitHub Action that kept the Streamlit Community Cloud deployment
  warm. It is retained for reference and deliberately not active — the production deployment is now
  Netlify + EC2 (`../docs/deployment.md`).
- `docs/` holds the Streamlit-era deployment and AI-guide notes.
