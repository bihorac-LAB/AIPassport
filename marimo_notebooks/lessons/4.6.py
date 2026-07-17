# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="4.6 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "4.6",
  "module": "4",
  "module_name": "Machine Learning",
  "title": "Model Generalizability Sandbox",
  "objectives": [],
  "sections": [
    {
      "title": "Learning Activities",
      "body": [
        "Use the menu below to navigate between the three different activities in this module."
      ],
      "prompts": []
    },
    {
      "title": "Activity 1: Overfitting vs. Underfitting",
      "body": [
        "1. Compare a 'Complex' model (Low k) to a 'Simple' model (High k) using the inputs below.\n2. Observe how the complex model attempts to draw boundaries around every single outlier, while the simple model draws a generalized regional boundary.\n3. Use the sidebar on the left to navigate to Activity 2 when you are ready."
      ],
      "prompts": []
    },
    {
      "title": "Visualizing Decision Boundaries (Top 2 Features)",
      "body": [
        "Colorblind-accessible contour plot displaying model decision boundaries. Yellow regions predict one class outcome, while dark blue regions predict the other. White-outlined dots represent individual patient or cell sample data points.",
        "Models with low k values create highly jagged decision boundaries, essentially memorizing the training data (overfitting). Models with high k values create smooth, broad boundaries, which may miss critical patterns (underfitting)."
      ],
      "prompts": []
    },
    {
      "title": "Activity 2: Hyperparameter Tuning",
      "body": [
        "1. Adjust the 'maximum k' slider to generate the Accuracy Curve.\n2. Observe where the Train and Test accuracy lines begin to separate. This divergence indicates the exact point where the model stops learning general rules and starts memorizing the training data.\n3. Use the sidebar on the left to navigate to Activity 3 when you are ready."
      ],
      "prompts": []
    },
    {
      "title": "Accuracy Curve",
      "body": [
        "Line graph comparing model accuracy on training data versus testing data across different values of k. The dark blue line represents training accuracy, and the yellow line represents testing accuracy.",
        "The optimal hyperparameter is found just before the training and testing curves diverge significantly. A large gap between high training accuracy and low testing accuracy is the mathematical signature of overfitting."
      ],
      "prompts": []
    },
    {
      "title": "Activity 3: Cross-Validation Strategies",
      "body": [
        "1. Adjust the 'Number of Folds' slider to see how stable the model performance is.\n2. Observe the variance in the boxplot. A wide box indicates the model is highly sensitive to how the data is split.\n3. Compare the mean accuracies and standard deviations of K-Fold, Stratified K-Fold, and LOO-CV.",
        "Boxplot displaying the spread of accuracy scores across multiple data folds. Wider boxes indicate greater instability in the model's performance."
      ],
      "prompts": []
    },
    {
      "title": "Comparing Validation Strategies",
      "body": [
        "Bar chart comparing the mean accuracy of K-Fold, Stratified K-Fold, and Leave-One-Out cross-validation. Error bars represent the standard deviation of scores.",
        "Stratified K-Fold is generally preferred for biomedical datasets as it ensures the ratio of positive to negative outcomes remains consistent across all test folds. LOO-CV provides an unbiased estimate but at a high computational cost and potentially high variance."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/4.6_clinical.py"
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
          <h1>4.6 · Model Generalizability Sandbox</h1>
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
