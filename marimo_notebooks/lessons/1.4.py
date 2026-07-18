# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.4 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.4",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Training, Validation, and Generalizability",
  "objectives": [
    "Identify risks in simple random splitting for clinical imaging datasets.",
    "Design clinically meaningful internal and external validation.",
    "Plan calibration, robustness, subgroup fairness, and continuous monitoring.",
    "Communicate performance and generalizability limits to clinical stakeholders."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**🗂 Datasets:**  \n- [MIMIC-CXR](https://physionet.org/content/mimic-cxr/2.0.0/)  \n- [NIH Chest X-ray Dataset](https://www.nih.gov/news-events/news-releases/nih-clinical-center-provides-one-largest-publicly-available-chest-x-ray-datasets-scientific-community)  \n\n**🛠 Tools:**  \n- [Keras (deep learning framework)](https://keras.io/)  \n- [ML-fairness-gym (fairness experiments)](https://github.com/google/ml-fairness-gym)",
        "This assignment will guide you step-by-step through robust validation and fairness strategies for developing deep learning models to detect pneumonia from chest X-rays.",
        "Click to expand each section, and interact with checkboxes, radios, and text boxes to develop your experimental design!",
        "**Clinical Case:**\nYour institution collected **10,000 chest X-rays** from three hospitals over 3 years, using five X-ray machines, with a diverse, mostly urban patient population."
      ],
      "prompts": []
    },
    {
      "title": "1.1 Issues with Simple Random Train-Test Split",
      "body": [],
      "prompts": [
        "Elaborate on the issues you selected and describe at least three risks of a simple random split."
      ]
    },
    {
      "title": "1.2 Advanced Data Splitting Strategy",
      "body": [
        "Design a splitting strategy that addresses:",
        "- Temporal factors\n- Equipment differences\n- Demographics\n- Prevalence variability"
      ],
      "prompts": [
        "Describe your proposed data splitting strategy in detail:"
      ]
    },
    {
      "title": "1.3 Linking Split to Identified Issues",
      "body": [
        "**Goal:** Evaluate your model robustly using the splits you designed."
      ],
      "prompts": [
        "Explain how your splitting strategy resolves the issues you chose in Task 1.1."
      ]
    },
    {
      "title": "2.1 Cross-Validation Framework",
      "body": [],
      "prompts": [
        "How would you stratify? (e.g., by outcome label, hospital, demographic variables)"
      ]
    },
    {
      "title": "2.2 Additional Internal Validation",
      "body": [],
      "prompts": [
        "Describe the additional approaches and their benefits."
      ]
    },
    {
      "title": "2.3 Calibration Approach",
      "body": [
        "How will you ensure your model's output probabilities are well-calibrated?",
        "**Clinical Case:**\nYour model (trained internally) will be tested on the **NIH Chest X-ray dataset**."
      ],
      "prompts": [
        "Describe your visualization(s) and how you will quantify calibration.",
        "Describe your recalibration approach (if needed)."
      ]
    },
    {
      "title": "3.1 External Validation Framework",
      "body": [],
      "prompts": [
        "How will you preprocess the external dataset to ensure compatibility?",
        "How will you compare model performance between internal and external datasets?"
      ]
    },
    {
      "title": "3.2 Addressing Generalizability Gaps",
      "body": [],
      "prompts": [
        "Your model underperforms on pediatric patients and portable machine X-rays. Propose a strategy to improve generalizability WITHOUT overfitting to this external dataset."
      ]
    },
    {
      "title": "3.3 Systematic Subgroup Evaluation",
      "body": [
        "How will you evaluate and address disparities?",
        "**Goal:** Model should remain accurate despite benign image variation."
      ],
      "prompts": [
        "Describe how you would (i) identify & quantify subgroup performance (demographics, clinical context), (ii) test for statistical significance, and (iii) address significant disparities detected."
      ]
    },
    {
      "title": "4.1 Robustness Experiments",
      "body": [],
      "prompts": [
        "For each selected variation, how would you implement and evaluate robustness?"
      ]
    },
    {
      "title": "4.2 Improving Device Robustness",
      "body": [],
      "prompts": [
        "Your model degrades with medical devices in images. Describe an approach to improve this (e.g., additional training, augmentations, post-processing, etc.)."
      ]
    },
    {
      "title": "4.3 Continuous Model Monitoring",
      "body": [
        "Develop a monitoring plan after deployment:",
        "**Goal:** Ensure model equitability across populations."
      ],
      "prompts": [
        "What continuous metrics will you track over time & how often will you evaluate robustness?",
        "How will you update models in production WITHOUT disrupting clinical workflow?"
      ]
    },
    {
      "title": "5.1 Evaluating Across Groups",
      "body": [],
      "prompts": [
        "Briefly describe your approach for evaluating performance in these subgroups."
      ]
    },
    {
      "title": "5.2 Common Pitfalls in Stratified Performance",
      "body": [],
      "prompts": [
        "How does your approach avoid these pitfalls?"
      ]
    },
    {
      "title": "5.3 Addressing and Communicating Group Disparities",
      "body": [],
      "prompts": [
        "Describe your approach for (i) identifying causes of disparities, (ii) mitigating without new bias, (iii) validating mitigation, and (iv) transparent communication."
      ]
    },
    {
      "title": "6.1 Performance-Generalizability Tradeoff",
      "body": [],
      "prompts": [
        "How would you handle trade-offs between improving performance on one subgroup at the expense of another?"
      ]
    },
    {
      "title": "6.2 Informing Future Data Collection",
      "body": [],
      "prompts": [
        "Based on your validation results, how would you guide future data collection? What would you prioritize?"
      ]
    },
    {
      "title": "6.3 Communication Strategy",
      "body": [
        "Assignment marked as complete! Review and save your responses as needed.",
        "You can show/hide sections as needed. Use the checklists, radios, and text entry points to structure your thinking throughout the assignment."
      ],
      "prompts": [
        "How would you communicate your model’s strengths and limitations to technical staff?",
        "To clinical end users?",
        "To hospital leadership?"
      ]
    },
    {
      "title": "Understanding Training and Validation Fundamentals",
      "body": [
        "Show why clinical imaging data needs careful splits.",
        "Select risks of random splitting, then design a temporal, hospital-aware, equipment-aware, or hybrid split."
      ],
      "prompts": []
    },
    {
      "title": "Internal Validation Techniques",
      "body": [
        "Build confidence before external testing.",
        "Choose cross-validation type, folds, stratification, metrics, internal holdouts, and calibration methods."
      ],
      "prompts": []
    },
    {
      "title": "External Validation and Generalizability",
      "body": [
        "Plan testing on the NIH Chest X-ray dataset.",
        "Describe compatibility preprocessing, performance comparison, refinement thresholds, and subgroup gaps."
      ],
      "prompts": []
    },
    {
      "title": "Model Robustness",
      "body": [
        "Evaluate model behavior under real-world image variation.",
        "Select variations to test and write monitoring/update plans."
      ],
      "prompts": []
    },
    {
      "title": "Demographic and Geographic Considerations",
      "body": [
        "Evaluate equitable performance across patient groups.",
        "Choose groups, identify pitfalls, and describe mitigation plus communication."
      ],
      "prompts": []
    },
    {
      "title": "Reflection",
      "body": [
        "Connect validation tradeoffs to deployment decisions.",
        "Write how to balance subgroup performance, future data collection, and stakeholder communication."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/1.4_clinical.py"
}""")
    return (lesson,)


@app.cell
def _(lesson, mo):
    mo.Html(
        """
        <style>
          :root {
            --gator-blue: #0021a5;
            --uf-orange: #fa4616;
            --ink: #17223b;
            --mist: #f4f7fb;
          }
          .aip-hero {
            border-left: 7px solid var(--uf-orange);
            border-radius: 14px;
            background: linear-gradient(135deg, #0021a5, #001a57);
            color: white;
            padding: 1.3rem 1.5rem;
            margin: .4rem 0 1.2rem;
          }
          .aip-kicker {
            color: #ffd8ca;
            font-size: .78rem;
            font-weight: 750;
            letter-spacing: .09em;
            text-transform: uppercase;
          }
          .aip-hero h1 { color: white; margin: .22rem 0 .35rem; }
          .aip-hero p { margin: 0; opacity: .88; }
          .aip-card {
            border: 1px solid #d9e2ef;
            border-radius: 12px;
            background: white;
            padding: 1rem 1.15rem;
          }
          .aip-source { color: #5f6b7c; font-size: .8rem; }
        </style>
        <div class="aip-hero">
          <div class="aip-kicker">AI Passport · Module 1: Fundamentals</div>
          <h1>1.4 · Training, Validation, and Generalizability</h1>
          <p>Interactive marimo lesson · browser-safe app mode</p>
        </div>
        """
    )
    return


@app.cell
def _(lesson, mo):
    section_options = {
        section["title"]: index
        for index, section in enumerate(lesson["sections"])
    }
    section_picker = mo.ui.dropdown(
        options=section_options,
        value=lesson["sections"][0]["title"],
        label="Lesson section",
        full_width=True,
    )
    objective_text = (
        "\n".join(f"- {objective}" for objective in lesson["objectives"])
        if lesson["objectives"]
        else "Use the activities to connect the lesson concepts to biomedical AI practice."
    )
    mo.vstack(
        [
            mo.accordion({"Learning objectives": mo.md(objective_text)}),
            section_picker,
        ],
        gap=1,
    )
    return (section_picker,)



@app.cell
def _(lesson, mo, section_picker):
    section = lesson["sections"][section_picker.value]
    section_body = "\n\n".join(section["body"])
    prompts = section["prompts"] or [
        "What is the most important idea or result from this section?"
    ]
    response_widgets = mo.ui.array(
        [
            mo.ui.text_area(
                label=prompt,
                placeholder="Write your response or notes here…",
                rows=3,
                full_width=True,
            )
            for prompt in prompts
        ],
        label="Your workspace",
    )
    mo.vstack(
        [
            mo.md(f"## {section['title']}"),
            mo.md(section_body) if section_body else mo.md(
                "Work through the prompts below and record your reasoning."
            ),
            response_widgets,
        ],
        gap=1,
    )
    return prompts, response_widgets, section


@app.cell
def _(lesson, mo, prompts, response_widgets, section):
    answers = response_widgets.value
    completed = sum(bool(answer.strip()) for answer in answers)
    export_lines = [
        f"# {lesson['id']} · {lesson['title']}",
        "",
        f"## {section['title']}",
        "",
    ]
    for prompt, answer in zip(prompts, answers):
        export_lines.extend([f"### {prompt}", "", answer or "_No response yet._", ""])
    export_markdown = "\n".join(export_lines)
    mo.hstack(
        [
            mo.md(f"**Progress:** {completed} / {len(prompts)} responses"),
            mo.download(
                data=export_markdown,
                filename=f"ai-passport-{lesson['id']}-responses.md",
                label="Download responses",
            ),
        ],
        justify="space-between",
        align="center",
        widths=[2, 1],
    )
    return


@app.cell
def _(lesson, mo):
    mo.Html(
        f'<p class="aip-source">Ported from <code>{lesson["source"]}</code> '
        f'on the consolidated <code>dev</code> branch.</p>'
    )
    return


if __name__ == "__main__":
    app.run()
