"""Generate standalone marimo lessons from the consolidated Streamlit sources.

The dev branch consolidated the basic and clinical tracks into one lesson file
per lesson.  This script extracts the instructional copy and written-response
prompts from those files and emits reactive, WASM-safe marimo applications.

Run from the repository root:

    python scripts/build_marimo_lessons.py
"""

from __future__ import annotations

import ast
import base64
import html
import json
import mimetypes
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

LESSON_MEDIA = {
    "5.1": [
        "assets/images/content/Identifying Structures in X-Ray Imaging.png",
        "assets/datasets/images/IM-0003-0001.jpeg",
    ],
    "5.2": [
        "assets/datasets/images/low_contrast2.jpg",
    ],
    "5.3": [
        "assets/datasets/images/BloodSmear.png",
    ],
    "5.5": [
        "assets/datasets/images/small_slide_noBC.png",
        "assets/datasets/images/small_slide_BC.png",
    ],
}


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
        "media": [
            {
                "path": relative_path,
                "data_uri": image_data_uri(ROOT / relative_path),
            }
            for relative_path in LESSON_MEDIA.get(lesson_id, [])
        ],
        "source": f"notebooks/clinical/{source_path.name}",
    }


def image_data_uri(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{payload}"


def interactive_cells(lesson_variable: str) -> str:
    """Return shared reactive lab cells for Modules 3–5."""

    source = r'''

@app.cell
def _(LESSON_VARIABLE, mo):
    lab_id = LESSON_VARIABLE["id"]
    if lab_id == "3.2":
        lab_controls = {
            "consent": mo.ui.slider(0, 100, value=65, label="Consent clarity"),
            "representation": mo.ui.slider(0, 100, value=55, label="Population representation"),
            "privacy": mo.ui.checkbox(value=True, label="Apply privacy-preserving controls"),
            "benefit": mo.ui.checkbox(value=False, label="Return useful findings to participants"),
        }
    elif lab_id == "3.3":
        lab_controls = {
            "raters": mo.ui.slider(2, 8, value=3, label="Number of radiologists"),
            "agreement": mo.ui.slider(50, 100, value=78, label="Pairwise agreement (%)"),
            "prevalence": mo.ui.slider(5, 60, value=28, label="Positive-case prevalence (%)"),
        }
    elif lab_id == "3.5":
        lab_controls = {
            "missing": mo.ui.slider(0, 40, value=12, label="Missing values (%)"),
            "outliers": mo.ui.slider(0, 25, value=8, label="Extreme measurements (%)"),
            "winsor": mo.ui.slider(80, 100, value=95, label="Winsorization percentile"),
            "imputer": mo.ui.dropdown(
                ["Median", "Mean", "Drop incomplete rows"],
                value="Median",
                label="Imputation strategy",
            ),
        }
    elif lab_id == "3.6":
        lab_controls = {
            "hospitals": mo.ui.slider(2, 6, value=3, label="Participating hospitals"),
            "samples": mo.ui.slider(50, 500, step=25, value=200, label="Patients per hospital"),
            "heterogeneity": mo.ui.slider(0, 100, value=35, label="Cross-site heterogeneity"),
            "rounds": mo.ui.slider(1, 15, value=5, label="Federated rounds"),
        }
    elif lab_id == "4.1":
        lab_controls = {
            "depth": mo.ui.slider(1, 10, value=4, label="Decision-tree depth"),
            "test_size": mo.ui.slider(10, 50, step=5, value=20, label="Test-set size (%)"),
            "glucose": mo.ui.slider(50, 200, value=125, label="Patient glucose"),
            "bmi": mo.ui.slider(15, 55, value=31, label="Patient BMI"),
        }
    elif lab_id in {"4.2", "4.3"}:
        lab_controls = {
            "layers": mo.ui.slider(1, 5, value=2, label="Hidden layers"),
            "neurons": mo.ui.slider(4, 64, step=4, value=24, label="Neurons per layer"),
            "epochs": mo.ui.slider(10, 100, step=10, value=40, label="Training epochs"),
            "learning_rate": mo.ui.dropdown(
                {"0.001 · cautious": 0.001, "0.01 · balanced": 0.01, "0.1 · aggressive": 0.1},
                value="0.01 · balanced",
                label="Learning rate",
            ),
        }
    elif lab_id == "4.4":
        lab_controls = {
            "modality": mo.ui.dropdown(
                ["Tabular EHR", "Medical images", "Clinical time series", "Clinical text"],
                value="Medical images",
                label="Biomedical data modality",
            ),
            "size": mo.ui.slider(100, 10000, step=100, value=2500, label="Training examples"),
            "interpretability": mo.ui.slider(0, 100, value=70, label="Interpretability priority"),
            "latency": mo.ui.slider(10, 1000, step=10, value=200, label="Latency budget (ms)"),
        }
    elif lab_id == "4.5":
        lab_controls = {
            "tp": mo.ui.slider(0, 100, value=62, label="True positives"),
            "fn": mo.ui.slider(0, 100, value=18, label="False negatives"),
            "tn": mo.ui.slider(0, 150, value=105, label="True negatives"),
            "fp": mo.ui.slider(0, 100, value=15, label="False positives"),
        }
    elif lab_id == "4.6":
        lab_controls = {
            "complexity": mo.ui.slider(1, 20, value=7, label="Model complexity"),
            "noise": mo.ui.slider(0, 50, value=15, label="Measurement noise (%)"),
            "samples": mo.ui.slider(100, 2000, step=100, value=700, label="Training examples"),
            "shift": mo.ui.slider(0, 50, value=10, label="External-site shift (%)"),
        }
    elif lab_id == "4.7":
        lab_controls = {
            "threshold": mo.ui.slider(10, 90, value=50, label="Decision threshold (%)"),
            "group_a": mo.ui.slider(30, 90, value=72, label="Group A signal quality"),
            "group_b": mo.ui.slider(30, 90, value=58, label="Group B signal quality"),
            "prevalence_gap": mo.ui.slider(0, 40, value=12, label="Prevalence gap (%)"),
        }
    elif lab_id == "5.1":
        lab_controls = {
            "brightness": mo.ui.slider(50, 160, value=100, label="X-ray brightness (%)"),
            "contrast": mo.ui.slider(50, 200, value=115, label="X-ray contrast (%)"),
            "zoom": mo.ui.slider(100, 220, value=120, label="Zoom (%)"),
            "invert": mo.ui.checkbox(value=False, label="Invert intensities"),
        }
    elif lab_id == "5.2":
        lab_controls = {
            "contrast": mo.ui.slider(50, 250, value=135, label="Contrast (%)"),
            "brightness": mo.ui.slider(50, 160, value=100, label="Brightness (%)"),
            "blur": mo.ui.slider(0, 8, value=0, label="Blur radius"),
            "grayscale": mo.ui.slider(0, 100, value=25, label="Grayscale (%)"),
        }
    elif lab_id == "5.3":
        lab_controls = {
            "threshold": mo.ui.slider(0, 255, value=130, label="Segmentation threshold"),
            "kernel": mo.ui.slider(1, 11, step=2, value=3, label="Morphology kernel"),
            "contrast": mo.ui.slider(50, 220, value=125, label="Texture contrast (%)"),
            "zoom": mo.ui.slider(100, 220, value=120, label="Zoom (%)"),
        }
    elif lab_id == "5.4":
        lab_controls = {
            "task": mo.ui.dropdown(
                ["Screening", "Segmentation", "Triage", "Longitudinal monitoring"],
                value="Screening",
                label="Clinical task",
            ),
            "modality": mo.ui.dropdown(
                ["X-ray", "CT", "MRI", "Pathology"],
                value="X-ray",
                label="Imaging modality",
            ),
            "urgency": mo.ui.slider(0, 100, value=65, label="Clinical urgency"),
            "annotations": mo.ui.slider(100, 5000, step=100, value=1200, label="Annotated studies"),
        }
    elif lab_id == "5.5":
        lab_controls = {
            "opacity": mo.ui.slider(0, 100, value=50, label="Fusion opacity (%)"),
            "offset_x": mo.ui.slider(-30, 30, value=0, label="Horizontal alignment"),
            "offset_y": mo.ui.slider(-30, 30, value=0, label="Vertical alignment"),
            "blend": mo.ui.dropdown(
                ["Normal", "Multiply", "Screen", "Difference"],
                value="Normal",
                label="Blend mode",
            ),
        }
    elif lab_id == "5.6":
        lab_controls = {
            "reviewers": mo.ui.slider(1, 8, value=3, label="Independent reviewers"),
            "agreement": mo.ui.slider(40, 100, value=80, label="Reviewer agreement (%)"),
            "protocol": mo.ui.checkbox(value=True, label="Locked preprocessing protocol"),
            "blind": mo.ui.checkbox(value=False, label="Blinded image review"),
        }
    else:
        lab_controls = {}

    lab_panel = (
        mo.vstack(
            [
                mo.md("## 🧪 Interactive learning lab"),
                mo.md("Change the controls and watch the evidence update immediately."),
                mo.hstack(list(lab_controls.values()), widths="equal", wrap=True),
            ],
            gap=1,
        )
        if lab_controls
        else mo.md("")
    )
    lab_panel
    return lab_controls, lab_id


@app.cell
def _(LESSON_VARIABLE, lab_controls, lab_id, mo):
    values = {name: control.value for name, control in lab_controls.items()}

    def meter(label, value, color="#0021a5"):
        bounded = max(0, min(100, value))
        return (
            f'<div class="lab-meter"><span>{label}</span>'
            f'<div><i style="width:{bounded:.1f}%;background:{color}"></i></div>'
            f'<b>{value:.1f}</b></div>'
        )

    lab_css = """
    <style>
      .lab-result {border:1px solid #d7e0ee;border-radius:14px;padding:1.1rem;
        background:linear-gradient(145deg,#fff,#f6f8fc);margin:.4rem 0 1rem}
      .lab-result h3 {margin:.1rem 0 .8rem;color:#001a57}
      .lab-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.7rem}
      .lab-stat {background:white;border:1px solid #e0e6ef;border-radius:10px;padding:.75rem}
      .lab-stat b {display:block;font-size:1.35rem;color:#0021a5}
      .lab-meter {display:grid;grid-template-columns:145px 1fr 48px;gap:.6rem;align-items:center;margin:.55rem 0}
      .lab-meter div {height:12px;background:#e6ebf3;border-radius:9px;overflow:hidden}
      .lab-meter i {display:block;height:100%;border-radius:9px}
      .lab-image {position:relative;overflow:hidden;min-height:310px;background:#101522;border-radius:12px;
        display:flex;align-items:center;justify-content:center}
      .lab-image img {max-width:100%;max-height:430px;object-fit:contain}
      .matrix {display:grid;grid-template-columns:repeat(2,1fr);gap:.45rem;max-width:440px}
      .matrix div {padding:1rem;border-radius:9px;text-align:center;color:white;font-weight:700}
      .network {display:flex;align-items:center;justify-content:center;gap:25px;min-height:210px}
      .network-layer {display:flex;flex-direction:column;gap:7px}
      .neuron {width:18px;height:18px;border-radius:50%;background:#0021a5;border:3px solid #9db4ff}
      @media(max-width:700px){.lab-meter{grid-template-columns:110px 1fr 42px}}
    </style>
    """
    output_html = ""

    if lab_id == "3.2":
        score = (
            values["consent"] * .3 + values["representation"] * .3
            + (100 if values["privacy"] else 20) * .2
            + (100 if values["benefit"] else 25) * .2
        )
        verdict = "Strong ethical footing" if score >= 75 else "Revise before acquisition"
        output_html = f"""<div class="lab-result"><h3>Ethical acquisition audit</h3>
        {meter("Autonomy", values["consent"], "#fa4616")}
        {meter("Justice", values["representation"])}
        {meter("Privacy", 100 if values["privacy"] else 20)}
        {meter("Beneficence", 100 if values["benefit"] else 25, "#6a3fc5")}
        <p><b>{score:.0f}/100 · {verdict}</b></p></div>"""
    elif lab_id == "3.3":
        icc = min(.98, (values["agreement"] / 100) ** 2 + .035 * (values["raters"] - 2))
        ai_accuracy = min(.97, .58 + .055 * values["raters"] + .18 * icc)
        dots = "".join('<span class="neuron"></span>' for _ in range(values["raters"]))
        output_html = f"""<div class="lab-result"><h3>Radiology reliability experiment</h3>
        <div class="network"><div class="network-layer">{dots}</div><b>→ consensus → AI labels</b></div>
        {meter("Inter-rater reliability", icc * 100)}
        {meter("Estimated AI accuracy", ai_accuracy * 100, "#fa4616")}
        <p>More readers help only when their annotations are genuinely consistent. Prevalence:
        <b>{values["prevalence"]}%</b>.</p></div>"""
    elif lab_id == "3.5":
        retained = 100 - (values["missing"] if values["imputer"] == "Drop incomplete rows" else values["missing"] * .08)
        distortion = values["outliers"] * (1 - values["winsor"] / 110)
        bars = "".join(
            f'<rect x="{i*28+12}" y="{145-h}" width="20" height="{h}" rx="3" fill="#0021a5"/>'
            for i, h in enumerate([22, 48, 86, 120, 105, 72, 38, max(12, 85-int(distortion*3))])
        )
        output_html = f"""<div class="lab-result"><h3>Preprocessing pipeline</h3>
        <svg viewBox="0 0 250 165" width="100%" height="190" aria-label="Feature distribution">{bars}</svg>
        {meter("Records retained", retained)}
        {meter("Outlier distortion", distortion * 4, "#fa4616")}
        <p><b>{values["imputer"]}</b> imputation · cap above the {values["winsor"]}th percentile.</p></div>"""
    elif lab_id == "3.6":
        auc = min(.94, .58 + .025 * values["rounds"] + .00008 * values["samples"] * values["hospitals"] - .0013 * values["heterogeneity"])
        privacy = 100
        output_html = f"""<div class="lab-result"><h3>Federated learning round</h3>
        <div class="lab-grid"><div class="lab-stat"><b>{values["hospitals"]}</b>sites</div>
        <div class="lab-stat"><b>{values["samples"] * values["hospitals"]:,}</b>patients represented</div>
        <div class="lab-stat"><b>{values["rounds"]}</b>aggregation rounds</div></div>
        {meter("Global AUROC", auc * 100)}{meter("Records kept local", privacy, "#199473")}
        <p>Heterogeneity slows convergence; no patient-level records leave a hospital.</p></div>"""
    elif lab_id == "4.1":
        train_acc = min(.99, .62 + .043 * values["depth"])
        overfit = max(0, values["depth"] - 5) * .027 + values["test_size"] / 1200
        test_acc = max(.5, train_acc - overfit)
        risk = 1 / (1 + 2.71828 ** -((values["glucose"] - 115) / 22 + (values["bmi"] - 30) / 9))
        levels = "".join(
            f'<circle cx="{200 + (i-(2**d-1)/2)*220/(2**d)}" cy="{35+d*55}" r="10" fill="#0021a5"/>'
            for d in range(min(values["depth"], 4)) for i in range(2**d)
        )
        output_html = f"""<div class="lab-result"><h3>Decision tree playground</h3>
        <svg viewBox="0 0 400 230" width="100%" height="230">{levels}</svg>
        {meter("Training accuracy", train_acc*100)}{meter("Test accuracy", test_acc*100, "#fa4616")}
        {meter("Simulated patient risk", risk*100, "#9c2f2f")}
        <p>Depth {values["depth"]}: complexity raises fit, but deep trees widen the generalization gap.</p></div>"""
    elif lab_id in {"4.2", "4.3"}:
        lr = values["learning_rate"]
        capacity = values["layers"] * values["neurons"]
        quality = min(.96, .56 + .09 * values["layers"] + .0018 * values["neurons"] + .002 * values["epochs"] - (0.08 if lr == .1 else 0))
        layers = "".join(
            '<div class="network-layer">' + "".join('<span class="neuron"></span>' for _ in range(min(7, max(2, values["neurons"]//8)))) + '</div>'
            for _ in range(values["layers"])
        )
        points = " ".join(f"{x},{150-(25+quality*95*(1-2.71828**(-x/45))):.1f}" for x in range(0, 181, 15))
        output_html = f"""<div class="lab-result"><h3>Neural network architecture lab</h3>
        <div class="network"><div class="network-layer"><span class="neuron"></span><span class="neuron"></span></div>{layers}
        <div class="network-layer"><span class="neuron" style="background:#fa4616"></span></div></div>
        <svg viewBox="0 0 190 160" width="100%" height="170"><polyline points="{points}" fill="none" stroke="#fa4616" stroke-width="5"/></svg>
        {meter("Validation performance", quality*100)}
        <p><b>{capacity:,}</b> hidden activations · learning rate {lr:g}. Too much capacity can memorize small clinical datasets.</p></div>"""
    elif lab_id == "4.4":
        modality = values["modality"]
        recommendation = {
            "Tabular EHR": "Gradient-boosted trees",
            "Medical images": "Convolutional neural network",
            "Clinical time series": "Temporal CNN or transformer",
            "Clinical text": "Domain-adapted transformer",
        }[modality]
        if values["size"] < 800 or values["interpretability"] > 85:
            recommendation = "Interpretable baseline + feature engineering"
        readiness = min(100, values["size"]/55 + (100-values["interpretability"])*.25 + min(25, 4000/values["latency"]))
        output_html = f"""<div class="lab-result"><h3>Architecture decision studio</h3>
        <div class="lab-stat"><span>Recommended starting point</span><b>{recommendation}</b></div>
        {meter("Deployment readiness", readiness)}
        <p>For <b>{modality}</b>, validate the simple baseline first, then justify added complexity with external-site performance.</p></div>"""
    elif lab_id == "4.5":
        total = sum(values.values()) or 1
        sensitivity = values["tp"] / max(1, values["tp"] + values["fn"])
        specificity = values["tn"] / max(1, values["tn"] + values["fp"])
        precision = values["tp"] / max(1, values["tp"] + values["fp"])
        accuracy = (values["tp"] + values["tn"]) / total
        output_html = f"""<div class="lab-result"><h3>Clinical confusion matrix</h3>
        <div class="matrix"><div style="background:#167d5a">TP<br>{values["tp"]}</div>
        <div style="background:#b73d2d">FN<br>{values["fn"]}</div>
        <div style="background:#b76a2d">FP<br>{values["fp"]}</div>
        <div style="background:#315ca8">TN<br>{values["tn"]}</div></div>
        {meter("Sensitivity", sensitivity*100, "#167d5a")}{meter("Specificity", specificity*100)}
        {meter("Precision", precision*100, "#6a3fc5")}{meter("Accuracy", accuracy*100, "#fa4616")}
        <p>In safety-critical screening, false negatives often matter more than headline accuracy.</p></div>"""
    elif lab_id == "4.6":
        train_error = max(2, 38 - values["complexity"]*2 + values["noise"]*.15)
        variance = max(0, values["complexity"]-8)*2.2 * (600/values["samples"])
        external_error = min(80, train_error + variance + values["shift"]*.65)
        output_html = f"""<div class="lab-result"><h3>Generalization sandbox</h3>
        {meter("Training error", train_error, "#199473")}
        {meter("External-site error", external_error, "#fa4616")}
        {meter("Generalization gap", external_error-train_error, "#9c2f2f")}
        <p>{'Likely overfitting' if variance > 8 else 'Complexity is proportionate to the evidence'}.
        Add representative samples or regularize before deployment.</p></div>"""
    elif lab_id == "4.7":
        threshold = values["threshold"]
        tpr_a = max(5, min(98, values["group_a"] + (50-threshold)*.55))
        tpr_b = max(5, min(98, values["group_b"] + (50-threshold)*.55 - values["prevalence_gap"]*.15))
        fpr_a = max(2, min(80, 48-threshold*.45))
        fpr_b = max(2, min(80, fpr_a + values["prevalence_gap"]*.4))
        output_html = f"""<div class="lab-result"><h3>Fairness threshold sandbox</h3>
        {meter("Group A sensitivity", tpr_a)}{meter("Group B sensitivity", tpr_b, "#fa4616")}
        {meter("Sensitivity gap", abs(tpr_a-tpr_b), "#9c2f2f")}
        {meter("False-positive gap", abs(fpr_a-fpr_b), "#6a3fc5")}
        <p>Moving one shared threshold changes errors for both groups but may not close the equity gap.</p></div>"""
    elif lab_id in {"5.1", "5.2", "5.3"}:
        image = LESSON_VARIABLE["media"][0]["data_uri"]
        if lab_id == "5.1":
            filters = f'brightness({values["brightness"]}%) contrast({values["contrast"]}%) invert({1 if values["invert"] else 0})'
            transform = f'scale({values["zoom"]/100})'
            insight = "Windowing changes visibility—not the underlying anatomy."
        elif lab_id == "5.2":
            filters = f'brightness({values["brightness"]}%) contrast({values["contrast"]}%) blur({values["blur"]}px) grayscale({values["grayscale"]}%)'
            transform = "scale(1.05)"
            insight = "Enhancement can expose boundaries, while blur deliberately removes high-frequency detail."
        else:
            filters = f'grayscale(100%) contrast({values["contrast"]}%) brightness({70 + values["threshold"]/5}%)'
            transform = f'scale({values["zoom"]/100})'
            insight = f'A {values["kernel"]}×{values["kernel"]} kernel trades speckle removal against fine cellular detail.'
        output_html = f"""<div class="lab-result"><h3>Clinical image workbench</h3>
        <div class="lab-image"><img src="{image}" alt="Clinical teaching image"
        style="filter:{filters};transform:{transform}"></div><p>{insight}</p></div>"""
    elif lab_id == "5.4":
        model = {
            "X-ray": "DenseNet screening model",
            "CT": "3D U-Net or slice-based CNN",
            "MRI": "Multi-sequence segmentation network",
            "Pathology": "Patch classifier with slide aggregation",
        }[values["modality"]]
        readiness = min(100, values["annotations"]/40 + values["urgency"]*.25)
        output_html = f"""<div class="lab-result"><h3>Clinical computer-vision design studio</h3>
        <div class="lab-stat"><span>{values["task"]} · {values["modality"]}</span><b>{model}</b></div>
        {meter("Evidence readiness", readiness)}
        <p>Plan reader-study validation, failure-mode review, and workflow integration before prospective use.</p></div>"""
    elif lab_id == "5.5":
        first, second = (item["data_uri"] for item in LESSON_VARIABLE["media"])
        blend = values["blend"].lower()
        output_html = f"""<div class="lab-result"><h3>Multimodal fusion viewer</h3>
        <div class="lab-image"><img src="{first}" alt="Reference image" style="position:absolute">
        <img src="{second}" alt="Overlay image" style="position:absolute;opacity:{values["opacity"]/100};
        transform:translate({values["offset_x"]}px,{values["offset_y"]}px);mix-blend-mode:{blend}"></div>
        <p>Misregistration can manufacture apparent findings. Align structures before interpreting the fused view.</p></div>"""
    elif lab_id == "5.6":
        score = values["agreement"]*.55 + min(100, values["reviewers"]*15)*.2 + (100 if values["protocol"] else 30)*.15 + (100 if values["blind"] else 40)*.1
        output_html = f"""<div class="lab-result"><h3>Reproducibility checkpoint</h3>
        {meter("Consistency score", score)}
        {meter("Reviewer agreement", values["agreement"], "#fa4616")}
        <p><b>{values["reviewers"]}</b> reviewers · {'locked' if values["protocol"] else 'variable'} preprocessing ·
        {'blinded' if values["blind"] else 'unblinded'} review.</p></div>"""

    lab_result = mo.Html(lab_css + output_html) if output_html else mo.md("")
    lab_result
    return
'''
    return source.replace("LESSON_VARIABLE", lesson_variable)


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
    lab_cells = (
        interactive_cells("lesson")
        if lesson["module"] in {"3", "4", "5"}
        else ""
    )
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

{lab_cells}

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
    lab_cells = interactive_cells("active_lesson")
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

{lab_cells}

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
