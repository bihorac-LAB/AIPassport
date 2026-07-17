# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="4.3 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "4.3",
  "module": "4",
  "module_name": "Machine Learning",
  "title": "Applied Fundamentals of ML and DL",
  "objectives": [],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "### Navigation"
      ],
      "prompts": []
    },
    {
      "title": "Activity 1: Exploring Data Types",
      "body": [
        "### Instructions",
        "Complete each activity in order and record your responses to the module activities exclusively in your Canvas submission area.",
        "Before training a model, researchers must inspect the raw data to understand feature distributions and identify class imbalances."
      ],
      "prompts": []
    },
    {
      "title": "Data Preview",
      "body": [
        "Variable types recognized for each column:"
      ],
      "prompts": []
    },
    {
      "title": "Feature Distributions",
      "body": [
        "**Outcome Distribution**",
        "**The Job Task:** The objective is to predict in-hospital mortality using demographic and lab data to support ICU triage.\n**The Algorithmic Advantage:** A Deep Neural Network evaluates the non-linear interactions between variables. A specific blood pressure value may be safe for one patient but critical for another when combined with specific BMI and Glucose levels.\n**Understanding the Data Format:** Features are standardized so that large numerical values do not dominate the model's weight updates, ensuring all clinical metrics are treated proportionally."
      ],
      "prompts": []
    },
    {
      "title": "Activity 2: Model Optimization",
      "body": [
        "### Instructions",
        "Configure the optimization parameters to dictate how the network updates its internal weights. Execute the training pipeline and evaluate the resulting learning curve."
      ],
      "prompts": []
    },
    {
      "title": "Deep Neural Network Architecture",
      "body": [
        "Training Complete"
      ],
      "prompts": []
    },
    {
      "title": "Model Learning Curve",
      "body": [
        "**Comparison to MS1:** The DNN can reach higher accuracy than the Decision Tree by finding hidden layers of risk, but global accuracy alone is deceptive.\n**Metric Suitability:** In mortality prediction, accuracy is an insufficient metric. Because most patients survive, the model could guess 'Survival' for everyone and still appear accurate while failing to detect at-risk patients."
      ],
      "prompts": []
    },
    {
      "title": "Activity 3: Cross-Validation and Trade-Offs",
      "body": [
        "### Instructions",
        "Execute the 5-fold cross-validation analysis. Adjust the classification threshold to observe the statistical trade-offs between Sensitivity and Specificity.",
        "Evaluation Metrics Generated",
        "**Performance Evaluation:** Lowering the threshold improves Sensitivity (catching more deaths) but reduces Specificity (more false alarms). This adjustment is the interactive equivalent of moving along an ROC curve to find the optimal clinical balance."
      ],
      "prompts": []
    },
    {
      "title": "Activity 4: Strategic Evaluation",
      "body": [
        "### Instructions",
        "Determine the optimal algorithmic approach based on organizational requirements for interpretability versus performance."
      ],
      "prompts": []
    },
    {
      "title": "Architectural Comparison",
      "body": [
        "**Decision Tree (MS1)**",
        "- Logic: Interpretable 'If-Then' splits.",
        "- Transparency: High (White Box).",
        "**Deep Neural Network (Current)**",
        "- Logic: Complex non-linear combinations across hidden layers.",
        "- Transparency: Low (Black Box).",
        "Strategy: Use the Decision Tree. Clinician trust often relies on being able to follow the model's logic step-by-step.",
        "Strategy: Use the DNN. Raw predictive power is prioritized to maximize patient safety and triage accuracy.",
        "Strategy: A balanced approach may require hybrid models or post-hoc explainability tools.",
        "**Model Selection:** The DNN trades human readability for mathematical capacity. It is chosen for its superior ability to map complex features, but the Decision Tree remains the standard if structural transparency is the priority."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/4.3_clinical.py"
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
          <div class="aip-kicker">AI Passport · Module 4: Machine Learning</div>
          <h1>4.3 · Applied Fundamentals of ML and DL</h1>
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
