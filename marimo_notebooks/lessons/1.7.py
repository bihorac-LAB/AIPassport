# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.7 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.7",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Mentorship and Peer Review in Biomedical AI",
  "objectives": [
    "Identify communication, expectation, workload, and career-dynamic problems in clinical AI mentorship.",
    "Draft a professional message that balances urgency, respect, and independence.",
    "Reflect on mentorship challenges specific to clinical AI and clinical research teams."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**Objective:**  \nDevelop the skills to identify and effectively address challenges in mentoring relationships within clinical research/AI teams.\n\n---",
        "**Clinical Case:**  \nDr. Jordan, an early-career clinician-researcher, is being mentored by Dr. Martinez, a senior attending physician and clinical AI leader.  \nInitially, their mentorship meetings were productive—Dr. Martinez provided guidance on integrating AI-driven risk prediction models into clinical workflows for heart failure patients.  \nHowever, recently, Dr. Martinez has frequently rescheduled or shortened their meetings. Dr. Jordan feels increasingly unsupported, especially with a deadline approaching for a multicenter study protocol and IRB submission.\n\nDr. Martinez perceives Dr. Jordan as becoming overly dependent, waiting for advice instead of proactively troubleshooting workflow and data obstacles. Frustrations are mounting on both sides.\n\n---",
        "----"
      ],
      "prompts": []
    },
    {
      "title": "1. Identify the Challenges",
      "body": [
        "Separate communication breakdown, expectation mismatch, workload conflict, and career-stage dynamics.",
        "Write bullet points describing the clinical mentoring problems, then optionally compare with the example.",
        "List the problems in this clinical mentoring relationship.  \nConsider issues like communication, expectations, workload, and career dynamics.",
        "Example:\n\n- **Communication breakdown:** Dr. Martinez frequently reschedules/shortens meetings, but hasn't clearly communicated new availability or reasons, leaving Dr. Jordan uncertain.\n\n- **Expectation mismatch:** Dr. Jordan expects hands-on support for urgent tasks (protocol prep, IRB submission), while Dr. Martinez expects more independent troubleshooting with less direct oversight. These clashing assumptions fuel frustration.\n\n- **Workload management/conflict:** Both are busy clinicians/researchers; rescheduling meetings may signal overcommitment or competing priorities.\n\n- **Role/career imbalance:** Dr. Jordan may feel hesitant to push for help or clarity due to career stage; Dr. Martinez may underestimate the need for guidance at critical clinical research milestones.",
        "----"
      ],
      "prompts": [
        "Write your answer here (bullet points or text):"
      ]
    },
    {
      "title": "2. Draft a Professional Communication",
      "body": [
        "Practice respectful, concrete communication for busy clinical environments.",
        "Draft a message that requests a meeting, acknowledges clinical workload, and proposes structured check-ins or agendas.",
        "Imagine you are **Dr. Jordan**.  \nCompose a message requesting a meeting with Dr. Martinez to discuss and improve the situation:\n- Clearly and professionally explain the issues.\n- Show you recognize Dr. Martinez’s perspective.\n- Propose concrete, actionable changes to your working relationship, tailored for busy clinical environments.",
        "Dear Dr. Martinez,\n\nI hope this message finds you well. I’d like to request a meeting to discuss our current working relationship and some challenges I’ve been experiencing. Your insights on integrating AI into our heart failure protocols have been extremely valuable, and I am grateful for your mentorship.\n\nRecently, I’ve noticed our meetings have become less frequent and are sometimes cut short. I completely appreciate your clinical and research obligations, especially as new projects arise. However, with the upcoming multicenter protocol deadline and IRB submission, I’ve felt unsure at times how to proceed when obstacles arise.\n\nI also realize I could be more proactive in troubleshooting workflow bottlenecks before seeking your direct guidance. Would we be able to set a recurring check-in (even biweekly) and perhaps agree on short agendas to maximize our time? I’d like to become more independent but still benefit from your targeted advice during critical moments.\n\nThank you for considering this. I am eager to find a balance that supports both your schedule and my professional growth.\n\nBest regards,  \nDr. Jordan",
        "----"
      ],
      "prompts": [
        "Write your email/message here:"
      ]
    },
    {
      "title": "3. Reflection (Clinical AI Teams)",
      "body": [
        "Apply the scenario to clinical AI teams.",
        "Write what makes clinical AI mentorship hard and how these techniques could help in your own team.",
        "- What aspects make mentorship relationships in clinical AI particularly challenging?\n- How can you apply techniques from this activity in your own clinical or research team experience?",
        "Thank you! You have completed the clinical mentorship and peer review skills activity.",
        "---\n**Key Takeaways for Clinical Teams:**\n- Busy clinical schedules demand clear, structured, and respectful communication.\n- Explicitly revisiting expectations helps prevent conflicts in high-stakes, time-pressured AI/clinical projects.\n- Proactive troubleshooting empowers mentees, while “just-in-time” mentoring can make limited mentor time more effective.\n\n**For further reading:**  \n- [Effective mentoring in clinical research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4564451/)\n- [Nature - How to be a good mentee](https://www.nature.com/articles/d41586-020-02927-0)"
      ],
      "prompts": [
        "Write your reflection here (optional):"
      ]
    },
    {
      "title": "Clinical Case",
      "body": [
        "Introduce a strained mentorship relationship around workflow integration, protocol deadlines, and IRB submission.",
        "Read the case and notice both Dr. Jordan's support needs and Dr. Martinez's concern about independence."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/1.7_clinical.py"
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
          <h1>1.7 · Mentorship and Peer Review in Biomedical AI</h1>
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
