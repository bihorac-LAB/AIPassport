# AIPassport Legacy Audit

Audit of the Streamlit implementation (now preserved under `legacy/`) that serves as the
educational source material for the React + FastAPI rebuild.

- **Audited commit:** `25dbb13` ("Polish notebook modules and AI guide")
- **Legacy entry point:** `legacy/aipassport_notebooks.py`
- **Legacy content:** `legacy/notebooks/{basic,clinical}/*.py` (65 files, ~15,300 LOC)
- **Legacy assets:** `legacy/assets/` (datasets, images, LLM instructions, notebook context, widgets)

---

## 1. How the legacy application worked

| Concern | Legacy implementation |
| --- | --- |
| Shell / navigation | `st.navigation(..., position="hidden")` builds a sidebar dict of `Module N` → `Microskill N.M`. Sidebar is hidden for iframe embedding, so a `render_home_page()` index of buttons is the only navigation. |
| Page rendering | Each microskill page is a **standalone Python file executed with `exec()`** into a copied global namespace, with a shim that fakes IPython's `display()` and `Image`. Import errors are caught and rendered as "Requirement Missing" warnings. |
| Tracks | Two parallel content trees, `notebooks/basic/` and `notebooks/clinical/`. The track lives in `st.session_state["track"]` and `?track=` and is switched with a `st.segmented_control`. |
| AI tutor ("AIP Guide") | `legacy/packages/aip_chat_simple/chat.py`. A fixed 450px right-hand column toggled by a hand-rolled `components.html` + JS bridge that clicks a hidden Streamlit button. Talks to **UF NaviGator Toolkit** (`https://api.ai.it.ufl.edu/v1`, OpenAI-compatible) with model `gemma-4-31b-it` from `aipassport_config.py`. API key read from `st.secrets["NAVIGATOR_TOOLKIT_API_KEY"]`. |
| Tutor context | `context_fn` passes current page title, url_path, track, and `assets/notebook_context/<id>_<track>.json` (objectives, sections, chatbot guidance, common questions). Activities can additionally push `st.session_state["_live_state"]` (e.g. the Fact-or-Fiction verdict) and even a base64 screenshot via `_screen_image`. |
| Persistence | **None.** Every learner answer lives in `st.session_state` and is lost on refresh. `1.3_clinical` and `1.4_basic` explicitly tell learners to "copy your responses to save or submit them". |
| Auth | **None.** No users, no sessions, no analytics. |
| Secrets | `GEMINI_API_KEY` / `NAVIGATOR_TOOLKIT_API_KEY` in `.streamlit/secrets.toml`, read server-side (fine in Streamlit, impossible to reuse in a SPA). |
| Deployment | Streamlit Community Cloud, kept warm by a GitHub Action (`.github/workflows/keep_alive.yml`). |

### Notable legacy defects the rebuild must not inherit

1. **Rerun-driven recomputation.** Every widget change re-executes the whole page file, retrains
   scikit-learn models, and regenerates synthetic data. `st.cache_data` is applied inconsistently.
