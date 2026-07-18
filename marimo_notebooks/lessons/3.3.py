# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.17.8",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium", app_title="3.3 · AI Passport")


@app.cell
def _():
    import json
    import marimo as mo
    return json, mo


@app.cell
def _(json):
    lesson = json.loads(r"""{
  "id": "3.3",
  "module": "3",
  "module_name": "Data",
  "title": "Radiology AI Reliability",
  "objectives": [
    "Simulate or upload radiologist annotation data.",
    "Measure inter-rater reliability with ICC.",
    "Identify high-disagreement images for review.",
    "Compare model accuracy as the number of radiologists changes."
  ],
  "sections": [
    {
      "title": "Overview",
      "body": [
        "**DATA PRIVACY NOTICE**: \nThis application is for demonstration and research simulation purposes only. \n**Do not upload** any Personally Identifiable Information (PII), Protected Health Information (PHI), or any confidential patient data. \nEnsure all datasets are fully anonymized before uploading.",
        "### Case Study: Lung Cancer Detection\n**Context:** Radiologists label chest X-rays as either **Cancerous (1)** or **Benign (0)**. Inconsistencies among radiologists can confuse AI models.\n\n**Objectives:**\n1.  **Quantify Agreement:** Use ICC to measure how consistently radiologists rate the images.\n2.  **Identify Ambiguity:** Find specific X-rays with high disagreement for potential re-review.\n3.  **Optimize Annotators:** Determine how many radiologists are needed to train a reliable AI model."
      ],
      "prompts": []
    },
    {
      "title": "Simulated Radiologist Diagnoses",
      "body": [
        "0 = Benign, 1 = Cancerous. Rows represent individual X-rays."
      ],
      "prompts": []
    },
    {
      "title": "Review High-Disagreement Images",
      "body": [
        "Find cases with the most diagnostic variance.",
        "The X-rays below have the highest variance in diagnosis (e.g., split decisions). These are candidates for expert re-review."
      ],
      "prompts": []
    },
    {
      "title": "AI Model Performance vs. Number of Radiologists",
      "body": [
        "Show how consensus size affects model accuracy.",
        "This curve shows how adding more radiologists to the consensus label improves the AI's ability to detect cancer.",
        "scikit-learn is not installed. Please install it to run the model simulation.",
        "**Interpretation:** * **Diminishing Returns:** Notice how the accuracy curve typically flattens out. The \"elbow\" of this curve suggests the optimal number of radiologists needed (cost-benefit).\n* **Noise Reduction:** More radiologists = stable consensus = better training data for the AI.",
        "### References",
        "* **Inter-rater Reliability:** \n* **Consensus Labeling:** Using majority vote or expert review to correct noisy labels."
      ],
      "prompts": []
    },
    {
      "title": "Simulation Settings",
      "body": [
        "Configure sample count, raters, disagreement rate, or upload annotations."
      ],
      "prompts": []
    },
    {
      "title": "Inter-Rater Reliability",
      "body": [
        "Use ICC to quantify diagnostic agreement."
      ],
      "prompts": []
    }
  ],
  "media": [],
  "source": "notebooks/clinical/3.3_clinical.py"
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
          <div class="aip-kicker">AI Passport · Module 3: Data</div>
          <h1>3.3 · Radiology AI Reliability</h1>
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
def _(lesson, lab_controls, lab_id, mo):
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
