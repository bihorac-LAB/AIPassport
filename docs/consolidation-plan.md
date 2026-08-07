# AIPassport Curriculum Consolidation Plan

**Goal:** every instructional module presents exactly **two** learner-facing subsections.

**Status:** Phase 1 deliverable — proposal only. No application code has been modified. No branch created.

**Scope of this document:** repository inventory, evidence-cited architecture map, per-module
consolidation proposal, removal list, size estimates, and the technical risk register that Phase 2
must respect.

---

## 1. Repository Architecture

### 1.1 Entrypoint and dependency surface

| Concern | Evidence |
| --- | --- |
| Streamlit entrypoint | `aipassport_notebooks.py` (confirmed by `README.md` → `streamlit run aipassport_notebooks.py`, and `docs/deployment_doc.md` → main file path `AIPassport/aipassport_notebooks.py`) |
| Page config | `aipassport_notebooks.py:16-20` — `st.set_page_config(...)` called **once**, in the entrypoint only |
| Global config constants | `aipassport_config.py` → `DEFAULT_MODEL`, `NAVIGATOR_TOOLKIT_BASE_URL`, `AI_GUIDE_TITLE`, `AI_GUIDE_PLACEHOLDER`, `AI_GUIDE_SYSTEM_PROMPT`, `GATOR_BLUE`, `UF_ORANGE` |
| Internal package path injection | `aipassport_notebooks.py:10-14` — prepends `packages/` to `sys.path`, then `from aip_chat_simple import render_ai_guide` |
| Runtime | `runtime.txt` → `python-3.12`; `packages.txt` → `libgl1`, `build-essential`; deps in `requirements.txt` |

### 1.2 How the curriculum is actually assembled

There is **no** module registry file, no YAML/JSON curriculum config, and no per-module Python
module. The curriculum is assembled **by filename convention** at startup:

```
aipassport_notebooks.py:90   N_MICROSKILLS_PER_MODULE = 7
aipassport_notebooks.py:92   MODULE_NAMES = [ "Module 1 - Fundamentals", ... "Module 7 - Impact Project" ]
aipassport_notebooks.py:105  get_notebook_path(url_path, track)
                             -> notebooks/{track}/{url_path}_{track}.py
aipassport_notebooks.py:110  get_available_tracks(url_path)   # ("clinical", "basic") filtered by file existence
aipassport_notebooks.py:121  load_notebook_context(url_path, track)
                             -> assets/notebook_context/{url_path}_{track}.json
aipassport_notebooks.py:258  # registration loop
   for module_idx, module_name in enumerate(MODULE_NAMES):
       for microskill_idx in range(N_MICROSKILLS_PER_MODULE):
           if clinical_exists or basic_exists:
               st.Page(page=render_notebook_page,
                       title=f"Microskill {m}.{n}",
                       icon="📝",
                       url_path=f"{m}.{n}")
aipassport_notebooks.py:276  pg = st.navigation(sidebar, position="hidden")
aipassport_notebooks.py:420  pg.run()
```

**Therefore a "microskill" == a `notebooks/{track}/{M}.{N}_{track}.py` file**, and it becomes a
learner-facing subsection purely because a file with that name exists. Deleting the file removes the
subsection; the loop iterates `1..N_MICROSKILLS_PER_MODULE` and skips numbers with no file on either
track. This is the single most important architectural fact for this task: **consolidation is done by
merging/deleting notebook files and adjusting `N_MICROSKILLS_PER_MODULE`, not by editing a config.**

### 1.3 Rendering path

`render_notebook_page()` (`aipassport_notebooks.py:168-256`):

1. Resolves `pg.url_path` → available tracks; coerces `st.session_state["track"]` and
   `st.query_params["track"]` if the current track has no file (`:173-179`).
2. Renders `st.title(pg.title)` plus the track selector, but **only when
   `"_" not in current_url_path`** (`:183`) — the heuristic that distinguishes a microskill page from
   the demo page.
3. Track switch uses `st.segmented_control(..., key="track_selector")` (`:188-195`) and writes both
   `st.session_state["track"]` and `st.query_params["track"]`, then `st.rerun()`.
4. Reads the notebook file as text and executes it with
   `exec(code, exec_globals)` where `exec_globals = globals().copy()` (`:228-235`), augmented with a
   Jupyter compatibility shim: a `display()` function and an `ImageCompatibility` class (`:216-232`).
5. `ImportError`/`ModuleNotFoundError` is caught and rendered as a friendly "Requirement Missing"
   warning (`:236-240`); all other exceptions become `st.error` + `st.exception` (`:241-243`).

Consequences that constrain Phase 2:

- Notebooks are **scripts, not modules**. They cannot `import` each other. There are no shared
  rendering utilities for notebook content — every notebook re-declares its own helpers
  (`load_data`, `build_eicu_data`, `get_processed_data`, `icc`, `cap_outliers`, …).
- Because each notebook runs in a copy of the entrypoint's globals, `st`, `os`, `sys`, `json`,
  `components`, and `render_ai_guide` are already in scope, and `packages/` is importable.
- Any `st.stop()` inside a notebook aborts the whole script run — including anything that would have
  rendered after it. There are 13 `st.stop()` call sites (see §8).

### 1.4 Navigation and table of contents

- `st.navigation(sidebar, position="hidden")` — the Streamlit sidebar is **hidden** (for Canvas iframe
  embedding).
- The learner-facing index is `render_home_page()` (`aipassport_notebooks.py:155-166`): one
  `st.expander(f"📂 {module_name}")` per module, 3-column grid of
  `st.button(p.title, key=f"btn_{p.url_path}")` → `st.switch_page(p)`.
- Page labels are generic: `title=f"Microskill {module_idx+1}.{microskill_idx+1}"`. The home page
  therefore shows buttons reading "Microskill 4.3", not the lesson name. The real lesson title lives
  inside each notebook's own `st.title(...)` and in `assets/notebook_context/*.json` → `"title"`.
- A `sidebar["Demo"]` group is registered only if `reference/demos/aip_streamlit_demo.py` exists
  (`aipassport_notebooks.py:144-152`). That path does **not** exist in this repository, so the group
  is never created.

### 1.5 Deep links / query parameters (critical)

`docs/deployment_doc.md` §2 documents the Canvas embedding contract:

```html
<iframe src="https://your-app.streamlit.app/1.1?track=clinical&embed=true" ...>
```

So **every `url_path` (`1.1`, `2.3`, `4.7`, …) is a published external deep link** consumed by Canvas
course pages outside this repository. `?track=` is read at `aipassport_notebooks.py:280`. Renumbering
subsections silently breaks live course content. See §7 and §9.

### 1.6 Session state, widget keys, and progress tracking

- **There is no progress/completion tracking, no analytics, and no persistence.** Nothing writes to
  disk or to a database. "Assignment complete" is cosmetic (`st.success` in `1.3_basic.py:183-184`,
  `1.4_basic.py:249`, `1.7_basic.py:95`). There are no assessment mappings and no gradebook hooks.
- Entrypoint-owned session state: `track` (`:281-282`), `_chat_open` (`:285-286`).
  Entrypoint widget keys: `track_selector` (`:194`), `__aip_toggle__` (`:393`),
  `btn_{url_path}` (`:165`).
- AI Guide state (`packages/aip_chat_simple/chat.py`): `messages` (`:55`), `chat_error` (`:58`),
  `_quick_action` (`:90-97`, popped at `:104`), and read-only consumption of `_live_state` (`:123`)
  and `_screen_image` (`:128`).
- Only one notebook feeds the AI Guide live state: `notebooks/clinical/1.1_clinical.py:131-138`
  writes `st.session_state["_live_state"]` with the Fact-or-Fiction verdict. The basic variant does
  not. This is the "content-aware guide" feature described in `README.md`.
- Notebook-owned session state: `statement`/`verdict`/`text_input` (1.1 both tracks),
  `proc_run` (2.7, 4.5), `act2_history`/`act3_results` (4.2, 4.3), `selected_features`/
  `current_context` (4.6), `xray_image` (5.1 basic), `experiment_input`/`input`/`output`/`_pending`/
  `experiment_idea`/`experiment_feedback` (all of Module 7).
- Widget keys are declared inline per notebook. Because each notebook is its own page, there are
  currently **zero duplicate-key collisions** (verified by scan). Merging changes that — see §8.

### 1.7 Content and asset inventory

| Path | Contents | Notes |
| --- | --- | --- |
| `notebooks/basic/` | 31 files | `1.1–1.7`, `2.1 2.3 2.5 2.6 2.7`, `3.2–3.6`, `4.1–4.7`, `5.1–5.6`, `7.1` |
| `notebooks/clinical/` | 37 files | same, minus `3.4`, plus `7.2–7.7`, plus one dead WIP file |
| `assets/notebook_context/` | 59 JSON | one per registered notebook **except all of Module 7** (9 missing) |
| `assets/llm/` | 8 system-instruction `.txt` + 2 response schemas | `1.1`, `7.1`–`7.7` |
| `assets/widgets/1.1_ai_timeline.json` | AI history timeline data | consumed by `1.1_basic.py:32`, `1.1_clinical.py` |
| `assets/images/headers/` | `1.1_header.png`, `7.1_header.png` | both referenced |
| `assets/images/content/` | 5 PNG | only `Identifying Structures in X-Ray Imaging.png` is referenced (`5.1_clinical.py:27`). **`3.3 basic fig1/fig2.png` and `3.3 clinical fig1/fig2.png` are referenced nowhere** |
| `assets/datasets/csv/` | `diabetes.csv`, `eicu_demo.csv`, `data_clean_v2.csv` | first two heavily used; `data_clean_v2.csv` is referenced **only** by the dead WIP file, and under a wrong path (`module_2_alignment/data/…`) |
| `assets/datasets/images/` | 10 images | `IFCells.jpg`, `BloodSmear.png` (×2 refs each), `kidney_mri.jpg`, `breast.png`, `low_contrast2.jpg`, `small_slide_BC.png`, `small_slide_noBC.png`, `breast_US.png` referenced. **`IM-0003-0001.jpeg` and `fracture.jpg` referenced nowhere** |
| `.github/workflows/keep_alive.yml` | 6-hourly curl to `https://aipassport-uf.streamlit.app/` | no module/subsection names — unaffected |

