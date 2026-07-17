"""Generate standalone marimo lessons from the consolidated Streamlit sources.

The dev branch consolidated the basic and clinical tracks into one lesson file
per lesson.  This script extracts the instructional copy and written-response
prompts from those files and emits reactive, WASM-safe marimo applications.

Run from the repository root:

    python scripts/build_marimo_lessons.py
"""

from __future__ import annotations

import ast
import html
import json
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "notebooks" / "clinical"
CONTEXT_DIR = ROOT / "assets" / "notebook_context"
OUTPUT_DIR = ROOT / "marimo_notebooks" / "lessons"

MODULE_NAMES = {
    "1": "Fundamentals",
    "2": "Alignment",
    "3": "Data",
    "4": "Machine Learning",
    "5": "Images",
    "6": "Generative AI",
    "7": "Impact Project",
}

DISPLAY_CALLS = {
    "caption",
    "error",
    "info",
    "markdown",
    "success",
    "text",
    "warning",
    "write",
}
SECTION_CALLS = {"header", "subheader", "title"}
RESPONSE_CALLS = {"text_area", "text_input"}


def constant_text(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return textwrap.dedent(node.value).strip()
    return None


def streamlit_call(node: ast.Call) -> str | None:
    function = node.func
    if (
        isinstance(function, ast.Attribute)
        and isinstance(function.value, ast.Name)
        and function.value.id == "st"
    ):
        return function.attr
    return None


class LessonExtractor(ast.NodeVisitor):
    """Collect user-facing content in source order."""

    def __init__(self) -> None:
        self.title: str | None = None
        self.sections: list[dict[str, object]] = [
            {"title": "Overview", "body": [], "prompts": []}
        ]

    @property
    def section(self) -> dict[str, object]:
        return self.sections[-1]

    def visit_Call(self, node: ast.Call) -> None:
        name = streamlit_call(node)
        first = constant_text(node.args[0]) if node.args else None

        if name == "title" and first and self.title is None:
            self.title = first
        elif name in SECTION_CALLS and first:
            if first != self.title:
                self.sections.append({"title": first, "body": [], "prompts": []})
        elif name in DISPLAY_CALLS and first and not should_skip_text(first):
            body = self.section["body"]
            assert isinstance(body, list)
            if not body or body[-1] != first:
                body.append(first)
        elif name in RESPONSE_CALLS and first:
            prompts = self.section["prompts"]
            assert isinstance(prompts, list)
            if first not in prompts:
                prompts.append(first)

        self.generic_visit(node)


def should_skip_text(value: str) -> bool:
    stripped = value.strip()
    return (
        not stripped
        or "<style" in stripped.lower()
        or stripped in {"---", "***"}
        or stripped.startswith("<script")
    )


def load_context(lesson_id: str) -> dict[str, object]:
    path = CONTEXT_DIR / f"{lesson_id}_clinical.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_sections(
    sections: list[dict[str, object]], objectives: list[str]
) -> list[dict[str, object]]:
    cleaned: list[dict[str, object]] = []
    for section in sections:
        body = [
            clean_markdown(item)
            for item in section["body"]
            if isinstance(item, str) and clean_markdown(item)
        ]
        prompts = [
            clean_inline(item)
            for item in section["prompts"]
            if isinstance(item, str) and clean_inline(item)
        ]
        if body or prompts:
            cleaned.append(
                {
                    "title": clean_inline(str(section["title"])),
                    "body": body,
                    "prompts": prompts,
                }
            )

    if not cleaned:
        cleaned.append(
            {
                "title": "Lesson workspace",
                "body": objectives
                or ["Use this workspace to record notes and reflect on the lesson."],
                "prompts": [],
            }
        )
    return cleaned


def clean_inline(value: str) -> str:
    value = re.sub(r":material/[a-z_]+:", "", value)
    value = re.sub(r"\s+", " ", value)
    return html.unescape(value).strip()


def clean_markdown(value: str) -> str:
    value = value.replace(":material/", "")
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return html.unescape(textwrap.dedent(value).strip())


def extract_lesson(source_path: Path) -> dict[str, object]:
    lesson_id = source_path.name.removesuffix("_clinical.py")
    module = lesson_id.split(".", maxsplit=1)[0]
    context = load_context(lesson_id)
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    extractor = LessonExtractor()
    extractor.visit(tree)

    objectives = context.get("objectives", context.get("learning_objectives", []))
    if not isinstance(objectives, list):
        objectives = []
    objectives = [clean_inline(str(item)) for item in objectives]
    sections = normalize_sections(extractor.sections, objectives)
    enrich_sections_from_context(sections, context.get("sections", []))

    return {
        "id": lesson_id,
        "module": module,
        "module_name": MODULE_NAMES[module],
        "title": clean_inline(
            str(context.get("title") or extractor.title or f"Lesson {lesson_id}")
        ),
        "objectives": objectives,
        "sections": sections,
        "source": f"notebooks/clinical/{source_path.name}",
    }


