# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="2.5 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "2.5",
  "module": "2",
  "module_name": "Alignment",
  "title": "Biomedical AI Quality and Safety Simulator",
  "objectives": [
    "Recognize covariate shift in a simulated sepsis prediction model.",
    "Compare doing nothing versus retraining under clinical distribution shift.",
    "Evaluate vendor model discrimination and calibration on a mismatched local population.",
    "Build a model card documenting intended clinical use, limitations, metrics, and ethical considerations."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**Interactive Simulator:**\n* **Activity 1 (Drift):** Visualize **Covariate Shift** in a Sepsis model and practice **Retraining**.\n* **Activity 2 (Evaluation):** Compare **Calibration vs. Discrimination** in a vendor model.\n* **Activity 3 (Transparency):** Build a **Model Card** to document limits and intended use."
      ],
      "prompts": []
    },
    {
      "title": "Activity 1: Recognizing Data Drift",
      "body": [
        "Simulate how model performance degrades over time due to covariate shift, and test if retraining fixes the issue."
      ],
      "prompts": []
    },
    {
      "title": "Simulation Controls",
      "body": [
        "Model has 'learned the new normal' (Retrained).",
        "A high False Positive rate leads to 'Alert Fatigue' and unnecessary antibiotics."
      ],
      "prompts": []
    },
    {
      "title": "Visualizing Covariate Shift",
      "body": [
        "This graph demonstrates **Covariate Shift**: The input data (Lactate) has changed distribution, confusing the original model."
      ],
      "prompts": []
    },
    {
      "title": "Activity 2: Calibration vs. Discrimination",
      "body": [
        "Analyze a vendor model's performance on a local population by comparing Discrimination (ranking) and Calibration (reliability)."
      ],
      "prompts": []
    },
    {
      "title": "Vendor Model Check",
      "body": [
        "High Discrimination (Good at ranking patients).",
        "Low Discrimination."
      ],
      "prompts": []
    },
    {
      "title": "Calibration Curve (Reliability Diagram)",
      "body": [
        "**How to read this:**\n* **On the Diagonal:** Perfect Calibration.\n* **Below Diagonal:** The model **Overestimates** risk (Predicted 80%, Actual 40%).\n* **Above Diagonal:** The model **Underestimates** risk."
      ],
      "prompts": []
    },
    {
      "title": "Activity 3: Model Card Builder",
      "body": [
        "Practice clinical model documentation before deployment.",
        "Fill in intended users, caveats, and ethical considerations, then review the generated model card.",
        "Create a transparency document to communicate the model's intended use and limitations."
      ],
      "prompts": []
    },
    {
      "title": "Enter Model Details",
      "body": [],
      "prompts": [
        "Model Name",
        "Developer",
        "Intended Users",
        "Caveats / Limitations",
        "Ethical Considerations"
      ]
    },
    {
      "title": "Sepsis Drift",
      "body": [
        "Show how changing patient populations or lab distributions can affect alerts.",
        "Move the months slider, compare lactate distributions, choose a mitigation strategy, and watch false positive rate."
      ],
      "prompts": []
    },
    {
      "title": "Vendor Calibration",
      "body": [
        "Evaluate whether a vendor model is reliable on the local population.",
        "Adjust population mismatch, review AUC, and inspect calibration to see whether predicted risks match actual risks."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/2.5_clinical.py"
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
          <div class="aip-kicker">AI Passport · Module 2: Alignment</div>
          <h1>2.5 · Biomedical AI Quality and Safety Simulator</h1>
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
