# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="3.3 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "3.3",
  "module": "3",
  "module_name": "Data",
  "title": "Radiology AI Reliability",
  "objectives": [
    "Simulate or upload radiologist annotation data.",
    "Measure inter-rater reliability with ICC.",
    "Identify high-disagreement images for review.",
    "Compare model accuracy as the number of radiologists changes."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**DATA PRIVACY NOTICE**: \nThis application is for demonstration and research simulation purposes only. \n**Do not upload** any Personally Identifiable Information (PII), Protected Health Information (PHI), or any confidential patient data. \nEnsure all datasets are fully anonymized before uploading.",
        "### Case Study: Lung Cancer Detection\n**Context:** Radiologists label chest X-rays as either **Cancerous (1)** or **Benign (0)**. Inconsistencies among radiologists can confuse AI models.\n\n**Objectives:**\n1.  **Quantify Agreement:** Use ICC to measure how consistently radiologists rate the images.\n2.  **Identify Ambiguity:** Find specific X-rays with high disagreement for potential re-review.\n3.  **Optimize Annotators:** Determine how many radiologists are needed to train a reliable AI model."
      ],
      "prompts": []
    },
    {
      "title": "Simulated Radiologist Diagnoses",
      "body": [
        "0 = Benign, 1 = Cancerous. Rows represent individual X-rays."
      ],
      "prompts": []
    },
    {
      "title": "Review High-Disagreement Images",
      "body": [
        "Find cases with the most diagnostic variance.",
        "The X-rays below have the highest variance in diagnosis (e.g., split decisions). These are candidates for expert re-review."
      ],
      "prompts": []
    },
    {
      "title": "AI Model Performance vs. Number of Radiologists",
      "body": [
        "Show how consensus size affects model accuracy.",
        "This curve shows how adding more radiologists to the consensus label improves the AI's ability to detect cancer.",
        "scikit-learn is not installed. Please install it to run the model simulation.",
        "**Interpretation:** * **Diminishing Returns:** Notice how the accuracy curve typically flattens out. The \"elbow\" of this curve suggests the optimal number of radiologists needed (cost-benefit).\n* **Noise Reduction:** More radiologists = stable consensus = better training data for the AI.",
        "### References",
        "* **Inter-rater Reliability:** \n* **Consensus Labeling:** Using majority vote or expert review to correct noisy labels."
      ],
      "prompts": []
    },
    {
      "title": "Simulation Settings",
      "body": [
        "Configure sample count, raters, disagreement rate, or upload annotations."
      ],
      "prompts": []
    },
    {
      "title": "Inter-Rater Reliability",
      "body": [
        "Use ICC to quantify diagnostic agreement."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/3.3_clinical.py"
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
          <h1>3.3 · Radiology AI Reliability</h1>
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
