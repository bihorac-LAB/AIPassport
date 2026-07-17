# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.3 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.3",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Designing Biomedical Artificial Intelligence Experiments",
  "objectives": [
    "Identify knowledge gaps in clinical AI readmission prediction.",
    "Turn clinical problems into SMART research questions.",
    "Plan data selection, preprocessing, splitting, modeling, and evaluation.",
    "Address concept drift, transparency, fairness, prospective readiness, ethics, and communication."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "You are a clinical informatics researcher at a large academic medical center. Your hospital has higher-than-expected 30-day readmission rates for CHF patients.\n\n**Your Task:**  \nDesign an AI experiment to predict readmission risk and support enhanced discharge planning.  \nFollow each part, provide your responses using the inputs below. No programming required."
      ],
      "prompts": []
    },
    {
      "title": "Resources: Datasets & Tools",
      "body": [
        "**Datasets:**  \n- [MIMIC-IV](https://physionet.org/content/mimiciv/2.2/)  \n- [UK Biobank Imaging Data](https://www.ukbiobank.ac.uk/enable-your-research/about-our-data/imaging-data)  \n\n**Tools:**  \n- [Google Colab](https://colab.research.google.com/)  \n- [TensorFlow](https://www.tensorflow.org/)"
      ],
      "prompts": []
    },
    {
      "title": "1.1 Review the Current Literature",
      "body": [
        "Identify at least **three knowledge gaps or limitations** in current AI-based readmission prediction approaches for CHF patients."
      ],
      "prompts": [
        "Knowledge Gap 1",
        "Knowledge Gap 2",
        "Knowledge Gap 3"
      ]
    },
    {
      "title": "1.2 Research Questions (SMART Criteria)",
      "body": [],
      "prompts": [
        "Primary Research Question",
        "Secondary Research Question 1",
        "Secondary Research Question 2"
      ]
    },
    {
      "title": "1.3 Relevance and Impact",
      "body": [],
      "prompts": [
        "How do your research questions address the identified gaps and improve patient care?"
      ]
    },
    {
      "title": "2.1 Data Selection Approach",
      "body": [],
      "prompts": [
        "Specify other data elements:",
        "Inclusion criteria",
        "Exclusion criteria",
        "How will you handle missing data?",
        "How will you address potential biases in the data?"
      ]
    },
    {
      "title": "2.2 Data Preprocessing Pipeline",
      "body": [],
      "prompts": [
        "Feature extraction from unstructured clinical notes",
        "How will you normalize laboratory values?",
        "Handling of temporal data (E.g., time series, hospital stays)",
        "Creation of clinically relevant derived variables"
      ]
    },
    {
      "title": "2.3 Data Splitting Strategy",
      "body": [
        "How will you split your data to account for the considerations below?"
      ],
      "prompts": [
        "Handling temporal shifts in clinical practice",
        "Specify other approach to class imbalance:",
        "How will you ensure patient demographic representation?",
        "How will you evaluate generalizability across different hospital units?"
      ]
    },
    {
      "title": "3.1 Modelling Approach",
      "body": [
        "Briefly describe three candidate AI/ML algorithms for readmission prediction:"
      ],
      "prompts": [
        "Algorithm 1",
        "Algorithm 2",
        "Algorithm 3",
        "Which algorithm did you choose and why?",
        "How does your approach address the limitations identified in Part 1?"
      ]
    },
    {
      "title": "3.2 Evaluation Framework",
      "body": [],
      "prompts": [
        "Specify additional metrics:",
        "Justify your choice of metrics",
        "Describe your cross-validation strategy",
        "How will you assess clinical relevance, not just statistical significance?"
      ]
    },
    {
      "title": "3.3 Addressing Challenges",
      "body": [
        "Prepare the model for clinical reality.",
        "Explain how to handle concept drift, transparency, fairness across populations, and prospective evaluation readiness."
      ],
      "prompts": [
        "How will you handle concept drift over time?",
        "How will you ensure the model is transparent for clinical interpretation?",
        "How will you assess fairness across patient populations?",
        "How will you determine if the model is ready for prospective evaluation?"
      ]
    },
    {
      "title": "4.2 Handling Incidental Findings",
      "body": [],
      "prompts": [
        "How would you handle and report incidental findings (e.g., unexpected medication associations)?"
      ]
    },
    {
      "title": "4.3 Limitations",
      "body": [],
      "prompts": [
        "Acknowledge limitations of your approach and discuss how they may affect interpretation or application."
      ]
    },
    {
      "title": "5.1 Iterative Design",
      "body": [],
      "prompts": [
        "How might results from your initial experiment inform future research directions?"
      ]
    },
    {
      "title": "5.2 Multidisciplinary Collaboration",
      "body": [],
      "prompts": [
        "How does your design incorporate multidisciplinary perspectives? Where would clinical input be essential?"
      ]
    },
    {
      "title": "5.3 Communicating Your Design",
      "body": [
        "Describe your strategy for communicating your experiment to each audience:",
        "You have completed all parts of the assignment! Please copy your responses to save or submit them as instructed by your course/instructor."
      ],
      "prompts": [
        "AI/ML Technical Peers",
        "Clinical Providers without AI expertise",
        "Institutional Review Boards/Ethics Committees"
      ]
    },
    {
      "title": "Your Answers Summary",
      "body": [
        "**Part 1: Knowledge Gaps & Research Questions**",
        "**Part 2: Data Management**",
        "**Part 3: Experimental Design**",
        "**Part 4: Ethics & Limitations**",
        "**Part 5: Reflection**",
        "Copy this output as your assignment review or for archiving."
      ],
      "prompts": []
    },
    {
      "title": "Knowledge Gaps and Research Questions",
      "body": [
        "Frame a clinically meaningful AI experiment.",
        "Write three gaps in current readmission prediction work, then define primary and secondary SMART research questions."
      ],
      "prompts": []
    },
    {
      "title": "Data Management Strategy",
      "body": [
        "Plan clinical data elements, preprocessing, temporal handling, and split strategy.",
        "Select MIMIC-IV data elements, specify inclusion and exclusion criteria, handle missing data, and plan bias mitigation."
      ],
      "prompts": []
    },
    {
      "title": "Experimental Design",
      "body": [
        "Choose models and metrics beyond accuracy.",
        "Describe candidate algorithms, pick a main model, justify metrics, and explain clinical relevance."
      ],
      "prompts": []
    },
    {
      "title": "Ethics and Reflection",
      "body": [
        "Connect experiment design to responsible clinical use.",
        "Address privacy, consent, security, fairness, clinical accountability, incidental findings, limitations, and communication."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/1.3_clinical.py"
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
          <h1>1.3 · Designing Biomedical Artificial Intelligence Experiments</h1>
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
