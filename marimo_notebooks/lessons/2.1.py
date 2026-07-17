# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="2.1 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "2.1",
  "module": "2",
  "module_name": "Alignment",
  "title": "The Fundamental Principles of Bioethics",
  "objectives": [
    "Identify the four principles of bioethics in a clinical AI privacy case.",
    "Explain conflicts between AI accuracy, patient privacy, harm prevention, and fairness.",
    "Justify which principle should guide hospital policy when re-identification risk exists.",
    "Reflect on rare groups, de-identification limits, and trust in clinical AI."
  ],
  "sections": [
    {
      "title": "Navigating AI and Bioethical Principles in Clinical Practice",
      "body": [
        "Map the case to autonomy, beneficence, non-maleficence, and justice.",
        "Select all relevant principles, then optionally compare with the example.",
        "**Objective:**  \nDevelop the skills to navigate ethical issues arising from the use of AI using the four principles of bioethics.",
        "A hospital is piloting an AI system to predict disease risks and support early diagnosis, hoping to improve patient outcomes.  \nThe system uses vast amounts of **de-identified patient data**, such as demographics, clinical histories, and lifestyle information.  \nDe-identified data means no names or addresses, but the AI still analyzes broad health trends.\n\n**Ethical Dilemma:** For maximum accuracy, the AI benefits from detailed geographic and demographic information.  \nBut: such details can sometimes allow \"re-identification\"—figuring out who an individual is, especially in unique combinations or rare diseases.\n\nIf a patient’s health information were re-identified and accessed by third parties (employers, insurers, cybercriminals),  \nit could lead to discrimination, financial harm, and loss of privacy."
      ],
      "prompts": []
    },
    {
      "title": "1. Which of the four principles of bioethics apply here?",
      "body": [
        "All four principles are relevant:\n- **Autonomy**: Patients expect control over their private information; re-identification risks violate their autonomy and privacy.\n- **Beneficence**: The AI could improve diagnosis and outcomes (population benefit).\n- **Non-maleficence**: Re-identification could cause real harm (discrimination, financial harm).\n- **Justice**: If certain groups are more at risk for re-identification (rare conditions, small communities), or are excluded for privacy, this raises fairness concerns."
      ],
      "prompts": []
    },
    {
      "title": "2. Which principles are in conflict? Why?",
      "body": [
        "- **Beneficence** (improving care via better AI) vs. **Autonomy**/**Non-maleficence** (protecting privacy, preventing harm):\n• The more detailed the data, the more AI helps patients—BUT the higher the risk of re-identification and harm.\n- **Justice** can also conflict if privacy risks are unequally distributed, or if some populations are excluded to protect privacy."
      ],
      "prompts": [
        "Explain which principles may come into conflict and describe how:"
      ]
    },
    {
      "title": "3. On your view, which principle should take precedence? Why?",
      "body": [
        "Practice defending an ethical clinical policy position.",
        "Choose which principle should guide clinicians and hospital policy, then justify the tradeoff.",
        "Example: While beneficence is important, **non-maleficence** (do no harm) and **autonomy** (patient privacy) should take precedence—especially where privacy breaches can cause irreversible harm. The hospital must put safeguards in place so that no patient can be re-identified, even if it reduces AI accuracy somewhat; otherwise, trust is lost and harm may result."
      ],
      "prompts": [
        "Defend your view: which principle should guide clinicians and hospital policy here, and why?"
      ]
    },
    {
      "title": "Reflection",
      "body": [
        "Connect bioethics to patient trust and vulnerable groups.",
        "Reflect on rare demographic groups, privacy safeguards, and questions raised by AI data use.",
        "- What new questions do you have about the use of AI and patient data in healthcare?\n- How might your thinking change if you were a member of a rare demographic group?",
        "Thank you for your thoughtful engagement with AI and bioethics in clinical care.",
        "---\n**Key Concepts:**  \n- Autonomy = respecting patients’ wishes and privacy  \n- Beneficence = doing good for the patient/population  \n- Non-maleficence = avoiding harm  \n- Justice = fairness in distribution of risks and benefits\n\n**Further reading:** [Principlism in Clinical Ethics (Stanford)](https://plato.stanford.edu/entries/principle-bioethics/)"
      ],
      "prompts": [
        "Optional: Add your reflections here"
      ]
    },
    {
      "title": "Clinical Case",
      "body": [
        "Introduce a hospital AI system using de-identified data with re-identification risk.",
        "Read the case and notice the tension between detailed data for accuracy and privacy risks."
      ],
      "prompts": []
    },
    {
      "title": "Principle Conflicts",
      "body": [
        "Explain ethical tensions around detailed clinical data use.",
        "Describe how improving care can conflict with privacy, harm prevention, and fairness."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/2.1_clinical.py"
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
          <h1>2.1 · The Fundamental Principles of Bioethics</h1>
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
