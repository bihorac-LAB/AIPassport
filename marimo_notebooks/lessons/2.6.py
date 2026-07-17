# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="2.6 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "2.6",
  "module": "2",
  "module_name": "Alignment",
  "title": "Human-AI Collaboration in Biomedicine",
  "objectives": [
    "Identify human-AI collaboration tools currently used in clinical practice.",
    "Evaluate benefits, drawbacks, governance, and data-management practices for those tools.",
    "Analyze possible hospital responses to AI transcription errors in patient-care settings.",
    "Practice balancing documentation efficiency against patient safety, fairness, trust, and privacy risks."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "### Question 1",
        "Identify and list all the human-AI collaboration tools currently at use in your clinical \npractice. How do you or your colleagues use these tools. What are their benefits and drawbacks? \nExplain how you manage these systems, and the data created from them.",
        "### Question 2",
        "Consider the following case:\n\nA large hospital has implemented the use of an AI transcription system for hospital staff to use \nin care settings. The idea is that the AI tool will allow more accurate notes to be input into \npatient records. After testing the tool in various care settings for about a month, hospital \nstaff began reviewing the transcripts and notes from the tool. To their dismay, they found that \nalthough the tool transcribed patient interviews, it also:\n- Made up segments of conversations that did not happen.\n- Made certain patients appear to be being aggressive with staff, when this behavior was not present; and \n- Was not as accurate in conversations with patients with accents, from the around the US or otherwise.\n\n**What are the possible routes the hospital could take after reviewing the transcription data? \nWhat should the hospital do?  Explain your answer.**"
      ],
      "prompts": [
        "Your response to Question 1",
        "Your response to Question 2"
      ]
    },
    {
      "title": "Question 1",
      "body": [
        "Inventory current human-AI collaboration tools in clinical work.",
        "List tools used in clinical practice, explain how they are used, note benefits and drawbacks, and describe how outputs/data are managed."
      ],
      "prompts": []
    },
    {
      "title": "Question 2",
      "body": [
        "Analyze a flawed AI transcription system in hospital care.",
        "Consider hallucinated content, inaccurate tone, accent-related errors, documentation risk, patient safety, and what the hospital should do next."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/2.6_clinical.py"
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
          <h1>2.6 · Human-AI Collaboration in Biomedicine</h1>
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
