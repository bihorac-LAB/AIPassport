# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="5.5 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "5.5",
  "module": "5",
  "module_name": "Images",
  "title": "Fusion Tools Integration",
  "objectives": [],
  "sections": [
    {
      "title": "Lesson workspace",
      "body": [
        "Use this workspace to record notes and reflect on the lesson."
      ],
      "prompts": []
    }
  ],
  "media": [
    {
      "path": "assets/datasets/images/small_slide_noBC.png",
      "data_uri": "data:image/png;base64,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"
    },
    {
      "path": "assets/datasets/images/small_slide_BC.png",
      "data_uri": "data:image/png;base64,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"
    }
  ],
  "source": "notebooks/clinical/5.5_clinical.py"
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
          <h1>5.5 · Fusion Tools Integration</h1>
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
def _(lesson, mo):
    lab_id = lesson["id"]
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

    lab_controls = (
        mo.ui.dictionary(lab_controls, label="Interactive controls")
        if lab_controls
        else None
    )
    lab_panel = (
        mo.vstack(
            [
                mo.md("## 🧪 Interactive learning lab"),
                mo.md("Change the controls and watch the evidence update immediately."),
                lab_controls.hstack(widths="equal", wrap=True),
            ],
            gap=1,
        )
        if lab_controls is not None
        else mo.md("")
    )
    lab_panel
    return lab_controls, lab_id


@app.cell
def _(lesson, lab_controls, lab_id, mo):
    values = lab_controls.value if lab_controls is not None else {}

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
        image = lesson["media"][0]["data_uri"]
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
        first, second = (item["data_uri"] for item in lesson["media"])
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
