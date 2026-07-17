# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="4.1 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "4.1",
  "module": "4",
  "module_name": "Machine Learning",
  "title": "Shared Biomedical AI Vocabulary",
  "objectives": [],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "### Navigation",
        "Error: Could not find bundled diabetes dataset at assets/datasets/csv/diabetes.csv."
      ],
      "prompts": []
    },
    {
      "title": "Activity 1: Exploring Data Types",
      "body": [
        "### Instructions",
        "Before training a model, data scientists must inspect the raw data to understand feature distributions and identify correlations with the outcome variable. Use the controls below to preview the dataset and inspect the data types."
      ],
      "prompts": []
    },
    {
      "title": "Data Preview",
      "body": [
        "These are the variable types the computer recognizes for each column:"
      ],
      "prompts": []
    },
    {
      "title": "Feature Distributions",
      "body": [
        "By inspecting the dataset, you should notice there are 8 input features (predictors) containing numerical data (integers and floats), and 1 binary outcome variable containing integers (0 or 1)."
      ],
      "prompts": []
    },
    {
      "title": "Activity 2: Data Preprocessing and Splitting",
      "body": [
        "### Instructions",
        "Before a model can learn, the data must be partitioned into a Training Set and a Testing Set. Use the slider below to adjust the ratio of this split and observe how the data is divided.",
        "When following the notebook's default setting of 0.2, you should expect 80% of the patient records to be used for training the model, and 20% to be held back for testing.",
        "This separation is critical. If we evaluated the model on the exact same data it was trained on, it would likely memorize the answers (overfitting), resulting in falsely high performance metrics that would fail in real-world scenarios."
      ],
      "prompts": []
    },
    {
      "title": "Activity 3: Model Training and Interactive Prediction",
      "body": [
        "### Instructions",
        "With the data prepared, we can train the Decision Tree Classifier. Adjust the 'Max Depth' parameter to control how complex the model's rules can become. Then, explore the Decision Tree Visualization to trace the mathematical logic the model uses to make a prediction. Finally, test the model yourself using the live simulator."
      ],
      "prompts": []
    },
    {
      "title": "Decision Tree Visualization",
      "body": [
        "This graphic maps out the exact mathematical thresholds the algorithm uses to sort data and make decisions."
      ],
      "prompts": []
    },
    {
      "title": "Live Interactive Simulator",
      "body": [
        "Adjust the metrics below. The Decision Tree will process the inputs through the visual rules above and output a live prediction.",
        "Model Prediction: Outcome Detected (Class 1)",
        "Model Prediction: Outcome Not Detected (Class 0)",
        "Using the notebook's default Max Depth of 4, you should observe an accuracy of approximately 0.6948.",
        "Looking at the Decision Tree Visualization, you should expect to see the model heavily prioritizing features like Glucose and BMI near the top of the tree. These primary splits indicate the strongest predictors of the outcome variable within this dataset."
      ],
      "prompts": []
    },
    {
      "title": "Activity 4: Cross-Validation",
      "body": [
        "### Instructions",
        "A single Train/Test split can be sensitive to exactly how the data was randomly divided. Cross-validation provides a more robust evaluation by dividing the dataset into multiple 'folds'. The model is trained and tested on every fold. Adjust the number of folds below to see how the average metrics stabilize.",
        "Using the default 5 folds, you should expect the Average Accuracy to rise slightly to approximately 0.7305 compared to the single Train/Test split.",
        "You should also expect to see a higher Specificity (~0.7540) than Sensitivity (~0.6871). This reveals an important insight about the model: it is currently slightly better at correctly identifying stable patients (True Negatives) than it is at catching patients who experience failure/mortality (True Positives)."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/4.1_clinical.py"
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
          <div class="aip-kicker">AI Passport · Module 4: Machine Learning</div>
          <h1>4.1 · Shared Biomedical AI Vocabulary</h1>
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
