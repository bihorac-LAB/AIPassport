# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.2 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.2",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Artificial Intelligence Lifecycle",
  "objectives": [
    "Explore how deployed AI model performance changes across data batches.",
    "Connect data drift, validation checks, and retraining decisions.",
    "Practice interpreting accuracy, ROC-AUC, confusion matrices, and predicted probability distributions."
  ],
  "sections": [
    {
      "title": "Heart Disease Risk Predictor and Model Monitoring",
      "body": [
        "**Dataset:** Simulated Heart Disease Prediction Data (entirely included here)  \n---\n\nThis notebook simulates a deployed AI model for heart disease risk prediction.  \nYou will:  \n- **Explore model performance across deployment versions**\n- **Simulate data drift**\n- **Practice data validation**\n- **Decide when to trigger model retraining**\n- **Reflect on good AI lifecycle management**\n---\n### 1. Dataset Overview\n\nThis scenario uses a **simulated EHR dataset** for heart disease risk, each \"version\" containing 100 patients and these features:\n\n- `age` (years)\n- `systolic_bp` (mmHg)\n- `cholesterol` (mg/dL)\n- `bmi`\n- `smoker` (1/0)\n- `outcome` (1=Heart disease event, 0=No event)",
        "Sample of data (current batch):",
        "---\n## 2. Choose a Model Version and Test on New Data",
        "Distribution of predicted probabilities:",
        "---\n## 3. Observe Model Drift and Decide When to Retrain",
        "**Instructions:**  \n- Try different combinations above, e.g., test old (v1) model on recent (\"drifted\") batch, and compare vs. retrained models.\n- Watch for performance drop indicating “model drift”.\n\n**Q1: On which incoming batch does the performance of Model v1 FIRST significantly drop?**  \n**Q2: Does retraining recover performance?**  \nType your answers below.",
        "---\n## 4. Data Validation Checks",
        "**Practice data validation:**  \nArtificial Intelligence systems MUST check for data integrity before inference or retraining!\n\nBelow is a validator for 10 random patient records in the latest batch.  \nAdjust the validation thresholds to see impact.",
        "**Q3: What problems could arise if these validation steps are skipped?**",
        "---\n## 5. Lifecycle Management Scenario",
        "**Imagine:**  \nYou are responsible for the deployed **Model v2**. Over the last 3 months, performance dropped _from ROC-AUC 0.83 to 0.71_ due to population changes.  \n- **How would you handle model versioning?**  \n- **How would you document and monitor, e.g., with MLflow or DVC?**  \n- **What communication/actions would you take before retraining and deployment?**",
        "---\n**References:**  \n- [Jupyter notebook](https://jupyter.org/)  \n- [MLflow](https://mlflow.org/)  \n- [DVC](https://dvc.org/)  \n\n_This assignment simulates key components of AI clinical deployment, monitoring, and lifecycle practice!_"
      ],
      "prompts": [
        "Notes on model drift observations:",
        "Risks if no data validation:",
        "Your short action plan for lifecycle management:"
      ]
    },
    {
      "title": "Dataset Overview",
      "body": [
        "Introduce a simulated EHR-style heart disease risk dataset.",
        "Review the sample patient records and the outcome definition before changing model or batch selections."
      ],
      "prompts": []
    },
    {
      "title": "Model Version and New Data",
      "body": [
        "Compare deployed model versions against incoming batches.",
        "Change the model version and incoming batch. Watch how accuracy, ROC-AUC, the confusion matrix, and predicted probabilities change."
      ],
      "prompts": []
    },
    {
      "title": "Model Drift",
      "body": [
        "Help learners decide when model monitoring should trigger retraining.",
        "Try Model v1 on later batches, then compare against retrained versions. Use the notes box to record where performance changes."
      ],
      "prompts": []
    },
    {
      "title": "Data Validation Checks",
      "body": [
        "Show why clinical AI systems need input validation before inference or retraining.",
        "Adjust age, blood pressure, cholesterol, and BMI thresholds. Review which patient rows are flagged."
      ],
      "prompts": []
    },
    {
      "title": "Lifecycle Management Scenario",
      "body": [
        "Prompt learners to plan monitoring, versioning, documentation, and communication.",
        "Write a short action plan for model versioning, MLflow or DVC-style documentation, and stakeholder communication."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/1.2_clinical.py"
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
          <h1>1.2 · Artificial Intelligence Lifecycle</h1>
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
