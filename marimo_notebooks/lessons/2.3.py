# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="2.3 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "2.3",
  "module": "2",
  "module_name": "Alignment",
  "title": "Bias, Fairness, and Societal Impact of Biomedical AI",
  "objectives": [
    "Imagine a useful clinical AI system and identify fairness safeguards.",
    "Analyze possible bias vectors in an emergency-room triage algorithm.",
    "Explain risks from regional mismatch, demographic features, subjective inputs, and overreliance.",
    "Reflect on post-deployment fairness monitoring in clinical settings."
  ],
  "sections": [
    {
      "title": "Assignment 1: Imagine Your Ideal Clinical AI System",
      "body": [
        "Prompt learners to design a clinical AI tool with fairness safeguards.",
        "Describe what the system would do, why it is clinically useful, what data it would use, and how bias would be mitigated.",
        "> **Prompt:**  \n> Imagine that you could create any AI system to assist you with your clinical practice.  \n> - What would you design the system to do and why?  \n> - How might you safeguard against bias and unfairness?",
        "**Example:**\n\nI would create a system that cycles through patient data to predict which diseases are on the rise seasonally. This would allow hospitals to prepare for an influx of sickness and for clinicians to be on the lookout for specific symptoms. It would have to take in data from surrounding hospitals and clinics to be more accurate, as some hospitals serve certain demographics and without other data, we won’t have a very generalizable picture of what’s happening in the city or surrounding areas.\n\n**Guidance:**  \n- Describe a useful, necessary AI system for your clinical setting.  \n- Identify the types of data you would use and why.  \n- Explicitly consider risks of bias and unfairness, and how you would attempt to mitigate or monitor them."
      ],
      "prompts": [
        "Write your answer here (please address usefulness, necessity, and fairness/bias):"
      ]
    },
    {
      "title": "Assignment 2: Case Study on Algorithmic Triage in the ER",
      "body": [
        "A large hospital is the only level one trauma center in a 100-mile radius of a small city in the Southern United States.  \nBecause of this, the hospital receives an abundance of patients with traumatic injuries including vehicle crashes, shootings, catastrophic injuries, along with other injuries into its Emergency Room.  \nHospital staff and administration want to find a way to best determine which patients should receive the most immediate care.  \nTo do this, the hospital wants to decide whether to employ an algorithm that ranks patients by the acuity of their illness as calculated using the symptoms and demographic data input by hospital staff.\n\n> **Questions:**  \n> - What are the possible vectors of bias that might impact patient care?  \n> - What should the hospital consider before employing the algorithmic tool?  \n> - What are the possible negative outcomes?  \n> Explain your answer.",
        "**Example:**\n\nThe vectors of bias for the algorithm include the data and the people who will interpret the guidance from the algorithm. As the only trauma center in a 100-mile radius, the hospital will receive all kinds of terrible injuries that other hospitals may not receive, therefore, if the data that was used to train the algorithm is not similar, the resulting guidance will be off-base. Further, although the algorithms will only be used to offer guidance, some clinicians will think that the algorithm cannot be wrong, and they won’t critically consider the results.\n\n**Guidance:**  \n- Consider how the unique patient population (regional, demographic, trauma-specific) may or may not be reflected in the data used to train the model.  \n- Consider the risk that social, demographic, or subjective data could introduce or amplify bias.  \n- Reflect on the consequences (e.g., inequities in care, overreliance on algorithms, errors propagating)."
      ],
      "prompts": [
        "Write your answer here (please address data, bias, and practical implications):"
      ]
    },
    {
      "title": "Reflection and Takeaways",
      "body": [
        "Connect clinical AI fairness to monitoring and safe deployment.",
        "Write why societal impact matters and how fairness would be monitored after deployment.",
        "- Why is it important to account for societal impact and bias when designing clinical AI?\n- How would you monitor or check for fairness *after* deploying such a system?",
        "Thank you! Your careful thought on bias, fairness, and impact is essential for safe and effective clinical AI.",
        "---\n**Key Points:**  \n- Always consider how your data and clinical realities shape model fairness and effectiveness.\n- No algorithm is objective or immune to bias.\n- Both technical design and human interpretation can perpetuate or reduce inequity.\n\n*For further learning, see: [AAMC Artificial Intelligence in Medicine Case Studies](https://www.aamc.org/contact/ai-case-studies)*"
      ],
      "prompts": [
        "Write your reflections here (optional):"
      ]
    },
    {
      "title": "Algorithmic Triage Case Study",
      "body": [
        "Analyze fairness risks in a trauma-center triage algorithm.",
        "Read the case and write possible bias vectors, deployment considerations, and negative patient-care outcomes."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/2.3_clinical.py"
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
          <h1>2.3 · Bias, Fairness, and Societal Impact of Biomedical AI</h1>
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