### 1.8 Tests

**There is no test suite.** No `tests/`, no `pytest.ini`/`conftest.py`, no CI job that imports or
exercises modules. `.github/workflows/keep_alive.yml` is the only workflow and it only pings the
deployed URL. No test depends on module or subsection names.

### 1.9 Track duplication (a major structural finding)

The two tracks are separate files. For **18 of 30** microskill numbers the two files are **byte
identical**, i.e. the "track" distinction is fictional for them:

| Byte-identical across tracks | Meaningfully different across tracks |
| --- | --- |
| `2.5`, `2.7`, `3.2`, `3.6`, `4.1`, `4.2`, `4.3`, `4.4`, `4.5`, `4.6`, `4.7`, `5.5` | `1.1`(≈), `1.2`, `1.3`, `1.4`, `1.5`, `1.6`, `1.7`, `2.1`, `2.3`, `2.6`, `3.3`, `3.5`, `5.1`, `5.2`, `5.3`, `5.4`(≈), `5.6`(≈), `7.1`(title only) |

Worse, several of the "identical across tracks" files contain an **internal** track toggle that
duplicates the app's own track selector — e.g. `3.2_basic.py:47-67` (`st.radio("Select Research
Track:", ["Clinical Track (IC3 COVID-19)", "Basic Science Track (ImmPort)"])`),
`3.6_basic.py:14-19`, `4.1_basic.py:15-19`, `4.4_basic.py:23-27`, `4.5_basic.py:121-125`,
`4.6_basic.py:93-97`. Learners therefore pick a track twice, in two different widgets, with no
linkage between them.

**And `4.2` and `4.3` are byte-identical to each other** (in both tracks) — an entire duplicated
microskill, four duplicate files, and four duplicate context JSONs.

---

## 2. Current Module / Microskill Inventory

### Module 1 — Fundamentals (7 subsections)

| # | Title | Purpose | Key interactive/assessment content |
| --- | --- | --- | --- |
| 1.1 | Demystifying Artificial Intelligence | AI history + myth-busting | `streamlit_timeline` AI timeline (`assets/widgets/1.1_ai_timeline.json`); **"AI: Fact or Fiction?"** LLM activity with structured JSON verdict + 6 expander panels (`assets/llm/1.1_gemini_*`). Clinical variant also publishes `_live_state` to the AI Guide |
| 1.2 | AI Lifecycle | project lifecycle | **basic:** 4-step walkthrough (data source radio → preprocessing multiselect → model radio → validation multiselect) each with a canned "LLM Guidance" button. **clinical:** genuine simulator — 3 synthetic deployment batches, model-version × data-batch matrix, accuracy/AUC/confusion matrix, prediction-probability histogram, threshold-slider data validator, drift narrative |
| 1.3 | Designing Biomedical AI Experiments | study design worksheet | 5 expanders, ~14 multiselect/radio/select widgets and **~22 free-text fields**; ends with a cosmetic "Mark assignment as complete" button |
| 1.4 | Training, Validation & Generalizability | validation design | `st.selectbox` over 7 sections; **18 free-text tasks** (`key="task1.1"`…`"task6.3"`), zero interactive computation |
| 1.5 | Leveraging Multidisciplinary Team Strengths | team formation | 6 parts; 5 role `st.form`s, a 10-term glossary form, 3 tool selectboxes + descriptions, 2 pre-filled document templates, ~16 more text areas. Two small illustrative `st.dataframe`s |
| 1.6 | Basics of Scientific Rigor & Reproducibility | outliers & reporting | **Genuinely interactive:** simulated eICU vitals, plotly boxplot, 1.5×IQR threshold calculator, outlier table, with/without summary-stat comparison, 3 handling strategies (remove/winsorize/impute), reflection |
| 1.7 | Mentorship and Peer Review | professional practice | Mentor/mentee case; identify-challenges text area with a **"Show Example"** reveal; draft-a-professional-email exercise with a full worked example; reflection |

**Duplication inside Module 1:** "reflection on transparent reporting" appears in 1.3 (Part 5),
1.4 (Part 6), and 1.6 (Part 5). Dataset/tool link lists are repeated at the top of 1.3, 1.4, 1.5, 1.6
and again at the bottom of 1.5 and 1.6. Generalizability/subgroup-performance prompts appear in
1.3 §3.2, 1.4 Parts 3 + 5, and again in 1.4 Part 6.

### Module 2 — Alignment (5 subsections; 2.2 and 2.4 do not exist)

| # | Title | Purpose | Key content |
| --- | --- | --- | --- |
| 2.1 | The Fundamental Principles of Bioethics | 4-principles reasoning | Dr. Lee genetic-risk-model case; principles `multiselect`; conflict + precedence text areas; 3 "Show Example" reveals |
| 2.3 | Bias, Fairness, and Societal Impacts | bias reasoning | Assignment 1 "imagine your ideal AI system" (open essay + reveal); Assignment 2 public-health-crisis algorithm case (essay + reveal); reflection |
| 2.5 | AI Quality & Safety Simulator | quality/safety measurement | **3 `st.tabs`:** (1) sepsis covariate-shift simulator with retrain toggle and FPR metric; (2) vendor-model **calibration curve vs AUC** with population-mismatch slider; (3) **Model Card builder** with live HTML preview. Sklearn `LogisticRegression`, `calibration_curve` |
| 2.6 | Human-AI Collaboration | oversight reasoning | Two essay prompts; the second is an excellent concrete case (AI transcription tool that hallucinates, mislabels tone, degrades on accents, leaks PII in metadata) |
| 2.7 | Sex-Specific Modeling | subgroup evaluation | `st.selectbox` over 4 stages: preprocessing pipeline on `eicu_demo.csv`; data explorer with 5 filter widgets; sex-split mean-value bar chart; **MCQ Q1** with feedback; univariate odds-ratio loop (statsmodels `logit` × 3 cohorts × N vars, progress bar); multivariate AUROC by sex; **MCQ Q2** with feedback |

**Dead code:** `notebooks/clinical/2.5_clinical_converted_from_ipynb_WIP.py` — 2,199 lines, **1,504 of
them commented out**, not registered by the navigation loop (the filename does not match
`{M}.{N}_{track}.py`, so `get_notebook_path` never resolves it), and its live path depends on
`module_2_alignment/data/data_clean_v2.csv` plus two `.pkl` model files that are not in the repo.

### Module 3 — Data (5 subsections; 3.1 does not exist; 3.4 is basic-only)

| # | Title | Purpose | Key content |
| --- | --- | --- | --- |
| 3.2 | Ethical Data Acquisition Audit | four ethical pillars | `st.selectbox` over 5 sections: static "Four Pillars" intro; **Autonomy** consent-language `select_slider` with rewritten text; **Justice** REP-EQUITY simulation (underserved group, target slider, 3 strategy checkboxes, plotly bar, pass/fail verdict); **Privacy** 4-checkbox security score; **Beneficence** single button that reveals an impact report. ~40 lines of custom CSS |
| 3.3 | Genomic AI Reproducibility (basic) / Radiology AI Reliability (clinical) | label quality | Both: simulate N annotators with adjustable disagreement → **ICC** metric → train a model on the consensus label. Basic adds CSV upload + 3 visual tabs. Clinical adds a **high-disagreement image table** and an **accuracy-vs-number-of-annotators curve** (the strongest single idea in the pair) |
| 3.4 | EHR to OMOP CDM Simulator | interoperability | `Faker`-generated source records → OMOP `person` table with gender/race/ethnicity **concept-ID mapping** → `condition_occurrence` from ICD-10→OMOP map. Two static "Knowledge Check" prose columns |
| 3.5 | Genomic (basic) / Cardiovascular (clinical) Preprocessing Lab | cleaning | Winsorization percentile sliders, imputation strategy, scaler choice; raw-vs-processed tables; z-score outlier count; before/after boxplot |
| 3.6 | Multi-Institutional Data Sharing Simulation | federated workflow | Step 1 inspect → Step 2 z-score outlier detection (slider, plotly scatter, `st.stop()` gate) → Step 3 imputation + scaling selectboxes → Step 4 **federated round**: per-institution weights, aggregated global model, "Patient Records Shared = 0" metric |

**Duplication inside Module 3:** 3.5 and 3.6 both teach outlier detection → imputation → scaling on
synthetic data with the same widget vocabulary; 3.6 Steps 2–3 fully subsume 3.5. 3.2 and 3.6 both
carry the same internal Clinical/Basic dataset toggle.

### Module 4 — Machine Learning (7 subsections)

