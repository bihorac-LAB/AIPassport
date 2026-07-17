# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="5.2 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "5.2",
  "module": "5",
  "module_name": "Images",
  "title": "Clinical Image Processing Suite",
  "objectives": [],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**Privacy Notice:**\n\nThis is an educational sandbox. Please **do not upload sensitive clinical data**, personally identifiable information (PII), or Protected Health Information (PHI)."
      ],
      "prompts": []
    },
    {
      "title": "Global Image Selection",
      "body": [
        "Please select or upload an image to begin."
      ],
      "prompts": []
    },
    {
      "title": "Image Processing & Augmentation",
      "body": [
        "**Instructions:** Adjust the sliders to scale pixel intensities (normalization) or apply spatial transformations (augmentation).",
        "**Normalization:** Lowering the factor will uniformly darken the image. In real model training, standardizing all images to a [0, 1] range ensures stable neural network gradients.\n\n**Augmentation:** Flipping and rotating the image changes its orientation without altering the underlying cellular features. This forces machine learning models to learn the actual shape of the cells rather than memorizing their position on the slide."
      ],
      "prompts": []
    },
    {
      "title": "Edge Detection with Filters",
      "body": [
        "**Instructions:** Apply spatial filters to extract structural features like cell walls.",
        "**Directional Edges:** The horizontal filter will highlight the top and bottom boundaries of the cells, while the vertical filter will highlight the left and right boundaries.\n\n**Magnitude & Sobel:** These combine the horizontal and vertical gradients into a single image, creating a bright, continuous outline around the cellular structures. This is a critical first step for automated cell counting or segmentation algorithms."
      ],
      "prompts": []
    },
    {
      "title": "Motion Blur Simulation",
      "body": [
        "**Instructions:** Use this tool to simulate imaging artifacts caused by camera shake or stage movement.",
        "You should expect the image to look 'smeared'. Increasing the **Blur Length** makes the smear stretch further, simulating a faster or longer physical movement during image capture. Changing the **Blur Angle** will alter the exact trajectory (e.g., diagonal, horizontal, or vertical) of that smear."
      ],
      "prompts": []
    },
    {
      "title": "Salt & Pepper Noise and Denoising",
      "body": [
        "**Instructions:** Introduce random sensor noise and attempt to clean it up using different filtering algorithms.",
        "**The Noise:** You will see random pure black and pure white pixels scattered across the image, common in faulty imaging sensors.\n\n**The Fix:** You should expect the **Median filter** to clean this up beautifully, as it replaces the extreme noise pixels with the middle value of their neighbors, keeping the cell edges sharp. Conversely, the **Gaussian filter** will likely just blur the noise into the surrounding pixels, making the image look muddy. This demonstrates why Median filters are strictly preferred for this specific artifact."
      ],
      "prompts": []
    }
  ],
  "source": "notebooks/clinical/5.2_clinical.py"
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
          <div class="aip-kicker">AI Passport · Module 5: Images</div>
          <h1>5.2 · Clinical Image Processing Suite</h1>
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
