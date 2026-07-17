# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.5 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.5",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Leveraging Multidisciplinary Team Strengths",
  "objectives": [
    "Identify essential roles for a real-time stroke triage AI project.",
    "Plan communication across clinical, technical, administrative, and patient-facing roles.",
    "Practice shared decision-making when accuracy and explainability trade off.",
    "Design training, collaboration tools, secure sharing, workflow integration, and ethics processes."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**Datasets**\n- [MIMIC-IV](https://physionet.org/content/mimiciv/2.2/): ICU/EHR data with patient encounters, ED visits, and outcomes.\n- [CheXpert](https://stanfordmlgroup.github.io/competitions/chexpert/): chest X-ray dataset with multi-label findings.\n\n**Collaboration tools**\n- [Microsoft Teams](https://www.microsoft.com/en-us/microsoft-teams/): chat, meetings, file sharing, channels.\n- [Trello](https://trello.com/): tasks, boards, assigned actions.",
        "Demo datasets shown are for assignment context only. Use linked resources for full data."
      ],
      "prompts": []
    },
    {
      "title": "Assignment Overview",
      "body": [
        "Welcome! In this assignment, you will explore strategies and best practices for **building, managing, and optimizing multidisciplinary teams** in clinical AI projects.\n\n**Clinical Focus:**\nYou are leading a project to develop an AI system that assists Emergency Department (ED) physicians in triaging suspected stroke patients.\n\n**You will:**  \n- Identify key team roles and responsibilities  \n- Develop team communication and problem-solving strategies  \n- Apply clinical and technical datasets (MIMIC-IV, CheXpert) as context for your planning  \n- Leverage modern collaboration tools  \n- Address workflow integration, training, and ethical challenges\n\n---  \n_Data previews for MIMIC-IV and CheXpert are available in the dataset expander above. Leverage these real-world datasets as you respond to planning and teamwork activities below._\n\n---"
      ],
      "prompts": []
    },
    {
      "title": "Part 1: Understanding the Multidisciplinary Landscape",
      "body": [
        "Define clinical AI team roles.",
        "List five roles, responsibilities, expertise, and project impact.",
        "**Case:**  \nYou're leading an AI project to develop a real-time stroke triage tool in the ED. Your resources include funding, stakeholder attention, and a 6-month timeline."
      ],
      "prompts": []
    },
    {
      "title": "Task 1.1: Essential Team Roles",
      "body": [
        "Identify at least **five essential roles** needed for this project. For each:\n* Key responsibilities\n* The expertise they bring\n* How their contribution will impact the project outcome"
      ],
      "prompts": []
    },
    {
      "title": "Task 1.2: Competing Priorities",
      "body": [],
      "prompts": [
        "Which roles might have competing priorities or different views on goals? Where might tension arise, and why?"
      ]
    },
    {
      "title": "Task 1.3: Organizational Structure",
      "body": [],
      "prompts": [
        "Describe (or sketch) an organizational structure for your team, with rationale."
      ]
    },
    {
      "title": "Part 2: Communication Strategies",
      "body": [
        "Plan communication for mixed clinical and technical expertise.",
        "Write a communication strategy, shared glossary, and patient/workflow focus plan.",
        "**Team:**  \nEmergency physician, neurologist, data scientist, software engineer, nurse informaticist, hospital administrator, patient advocate.\n\n**Challenge:**  \nDiverse expertise, technical and clinical knowledge varies."
      ],
      "prompts": []
    },
    {
      "title": "Task 2.1: Communication Strategy",
      "body": [
        "Plan for:",
        "- Meeting frequency, format, objectives\n- Documentation methods/standards\n- Knowledge sharing (tech & clinical)\n- Progress reporting to stakeholders"
      ],
      "prompts": [
        "Your Communication Strategy"
      ]
    },
    {
      "title": "Task 2.2: Shared Glossary",
      "body": [
        "**Term**",
        "**Definition (for clinicians & technologists)**"
      ],
      "prompts": []
    },
    {
      "title": "Task 2.3: Patient & Workflow Focus",
      "body": [],
      "prompts": [
        "Three strategies to ensure patient needs and clinical workflow stay central, even during technical discussions:"
      ]
    },
    {
      "title": "Part 3: Team-Based Decision-Making",
      "body": [
        "Evaluate accuracy versus explainability tradeoffs.",
        "Design a decision process, identify cognitive biases, and write a decision documentation template.",
        "Your team faces a choice:\n\n**Approach A:** Deep learning; higher accuracy (92%) but low explainability.  \n**Approach B:** More explainable; lower accuracy (88%) but can give reasons.\n\nTeam is divided."
      ],
      "prompts": []
    },
    {
      "title": "Task 3.1: Decision-Making Framework",
      "body": [
        "Design a process to fairly weigh both approaches, address all viewpoints, reach consensus, and document with rationale."
      ],
      "prompts": [
        "Decision-making framework"
      ]
    },
    {
      "title": "Task 3.2: Cognitive Biases",
      "body": [
        "Identify three biases that might affect the process and propose mitigations."
      ],
      "prompts": []
    },
    {
      "title": "Task 3.3: Decision Documentation Template",
      "body": [
        "Template should include all perspectives, rationale, decision, and contingencies."
      ],
      "prompts": [
        "Decision documentation template"
      ]
    },
    {
      "title": "Part 4: Training Opportunities",
      "body": [
        "Close knowledge gaps between clinical and technical members.",
        "Plan cross-training, shadowing, and external resources.",
        "Progress check:  \n- Clinical team struggles with model validation  \n- Technical team unsure about stroke protocols  \n- Divergent expectations for 'success'"
      ],
      "prompts": []
    },
    {
      "title": "Task 4.1: Cross-Training Plan",
      "body": [
        "- List specific topics for training\n- Who leads which part?\n- Format/duration\n- Effectiveness assessment"
      ],
      "prompts": [
        "Cross-training plan"
      ]
    },
    {
      "title": "Task 4.2: Shadowing Schedule",
      "body": [
        "Design a 'Day in the Life' schedule. What should each group focus on during observation?"
      ],
      "prompts": [
        "Shadowing schedule and focus points"
      ]
    },
    {
      "title": "Task 4.3: External Resources",
      "body": [
        "Identify three external resources (courses, workshops, key articles), and for each, what gap it will address."
      ],
      "prompts": []
    },
    {
      "title": "Part 5: Collaboration Tools",
      "body": [
        "Choose tools and secure sharing protocols.",
        "Pick tools, document their purpose and limitations, and define sharing protocols.",
        "Team is cross-departmental, some remote, some onsite, confidentiality critical."
      ],
      "prompts": []
    },
    {
      "title": "Task 5.1: Digital Tool Selection",
      "body": [
        "Pick three digital tools; for each, briefly justify:"
      ],
      "prompts": []
    },
    {
      "title": "Task 5.2: Secure Sharing Protocol",
      "body": [
        "- Sharing/document control for: docs, clinical data, code/specs, meeting notes"
      ],
      "prompts": [
        "Protocol for secure sharing"
      ]
    },
    {
      "title": "Task 5.3: Weekly Progress Dashboard",
      "body": [
        "Template should show milestones, challenges, deadlines, achievements"
      ],
      "prompts": [
        "Weekly dashboard template/design"
      ]
    },
    {
      "title": "Task 6.1: Integrating AI into Clinical Workflows",
      "body": [
        "What challenges might you encounter, and how can a multidisciplinary team reduce resistance to change?"
      ],
      "prompts": [
        "Integration reflection"
      ]
    },
    {
      "title": "Task 6.2: Team Effectiveness Metrics",
      "body": [
        "Suggest three ways to evaluate successful collaboration in your team."
      ],
      "prompts": []
    },
    {
      "title": "Task 6.3: Addressing Ethics",
      "body": [
        "Describe a process to identify, discuss, and resolve ethical issues as a multidisciplinary team.",
        "For more on the real-world data: [MIMIC-IV documentation](https://physionet.org/content/mimiciv/2.2/) | [CheXpert docs](https://stanfordmlgroup.github.io/competitions/chexpert/)."
      ],
      "prompts": [
        "Ethical issue resolution process"
      ]
    },
    {
      "title": "Introduction",
      "body": [
        "Frame the clinical AI teamwork scenario.",
        "Review the stroke triage case and optional sample data previews before choosing assignment sections."
      ],
      "prompts": []
    },
    {
      "title": "Reflection",
      "body": [
        "Connect teamwork to clinical workflow, adoption, effectiveness, and ethics.",
        "Reflect on integration challenges, success metrics, and ethical issue resolution."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/1.5_clinical.py"
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
          <h1>1.5 · Leveraging Multidisciplinary Team Strengths</h1>
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
