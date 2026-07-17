# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="3.2 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "3.2",
  "module": "3",
  "module_name": "Data",
  "title": "Ethical Data Acquisition Audit",
  "objectives": [
    "Review autonomy, justice, privacy, and beneficence as clinical data acquisition pillars.",
    "Revise consent language for clearer patient understanding.",
    "Evaluate representation gaps and recruitment strategies.",
    "Select privacy controls and return-of-value practices."
  ],
  "sections": [
    {
      "title": "Module MS2: Acquiring Ethically Sourced Biomedical Data",
      "body": [
        "**1. Autonomy**\n\nInformed Consent & Control",
        "**2. Justice**\n\nEquitable Representation",
        "**3. Privacy**\n\nData Security & Encryption",
        "**4. Beneficence**\n\nReturning Value to Society"
      ],
      "prompts": []
    },
    {
      "title": "Activity 1: The 'Fine Print' Audit (Autonomy)",
      "body": [
        "#### Current Protocol (Legal Standard)",
        "**Audit Finding:** Low comprehension. Participants may feel alienated or coerced.",
        "#### Revision Tool",
        "Status: No changes made. (See warning on left)",
        "Status: Improved, but still transactional.",
        "**Audit Result:** Compliant. The participant is empowered to make an informed choice."
      ],
      "prompts": []
    },
    {
      "title": "Activity 2: The 'Hidden Population' Audit (Justice)",
      "body": [
        "#### REP-EQUITY Toolkit Configuration",
        "Step 1: Define Underserved Groups",
        "Steps 3 & 4: Set Recruitment Goal",
        "Step 5: Manage External Factors (Select Strategies)",
        "Step 6: Evaluate Representation",
        "**Audit Result:** FAIL. Additional strategies are needed to reach the target goal."
      ],
      "prompts": []
    },
    {
      "title": "Security Protocol Checklist",
      "body": [
        "#### Simulation Results",
        "Status: SECURE. Multi-layered protocols are active. Compliance verified.",
        "Status: VULNERABLE. Some protections are in place, but gaps remain. High risk of breach.",
        "Status: CRITICAL RISK. Data is effectively unprotected. Protocol rejected."
      ],
      "prompts": []
    },
    {
      "title": "The Ethical Data Cycle",
      "body": [
        "Module MS2 | Course Materials | Based on the REP-EQUITY Toolkit and IC3 dataset"
      ],
      "prompts": []
    },
    {
      "title": "Intro: The Four Pillars",
      "body": [
        "Frame the ethical audit target and learner role."
      ],
      "prompts": []
    },
    {
      "title": "Autonomy: Consent Audit",
      "body": [
        "Compare legalistic consent language with patient-centered language."
      ],
      "prompts": []
    },
    {
      "title": "Justice: Representation Audit",
      "body": [
        "Use recruitment strategies to close representation gaps."
      ],
      "prompts": []
    },
    {
      "title": "Privacy: Security Audit",
      "body": [
        "Select layered security controls and inspect risk status."
      ],
      "prompts": []
    },
    {
      "title": "Beneficence: Impact Audit",
      "body": [
        "Complete the ethical data cycle by returning value to patients and communities."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/3.2_clinical.py"
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
          <h1>3.2 · Ethical Data Acquisition Audit</h1>
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
