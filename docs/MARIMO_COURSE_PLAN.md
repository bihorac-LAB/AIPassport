# AI Passport: course map and Marimo direction

## Purpose

AI Passport is a low/no-code AI upskilling course for biomedical and clinical researchers. Its public learning model is **See → Practice → Reflect → Share**: short didactic content introduces a concept, an interactive case-study notebook lets learners apply it, reflection connects it to their work, and community activity supports discussion and feedback. The interactive notebooks in this repository primarily implement the **Practice** layer; Canvas currently supplies much of the surrounding course sequence, reflection, submission, and community context.

The public curriculum describes seven core modules:

| Module | Semantic role | Current notebook coverage |
| --- | --- | --- |
| 1. Fundamentals | AI concepts and lifecycle; experiment design, validation, teams, rigor, and peer review | Complete: 1.1–1.7 in basic and clinical tracks |
| 2. Alignment | Bioethics, bias/fairness, quality and safety, human–AI collaboration, and sex-specific modeling | 2.1, 2.3, 2.5–2.7; 2.2 and 2.4 are absent |
| 3. Data | Ethical acquisition, reliability, standards, preprocessing, and multi-institutional sharing | 3.2–3.6 overall; basic has 3.4, clinical does not; 3.1 and 3.7 are absent |
| 4. Machine learning | Vocabulary, ML/DL fundamentals, model choice/training, evaluation, reproducibility, fairness, and explainability | Complete: 4.1–4.7 in both tracks |
| 5. Biomedical imaging | Modalities, image processing, feature extraction, computer vision, fusion, and consistency | 5.1–5.6 in both tracks; 5.7 is absent |
| 6. Generative AI | Generative biomedical AI and LLMs | No Module 6 notebooks are present |
| 7. Impact project | Experiment design, proposals, communication, translation, peer review, rigor, and responsibility | Clinical has 7.1–7.7; basic has only 7.1 |

The public site also advertises Agentic AI, but the current application navigation defines only the seven modules above. It should initially be treated as a future course/module decision rather than silently folded into this migration.

## How the repository currently composes the course

`aipassport_notebooks.py` is a hidden-navigation Streamlit shell. It generates routes from the `{module}.{microskill}_{track}.py` naming convention, chooses a `basic` or `clinical` file, executes that file, and places the AIP Guide beside it. `aipassport_config.py` holds shared model and presentation settings. JSON files under `assets/notebook_context/` give the guide lesson context; `assets/llm/` contains activity-specific prompts/schemas; images and widget data support individual exercises.

The inventory contains **37 routable microskills**, implemented by **67 standard track files** (31 basic and 36 clinical), plus one clinical WIP conversion file that is not routed. These are Python Streamlit pages, despite being called notebooks. Track separation is uneven: 12 basic/clinical pairs are currently byte-identical, while some nominally basic or clinical pages include their own internal track selector. The migration should therefore consolidate by **learning objective and activity**, not mechanically convert 67 files one-for-one.

Suggested Marimo target:

1. One Marimo app notebook per routable microskill, with shared lesson logic and track-specific content/data selected through a visible `mo.ui` control or trusted launch parameter.
2. Shared Python packages for branding, layouts, datasets, analytics events, and the AIP Guide; do not duplicate these across notebook cells.
3. A small course index/router that preserves stable IDs such as `4.3`, `track=clinical`, and a content version. Stable IDs are essential for Canvas links and longitudinal analytics.
4. Each app follows the same semantic template: orientation/objective, activity, feedback, reflection prompt, completion signal, and next step. The notebook remains useful in Marimo app mode with source code hidden.
5. Convert one representative vertical slice first (for example, a simple lesson, a data-heavy lesson, an image lesson, and an AIP Guide lesson), then establish conversion patterns before migrating the remainder.

## Measuring success

Page views alone will not demonstrate educational impact. Use a small, versioned event contract shared by every notebook and combine it with Canvas outcomes and brief surveys.

### Stakeholder measures

| Question | Measures |
| --- | --- |
| Are learners reaching the tools? | unique learners/sessions, launches by module and track, launch success rate |
| Are they engaging? | activity start rate, meaningful interactions, active time, return rate, AIP Guide use |
| Are they completing? | activity completion and module completion, time to completion, abandonment step |
| Are they learning? | pre/post knowledge or confidence change, embedded knowledge checks, rubric/assignment outcomes in Canvas |
| Does the software work? | error-free session rate, startup time, interaction latency, dependency/API failures |
| Is access equitable? | aggregate completion and outcome comparisons across approved demographic/accessibility groupings, with minimum-cell suppression |

Recommended events are `notebook_opened`, `activity_started`, `interaction_completed`, `knowledge_check_submitted`, `reflection_reached`, `activity_completed`, `guide_used`, and `app_error`. Each event should include a random event ID, timestamp, pseudonymous learner/session ID, module/microskill ID, track, content version, deployment, and a small activity-specific payload. Avoid collecting prompt/free-text contents, uploaded biomedical data, raw IP addresses, names, emails, or Canvas access tokens in the analytics stream.

