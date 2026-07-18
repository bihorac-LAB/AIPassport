# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="2.7 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "2.7",
  "module": "2",
  "module_name": "Alignment",
  "title": "Sex-Specific Modeling",
  "objectives": [
    "Prepare an eICU-style clinical dataset for sex-specific model analysis.",
    "Compare clinical variable patterns by sex and mortality status.",
    "Calculate univariate odds ratios for female, male, and full-cohort groups.",
    "Train multivariate models and compare AUROC across sex-specific cohorts."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "Clean the raw dataset, remove identifiers, and handle missing values.",
        "Visualize patient demographics and answer key conceptual questions.",
        "Calculate odds ratios for individual variables to see sex-specific risk factors.",
        "Train and evaluate models. Compare AUROC performance between sexes."
      ],
      "prompts": []
    },
    {
      "title": "Data Processing",
      "body": [
        "Clean identifiers, encode categories, impute missing values, and create a model-ready clinical dataset.",
        "### Removing Irrelevant Columns\nOne of the first logical steps is to remove the columns that contain no informational value. Some columns are unique random numeric identifiers (e.g., patient_id) with no discernible meaning. \n\nWe'll also remove weight_discharge and discharge_location because they will not be used as inputs.\n\n### Fast Preprocessing\nWe will save time with a heavy-handed approach:\n1. One-hot encode all categorical variables.\n2. Impute missing values in each numerical column with the mean."
      ],
      "prompts": []
    },
    {
      "title": "Raw Data Preview",
      "body": [
        "Preprocessing Complete!"
      ],
      "prompts": []
    },
    {
      "title": "Processed Data Preview",
      "body": [
        "First 10 rows after dropping identifiers, one-hot encoding categorical fields, and imputing missing numeric values."
      ],
      "prompts": []
    },
    {
      "title": "Brief Exploratory Analysis",
      "body": [
        "Filter patient data and inspect how selected clinical variables differ by sex and mortality status.",
        "Now, please take a moment to check the Data Explorer. Notice that, this isn’t about deep analysis, just getting a feel for the data at a glance. Keep it simple, you’re just getting familiar with the variable before modeling."
      ],
      "prompts": []
    },
    {
      "title": "Visualize the sex-specific patterns",
      "body": [
        "Before jumping into modeling, it is important to ask: \"Do males and females behave differently in this data?\" In many clinical datasets, combining all patients into a single analysis can blur important differences. Let’s split the lens and take a closer look."
      ],
      "prompts": []
    },
    {
      "title": "Question 1",
      "body": [
        "Why is it important to analyze clinical data separately for males and females before modeling?",
        "Correct! Clinical data often contains meaningful differences between males and females. When we analyze the entire dataset as a single group, these differences can get averaged out or hidden.",
        "Try again."
      ],
      "prompts": []
    },
    {
      "title": "Sex-specific Association Models",
      "body": [
        "We will now perform a univariate analysis using odds ratios separately for females and males. \n\nBy calculating odds ratios within each sex, we can uncover whether a variable (like elevated lactate) has differential predictive power for mortality in women versus men."
      ],
      "prompts": []
    },
    {
      "title": "Performance Evaluation by Sex",
      "body": [
        "Now we will evaluate how well our models perform not just overall, but within each sex. \nWe use the AUROC (Area Under the Receiver Operating Characteristic Curve) to measure discriminative ability.",
        "#### 1. Population Filter (Optional)",
        "#### 2. Model Features",
        "Select at least one predictor."
      ],
      "prompts": []
    },
    {
      "title": "Question 2",
      "body": [
        "When comparing the outcomes of these sex-specific models, what are we most interested in identifying?",
        "Correct! Our main goal is to see if the model performs differently across the two groups. Are predictions more accurate for one sex than the other? These performance differences can point to underlying biological, clinical, or systemic factors.",
        "Try again."
      ],
      "prompts": []
    },
    {
      "title": "Univariate Analysis",
      "body": [
        "Estimate one-variable odds ratios separately for female, male, and full-cohort data."
      ],
      "prompts": []
    },
    {
      "title": "Multivariate Analysis",
      "body": [
        "Train logistic models and compare model discrimination using AUROC."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/2.7_clinical.py"
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
          <h1>2.7 · Sex-Specific Modeling</h1>
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