def enrich_sections_from_context(
    sections: list[dict[str, object]], context_sections: object
) -> None:
    if not isinstance(context_sections, list):
        return

    for item in context_sections:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        name = clean_inline(str(item["name"]))
        guidance = [
            clean_markdown(str(item[key]))
            for key in ("purpose", "how_to_use")
            if item.get(key)
        ]
        if not guidance:
            continue

        matching = next(
            (
                section
                for section in sections
                if name.lower() in str(section["title"]).lower()
                or str(section["title"]).lower() in name.lower()
            ),
            None,
        )
        if matching is None:
            sections.append({"title": name, "body": guidance, "prompts": []})
        else:
            body = matching["body"]
            assert isinstance(body, list)
            body[:0] = [text for text in guidance if text not in body]


def notebook_source(lesson: dict[str, object]) -> str:
    lesson_json = json.dumps(lesson, ensure_ascii=False, indent=2)
    return f'''# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="{lesson["id"]} · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{lesson_json}""")
    return (lesson,)


@app.cell
def _(lesson, mo):
    mo.Html(
        """
        <style>
          :root {{
            --gator-blue: #0021a5;
            --uf-orange: #fa4616;
            --ink: #17223b;
            --mist: #f4f7fb;
          }}
          .aip-hero {{
            border-left: 7px solid var(--uf-orange);
            border-radius: 14px;
            background: linear-gradient(135deg, #0021a5, #001a57);
            color: white;
            padding: 1.3rem 1.5rem;
            margin: .4rem 0 1.2rem;
          }}
          .aip-kicker {{
            color: #ffd8ca;
            font-size: .78rem;
            font-weight: 750;
            letter-spacing: .09em;
            text-transform: uppercase;
          }}
          .aip-hero h1 {{ color: white; margin: .22rem 0 .35rem; }}
          .aip-hero p {{ margin: 0; opacity: .88; }}
          .aip-card {{
            border: 1px solid #d9e2ef;
            border-radius: 12px;
            background: white;
            padding: 1rem 1.15rem;
          }}
          .aip-source {{ color: #5f6b7c; font-size: .8rem; }}
        </style>
        <div class="aip-hero">
          <div class="aip-kicker">AI Passport · Module {lesson["module"]}: {lesson["module_name"]}</div>
          <h1>{lesson["id"]} · {lesson["title"]}</h1>
          <p>Interactive marimo lesson · browser-safe app mode</p>
        </div>
        """
    )
    return


@app.cell
def _(lesson, mo):
    section_options = {{
        section["title"]: index
        for index, section in enumerate(lesson["sections"])
    }}
    section_picker = mo.ui.dropdown(
        options=section_options,
        value=lesson["sections"][0]["title"],
        label="Lesson section",
        full_width=True,
    )
    objective_text = (
        "\\n".join(f"- {{objective}}" for objective in lesson["objectives"])
        if lesson["objectives"]
        else "Use the activities to connect the lesson concepts to biomedical AI practice."
    )
    mo.vstack(
        [
            mo.accordion({{"Learning objectives": mo.md(objective_text)}}),
            section_picker,
        ],
        gap=1,
    )
    return (section_picker,)


@app.cell
def _(lesson, mo, section_picker):
    section = lesson["sections"][section_picker.value]
    section_body = "\\n\\n".join(section["body"])
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
            mo.md(f"## {{section['title']}}"),
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
        f"# {{lesson['id']}} · {{lesson['title']}}",
        "",
        f"## {{section['title']}}",
        "",
    ]
    for prompt, answer in zip(prompts, answers):
        export_lines.extend([f"### {{prompt}}", "", answer or "_No response yet._", ""])
    export_markdown = "\\n".join(export_lines)
    mo.hstack(
        [
            mo.md(f"**Progress:** {{completed}} / {{len(prompts)}} responses"),
            mo.download(
                data=export_markdown,
                filename=f"ai-passport-{{lesson['id']}}-responses.md",
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
        f'<p class="aip-source">Ported from <code>{{lesson["source"]}}</code> '
        f'on the consolidated <code>dev</code> branch.</p>'
    )
    return


if __name__ == "__main__":
    app.run()
'''