2. **No durable learner data.** Nothing is attributable, nothing is analyzable, nothing survives refresh.
3. **`exec()` of page source** with a shared global namespace — page-to-page state leakage and no typing.
4. **Broken/degraded pages.** `5.4`, `5.5`, `5.6` are stubs ("The original embedded HTML export is not
   present in this repository"). `5.5` is a bare iframe to `fusion.hubmapconsortium.org`. `2.5_clinical_converted_from_ipynb_WIP.py`
   is a 2,199-line abandoned conversion.
5. **iframe-hostile chrome.** `position: fixed` chat panel at `100vh`, `padding-right: 480px` on the
   block container, and a parent-document JS click bridge — none of this survives a narrow Canvas frame.
6. **Heavy dependency surface** (`tensorflow`-class imports, `shap`, `lime`, `cv2`, `scikit-image`)
   with runtime `ImportError` handling as the fallback UX.
7. **Content gaps.** `MODULE_NAMES` advertises 7 modules × 7 microskills = 49 pages; only 32 exist.

---

## 2. Module and microskill map

`✓` = file exists. Module 6 (Generative AI) is advertised in navigation but **has no content at all**.

| ID | Title (legacy) | basic | clinical | Character |
| --- | --- | --- | --- | --- |
| 1.1 | Demystifying Artificial Intelligence | ✓ | ✓ | Timeline widget + AI "Fact or Fiction" (LLM, structured JSON) |
| 1.2 | AI Lifecycle | ✓ | ✓ | basic = 4-step form walkthrough w/ canned feedback; clinical = **real drift/retrain simulator** |
| 1.3 | Designing Biomedical AI Experiments | ✓ | ✓ | 24–37 `text_area`s. Pure worksheet. |
| 1.4 | Training, Validation, Generalizability | ✓ | ✓ | 18–22 `text_area`s across 6 "Parts". Pure worksheet. |
| 1.5 | Multidisciplinary Team Strengths | ✓ | ✓ | 19–20 `text_area`s + 10-term glossary form. Pure worksheet. |
| 1.6 | Scientific Rigor and Reproducibility | ✓ | ✓ | **Real outlier lab**: boxplot, IQR bounds, remove/winsorize/impute comparison |
| 1.7 | Mentorship and Peer Review | ✓ | ✓ | Case study + 3 text areas + "Show Example" reveals |
| 2.1 | Fundamental Principles of Bioethics | ✓ | ✓ | Case study, multiselect of 4 principles, 3 reveals |
| 2.2 | — | — | — | Missing |
| 2.3 | Bias, Fairness, Societal Impact | ✓ | ✓ | 2 scenario prompts + reveals |
| 2.4 | — | — | — | Missing |
| 2.5 | AI Quality & Safety Simulator | ✓ | ✓ | **Best legacy activity.** Drift slider + retrain, calibration curve, model-card builder |
| 2.6 | Human-AI Collaboration | ✓ | ✓ | 2 text areas (AI transcription failure case) |
| 2.7 | Sex-Specific Modeling | ✓ | ✓ | Large data lab: filters, odds ratios, per-sex AUROC, 2 graded MCQs |
| 3.1 | — | — | — | Missing |
| 3.2 | Ethical Data Acquisition Audit | ✓ | ✓ | 4-pillar audit: consent-language slider, REP-EQUITY recruitment sim, security checklist |
| 3.3 | Genomic AI Reproducibility / Radiology AI Reliability | ✓ | ✓ | Inter-rater reliability, disagreement review, accuracy vs. #raters |
| 3.4 | EHR → OMOP CDM Simulator | ✓ | — | Faker-generated source rows → OMOP `person` / `condition_occurrence` mapping |
| 3.5 | Data Pre-processing Explorer | ✓ | ✓ | Z-score outliers, raw vs. processed boxplots |
| 3.6 | Multi-Institutional Data Sharing | ✓ | ✓ | Z-threshold → imputation → scaling → **federated averaging simulation** |
| 4.1 | Shared Biomedical AI Vocabulary | ✓ | ✓ | Data types, split slider, decision tree viz, live prediction simulator, CV |
| 4.2 | Applied Fundamentals of ML/DL | ✓ | ✓ | Epochs/batch/architecture, learning curve, threshold slider, architecture comparison |
| 4.3 | (duplicate of 4.2) | ✓ | ✓ | **Byte-identical activity set to 4.2.** |
| 4.4 | Choosing the Right DL Model | ✓ | ✓ | 3 phases: StandardScaler, 1D sliding kernel, dropout mechanics, diagnosis MCQ |
| 4.5 | Evaluating ML Models | ✓ | ✓ | Cleaning engine, subgroup patterns, odds ratios, pipeline evaluation |
| 4.6 | Overfitting / Tuning / CV | ✓ | ✓ | kNN decision boundaries, accuracy curve, K-Fold vs Stratified vs LOO |
| 4.7 | Fairness & Explainability | ✓ | ✓ | Subgroup fairness, SHAP summary, LIME local, what-if slider simulator |
| 5.1 | Landscape of Biomedical Imaging | ✓ | ✓ | basic = **attenuation simulator + histogram**; clinical = labelled X-ray / CT-vs-MRI |
| 5.2 | Image Processing | ✓ | ✓ | Channels, gamma, contrast stretch, negative, hist-eq, CLAHE, log/power transforms |
| 5.3 | Texture & Morphology | ✓ | ✓ | GLCM texture, morphological closing, action map |
| 5.4 | Computer Vision Applications | ✓ | ✓ | **Stub** (original HTML export missing) |
| 5.5 | Fusion Tools | ✓ | ✓ | **Bare external iframe**, no instruction |
| 5.6 | Consistency in Image Analysis | ✓ | ✓ | **Stub** — 4 checkboxes + score |
| 6.x | Generative AI | — | — | **No content exists** |
| 7.1 | Designing Biomedical AI Experiments | ✓ | ✓ | LLM feedback on a learner-described experiment |
| 7.2 | Writing Successful Proposals | — | ✓ | LLM generates NIH-style project summary |
| 7.3 | Effective Scientific Communication | — | ✓ | LLM compresses an abstract to ≤100 words |
| 7.4 | Bridging Traditional Research with AI | — | ✓ | LLM proposes an AI application for a stated challenge |
| 7.5 | Peer Review and Feedback | — | ✓ | LLM produces reviewer-style critique |
| 7.6 | Robust Research Design | — | ✓ | LLM generates datasheet / model card |
| 7.7 | Responsible Research | — | ✓ | LLM grades answers to a research-misconduct case |

Module 7 pages 7.2–7.7 are **the same 71-line file** with a different system-instruction path. They are
a single interaction pattern (textarea → LLM → markdown) repeated seven times.

---

## 3. Interaction inventory (what actually exists)

Aggregate widget counts across all 65 legacy notebooks:

| Widget | Count | Verdict |
| --- | --- | --- |
| `st.text_area` | 231 | Overwhelmingly free-text worksheets. The single biggest content problem. |
| `st.slider` / `select_slider` | 96 | The genuinely valuable interactions. Preserve and expand. |
| `st.multiselect` | 40 | Mostly "pick 3 and elaborate" worksheet scaffolding. |
| `st.radio` | 40 | Half are *navigation* (activity switchers), not learning. |
| `st.text_input` | 30 | Mostly worksheet fields; 2 are LLM prompts. |
| `st.button` | 34 | Mostly "Show Example"/"LLM Guidance" reveals. |
| `st.checkbox` | 22 | Checklists and audit gates. |
| `st.plotly_chart` / `pyplot` | 33 | Core visual payload. |
| `st.file_uploader` | 8 | Image upload for the vision labs. |
| `st.dataframe` | 40 | Raw table dumps; mostly low pedagogical value at this volume. |

Only **2 questions in the entire application are actually graded** (`2.7` Question 1 and Question 2).
Everything else is ungraded free text with no persistence.

### Legacy activities worth preserving (redesigned)

1. AI timeline (1.1) — 15 curated milestones, 1950→2025.
2. AI Fact-or-Fiction (1.1) — rich structured LLM schema; the strongest AI activity.
3. Drift + retrain simulator (1.2 clinical, 2.5).
4. Calibration vs. discrimination / reliability diagram (2.5).
5. Model card builder (2.5).
6. Outlier lab: IQR/Z-score, remove vs. winsorize vs. impute (1.6, 3.5).
7. Four-pillar ethical data audit incl. REP-EQUITY recruitment simulation (3.2).
8. OMOP mapping walkthrough (3.4).
9. Inter-rater reliability / label-quality (3.3).
10. Federated averaging simulation (3.6).
11. Train/test split + decision tree + live prediction (4.1).
12. Overfitting vs. underfitting decision boundaries, accuracy curve, CV comparison (4.6).
13. Threshold slider → confusion matrix → metrics (4.2, 4.5).
14. Subgroup fairness + global/local explanation + what-if (4.7, 2.7).
15. X-ray attenuation simulator + intensity histogram (5.1).
16. Intensity transforms: gamma, contrast stretch, negative, hist-eq, CLAHE (5.2).
17. Convolution/edge/blur/noise-denoise, morphology (5.2, 5.3).
18. Module 7 LLM coaching patterns (7.1–7.7) — 7 distinct, well-written system instructions.

### Legacy assets worth preserving

| Asset | Use in rebuild |
| --- | --- |
| `assets/widgets/1.1_ai_timeline.json` | Ported to typed TS content (`module-1` timeline). External hotlinked images dropped. |
| `assets/llm/1.1_gemini_system_instruction.txt` + `_response_schema.json` | Ported to backend AI prompt registry (`fact_or_fiction`). |
| `assets/llm/7.1–7.7_gemini_system_instruction.txt` | Ported to backend AI prompt registry (7 coaching modes). |
| `assets/notebook_context/*.json` (54 files) | Objectives / section purposes folded into the typed page content and reused as AI-tutor page context. |
| `assets/datasets/csv/diabetes.csv` | Numeric feature set behind the ML/explainability activities (reimplemented client-side, see §6). |
| `assets/datasets/csv/eicu_demo.csv`, `data_clean_v2.csv` | Distribution parameters reused for synthetic cohort generation. |
| `assets/datasets/images/*` (10 files) | Kept in `legacy/`; the rebuilt imaging labs generate phantoms procedurally so nothing depends on redistributing clinical images. |
| Brand colors `#0021A5` / `#FA4616` | Carried into the design system as `--aip-blue` / `--aip-orange`. |

---

## 4. Question inventory

Legacy "questions" fall into four groups:

| Group | Count | Disposition |
| --- | --- | --- |
| Graded multiple choice | 2 | Preserved and expanded to a real question bank with stable IDs. |
| Structured selection (multiselect/radio with a "Show Example" reveal) | ~40 | Converted to real questions with immediate, specific feedback. |
| Reflection free text (`text_area`) | 231 | **Cut to ~30.** Kept only where the reflection is the learning objective. |
| Worksheet scaffolding (glossary grids, org-chart fields, dashboard templates, 5× role forms) | ~60 | Removed — see §7. |

---

## 5. Proposed two-page consolidation

Each module becomes exactly **two learner-facing pages**. `Explore` establishes and demonstrates
concepts; `Apply` puts the learner in the practitioner's seat. Track (basic-science vs. clinical) is a
**per-user preference** that swaps datasets and terminology inside activities rather than duplicating pages.

### Module 1 — Fundamentals
| Page | Sources | Sections |
| --- | --- | --- |
| **1A · Demystifying AI** | 1.1 | Concept nesting (AI ⊃ ML ⊃ DL) sorter · Interactive AI timeline (15 milestones, filterable by era/paradigm) · AI Fact-or-Fiction (LLM) · 3 comprehension questions |
| **1B · From Question to Model** | 1.2, 1.3, 1.4, 1.6, 1.7 | Lifecycle simulator (6 stages, each choice gets targeted feedback) · Splitting-strategy scenario (temporal/site/demographic leakage) · Outlier lab (IQR, remove vs. winsorize vs. median-impute, live mean/σ/median) · Rigor reflection |

### Module 2 — Alignment
| Page | Sources | Sections |
| --- | --- | --- |
| **2A · Principles in Tension** | 2.1, 2.3, 2.6 | Four principles explorer · Genetic-risk-model case: which principles apply / which conflict / which wins, with feedback · Subgroup performance explorer (fairness) · AI-transcription failure case |
| **2B · Quality, Safety, Accountability** | 2.5, 1.2c, 2.7 | Drift simulator (months since deployment → covariate shift → FPR, with "do nothing" vs. "retrain") · Calibration vs. discrimination (AUC high / calibration bad) · Model card builder (persisted structured response) |

### Module 3 — Data
| Page | Sources | Sections |
| --- | --- | --- |
| **3A · Sourcing Data Responsibly** | 3.2, 3.4 | Consent-language rewriter (3 literacy levels → comprehension outcome) · REP-EQUITY recruitment simulator (baseline + strategies vs. target) · Security-layer audit · OMOP standardization mapper (source row → concept IDs, learner maps them) |
| **3B · Preparing Data for AI** | 3.3, 3.5, 3.6 | Label quality / inter-rater agreement (κ, disagreement cases, accuracy vs. #annotators) · Outlier + imputation + scaling pipeline (each step's effect visible) · Federated learning simulation (weights leave, rows do not) |

### Module 4 — Machine Learning
| Page | Sources | Sections |
| --- | --- | --- |
| **4A · How Models Learn** | 4.1, 4.2, 4.4, 4.6 | Features/labels/split explorer · Predict-then-check: decision boundary at low vs. high complexity · Train/test accuracy curve (find the divergence) · Cross-validation comparison (K-Fold / Stratified / LOO variance) |
| **4B · Evaluating and Explaining** | 4.2, 4.5, 4.7, 2.7 | Threshold slider → confusion matrix → sensitivity/specificity/PPV/F1 (predict-first) · ROC + operating point · Subgroup fairness gaps · Global feature importance + local per-patient contributions · What-if patient simulator |

### Module 5 — Images
| Page | Sources | Sections |
| --- | --- | --- |
| **5A · Images as Data** | 5.1, 5.2 | Pixel-grid ↔ number-grid reveal · X-ray attenuation phantom (air/soft-tissue/bone sliders) · Live intensity histogram · Window/level and gamma · Modality comparison |
| **5B · Enhancing and Analyzing** | 5.2, 5.3, 5.4, 5.6 | Convolution kernel playground (identity/blur/sharpen/Sobel, with the 3×3 arithmetic shown) · Noise + denoising (salt-and-pepper vs. median filter) · Histogram equalization / CLAHE · Consistency & reproducibility checklist with scoring |

### Module 6 — Generative AI *(new content; no legacy source)*
| Page | Sections |
| --- | --- |
| **6A · How Generative Models Work** | Tokenization explorer · Next-token prediction with a temperature slider (see the distribution reshape) · Embeddings/similarity · Why hallucination happens (structural, not moral) |
| **6B · Using Generative AI Responsibly** | Prompt-craft lab: vague → specific, side-by-side (LLM) · Hallucination hunt (verify claims in a generated paragraph) · PHI / policy decision scenarios |

### Module 7 — Impact Project
| Page | Sources | Sections |
| --- | --- | --- |
| **7A · Design Your Study** | 7.1, 7.4, 7.6 | Structured study-design builder (question, data, model, comparator, metric, risk) · AI design review (7.1 instruction) · "Where could AI help?" (7.4) · Datasheet / model card generator (7.6) |
| **7B · Communicate and Review** | 7.2, 7.3, 7.5, 7.7 | Elevator pitch compressor (7.3) · NIH-style project summary (7.2) · Reviewer critique of your own idea (7.5) · Research-misconduct case with AI-assessed answers (7.7) |

**14 pages total.** Every page is designed to fit a 720px-wide Canvas iframe.

---

## 6. Proposed content removals and substitutions

Documented per Development Rule 6.

| Removed / changed | Volume | Rationale |
| --- | --- | --- |
| **Microskill 4.3** entirely | 568 LOC (both tracks) | Byte-identical activity set to 4.2. Pure duplication. |
| **Free-text worksheet bodies** of 1.3, 1.4, 1.5 (both tracks) | ~120 `text_area`s | These are Word-document assignments rendered in Streamlit. Nothing is checked, nothing is saved, no feedback is possible. The *learning objectives* (leakage-aware splitting, calibration, subgroup evaluation, team roles, communication) are preserved — relocated into 1B, 2B, and 4B as interactive activities with feedback, plus a small number of retained reflection prompts. |
| **1.5 glossary grid** (10 definition fields) and **role forms** (5 × 4 fields) | 30 fields | Data entry, not learning. Replaced by a single "who do you need on this team, and why" scenario in 1B. |
| **1.5 dashboard / decision-doc templates** | 3 prefilled `text_area`s | Project-management templates unrelated to AI literacy. |
| **5.5 Fusion Tools** | Whole page | A bare `<iframe>` to a third-party HuBMAP tool with no instructional wrapper. External availability is outside our control and it cannot be assessed. Removed; the concept (multimodal image fusion) is covered as a short explanation in 5B. |
| **5.4 / 5.6 stub pages** | Whole pages | Already broken in legacy ("original embedded HTML export is not present"). Their surviving checklist/review content is folded into 5B. |
| **2.5_clinical_converted_from_ipynb_WIP.py** | 2,199 LOC | Abandoned notebook conversion, never routed. Retained in `legacy/` only. |
| **Raw `st.dataframe` dumps** of synthetic cohorts | ~40 call sites | Showing 200 rows of generated data teaches nothing. Replaced with small illustrative samples (5–10 rows) plus distribution visuals. |
| **`st.radio` activity switchers** | ~15 | Navigation masquerading as content. Replaced by real in-page section navigation and progress. |
| **SHAP / LIME library plots** | 4.7 | The *concepts* (global vs. local attribution) are preserved with a purpose-built, accessible visualization computed from a transparent logistic model. Shipping `shap`+`lime`+matplotlib server-side to render a PNG per interaction is not viable in a SPA and the resulting images were not accessible. |
| **`file_uploader` image inputs** | 8 | Learner-uploaded images cannot be validated, may contain PHI, and are not needed: the rebuilt labs use procedurally generated phantoms plus the legacy sample images, which makes every learner's result comparable. |
| **Hotlinked timeline images** (Wikipedia / Medium) | 15 URLs | Third-party hotlinking; several already return errors. Timeline is rebuilt as a typographic/interactive timeline. |
| **Track duplication** | 32 duplicate files | Replaced by a single page set with a track preference that swaps dataset context and vocabulary. Both tracks' distinct scenarios are kept as selectable contexts inside the relevant activities. |

### Substitutions and additions

| Added | Why |
| --- | --- |
| **Module 6 (Generative AI), both pages** | Advertised in legacy navigation with zero content, and it is the single most requested topic for this audience. |
| **Predict-then-reveal** on every simulator | Legacy simulators showed the answer immediately. Committing to a prediction first is what makes the visualization stick. |
| **Immediate, specific feedback** on selection questions | Legacy used a "Show Example" button that printed the same canned paragraph regardless of the learner's answer. |
| **Persistence + autosave for every response** | Legacy told learners to copy-paste their work out of the browser. |
| **Accessible visuals** | Legacy relied on color-only encoding in several plots; rebuilt charts use shape/label/pattern in addition to color and expose a data table alternative. |

---

## 7. Learning objectives carried forward

Extracted from `assets/notebook_context/*.json` and the notebook bodies, deduplicated:

- **M1:** AI as a human-built tool for specific problems; AI/ML/DL relationship; historical arc;
  evaluating AI claims critically; the project lifecycle; leakage-aware data splitting; outliers and
  the reproducibility consequences of undocumented handling.
- **M2:** Four bioethics principles and their conflicts; algorithmic bias and disparate subgroup
  performance; drift and retraining; calibration vs. discrimination; transparency artifacts (model cards);
  appropriate reliance on AI tools.
- **M3:** Consent as comprehension not signature; equitable representation; data security layers;
  returning value to participants; standardization/common data models; label quality and inter-rater
  agreement; outlier/imputation/scaling decisions; privacy-preserving collaboration.
- **M4:** Features/labels/splits; underfitting vs. overfitting; hyperparameters; cross-validation;
  threshold choice and its clinical consequences; metric selection beyond accuracy; global vs. local
  explanation; fairness auditing.
- **M5:** Images are numeric arrays; attenuation and intensity; histograms; window/level and contrast
  transforms; convolution; noise and denoising; morphology; reproducibility of image pipelines.
- **M6:** Tokens and next-token prediction; sampling temperature; embeddings; why hallucinations occur;
  prompt specificity; verification discipline; PHI and policy boundaries.
- **M7:** Framing a researchable AI question; identifying AI opportunity in an existing program;
  datasheets and model cards; scientific communication at three levels of expertise; anticipating
  peer review; research misconduct and responsible conduct.

---

## 8. AI features in legacy, and their fate

| Legacy AI feature | Fate |
| --- | --- |
| AIP Guide side panel (NaviGator/`gemma`, page-aware) | **Preserved and improved.** Now a backend `LLMService` behind `POST /api/v1/ai/chat`, with server-side page context resolved from the content registry, per-user rate limiting, usage logging, and no key in the browser. |
| `_live_state` activity-result sharing | **Preserved** as an explicit, allow-listed `activity_context` field on the chat request (bounded size, no PII). |
| `_screen_image` base64 screenshot upload | **Removed.** Uncontrolled screen capture sent to a third-party model is not appropriate for an authenticated educational product, and the panel context now carries the same information as structured text. |
| Fact-or-Fiction structured verdict (1.1) | **Preserved**, prompt + JSON schema moved server-side; response validated with Pydantic before it reaches the client. |
| 7 Module-7 coaching instructions | **Preserved** as named prompt templates in the backend registry. |
| `gemma-4-31b-it` via UF NaviGator | **Kept as a configurable provider.** `LLMService` abstracts provider selection; Gemini and any OpenAI-compatible endpoint (incl. NaviGator) are both supported via env config so no UI change is needed to switch. |

---

## 9. Dependencies

Legacy `requirements.txt` pulls streamlit, pandas, numpy, matplotlib, seaborn, scikit-learn,
scikit-image, statsmodels, plotly, altair, google-genai, openai, streamlit-timeline, Faker, psutil,
GitPython, tenacity, requests, Pillow, pydeck, pyarrow, shap, lime — plus apt packages `libgl1`,
`build-essential` for OpenCV.

The rebuild's backend needs **none** of the scientific stack: all simulations are deterministic maths
that run in the browser, which removes the server round-trip per slider tick that made the legacy app
feel slow. Backend dependencies are limited to FastAPI, SQLAlchemy, Alembic, Pydantic, psycopg,
argon2-cffi, python-jose-free JWT (PyJWT), httpx, and structlog.

---

## 10. Running the legacy app

Preserved verbatim under `legacy/`. Because the notebooks use repo-relative asset paths, it must be
run from inside `legacy/`:

```bash
cd legacy
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# .streamlit/secrets.toml needs NAVIGATOR_TOOLKIT_API_KEY
streamlit run aipassport_notebooks.py
```

Note: this repository's `.gitignore` already excludes `.streamlit/secrets.toml`. Without a key, the
1.1 and 7.x activities render an "AI feedback is unavailable" notice and the rest of the app works.
The pages depending on `cv2` (5.1–5.3) additionally require `libgl1`.
