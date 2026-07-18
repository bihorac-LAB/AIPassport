# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="1.6 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "1.6",
  "module": "1",
  "module_name": "Fundamentals",
  "title": "Basics of Scientific Rigor and Reproducibility",
  "objectives": [
    "Explore simulated hospital admission and outcome data for CHF readmission analysis.",
    "Visualize and detect outliers in age, length of stay, BNP, and sodium.",
    "Calculate 1.5x IQR thresholds and inspect flagged patient rows.",
    "Compare summary statistics before and after outlier exclusion.",
    "Evaluate remove, winsorize, and median-imputation strategies in clinical context."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "Introduce simulated CHF-related hospital data.",
        "Review each variable and remember that extreme clinical values may be valid, errors, or clinically important signals.",
        "**Dataset:** Simulated Hospital Admission/Outcome Dataset (mimicking eICU/EHR data)  \n**Tool:** [Jupyter notebook](https://jupyter.org/) (and this Streamlit app)\n\n---\n\nThis notebook will guide you through:\n- Exploring clinical data, visualizing and detecting outliers\n- Calculating outlier thresholds (with 1.5x IQR)\n- Identifying and handling outliers via different strategies\n- Comparing summary statistics and discussing scientific rigor\n\n---"
      ],
      "prompts": []
    },
    {
      "title": "1. Clinical Dataset Overview",
      "body": [
        "**Data context:**  \nA hospital wants to analyze characteristics and outcomes of patients with congestive heart failure (CHF) to investigate 30-day readmission.\n\n**Variables:**  \n- `age`: age of patient (years)  \n- `length_of_stay`: duration of hospitalization (days)  \n- `bnp`: admission B-type Natriuretic Peptide (BNP, pg/mL)  \n- `sodium`: admission Sodium (mmol/L)  \n- `readmit_30d`: 1=readmitted within 30 days, 0=no"
      ],
      "prompts": []
    },
    {
      "title": "2. Visualize Outliers with Boxplots",
      "body": [
        "Spot extreme clinical values visually.",
        "Select a variable, inspect the box plot, and note patient IDs and values that look unusual.",
        "Explore variable distributions and visually spot possible outliers.\n\n**Choose a variable to plot:**",
        "_What looks like a potential outlier in your chosen variable? Note their patient IDs and values below._"
      ],
      "prompts": [
        "Notes on possible outliers:"
      ]
    },
    {
      "title": "3. Calculate Outlier Thresholds (IQR Method)",
      "body": [
        "Apply the 1.5x IQR rule to clinical variables.",
        "Choose a variable and review Q1, Q3, IQR, bounds, and flagged patient rows.",
        "The standard 1.5x IQR rule defines outliers as any value >Q3 + 1.5×IQR or <Q1 - 1.5×IQR.\n\n**Choose a variable to see its IQR thresholds and outliers:**",
        "**Outlier Rows:**"
      ],
      "prompts": [
        "Patient IDs and values flagged as outliers (IQR rule):"
      ]
    },
    {
      "title": "4. Effect of Outliers on Clinical Summary Statistics",
      "body": [
        "**All Data:**",
        "**No Outliers:**"
      ],
      "prompts": [
        "How did mean, std, or median change? Why is this important in clinical data analysis?"
      ]
    },
    {
      "title": "5. Outlier Handling Approaches",
      "body": [
        "Compare removal, winsorization, and imputation.",
        "Choose a strategy and explain clinical risks if valid extreme values are mishandled.",
        "Explore three common clinical data strategies:  \n- Remove outliers  \n- Winsorize (set outliers to threshold)  \n- Impute with median  \n\n**Try one and see the summary statistics change!**"
      ],
      "prompts": [
        "Comment: Pros/cons of your chosen strategy, and specific clinical risks if outliers are mishandled:"
      ]
    },
    {
      "title": "6. Reflection: Scientific Rigor & Reproducibility in Clinical Settings",
      "body": [
        "Connect outlier handling to reproducible clinical research.",
        "Write what should be reported in methods and how poor handling could affect clinical conclusions.",
        "- Why is transparent description of outlier handling crucial in clinical research?  \n- What should always be reported in methods?\n- How could poor outlier handling impact clinical conclusions?",
        "---\n**Links:**  \n- [Jupyter notebook](https://jupyter.org/)  \n- [eICU Collaborative Research Database](https://eicu-crd.mit.edu/)"
      ],
      "prompts": [
        "Your reflection:"
      ]
    },
    {
      "title": "Effect on Clinical Summary Statistics",
      "body": [
        "Show how outliers influence clinical summaries.",
        "Compare mean, standard deviation, and median with all values versus no outliers."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/1.6_clinical.py"
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
          <h1>1.6 · Basics of Scientific Rigor and Reproducibility</h1>
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