| # | Title | Purpose | Key content |
| --- | --- | --- | --- |
| 4.1 | Shared Biomedical AI Vocabulary | supervised pipeline | 4 activities on `diabetes.csv`: data preview + `.dtypes` + plotly histogram by outcome; train/test split donut; **decision tree** train + `plot_tree` + `export_text` accessible alternative + **live 8-slider prediction simulator**; cross-validation with 4 metrics + per-fold bar chart. Each activity has a "Reveal Expected Insights" expander with the exact expected numbers |
| 4.2 | Applied Fundamentals of ML and DL | DNN | 4 activities: data exploration + class-imbalance framing; `MLPClassifier` training with epochs/batch sliders and a Keras `Sequential` code block; 5-fold evaluation with a **classification-threshold slider** driving sensitivity/specificity; interpretability-vs-performance `select_slider` strategy advisor |
| **4.3** | **(byte-identical to 4.2)** | — | **pure duplicate** |
| 4.4 | Choosing the Right Deep Learning Model | CNN mechanics | 3 phases: **StandardScaler on/off toggle** showing one patient row; **Conv1D sliding-kernel visualiser** (HTML); Conv1D `Sequential` code block; **Dropout neuron visualiser** (HTML); then a fold-metrics selectbox over **hardcoded numbers** and a threshold slider driven by an invented linear formula (`sim_sens = 0.598 + (0.5-threshold)*0.8`) |
| 4.5 | Evaluating Machine Learning Models | subgroup evaluation | **Near-clone of 2.7**: same `build_eicu_data`/`get_processed_data`, same 4-stage nav, same data explorer, same sex-split means, same univariate odds ratios, same multivariate AUROC-by-sex — rendered with matplotlib instead of plotly, and **without** 2.7's two MCQs |
| 4.6 | (Overfitting / Tuning / CV) | generalization | 3 activities on eICU **or** a synthetic `make_classification` "foundational" dataset: KNN **decision-boundary contour comparison** (low k vs high k); **train-vs-test accuracy curve** over k; CV boxplot + **K-Fold vs Stratified K-Fold vs LOO-CV** comparison. Colour-blind-safe palette and text captions throughout |
| 4.7 | (Fairness / SHAP / LIME / What-if) | accountability | 4 activities on `diabetes.csv` + `LogisticRegression`: **age-subgroup fairness table** with adjustable bin threshold; **SHAP** global summary plot; **LIME** per-patient explanation; **what-if simulator** with live prediction + confidence |

**Duplication inside Module 4:** "Activity 1 - Data Exploration" (identical preview slider,
`.dtypes` expander, feature selectbox) appears in 4.1, 4.2, and 4.3. Cross-validation is taught four
times (4.1 Act 4, 4.2 Act 3, 4.4 Phase 3, 4.6 Act 3). The "Notebook Directives / record your
responses only in your Canvas submission area" block is repeated verbatim 3× inside 4.4 alone.

### Module 5 — Images (6 subsections)

| # | Title | Purpose | Key content |
| --- | --- | --- | --- |
| 5.1 | Landscape of Biomedical Imaging (basic) / Clinical Assignment (clinical) | image formation | **basic:** 3 tissue-density sliders → synthetic X-ray (`cv2.circle`/`rectangle`) → **pixel-intensity histogram** whose peaks track the sliders. **clinical:** Canny edge detection with dual thresholds; contrast/brightness CT-vs-MRI comparison |
| 5.2 | Image Processing Suite | intensity + augmentation | **basic:** 7 sections — channel separation, gamma, contrast rescale, negative, histogram equalization, **CLAHE**, non-linear (m/E) transform; each with an "Expected Outcome" expander. **clinical:** 4 modules — normalization + rotate/flip augmentation, **directional + Sobel edge filters**, motion blur, **salt-&-pepper noise with median-vs-Gaussian denoising** |
| 5.3 | (Edge/threshold basic; texture/morphology clinical) | features | **basic:** Sobel kernel size, Canny dual thresholds, Gaussian blur → **Otsu** auto-threshold, 4-panel comparison with per-panel "Reveal Logic" checkboxes. **clinical:** **GLCM** contrast/correlation on malignant vs benign slides; morphological **closing** with a difference "action map" |
| 5.4 | Biomedical Computer Vision Applications | — | **Self-declared placeholder:** "The original embedded HTML export is not present in this repository." An application selectbox + 3 `st.metric` + 3 text areas |
| 5.5 | Fusion Tools Integration | — | **11 lines.** A bare `st.components.v1.iframe` to `https://fusion.hubmapconsortium.org/Visualization`. No instructions, no prompts, no assessment |
| 5.6 | Consistency in Biomedical Image Analysis | reliability | **Self-declared placeholder** too, but genuinely useful: a 4-item consistency checklist with a score metric + 2 reflection prompts |

### Module 6 — Generative AI (**0 subsections**)

Registered at `aipassport_notebooks.py:98` but **no notebook files, no context JSON, no assets
exist**. The registration loop creates `sidebar["Module 6 - Generative AI"] = []` and
`render_home_page()` renders an empty `📂 Module 6 - Generative AI` expander. It is not an
instructional module today.

### Module 7 — Impact Project (7 subsections; `basic` exists only for 7.1)

All seven are the **same ~72-line template**: title → one-paragraph blurb → an
`st.text_area(key="experiment_input")` → `st.button("✅ Submit")` → `_pending` flag → `st.rerun()` →
OpenAI-compatible call to `https://api.ai.it.ufl.edu/v1` with `model_id = "gemma-3-27b-it"` and a
per-microskill system instruction from `assets/llm/7.N_gemini_system_instruction.txt` → fake
line-by-line streaming (`time.sleep(0.04)`).

| # | Title | Differs only in | Notes |
| --- | --- | --- | --- |
| 7.1 | Designing Biomedical AI Experiments | header image, longer blurb, extra markdown-formatting preamble injected into the system prompt, `experiment_idea`/`experiment_feedback` state names | the only one with an `assets/images/headers/` image |
| 7.2 | Writing Successful Biomedical AI Proposals | input label, `7.2` instruction file | → NIH-style project summary |
| 7.3 | Effective Scientific Communication | ″ | → elevator pitch |
| 7.4 | Bridging Traditional Research with AI Innovation | ″ | → AI approach for a stated gap |
| 7.5 | Peer Review and Feedback | ″ | → critique of the learner's idea |
| 7.6 | Robust Biomedical AI Research Design | ″ | → datasheet / model card |
| 7.7 | Responsible Biomedical AI Research | ″ | → misconduct-case analysis. **The case text and the two questions exist only inside `assets/llm/7.7_gemini_system_instruction.txt`; the page asks "Provide your responses to Q1 and Q2" without ever showing Q1, Q2, or the case.** |

---

## 3. Core Learning Outcomes by Module

Derived from the content actually present, not from titles.

| Module | After this module a learner should be able to… |
| --- | --- |
| 1 — Fundamentals | (a) explain what AI is and is not, and place today's capabilities in historical context; (b) walk an AI project through its lifecycle and say what decision each stage requires; (c) design defensible data splits and validation for a biomedical study, including external validation and subgroup performance; (d) detect and handle outliers and report those choices reproducibly; (e) communicate professionally inside a mixed-expertise team |
| 2 — Alignment | (a) apply the four bioethical principles to a concrete AI case and name which principles conflict; (b) identify how training-population mismatch becomes deployed harm; (c) decide when a human must stay in the loop; (d) **measure** drift, discrimination, calibration, and subgroup performance; (e) document a model's intended use and limits in a model card |
| 3 — Data | (a) audit a data-acquisition protocol for consent, representation, privacy, and return of value; (b) judge label quality (inter-rater agreement) and its effect on a model; (c) map source data to a common data model; (d) clean data (outliers, missing values, scaling) reproducibly; (e) collaborate across institutions without moving raw data |
| 4 — Machine Learning | (a) run a supervised pipeline end to end and read its outputs; (b) explain what a decision tree, a dense network, and a 1-D convolution actually do; (c) recognise overfitting/underfitting and tune to avoid it; (d) choose validation strategies and thresholds deliberately; (e) audit a model for subgroup fairness and explain individual predictions |
| 5 — Images | (a) explain how physical signal becomes pixel intensity, and read a histogram; (b) apply intensity/contrast operations and say why; (c) apply augmentation, denoising, edge detection, thresholding, texture, and morphology, and choose the right one for an artefact; (d) judge whether an imaging pipeline is consistent enough to trust |
| 6 — Generative AI | **No content exists.** No outcomes can be derived. |
| 7 — Impact Project | (a) turn a research interest into a specific, feasible AI study design with a rigor artefact (datasheet/model card); (b) communicate it to funders and lay audiences, absorb critique, and handle research-integrity pressure |

---

## 4. Proposed Two-Subsection Structure

### 4.1 Naming and numbering recommendation: **hybrid**

- **Consistent numbering:** every module becomes exactly `M.1` and `M.2`, and
  `N_MICROSKILLS_PER_MODULE` becomes `2`. This is required for a clean structure, since Modules 2 and
  3 do not currently even have an `M.1` (2.2, 2.4, 3.1 are missing).
- **Module-specific titles**, not a repeated "Foundations / Practice" pair. Six identical button
  pairs on the home page would make the index unusable, and the modules are not parallel (Module 7 is
  a capstone; Module 2 is half ethics, half measurement). Every pair still follows an explicit
  **Understand → Apply** arc.
