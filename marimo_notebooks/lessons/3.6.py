# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="3.6 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "3.6",
  "module": "3",
  "module_name": "Data",
  "title": "Multi-Institutional Data Sharing Simulation",
  "objectives": [
    "Generate simulated hospital datasets.",
    "Detect and remove outliers before collaboration.",
    "Impute and scale local clinical data consistently.",
    "Run a federated-learning-style round without sharing patient records."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "### Interactive Federated Learning Simulation",
        "INSTRUCTIONS: This simulation guides you through the process of preparing a local dataset and collaborating with another institution without sharing raw data. Follow the numbered steps below, adjusting parameters in the sidebar and main area to observe changes.",
        "**Current Scenario:** Harmonizing patient data from multiple hospitals (City General vs. Mountain View) to predict COVID-19 severity.\n**Challenge:** Outliers (measurement errors) and Missing Data (O2 Saturation) must be handled locally before the model can be shared."
      ],
      "prompts": []
    },
    {
      "title": "Step 1: Local Data Inspection",
      "body": [
        "Inspect the raw local dataset.",
        "Before collaboration, inspect your local data for issues.",
        "Note: 'Feature_Target' contains the critical values for the model, and 'Feature_Secondary' contains missing values (NaN)."
      ],
      "prompts": []
    },
    {
      "title": "Step 2: Outlier Detection",
      "body": [
        "Use a z-score threshold to identify values for removal.",
        "Outliers can severely skew Federated Learning models. Use the Z-Score method to identify and remove data points that are statistically improbable."
      ],
      "prompts": []
    },
    {
      "title": "Configuration",
      "body": [
        "Please check 'Apply Filter and Proceed' to move to the next step."
      ],
      "prompts": []
    },
    {
      "title": "Step 3: Standardization & Imputation",
      "body": [
        "Federated Learning requires all institutions to preprocess data identically so the model weights are compatible."
      ],
      "prompts": []
    },
    {
      "title": "Step 4: Federated Learning Simulation",
      "body": [
        "Aggregate model weights instead of sharing raw patient data.",
        "In this step, we simulate the **NVIDIA FLARE** workflow.\nInstead of sending this cleaned data to a central server, we will:\n1. Train a local model (calculate weights) on Institution A.\n2. Train a local model on Institution B.\n3. Send ONLY the weights to the aggregator.",
        "#### Institution Node A",
        "Local Weights (Private)",
        "#### Institution Node B",
        "Local Weights (Private)",
        "#### Global Server",
        "Aggregated Global Model",
        "Federated Round Complete. Global model updated without data leakage."
      ],
      "prompts": []
    },
    {
      "title": "Simulation Settings",
      "body": [
        "Choose scenario, sample size, and outlier contamination."
      ],
      "prompts": []
    },
    {
      "title": "Standardization and Imputation",
      "body": [
        "Prepare compatible clinical data locally."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/3.6_clinical.py"
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
          <div class="aip-kicker">AI Passport · Module 3: Data</div>
          <h1>3.6 · Multi-Institutional Data Sharing Simulation</h1>
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
