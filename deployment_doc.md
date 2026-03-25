# AIPassport Deployment & Canvas Integration Guide

This document outlines how to deploy the Gemini-powered AI Passport application and embed specific modules into Canvas.

---

## 🚀 1. Deploying to Streamlit Cloud

1.  **Repository Setup**: 
    - Ensure all changes are committed and pushed to your GitHub repository.
    - The repository structure should have `AIPassport/` as a subfolder containing `aipassport_notebooks.py`.

2.  **Streamlit Cloud Configuration**:
    - Go to [share.streamlit.io](https://share.streamlit.app/) and click **"New app"**.
    - **Repository**: Select your `AIP-Guide` repo.
    - **Branch**: `main`.
    - **Main file path**: `AIPassport/aipassport_notebooks.py`.

3.  **Secrets & Environment**:
    - Click **"Advanced settings..."** before deploying (or go to App Settings > Secrets after deploying).
    - Add your Gemini API Key:
      ```toml
      GEMINI_API_KEY = "your_actual_key_here"
      ```

---

## 📦 2. Embedding in Canvas (Iframe)

To embed a specific microskill (e.g., 1.1) with a pre-selected track, use the following `<iframe>` format in the Canvas Rich Text Editor:

### Example: Clinical Track
```html
<iframe 
  src="https://your-app.streamlit.app/1.1?track=clinical&embed=true" 
  width="100%" 
  height="900px" 
  style="border:none;">
</iframe>
```

### Example: Basic Track
```html
<iframe 
  src="https://your-app.streamlit.app/1.1?track=basic&embed=true" 
  width="100%" 
  height="900px" 
  style="border:none;">
</iframe>
```

### URL Parameters Explained:
- **`track=clinical`**: Pre-selects the "Clinical" version of the microskill.
- **`track=basic`**: Pre-selects the "Basic" version.
- **`embed=true`**: Hides the Streamlit header and sidebar for a native "app-like" look.

---

## 🏠 3. Navigating the Module Index
If you land on the root URL (`https://your-app.streamlit.app/`), you will see a **Home Page Index**. This dashboard allows you to browse and navigate all available modules manually while the sidebar is hidden.

### To embed the entire directory:
```html
<iframe 
  src="https://your-app.streamlit.app/?embed=true" 
  width="100%" 
  height="1000px" 
  style="border:none;">
</iframe>
```

---

## 🛠️ 4. Maintenance
- **Updating Notebooks**: Simply drop new `.py` files into `notebooks/clinical/` or `notebooks/basic/` following the `{module}.{skill}_{track}.py` naming convention. The app will automatically detect and list them on the Home page.