def dashboard_source(lessons: list[dict[str, object]]) -> str:
    catalog_json = json.dumps(lessons, ensure_ascii=False, indent=2)
    return f'''# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="full", app_title="AI Passport · marimo")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    catalog = json.loads(r"""{catalog_json}""")
    module_names = {{
        "1": "Fundamentals",
        "2": "Alignment",
        "3": "Data",
        "4": "Machine Learning",
        "5": "Images",
        "6": "Generative AI",
        "7": "Impact Project",
    }}
    return catalog, module_names


@app.cell
def _(mo):
    mo.Html(
        """
        <style>
          :root {{
            --gator-blue: #0021a5;
            --uf-orange: #fa4616;
            --dark-blue: #001a57;
            --mist: #f4f7fb;
          }}
          body {{ background: #f7f9fc; }}
          .passport-banner {{
            background:
              radial-gradient(circle at 90% 20%, rgba(250,70,22,.32), transparent 26%),
              linear-gradient(125deg, #001a57, #0021a5 72%);
            border-radius: 18px;
            color: white;
            padding: 1.5rem 1.8rem;
            box-shadow: 0 14px 38px rgba(0,33,165,.17);
          }}
          .passport-banner h1 {{ color: white; margin: .2rem 0 .35rem; }}
          .passport-banner p {{ margin: 0; opacity: .88; }}
          .passport-kicker {{
            color: #ffd5c8;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
          }}
          .lesson-card {{
            background: white;
            border: 1px solid #dbe3ef;
            border-top: 5px solid var(--uf-orange);
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
          }}
          .lesson-card h2 {{ margin-top: .15rem; }}
          .source-note {{ color: #647084; font-size: .8rem; }}
        </style>
        <div class="passport-banner">
          <div class="passport-kicker">University of Florida · AI Passport</div>
          <h1>Biomedical AI learning lab</h1>
          <p>{len(lessons)} consolidated lessons, ported to reactive marimo apps.</p>
        </div>
        """
    )
    return


@app.cell
def _(module_names, mo):
    module_picker = mo.ui.dropdown(
        options={{f"Module {{key}} · {{value}}": key for key, value in module_names.items()}},
        value="Module 1 · Fundamentals",
        label="Module",
        full_width=True,
    )
    module_picker
    return (module_picker,)


@app.cell
def _(catalog, mo, module_picker):
    module_lessons = [
        lesson for lesson in catalog if lesson["module"] == module_picker.value
    ]
    lesson_options = {{
        f"{{lesson['id']}} · {{lesson['title']}}": index
        for index, lesson in enumerate(module_lessons)
    }}
    lesson_picker = mo.ui.dropdown(
        options=lesson_options,
        value=next(iter(lesson_options)),
        label="Lesson",
        full_width=True,
    )
    lesson_picker
    return lesson_picker, module_lessons


@app.cell
def _(lesson_picker, mo, module_lessons):
    active_lesson = module_lessons[lesson_picker.value]
    section_options = {{
        section["title"]: index
        for index, section in enumerate(active_lesson["sections"])
    }}
    section_picker = mo.ui.dropdown(
        options=section_options,
        value=active_lesson["sections"][0]["title"],
        label="Section",
        full_width=True,
    )
    objective_text = (
        "\\n".join(f"- {{item}}" for item in active_lesson["objectives"])
        if active_lesson["objectives"]
        else "Use the activities to connect the lesson concepts to biomedical AI practice."
    )
    mo.vstack(
        [
            mo.Html(
                f"""
                <div class="lesson-card">
                  <div class="passport-kicker" style="color:#c93b10">
                    Module {{active_lesson["module"]}} · {{active_lesson["module_name"]}}
                  </div>
                  <h2>{{active_lesson["id"]}} · {{active_lesson["title"]}}</h2>
                  <div class="source-note">Source: {{active_lesson["source"]}}</div>
                </div>
                """
            ),
            mo.accordion({{"Learning objectives": mo.md(objective_text)}}),
            section_picker,
        ],
        gap=1,
    )
    return active_lesson, section_picker


@app.cell
def _(active_lesson, mo, section_picker):
    section = active_lesson["sections"][section_picker.value]
    section_body = "\\n\\n".join(section["body"])
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
            mo.md(f"## {{section['title']}}"),
            mo.md(section_body) if section_body else mo.md(
                "Work through the prompts below and record your reasoning."
            ),
            response_widgets,
        ],
        gap=1,
    )
    return prompts, response_widgets, section


@app.cell
def _(active_lesson, mo, prompts, response_widgets, section):
    answers = response_widgets.value
    completed = sum(bool(answer.strip()) for answer in answers)
    lines = [
        f"# {{active_lesson['id']}} · {{active_lesson['title']}}",
        "",
        f"## {{section['title']}}",
        "",
    ]
    for prompt, answer in zip(prompts, answers):
        lines.extend([f"### {{prompt}}", "", answer or "_No response yet._", ""])
    mo.hstack(
        [
            mo.md(f"**Progress:** {{completed}} / {{len(prompts)}} responses"),
            mo.download(
                data="\\n".join(lines),
                filename=f"ai-passport-{{active_lesson['id']}}-responses.md",
                label="Download responses",
            ),
        ],
        justify="space-between",
        align="center",
        widths=[2, 1],
    )
    return


if __name__ == "__main__":
    app.run()
'''


def main() -> None:
    source_paths = sorted(
        (
            path
            for path in SOURCE_DIR.glob("[1-7].[1-7]_clinical.py")
            if "converted_from_ipynb" not in path.name
        ),
        key=lambda path: tuple(
            int(part) for part in path.name.split("_", maxsplit=1)[0].split(".")
        ),
    )
    lessons = [extract_lesson(path) for path in source_paths]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for lesson in lessons:
        output = OUTPUT_DIR / f"{lesson['id']}.py"
        output.write_text(notebook_source(lesson), encoding="utf-8")

    dashboard = ROOT / "marimo_notebooks" / "ai_passport.py"
    dashboard.write_text(dashboard_source(lessons), encoding="utf-8")

    manifest = ROOT / "marimo_notebooks" / "lessons.json"
    manifest.write_text(
        json.dumps(lessons, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(lessons)} lessons in {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