- **Replace the generic page labels.** `title=f"Microskill {m}.{n}"` should become the real lesson
  name, sourced from a small literal in the entrypoint (proposed: `MODULE_SUBSECTIONS`, a
  `dict[str, list[str]]` replacing `N_MICROSKILLS_PER_MODULE`). This is a navigation change the
  consolidation makes necessary — with only two units per module, the label has to say what they are.

### 4.2 The table

Every existing microskill appears exactly once in the "folded into" or "removed" column.

| Module | Proposed Subsection 1 | Proposed Subsection 2 | Existing microskills/content folded into each | Content proposed for removal | Rationale |
| --- | --- | --- | --- | --- | --- |
| **1 — Fundamentals** | **1.1 What AI Is, and How an AI Project Works** | **1.2 Designing a Study You Can Defend** | **→1.1:** all of 1.1 (timeline, Fact-or-Fiction, `_live_state` hook); 1.2's lifecycle spine — clinical keeps the deployment-version/drift simulator + data validator, basic keeps the 4 lifecycle decision points collapsed into one form with a single consolidated guidance panel. **→1.2:** 1.6 in full (IQR lab is the module's best interactive asset); 1.4's Parts 1–3 reduced to 4 tasks (split design, CV design, external validation, subgroup performance); 1.3's Part 1 (gap → SMART question) and Part 2 (data selection/preprocessing/splitting) as the design brief that the 1.6 lab then executes against; 1.7's email-drafting exercise + worked example as the closing communication task; from 1.5, one prompt on who belongs on the team and how they'll communicate | 1.2 basic's four separate canned "LLM Guidance" blocks → one; 1.3 Parts 4–5 (ethics list + iterative-design/collaboration/communication reflections — Part 4 duplicates Module 2, Part 5 duplicates 1.4 Part 6); 1.4 Parts 4–6 (robustness, demographics, reflection — 9 free-text tasks that restate Part 3); **1.5's worksheet: 5 role forms, 10-term glossary form, shadowing schedule, 3 tool selectboxes + descriptions, dashboard template, 3 closing reflections**; repeated dataset/tool link blocks at the top and bottom of 1.3/1.4/1.5/1.6; the cosmetic "Mark assignment as complete" buttons | 1.3/1.4/1.5 are three long unmarked free-text worksheets (≈56 text fields combined) that teach by asking rather than by showing; 1.6 is the only place in the module where the learner manipulates data. Keeping one design brief → one hands-on lab → one communication artefact preserves every outcome while removing ~40 unassessed prompts |
| **2 — Alignment** | **2.1 Ethics, Bias, and Human Oversight** | **2.2 Measuring and Documenting Model Quality** | **→2.1:** 2.1's Dr. Lee case + 4-principles multiselect + conflict/precedence prompts + reveals (strongest ethics artefact); 2.3's Assignment 2 public-health-crisis case as the bias-vector exercise; 2.6's Question 2 transcription-tool case as the human-oversight decision. **→2.2:** all three of 2.5's activities (drift + retrain, calibration vs discrimination, Model Card builder); from 2.7, the subgroup-performance payoff — sex-split feature comparison, multivariate AUROC by sex, and **both MCQs** | 2.3 Assignment 1 ("imagine your ideal AI system") — open-ended, unassessed, and its bias sub-prompt is already covered by the Dr. Lee case; 2.6 Question 1 ("list the tools in your lab") — inventory task with no learning payoff; two of the three separate "Reflection and Takeaways" blocks; 2.7's 4-stage navigation, its 5-widget raw-data explorer, and its univariate odds-ratio stage (a statsmodels `logit` loop over up to 21 variables × 3 cohorts — slow, and the multivariate stage teaches the same point better); **`2.5_clinical_converted_from_ipynb_WIP.py` deleted entirely** | Ethics and measurement are the module's two real halves and they map cleanly onto Understand → Apply. The Model Card builder is the natural capstone and forward-links to 7.6. The WIP file is unreachable dead code (68% commented out, missing data files) |
| **3 — Data** | **3.1 Getting Data You Can Trust** | **3.2 Cleaning and Sharing Data Across Sites** | **→3.1:** 3.2's Autonomy consent-rewrite tool, Justice REP-EQUITY simulation, and Privacy security-score checklist; 3.3 merged to a single implementation — one ICC panel plus the **clinical** variant's high-disagreement table and accuracy-vs-annotator-count curve; 3.4's concept-ID mapping demo (source table → OMOP `person` → `condition_occurrence`), offered on both tracks. **→3.2:** 3.6 end to end (inspect → z-score outliers → impute + scale → federated round with the "0 records shared" metric); from 3.5, the before/after boxplot comparison and the winsorization option added to 3.6's Step 2 | 3.2's "Intro: The Four Pillars" section (four `st.info` boxes and a narrator paragraph — pure framing) and its Beneficence section (one button that prints a canned report); 3.2's ~40 lines of custom CSS and the `narrator()` styling device; 3.3's duplicate second ICC implementation and its CSV-upload branch; 3.4's two static "Knowledge Check" prose columns; **3.5 as a standalone page** (Steps 2–3 of 3.6 already teach outliers/imputation/scaling with better framing); the internal Clinical/Basic radio in 3.2 and 3.6 (the app already has a track selector) | Trust-in-the-data (consent, representation, label quality, standard vocabulary) and hands-on harmonisation are the two coherent halves. 3.5 vs 3.6 is the clearest redundancy in the repository; folding 3.5's one unique visual into 3.6 loses nothing |
| **4 — Machine Learning** | **4.1 Building a Model End to End** | **4.2 Evaluating and Explaining a Model** | **→4.1:** 4.1's full decision-tree pipeline (preview → split → train → `plot_tree` + `export_text` → **live prediction simulator** → CV) as the spine; from 4.2, the "when do you need more capacity" step — the Keras `Sequential` block, `MLPClassifier` training, the threshold slider's sensitivity/specificity trade-off, and the interpretability-vs-performance strategy selector; from 4.4, the two mechanism visualisers worth keeping — the **StandardScaler on/off toggle** and the **Dropout neuron visualiser** — plus the Conv1D sliding-kernel animation. **→4.2:** all of 4.6 (decision-boundary comparison, train-vs-test accuracy curve, CV-strategy comparison); all of 4.7 (subgroup fairness table, SHAP global, LIME local, what-if simulator) | **4.3 deleted entirely — byte-identical to 4.2** (4 files + 4 context JSONs); **4.5 deleted entirely — a near-clone of 2.7** (same eICU pipeline, same odds ratios, same AUROC-by-sex, matplotlib instead of plotly, and it drops 2.7's two MCQs); 4.4's hardcoded 5-fold metric table and its fabricated threshold formula (`sim_sens = 0.598 + (0.5-threshold)*0.8` — presents invented numbers as model output); 4.4's "Notebook Directives / Canvas submission area" block (repeated 3× in one file); the duplicated "Activity 1 - Data Exploration" from 4.2/4.3; LOO-CV computation in 4.6 Act 3 (kept as a caption — `LeaveOneOut` over 200 rows for a teaching point about cost); the internal track radios in 4.1/4.4/4.5/4.6 | Module 4 has the worst duplication in the repository: 7 subsections carrying ~4 distinct lessons. Build-it/judge-it is the natural split, and it puts every cross-validation treatment in one place instead of four |
| **5 — Images** | **5.1 How Biomedical Images Become Data** | **5.2 Preprocessing, Features, and Trustworthy Pipelines** | **→5.1:** 5.1 in full (basic: density sliders → synthetic X-ray → intensity histogram; clinical: Canny structure-finding and the CT-vs-MRI contrast comparison); from 5.2, the intensity half — gamma, contrast rescaling, histogram equalization, and CLAHE, each keeping its "Expected Outcome" reveal. **→5.2:** from 5.2, the augmentation/artefact half — normalization + rotate/flip, directional and Sobel edge filters, motion blur, and salt-&-pepper noise with the **median-vs-Gaussian** comparison; all of 5.3 (basic: Sobel/Canny/Otsu 4-panel with per-panel reveals; clinical: GLCM texture on malignant vs benign, morphological closing with the action map); 5.6's consistency checklist + reflection as the closing reliability gate | 5.2's channel-separation section (its instructions reference a "Mandrill" image that does not exist in the repo), negative transformation, and the non-linear m/E intensity transform (three near-identical slider-plus-formula panels after gamma/rescale/equalization/CLAHE have made the point); **5.4 removed** — a self-declared placeholder for a missing HTML export, whose three reflection prompts are absorbed by 5.6's checklist; **5.5 removed** — 11 lines, a bare third-party iframe with no instruction, prompt, or assessment, and a hard dependency on an external site | Formation-and-appearance vs operate-and-verify. Ending on the consistency checklist turns a tool tour into a pipeline-judgement lesson |
| **6 — Generative AI** | *(no change proposed)* | *(no change proposed)* | Nothing. The module has zero notebooks, zero context files, zero assets | Nothing to remove | **Not an instructional module.** Creating two subsections would mean inventing curriculum, which is outside this task. See §9 R-6 for the empty-expander cosmetic issue |
| **7 — Impact Project** | **7.1 From Idea to Study Design** | **7.2 Communicating and Defending Your Work** | **→7.1:** 7.4 (gap in your field → candidate AI approach) as the on-ramp; 7.1 (design-feedback generator, header image, markdown-formatting preamble) as the core; 7.6 (datasheet / model-card generator) as the rigor artefact. **→7.2:** 7.2 (NIH-style project summary); 7.3 (elevator pitch); 7.5 (critique generator); 7.7 (misconduct case) — **with the case text and Q1/Q2 surfaced on the page**, lifted out of `assets/llm/7.7_gemini_system_instruction.txt`. Both pages present their 3–4 activities through one in-page selector, which is an internal component, not a subsection | The 7× duplicated LLM boilerplate (~60 lines each: client construction, `_pending` flag, `st.rerun()`, fake streaming loop) collapses to one helper defined once per page. `import time` inside the streaming loop (7.2–7.7). The duplicated "This is an educational tool, not a peer review system" caption → once per page | Seven subsections that are one template with seven prompts is the definition of fragmentation. All seven `assets/llm/7.*.txt` instruction files are **kept and still used** — the consolidation changes the wrapper, not the pedagogy. Idea-to-design vs communicate-and-defend is the real division |

### 4.3 Every microskill accounted for

| Merged into Subsection 1 | Merged into Subsection 2 | Removed | Reviewer decision required |
| --- | --- | --- | --- |
| 1.1, 1.2, 2.1, 2.3(partial), 2.6(partial), 3.2(partial), 3.3, 3.4, 4.1, 4.2, 4.4(partial), 5.1, 5.2(partial), 7.1, 7.4, 7.6 | 1.3(partial), 1.4(partial), 1.6, 1.7, 2.5, 2.7(partial), 3.5(partial), 3.6, 4.6, 4.7, 5.2(partial), 5.3, 5.6, 7.2, 7.3, 7.5, 7.7 | **4.3** (exact duplicate of 4.2), **4.5** (duplicate of 2.7), **2.5_clinical_converted_from_ipynb_WIP.py** (dead) | **1.5** (default: reduce to one prompt inside 1.2, not delete); **5.4**, **5.5** (default: remove — see §9 R-2, R-3); **Module 6** (default: no change — §9 R-6); **3.4 clinical variant** (default: create — §9 R-4); **Module 7 basic variants** (default: create — §9 R-5) |

---

## 5. Learning Progression

| Module | Subsection 1 — foundational knowledge/skill | Subsection 2 — build on / apply it |
| --- | --- | --- |
| **1** | Sees what AI actually is (history, myths tested against evidence) and what decisions an AI project demands at each lifecycle stage. Leaves able to describe a project's shape and where it can go wrong. | Turns that into a defensible study: states a research question and data plan, then **executes** the rigor work in the outlier lab, decides splitting/validation/subgroup strategy, and writes the professional message that carries the decision to a mixed-expertise team. |
| **2** | Reasons about harm before touching a model: which bioethical principles are in tension, how a training-population mismatch becomes deployed harm, when a human must stay in the loop. | **Measures** what the first half reasoned about — drift, discrimination vs calibration, subgroup AUROC — and documents intended use and limits in a model card. Ethics becomes a metric and an artefact. |
| **3** | Judges whether data is worth using at all: consent quality, representation, privacy protection, inter-rater agreement, and whether it speaks a standard vocabulary. | Does the work: detects and handles outliers, imputes, scales, and then trains across two institutions without raw data leaving either one. |
| **4** | Builds one model end to end and can point at what each part does — split, fit, read the tree, predict live, then add capacity and see the accuracy/interpretability trade-off. | Stops trusting it: finds the overfitting point, compares validation strategies, checks subgroup fairness, and explains both the model globally (SHAP) and one patient individually (LIME). |
| **5** | Understands where pixel values come from and how intensity/contrast operations change what is visible without changing what is there. | Applies preprocessing and feature extraction to real artefacts (noise, blur, texture, gaps), then asks whether the pipeline is consistent enough to trust. |
| **7** | Converts a gap in the learner's own field into a specific AI study design, and produces the datasheet/model card that makes it rigorous. | Pitches it to funders and to a lay audience, takes an AI-generated critique, and works through a research-integrity case. |

---

## 6. Estimated Post-Consolidation Lengths

Sizes are per track. "Current combined" sums the source files that feed the subsection. Prose words
are an approximation (words inside string literals). Full per-file measurements are in §11.3.

| Module | Subsection | Estimated current combined size | Estimated size after editing | Bloat risk |
| --- | --- | --- | --- | --- |
| 1 | 1.1 What AI Is, and How an AI Project Works | 421–488 lines / ≈830–1,220 words | ≈230 lines / ≈500 words | Low |
| 1 | 1.2 Designing a Study You Can Defend | 936–997 lines / ≈3,160–3,210 words | ≈330 lines / ≈900 words | **High** |
| 2 | 2.1 Ethics, Bias, and Human Oversight | 225–239 lines / ≈1,230–1,350 words | ≈170 lines / ≈650 words | Medium |
| 2 | 2.2 Measuring and Documenting Model Quality | 726 lines / ≈980 words | ≈380 lines / ≈600 words | **High** (code volume, not prose) |
| 3 | 3.1 Getting Data You Can Trust | 485–619 lines / ≈1,230–1,480 words | ≈330 lines / ≈700 words | Medium |
| 3 | 3.2 Cleaning and Sharing Data Across Sites | 410–431 lines / ≈480–670 words | ≈250 lines / ≈450 words | Low |
| 4 | 4.1 Building a Model End to End | 813 lines / ≈2,650 words | ≈380 lines / ≈800 words | **High** |
| 4 | 4.2 Evaluating and Explaining a Model | 492 lines / ≈760 words | ≈330 lines / ≈550 words | Medium |
| 5 | 5.1 How Biomedical Images Become Data | 210–263 lines / ≈580–740 words | ≈200 lines / ≈450 words | Low |
| 5 | 5.2 Preprocessing, Features, and Trustworthy Pipelines | 261–282 lines / ≈430–630 words | ≈250 lines / ≈450 words | Low |
| 7 | 7.1 From Idea to Study Design | 232 lines / ≈360 words | ≈150 lines / ≈350 words | Low |
| 7 | 7.2 Communicating and Defending Your Work | 288 lines / ≈310 words | ≈180 lines / ≈500 words | Low (grows: 7.7's case text moves onto the page) |

Repository-wide: **67 registered notebook files → ≈24** (12 subsections × 2 tracks, per §9 R-4/R-5),
plus one dead file deleted. ≈14,900 notebook lines → ≈6,200.

### Bloat mitigations for the four flagged subsections

**1.2 (High).** The inputs are five files and ≈3,200 words, mostly unmarked free-text prompts.
Mitigation: cap the subsection at **one design brief (≤6 inputs) → the 1.6 lab unchanged → four
validation tasks → one communication artefact**. Anything beyond that is cut, not moved to an
expander. Specifically: 1.4's 18 tasks → 4; 1.3's 22 fields → 6; 1.5's ~30 fields → 1. The 1.6 lab is
kept whole because it is the only computational content and is already tight (199 lines).

**2.2 (High, code volume).** 2.5 (241 lines) + 2.7 (485 lines) both carry heavyweight data plumbing.
Mitigation: drop 2.7's `build_eicu_data()` network-fallback branch and its 5-widget explorer; keep
`eicu_demo.csv` as the only path (the fallback downloads three Dropbox CSVs at runtime); drop the
univariate odds-ratio loop entirely. That removes ≈200 lines of 2.7 while keeping the subgroup lesson
and both MCQs. 2.5's three activities move across essentially unchanged — they are already the right
size.

**4.1 (High).** Three source files, ≈2,650 prose words, much of it repeated "Instructions" and
"Reveal Expected Insights" scaffolding. Mitigation: one `Instructions` block for the whole
subsection instead of one per activity (currently 3 per file × 3 files); one shared `load_data()`
and one shared train/test split instead of three; keep exactly **two** models (decision tree, dense
network) and **three** mechanism visualisers (scaler toggle, Conv1D kernel, dropout) — the Conv1D
architecture discussion becomes a code block plus the kernel animation, not a third full phase.

**4.2 (Medium).** 4.6 + 4.7 are already lean. Mitigation: drop the LOO-CV computation, share one
model/split across all four activities instead of 4.6 and 4.7 each building their own, and keep
4.6's synthetic-vs-eICU dataset toggle **only if** it survives the internal-track-radio cleanup
(§9 R-7).

---

## 7. Navigation / State / Progress Dependencies

Every location Phase 2 must touch or verify.

| Location | Dependency | Required change |
| --- | --- | --- |
| `aipassport_notebooks.py:90` | `N_MICROSKILLS_PER_MODULE = 7` | → `2`, or replaced by the proposed `MODULE_SUBSECTIONS` literal |
| `aipassport_notebooks.py:92-100` | `MODULE_NAMES` | unchanged (module names are not consolidating) |
| `aipassport_notebooks.py:258-274` | registration loop; `title=f"Microskill {m}.{n}"`, `url_path=f"{m}.{n}"` | iterate the two subsections per module; emit real titles |
| `aipassport_notebooks.py:105-107` | `get_notebook_path` | unchanged — filename convention is preserved (`{M}.{1,2}_{track}.py`) |
| `aipassport_notebooks.py:110-118` | `get_available_tracks` | unchanged, but note it silently coerces the track when a file is missing on one side (§9 R-4/R-5) |
| `aipassport_notebooks.py:121-139` | `load_notebook_context` | unchanged; **the JSON files it reads must be renamed/rewritten** |
| `aipassport_notebooks.py:155-166` | `render_home_page()` — `st.expander` per module, `key=f"btn_{p.url_path}"` | keys change with `url_path`; empty Module 6 group still renders (§9 R-6) |
| `aipassport_notebooks.py:183` | `"_" not in current_url_path` guard for the title + track selector | still holds for `M.1`/`M.2` |
| `assets/notebook_context/*.json` | 59 files keyed `{M}.{N}_{track}.json`, each with `microskill`, `title`, `objectives[]`, `sections[]`, `chatbot_guidance[]`, `common_questions[]` | **rename to the new numbering and rewrite `title`/`objectives`/`sections` to match the merged lessons.** Stale `sections` would make the AI Guide describe controls that no longer exist |
| `docs/deployment_doc.md` §2 | documents `/{M}.{N}?track=…&embed=true` Canvas iframes | update the example; add the old→new path map |
| **External Canvas pages** | iframe `src` per old microskill number | **out of repository.** Cannot be fixed here — see R-1 |
| `docs/aip_guide_architecture.md` | 0 bytes | empty; no dependency |
| `README.md` §3 | describes `notebooks/clinical/` and `notebooks/basic/` generically | no per-microskill references; optional refresh |
| `.github/workflows/keep_alive.yml` | pings the app root only | no change |
| Progress / completion / analytics / assessment mappings | **none exist** | nothing to update |
| Tests | **none exist** | nothing to update |

---

## 8. Potential Widget-Key or Session-State Risks

Merging files that were previously separate Streamlit pages puts their widgets on one render path.
Findings from a scan of all 68 notebook files:

**Today: no duplicate keys anywhere.** Every file's explicit keys are unique within that file.

**After merging, these collide:**

| Risk | Evidence | Mitigation |
| --- | --- | --- |
| **Module 7 explicit key collision** | `key="experiment_input"` in all 8 Module 7 files; session keys `input`, `output`, `_pending` in 7.2–7.7; `experiment_idea`, `experiment_feedback` in 7.1 | Namespace per activity: `key="m7_design_input"`, `st.session_state["m7_design_pending"]`, etc. The shared helper must take a `slug` and derive every key and state name from it |
| **Module 4 unkeyed-label collision** | 4.1 and 4.2 both call `st.radio("Go to:", [...])` and `st.slider("Number of records to display", …)` with **no `key=`** — Streamlit derives the ID from type + label + params, so identical unkeyed widgets on one page raise `DuplicateWidgetID` | The merge already deletes 4.2's duplicate data-exploration activity and replaces both nav radios with one selector, which removes both. Add explicit keys to every surviving widget in the merged files |
| **Unkeyed widgets generally** | Large numbers of `st.text_area`/`st.radio`/`st.slider` calls have no `key=` (e.g. `1.3_basic.py` has ~12 unkeyed text areas; `2.1_basic.py` has 3 unkeyed buttons `"Show Example Principles"`/`"Show Example Conflicts"`/`"Show Example Justification"`) | **Give every widget in a merged file an explicit, prefixed key.** This is the single highest-value defensive step in Phase 2 |
| **`key="reflection"`** | `1.6_basic.py:190`, `2.3_basic.py:85` (+ a third in Module 2 clinical) | Different modules, so no collision under this plan — but rename to `m1_rigor_reflection` / `m2_ethics_reflection` while merging |
| **`key="q1"`/`"q2"`, `"a1"`/`"a2"`, `"text_input"`** | 2.7 (q1/q2), 2.6 (a1/a2), 1.1 (text_input) — each pair is one microskill across two tracks | Safe (only one track renders at a time), but 2.6's `a2` moves into 2.1 while 2.7's `q1`/`q2` move into 2.2 — verify they stay in different files |
| **`st.stop()` truncating a merged page** | 13 call sites: `3.6_*.py:174` (gates Steps 3–4 behind a checkbox), `2.7_*`/`4.5_*`/`4.7_*`/`4.1_clinical` (inside button handlers), `5.1_clinical` (×2), `5.2_clinical:68` (no image selected) | After merging, an early `st.stop()` silently hides everything downstream. **Replace the 3.6 gate with an `if apply_filter:` block**; keep `st.stop()` only where it is the last thing on the page |
| **Duplicate helper-function names shadowing silently** | `load_data()` is defined in `3.5`, `4.1`, `4.2`, `4.3`, `4.4`, `4.6`(as `load_clinical_data`/`load_foundational_data`), `5.2`, `1.1`(`load_timeline_data`); `build_eicu_data()`+`get_processed_data()` in both `2.7` and `4.5`; `cap_outliers()` in `3.5_basic` and `3.5_clinical`; an `icc`/`calculate_icc` in both `3.3` variants | Merging `4.1`+`4.2`+`4.4` puts three different `load_data()` definitions in one namespace — Python keeps the last one, **without an error**, and `@st.cache_data` will happily cache the wrong one. Define **one** loader per merged file and delete the rest |
| **`@st.cache_data` on merged loaders** | 37 cached function definitions across the notebooks | Streamlit's cache key includes the function body, so distinct implementations do not collide — but consolidating to one loader per file makes this moot and is required by the item above |
| **`st.session_state.proc_run`** | `2.7_*.py:151`, `4.5_*.py:165` | 4.5 is deleted, so the collision disappears; verify no other page sets it |
| **`st.session_state.selected_features` / `current_context`** | `4.6_*.py:121-125` | Moves into 4.2 together with the dataset toggle; prefix as `m4_eval_*` |
| **`_live_state`** | written by `1.1_clinical.py:131-138`, read by `chat.py:123` | **Preserve.** It is the only live-context hook feeding the AI Guide. It must survive the 1.1 merge, and 1.1 basic should arguably gain it (§9 R-8) |
| **`_pending` + `st.rerun()` pattern** | all 8 Module 7 files; commit `92ee043` ("use pending-flag pattern for reliable button-triggered streaming") and `cd86062` ("remove widget-key clear in submit() to prevent StreamlitAPIException") show this was hard-won | **Do not refactor this pattern.** Reproduce it verbatim per activity with namespaced state. Note the related constraint in `1.1_*.py:107-112`, where `submit()` sets `st.session_state.text_input = ""` inside an `on_change` callback — legal only because it is a callback |
| **`st.set_page_config`** | called only in the entrypoint (`:16`); the sole notebook occurrence is commented out in the dead WIP file | Merged notebooks must **not** introduce one |
| **Track selector vs internal track radios** | `track_selector` (entrypoint) vs internal radios in `3.2`, `3.6`, `4.1`, `4.4`, `4.5`, `4.6` | See §9 R-7 |

---

## 9. Uncertain Content / Reviewer Decisions

### R-1 — Renumbering breaks live Canvas deep links *(highest impact; needs a decision)*

**What:** `docs/deployment_doc.md` documents Canvas iframes of the form
`https://<app>/1.1?track=clinical&embed=true`. Every current `url_path` is a published external
entry point. Consolidating to `M.1`/`M.2` changes 25 of 30 paths (`2.3`, `3.2`, `4.7`, …), and
Streamlit returns "page not found" for a stale path.

**Why it may be acceptable:** a clean two-per-module scheme is the point of the task, and Modules 2
and 3 have no `M.1` today, so some renumbering is unavoidable.

**Why it matters:** the Canvas pages are outside this repository. Nobody editing this repo can fix
them.

**Proposed default:** implement `M.1`/`M.2` **plus a compatibility alias layer** — a
`LEGACY_URL_ALIASES = {"1.3": "1.2", "2.3": "2.1", …}` literal in `aipassport_notebooks.py`
registering hidden `st.Page`s in a `sidebar["_legacy"]` group that `render_home_page()` skips, so old
links resolve to the new subsection while the learner-facing count stays exactly two per module.
Ship the old→new map in `docs/deployment_doc.md`. **Confirm before implementing** — the alias layer is
~15 lines of new navigation code, which brushes against the "don't expand architecture" constraint.
The alternative is a hard cutover plus a Canvas-side update task outside this repo.

### R-2 — Removing 5.4 (Biomedical Computer Vision Applications)

**What:** `5.4_{basic,clinical}.py` (43 lines each). **Why removable:** the page states its own
content is missing ("The original embedded HTML export is not present in this repository"); what
remains is an application selectbox, three decorative `st.metric`s, and three generic reflection
prompts. **Why it may still be valuable:** it is the only place naming concrete CV application areas
(fracture screening, pathology triage, ultrasound lesion assessment), and it is a placeholder for
real source material that may exist outside the repo. **Proposed default:** remove the page; carry
the application-area framing into 5.2's closing checklist so the vocabulary survives. Flag to the
content owner that the missing HTML export is still missing.

### R-3 — Removing 5.5 (Fusion Tools Integration)

**What:** `5.5_{basic,clinical}.py`, 11 lines, identical, a bare
`st.components.v1.iframe("https://fusion.hubmapconsortium.org/Visualization", height=800)`.
**Why removable:** no instructions, no prompts, no assessment, no explanation of what Fusion is or
what to do with it; a hard dependency on a third-party site; it will silently show a blank frame if
HuBMAP blocks framing. **Why it may still be valuable:** it exposes learners to a real
community-scale visualization platform, which no other page does. **Proposed default:** remove the
standalone page and add a single linked mention in 5.2. If the reviewer wants Fusion retained as an
activity, it needs actual instructional scaffolding written for it — a content task, not a
consolidation task.

### R-4 — Module 3 track parity (`3.4` is basic-only)

`3.4_basic.py` exists; there is no `3.4_clinical.py` and no `3.4_clinical.json`. The OMOP concept-ID
lesson is arguably *more* relevant to the clinical track. **Proposed default:** include the OMOP demo
in **both** tracks of the new 3.1, with track-appropriate framing (EHR source records vs specimen
records). Alternative: leave clinical without it, which means the two tracks of 3.1 teach different
outcomes.

### R-5 — Module 7 track parity (7.2–7.7 are clinical-only)

Only `7.1` has a basic variant, and it differs from clinical by one word in the title. Today a basic
learner reaching `/7.3` is silently switched to clinical by `get_available_tracks`
(`aipassport_notebooks.py:173-179`). **Proposed default:** create both tracks for the two new pages
(4 files) so the track selector behaves consistently. This is a small **increase** in file count for
Module 7 relative to a clinical-only reading, so it is called out rather than assumed.

### R-6 — Module 6 (Generative AI) is registered but empty

`MODULE_NAMES` includes it; there are no notebooks, no context files, no assets. `render_home_page()`
therefore draws an empty `📂 Module 6 - Generative AI` expander. **Why leave it:** the entry is
presumably a placeholder for planned content, and removing it is not consolidation. **Why change it:**
after this work every other module shows exactly two clearly-named buttons, and one empty box will
read as a bug. **Proposed default:** leave `MODULE_NAMES` untouched and make no content; optionally
add a one-line skip so `render_home_page()` does not render module groups with zero pages. **Do not
author Module 6 curriculum** — that is new content, not consolidation.

### R-7 — Internal track/perspective radios inside notebooks

`3.2`, `3.6`, `4.1`, `4.4`, `4.5`, `4.6` each contain their own Clinical/Basic (or "Select
Perspective") radio, duplicating the app-level `track_selector`. **Why remove:** learners choose a
track twice, in unlinked widgets; it is the direct cause of those files being byte-identical across
`notebooks/basic/` and `notebooks/clinical/`, which doubles maintenance. **Why keep:** in `4.6` the
toggle also swaps the **dataset** (eICU vs synthetic `make_classification`), which is a real
pedagogical choice, not just relabelling. **Proposed default:** drive the framing from the file's own
track (the app already knows it) and delete the radios in `3.2`, `3.6`, `4.1`, `4.4`; in `4.6` keep
the dataset choice but relabel it as a dataset selector, not a track selector. Flagged because it
changes the two tracks from identical files to genuinely divergent ones.

### R-8 — Adding `_live_state` to the basic track of 1.1

`1.1_clinical.py:131-138` publishes the Fact-or-Fiction verdict to the AI Guide; `1.1_basic.py` does
not, and also hardcodes `model_id = "gemma-3-27b-it"` instead of using `cfg.DEFAULT_MODEL`. **Why
change:** feature parity, and `README.md` advertises the live-state behaviour generally. **Why not:**
it is a behaviour addition, not a consolidation. **Proposed default:** align the two files while
merging (they are otherwise ~95% identical), and note the model-id divergence in §10.

### R-9 — 4.4's mechanism visualisers vs its fabricated metrics

The StandardScaler toggle, Conv1D sliding-kernel animation, and dropout neuron grid are the best
"what is this layer actually doing" content in the repository and are unambiguously worth keeping.
The **same file's** Phase 3 presents hardcoded fold metrics and a threshold slider driven by
`sim_sens = max(0.1, 0.598 + ((0.5 - threshold) * 0.8))` — invented numbers presented as model
output. **Proposed default:** keep the three visualisers, delete Phase 3, and let 4.2's *real*
threshold sweep (`4.2_*.py:224-242`, computed from actual `predict_proba`) carry the trade-off
lesson. Flagged because it deletes a whole "Phase" including its Canvas-referenced question.

### R-10 — 1.5 (Multidisciplinary Teams) reduced from a module to a prompt

1.5 is 193/260 lines and ≈30 input fields, all unassessed free text: five role forms, a ten-term
glossary, a shadowing schedule, three tool selectboxes, a dashboard template. **Why reduce:** it
teaches project management, not biomedical AI, and no other content depends on it. **Why keep:**
multidisciplinary collaboration is a stated outcome in `assets/notebook_context/1.5_*.json`, and the
glossary exercise does force learners to define terms in their own words. **Proposed default:**
reduce to one prompt inside 1.2 ("who do you need on this team, and how will you keep the biology
honest?") plus the glossary terms folded into that prompt as a checklist. **Not** a silent deletion —
if the reviewer wants the collaboration strand preserved at full weight, it belongs in Module 7's
communication page instead.

---

## 10. Pre-existing Issues and Inconsistencies

Documented, **not** in scope to fix unless they block the consolidation.

| # | Issue | Evidence | Blocks consolidation? |
| --- | --- | --- | --- |
| P-1 | **`4.2` and `4.3` are byte-identical** in both tracks — a whole duplicated microskill plus 4 duplicate context JSONs | `diff notebooks/basic/4.2_basic.py notebooks/basic/4.3_basic.py` → empty | Resolved by the plan (4.3 deleted) |
| P-2 | **`4.5` duplicates `2.7`** across modules — same eICU pipeline, same odds ratios, same AUROC-by-sex | `4.5_basic.py:12-116` vs `2.7_basic.py:11-110` | Resolved by the plan (4.5 deleted) |
| P-3 | **Dead file:** `2.5_clinical_converted_from_ipynb_WIP.py`, 2,199 lines, 1,504 commented out, unreachable by the naming convention, depends on `module_2_alignment/data/data_clean_v2.csv` + two absent `.pkl` files | filename does not match `{M}.{N}_{track}.py`, so `get_notebook_path` never resolves it | Resolved by the plan (deleted) |
| P-4 | **`opencv-python` is missing from `requirements.txt`** although `packages.txt` ships `libgl1` (its system dependency). `cv2` is imported by `5.1_basic`, `5.1_clinical`, `5.2_basic`, `5.2_clinical`, `5.3_basic`. The entrypoint's `ImportError` handler turns this into a "Requirement Missing" banner rather than a crash, so Module 5 may be silently degraded in the deployed app | `requirements.txt` (no opencv); `grep -l "import cv2" notebooks/` → 5 files | **Potentially.** Verifying that the merged 5.1/5.2 render requires `cv2`. Flag to the reviewer; adding the dependency would violate "do not add dependencies" without approval |
| P-5 | `scipy` is imported (`3.6_*.py:5`, `3.5_clinical.py:5`) but not listed in `requirements.txt` (it arrives transitively via scikit-learn) | `requirements.txt` | No |
| P-6 | `openai` is listed **twice** in `requirements.txt` | lines 15 and 27 | No |
| P-7 | **7.7 asks for answers to questions it never shows.** The case text and Q1/Q2 exist only in `assets/llm/7.7_gemini_system_instruction.txt`; the page renders `st.text_area("Provide your responses to Q1 and Q2:")` | `7.7_clinical.py:41` vs `assets/llm/7.7_gemini_system_instruction.txt` | No, but the plan fixes it while merging (the case moves onto the page) |
| P-8 | `docs/deployment_doc.md` and `README.md` describe a **Gemini/`GEMINI_API_KEY`** integration, and `.streamlit/secrets.toml.example` only lists `GEMINI_API_KEY`, but the code uses an **OpenAI-compatible NaviGator** client with `NAVIGATOR_TOOLKIT_API_KEY` (`chat.py:48-51`, `aipassport_notebooks.py:404`, all Module 7 files). Following the documented setup yields a non-functional AI Guide | `secrets.toml.example` vs `st.secrets.get("NAVIGATOR_TOOLKIT_API_KEY")` | No |
| P-9 | Module 7 uses `st.secrets["NAVIGATOR_TOOLKIT_API_KEY"]` (**subscript**), which raises if the key is absent, while 1.1 and the entrypoint use `.get()` and degrade gracefully | `7.1_clinical.py:32` vs `1.1_basic.py:92` | No, but the merge should adopt `.get()` for consistency |
| P-10 | `assets/images/content/3.3 basic fig1.png`, `3.3 basic fig2.png`, `3.3 clinical fig1.png`, `3.3 clinical fig2.png` and `assets/datasets/images/IM-0003-0001.jpeg`, `fracture.jpg` are **referenced nowhere** | repo-wide grep of `"assets/…"` string literals | No. **Do not delete** — they are plausibly intended for 3.3/5.x and are cheap to keep (§11.4) |
| P-11 | `assets/datasets/csv/data_clean_v2.csv` is referenced only by the dead WIP file, and under a path that does not exist (`module_2_alignment/data/`) | `2.5_clinical_converted_from_ipynb_WIP.py:280` | No. Keep the CSV; deleting the WIP file does not prove the CSV is unused elsewhere |
| P-12 | `docs/aip_guide_architecture.md` is **0 bytes** | `ls -l docs/` | No |
| P-13 | `render_home_page()` renders an empty expander for Module 6 | `aipassport_notebooks.py:159-166` + no Module 6 files | See R-6 |
| P-14 | `sidebar["Demo"]` registration targets `reference/demos/aip_streamlit_demo.py`, which does not exist | `aipassport_notebooks.py:144-152` | No (dead branch) |
| P-15 | Fallback data loaders fetch three CSVs from **Dropbox share links** at runtime (`2.7`, `4.5`, `4.6`) — an undeclared network dependency that will be slow or broken in a locked-down deployment | `2.7_basic.py:25-56`, `4.6_basic.py:43-56` | No. The plan drops the `2.7` fallback (bundled `eicu_demo.csv` exists); `4.6`'s should be reviewed |
| P-16 | Module 5 basic/clinical variants teach **different** topics under the same number (e.g. `5.3` basic = Sobel/Canny/Otsu, clinical = GLCM/morphology), so a learner switching tracks mid-page lands on unrelated content | `5.3_basic.py` vs `5.3_clinical.py` | No. The plan preserves both bodies of content; the merged 5.2 will still diverge by track |
| P-17 | `5.2_basic.py` instructions tell the learner to "Select an RGB image (like the Mandrill…)" — no Mandrill image exists in the repo | `5.2_basic.py:83` | No. The plan removes that section (§4.2) |
| P-18 | `1.1_basic.py` hardcodes `model_id = "gemma-3-27b-it"` while `1.1_clinical.py` uses `cfg.DEFAULT_MODEL` (= `"gemma-4-31b-it"`), so the two tracks call **different models**. All of Module 7 also hardcodes `"gemma-3-27b-it"`, ignoring `aipassport_config.py` | `1.1_basic.py:89` vs `1.1_clinical.py:91`; `aipassport_config.py:4` | No. See R-8 |
| P-19 | `1.1_*.py` defines `def get_property(property): try: return property except KeyError:` — a no-op wrapper (a bare name lookup cannot raise `KeyError`) that shadows the builtin `property`, and the surrounding code will still `KeyError` on a malformed LLM response | `1.1_basic.py:60-64` | No, but it is dead code the merge should drop |
| P-20 | `aipassport_notebooks.py:214-232` re-reads and re-`exec`s the notebook file on **every** rerun with no caching, so every widget interaction re-parses and re-executes the whole page | `render_notebook_page()` | No. Existing behaviour; merged pages are larger, so keep `@st.cache_data` on the loaders |

---

## 11. Expected Phase 2 File Changes

### 11.1 Entrypoint and docs

| File | Change |
| --- | --- |
| `aipassport_notebooks.py` | replace `N_MICROSKILLS_PER_MODULE` with a `MODULE_SUBSECTIONS` literal (module → two titles); rewrite the registration loop (`:258-274`) to emit two pages per module with real titles; optionally add `LEGACY_URL_ALIASES` + a `_legacy` page group skipped by `render_home_page()` (pending R-1); optionally skip empty module groups in `render_home_page()` (pending R-6) |
| `docs/deployment_doc.md` | update the iframe example; add the old→new `url_path` map |
| `docs/consolidation-plan.md` | this file (Phase 1 artefact; retained) |
| `README.md` | optional: note two subsections per module |
| `requirements.txt` | **no change** unless R-1/P-4 is approved |
| `aipassport_config.py` | **no change** |
| `packages/aip_chat_simple/` | **no change** — `_live_state`/`_screen_image`/`messages` contract preserved |

### 11.2 Notebooks

| Module | Created / rewritten | Deleted |
| --- | --- | --- |
| 1 | `1.1_{basic,clinical}.py`, `1.2_{basic,clinical}.py` | old `1.3`–`1.7` (10 files); old `1.1`/`1.2` rewritten in place |
| 2 | `2.1_{basic,clinical}.py`, `2.2_{basic,clinical}.py` | old `2.3`, `2.5`, `2.6`, `2.7` (8 files) + `2.5_clinical_converted_from_ipynb_WIP.py`; old `2.1` rewritten in place |
| 3 | `3.1_{basic,clinical}.py`, `3.2_{basic,clinical}.py` | old `3.3`, `3.4`(basic-only), `3.5`, `3.6` (7 files); old `3.2` becomes the new `3.1` |
| 4 | `4.1_{basic,clinical}.py`, `4.2_{basic,clinical}.py` | old `4.3`, `4.4`, `4.5`, `4.6`, `4.7` (10 files); old `4.1`/`4.2` rewritten in place |
| 5 | `5.1_{basic,clinical}.py`, `5.2_{basic,clinical}.py` | old `5.3`, `5.4`, `5.5`, `5.6` (8 files); old `5.1`/`5.2` rewritten in place |
| 6 | none | none |
| 7 | `7.1_{basic,clinical}.py`, `7.2_{basic,clinical}.py` | old `7.3`–`7.7` (5 files); old `7.1`/`7.2` rewritten in place; `7.2_basic.py` created (R-5) |

Net: **67 registered files → 24**, plus the dead WIP file removed.

### 11.3 Context JSON (`assets/notebook_context/`)

59 files → **24**, renamed to `{M}.{1,2}_{track}.json`. Each surviving file needs `microskill`,
`title`, `objectives[]`, and especially `sections[]` rewritten to describe the merged lesson's real
controls — the AI Guide reads `sections[].how_to_use` verbatim
(`aipassport_notebooks.py:121-139` → `chat.py:116-121`), so stale entries would make the tutor
describe widgets that no longer exist. **Module 7 currently has no context files at all** (9
missing); creating four is optional and should be treated as an improvement, not a requirement.

Per-file current measurements used for §6 (lines / approximate prose words), for reference during
editing:

```
M1  1.1 233/419 b  247/431 c | 1.2 188/797 b  241/395 c | 1.3 187/826 b  192/612 c
    1.4 250/818 b  242/867 c | 1.5 193/540 b  260/712 c | 1.6 199/412 b  192/398 c
    1.7 107/561 b  111/620 c
M2  2.1  98/440 b   95/505 c | 2.3 100/559 b   90/634 c | 2.5 241/291 (identical)
    2.6  41/228 b   40/211 c | 2.7 485/687 (identical) | WIP 2200/2403 (dead)
M3  3.2 288/911 (identical)  | 3.3 181/343 b  197/316 c | 3.4 150/226 (basic only)
    3.5 133/46  b  154/242 c | 3.6 277/430 (identical)
M4  4.1 269/861 | 4.2 285/804 | 4.3 285/804 (dup) | 4.4 259/981
    4.5 459/448 | 4.6 312/539 | 4.7 180/220        (all identical across tracks)
M5  5.1 103/291 b  120/399 c | 5.2 297/782 b  219/429 c | 5.3  93/197 b  121/63  c
    5.4  43/122 b   43/110 c | 5.5  11/1  (identical)   | 5.6  31/100 b   31/113 c
M7  7.1 88/195 (both) | 7.2–7.7 72/68–86 each (clinical only)
```

### 11.4 Assets

**No asset deletions are proposed.** Verification results:

- Still referenced after consolidation: `assets/widgets/1.1_ai_timeline.json`,
  `assets/llm/1.1_*` (2 files), `assets/llm/7.1`–`7.7_gemini_system_instruction.txt` (**all seven
  survive** — the Module 7 merge changes the wrapper, not the prompts),
  `assets/images/headers/1.1_header.png`, `assets/images/headers/7.1_header.png`,
  `assets/images/content/Identifying Structures in X-Ray Imaging.png`,
  `assets/datasets/csv/diabetes.csv`, `assets/datasets/csv/eicu_demo.csv`, and 8 of the 10 files in
  `assets/datasets/images/`.
- Already-unreferenced before this work (P-10, P-11) and **kept**: the four `3.3 * fig*.png`,
  `IM-0003-0001.jpeg`, `fracture.jpg`, `data_clean_v2.csv`. Their non-use is a pre-existing
  condition, not a consequence of consolidation, so deleting them is out of scope.

### 11.5 Proposed commit sequence

1. `Add curriculum consolidation plan` *(this file — Phase 1)*
2. `Remove duplicate and dead notebooks (4.3, 4.5, 2.5 WIP)`
3. `Consolidate Module 1 into two subsections`
4. `Consolidate Module 2 into two subsections`
5. `Consolidate Module 3 into two subsections`
6. `Consolidate Module 4 into two subsections`
7. `Consolidate Module 5 into two subsections`
8. `Consolidate Module 7 into two subsections`
9. `Register two subsections per module with real titles`
10. `Rewrite notebook context files for consolidated subsections`
11. `Add legacy URL aliases and update deployment docs` *(only if R-1 approved)*

### 11.6 Phase 2 verification plan

No Python dependencies are installed in this working copy (`import streamlit` fails), and there is no
test suite, so Phase 2 verification must begin with `pip install -r requirements.txt` in a fresh
virtualenv (`.gitignore` already excludes `venv/`). Planned checks:

1. `streamlit run aipassport_notebooks.py` starts without exception.
2. Home page shows exactly two buttons per module (Modules 1–5, 7) and, per R-6, whatever was
   decided for Module 6.
3. Each of the 12 subsections loads on **both** tracks — 24 page loads — with no
   `DuplicateWidgetID`, no `StreamlitAPIException`, and no `st.exception` traceback from the
   entrypoint's `exec` handler.
4. Exercise each surviving interactive element at least once (sliders, MCQ submit buttons, the
   Fact-or-Fiction and Module 7 LLM activities — the latter two need
   `NAVIGATOR_TOOLKIT_API_KEY`; if unavailable, confirm the graceful-degradation path instead and
   report it as untested rather than passing).
5. Repo-wide grep for removed identifiers: old `url_path` strings, `Microskill 4.3`,
   `build_eicu_data`, `experiment_input`, `proc_run`, `act2_history`, `act3_results`,
   `feature_goal_*_54`, `risk_*_56`, and the removed section titles.
6. Confirm every `assets/` string literal in the surviving notebooks resolves to a file on disk.
7. Note explicitly whether `cv2` was installable (P-4) and therefore whether Module 5 was verified
   end to end or only partially.
