# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.1 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.1",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Demystifying Artificial Intelligence",
  "objectives": [
    "Understand AI as a human-built tool for solving specific problems.",
    "Connect major AI milestones to the growth of modern biomedical and clinical AI.",
    "Evaluate common AI claims as fact, fiction, misleading, or context-dependent."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "Artificial intelligence can often seem mysterious, complex, or even magical—but at its core, AI is a \n            tool built by humans to solve specific problems. This assignment is designed to help \n            demystify AI by grounding it in history and critical thinking. \n\nFirst, you’ll explore an **Interactive AI Timeline** that highlights major milestones in the \ndevelopment of AI, providing a sense of how the field has evolved over time. \n\nNext, you will test your assumptions and beliefs about AI with **AI: Fact or Fiction?**, an \ninteractive activity that provides immediate feedback to separate myth from the reality\n\nTogether, these activities aim to build your foundational understanding and make AI feel a little \nless like science fiction and a little more like science.",
        "**Artificial Intelligence (AI)** has evolved from a bold academic concept into a transformative\nforce reshaping science, medicine, industry, and everyday life. This interactive timeline \nexplores key milestones in the history of AI—from the theoretical groundwork laid by Alan Turing \nin the 1950s, to the explosive rise of generative models and multimodal agents in the 2020s.\n\nAs you scroll through the AI timeline, consider how each technological breakthrough not only \neflects the state of computing at the time but also contributes to a larger story of increasing \nintelligence, autonomy, and impact.",
        "## gavel: AI: Fact or Fiction?",
        "**Note:** The following activity uses generative AI to automatically provide feedback. Accuracy and appropriateness of responses is not guaranteed.",
        "Artificial Intelligence can often feel like a mysterious black box—surrounded by hype, myths, and \nsometimes even fear. While some statements about AI reflect real technical capabilities and \nlimitations, others are based on outdated ideas or science fiction. As AI continues to grow more \npowerful and visible in our lives, it becomes increasingly important to distinguish fact from \nfiction.\n\nThis interactive tool invites you to put your assumptions to the test. Enter any statement you’ve \nheard or believed about AI—whether technical or philosophical—and our built-in AI assistant will \nhelp you evaluate whether it’s accurate, misleading, or just plain wrong.",
        "AI feedback is unavailable because NAVIGATOR_TOOLKIT_API_KEY is not configured.",
        "Click the tabs below for more information about your statement."
      ],
      "prompts": [
        "Enter any statement about AI you'd like to evaluate."
      ]
    },
    {
      "title": "Interactive AI Timeline",
      "body": [
        "Give learners historical context for how AI capabilities developed over time.",
        "Scroll through the timeline milestones. Ask learners to notice what changed between symbolic AI, expert systems, machine learning, deep learning, and generative AI."
      ],
      "prompts": []
    },
    {
      "title": "AI: Fact or Fiction?",
      "body": [
        "Help learners test assumptions about AI using structured feedback.",
        "Enter a statement about AI, then review the verdict, explanation, real-world biomedical examples, limitations, datasets, AI concepts, and research directions."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/1.1_clinical.py"
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
          <h1>1.1 · Demystifying Artificial Intelligence</h1>
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
