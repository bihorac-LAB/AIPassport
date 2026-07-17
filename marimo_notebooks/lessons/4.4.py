# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="4.4 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "4.4",
  "module": "4",
  "module_name": "Machine Learning",
  "title": "Choosing the Right Biomedical Deep Learning Model",
  "objectives": [],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "Instructions: Please use this sidebar menu below to navigate through the different phases of Activity 4. Complete each section in order before answering the final question in your Canvas submission area."
      ],
      "prompts": []
    },
    {
      "title": "Phase 1: Data Preprocessing",
      "body": [
        "**Notebook Directives:**\n* Complete each activity in order. Record your responses only in your Canvas submission area.\n* Open the sidebar to select the next phase in the activity.\n* **Clinical Scenario:** You are part of a hospital's clinical analytics team using a CNN model to predict in-hospital mortality.\n* **Task:** Preprocess the data before running the model."
      ],
      "prompts": []
    },
    {
      "title": "StandardScaler Transformation",
      "body": [
        "In the notebook, the data is passed through `StandardScaler()` to center the mean at 0 and scale the standard deviation to 1. Toggle the scaler below to see why this is a necessary preprocessing step.",
        "Data Normalized: Notice how the massive numerical difference between 'Glucose' and 'DiabetesPedigreeFunction' has been eliminated. This prevents large numbers from artificially dominating the neural network's weights.",
        "Raw Data: Feeding this directly into a CNN causes the model to over-value 'Glucose' simply because the raw integer is larger than the others."
      ],
      "prompts": []
    },
    {
      "title": "The 1D Sliding Kernel",
      "body": [
        "After preprocessing and reshaping the input to a 1D vector, the Conv1D layer slides a kernel (size=3) across the features.",
        "Text Description: The dark blue boxes represent the 3 adjacent features currently being multiplied by the kernel's weights to extract a latent pattern. The light gray boxes are currently inactive.",
        "Dataset not found. Please ensure that 'diabetes.csv' is uploaded to a folder named 'data' inside your repository."
      ],
      "prompts": []
    },
    {
      "title": "Phase 2: Model Training Structure",
      "body": [
        "**Notebook Directives:**\n* Complete each activity in order. Record your responses only in your Canvas submission area.\n* Open the sidebar to select the next phase in the activity.\n* **Notebook Interpretation:**\n  * There are 7 layers (1 input layer, 5 hidden layers, and 1 output layer) in the CNN model.\n  * The first and second hidden layers learn the latent factors from the data using 32 and 64 nodes.\n  * The Dropout layer randomly drops 30 percent of neurons during training, preventing overfitting."
      ],
      "prompts": []
    },
    {
      "title": "Interactive Mechanics: The Dropout Regularizer",
      "body": [
        "In the Dense layer, the notebook applies `Dropout(0.3)`. This randomly turns off 30 percent of the neurons during training so the model does not become overly reliant on any single feature pathway."
      ],
      "prompts": []
    },
    {
      "title": "Phase 3: Cross-Validation & Results",
      "body": [
        "**Notebook Directives:**\n* Complete each activity in order. Record your responses only in your Canvas submission area.\n* Open the sidebar to select the next phase in the activity.\n* **5-fold cross validation:** Split the data into 5 unoverlapped datasets. Instead of training on one dataset once, train and test the model five times, each time using a different part of the data as the test set.\n* **Question:** How is the performance? Is it better than the DNN that we used in Notebook 2? Why? (Record your response in Canvas)."
      ],
      "prompts": []
    },
    {
      "title": "Notebook Output Analysis",
      "body": [
        "These are the final averaged metrics across all 5 folds, exactly as printed at the end of Activity 4."
      ],
      "prompts": []
    },
    {
      "title": "Interactive Diagnosis: Evaluating Performance",
      "body": [
        "To answer the final notebook question, notice that the **Average Sensitivity is 0.598**. This means the model is missing approximately 40 percent of the positive cases.",
        "In the notebook, the prediction threshold is hardcoded to `0.5` (`y_pred_prob > 0.5`). Adjust the threshold slider below to simulate how performance shifts when prioritizing Sensitivity.",
        "Text Description: A bar chart displaying the trade-off between Sensitivity and Specificity based on the selected probability threshold."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/4.4_clinical.py"
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
          <h1>4.4 · Choosing the Right Biomedical Deep Learning Model</h1>
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