Use a first-party `/events` endpoint that validates the schema and writes to an institution-approved store. Build a stakeholder dashboard from aggregate data and join to Canvas outcome data only in a controlled analysis layer. Define the metric specification, baseline Streamlit cohort, target values, retention period, access roles, and data-quality checks before launch. A useful first evaluation is a pre/post comparison plus funnel and reliability reporting; if feasible, compare the existing Streamlit cohort with the Marimo pilot while accounting for cohort differences.

NIH sponsorship makes transparent evaluation and privacy practice especially important, but it does not by itself determine whether this evaluation is human-subjects research. Before attaching stable learner identity or analyzing demographic/outcome relationships, confirm the plan with UF's IRB/privacy/security and Canvas administrators. Publish a short notice describing the purpose, fields, vendors, retention, access, and opt-out behavior. NIH's own web-measurement notice is a useful model: it emphasizes aggregate mission-related use, access controls, retention, vendor disclosure, and avoiding PII.

## Hosting and Canvas integration

| Option | Best use | Analytics/identity implications |
| --- | --- | --- |
| Molab + GitHub | Fast public pilot and demonstrations | GitHub can remain the source of truth and Molab can share apps/iframes. Embedded apps run in browser WebAssembly, so every dependency and network call must be WASM/CORS compatible. Sessions are ephemeral and Molab should not be the system of record for learner analytics. Send approved events to a separate first-party endpoint. |
| Static Marimo WASM on UF/GitHub Pages/Cloudflare | Low-operations, scalable public activities | Good for fully client-side lessons. The host provides traffic logs, while meaningful learning events still require an event endpoint. Server-only Python, secrets, and many native packages will not work. |
| Self-hosted `marimo run` or Marimo mounted in FastAPI | Production course, server-side AI, durable analytics, institutional controls | Recommended when the AIP Guide needs protected API keys or when identity, middleware, audit logs, and reliable event collection matter. FastAPI can mount multiple Marimo apps and add UF authentication/analytics middleware. Requires operations, scaling, WebSocket/proxy configuration, and security review. |
| Current Streamlit Community Cloud | Baseline during migration | Keep temporarily for comparison and rollback, but do not build the long-term measurement architecture around platform-only traffic counts. |

**Recommended sequence:** pilot several WASM-compatible notebooks in Molab and iframe them in a Canvas sandbox; simultaneously prototype the common event schema and first-party collector. Decide on production hosting only after testing package compatibility, cold starts, concurrent users, Canvas behavior, accessibility, and analytics delivery. Move to self-hosting if protected AI calls, durable state, authenticated learner-level evaluation, or stronger service guarantees are required.

A plain Canvas iframe is appropriate for the pilot. Confirm that the host permits framing and that Canvas allows the required iframe `sandbox` attributes; Marimo requires JavaScript. Test third-party cookie behavior, mobile sizing, keyboard navigation, screen readers, downloads, popups, and full-screen views. Canvas can observe that a learner visited the containing page, but it cannot reliably see detailed cross-origin interactions inside the notebook, so the notebook must emit its own events.

For production, use **LTI 1.3** instead of query-string identity if the app must know the learner/course, return grades, or create trusted per-user linkage. Use the LTI subject as an input to an institution-controlled pseudonymization step, never as a public analytics identifier. If no identity or grade passback is needed, keep the iframe anonymous and let Canvas remain the completion/submission system.

## Immediate discovery work

- Confirm the authoritative Canvas module/microskill list and resolve the repository gaps, especially Module 6 and basic Module 7.
- Classify all activities as WASM-safe, server-required, or requiring redesign; include the AIP Guide and file uploads in this audit.
- Define a canonical lesson manifest: stable ID, title, objective, module, track variants, data/assets, dependencies, completion rule, Canvas URL, and analytics version.
- Agree on 5–8 stakeholder KPIs and the privacy/retention review before instrumentation begins.
- Convert and user-test the representative vertical slice before estimating the full migration.

## References

- [AI Passport public course description](https://aipassport.org/)
- [UF PRISMAp AI Passport overview](https://prismap.medicine.ufl.edu/research/ai-passport/)
- [Marimo: run in the cloud with Molab](https://docs.marimo.io/guides/molab/)
- [Marimo: embed notebooks in other webpages](https://docs.marimo.io/guides/publishing/embedding/)
- [Marimo: deploy notebook apps](https://docs.marimo.io/guides/deploying/)
- [Marimo: mount apps in FastAPI](https://docs.marimo.io/guides/deploying/programmatically/)
- [NIH web measurement and privacy notice](https://www.grants.nih.gov/web-policies-and-notices/privacy-notice)
- [NIH principles for protecting participant privacy](https://www.grants.nih.gov/policy-and-compliance/policy-topics/sharing-policies/dms/privacy/best-practices)
