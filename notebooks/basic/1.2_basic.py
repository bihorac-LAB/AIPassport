import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("1.2 Designing a Study You Can Defend (Basic Science)")

st.markdown(
    """
You are a computational biologist in a lab studying how cells respond to drug compounds. Your images
capture subtle phenotypic changes that traditional scoring misses, and you want to use AI to **classify
those phenotypes and surface novel responses**.

A design is only worth as much as the rigor behind it. This subsection moves in four steps:

1. **Write the design brief** — the gap, the question, and the data plan.
2. **Do the rigor work** — detect and handle outliers in a real table, and see what your choice does to the numbers.
3. **Commit to a validation strategy** — splitting, cross-validation, external validation, subgroup performance.
4. **Carry the decision to your team** — one professional message that a busy senior colleague will actually read.

**Resources:** [Cell Painting Dataset](https://broad.io/CellPainting) ·
[Allen Brain Atlas](https://portal.brain-map.org/) ·
[PyTorch](https://pytorch.org/) · [scikit-learn](https://scikit-learn.org/stable/)
"""
)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# Part 1 — The design brief
# ═══════════════════════════════════════════════════════════════════════════
st.header("1. The Design Brief")

st.markdown(
    """
Six inputs. Keep each one short and specific — a brief that says exactly what you will do is more
defensible than one that lists everything you *could* do.
"""
)

st.subheader("1.1 The gap and the question")
st.text_area(
    "**Gap.** Name one concrete limitation of current AI phenotype classification "
    "(e.g., small labelled sets, batch effects, no interpretable link to a pathway, failure to transfer "
    "across cell lines).",
    key="m1_design_gap",
)
st.text_area(
    "**Question.** State one primary research question that closes that gap, using SMART criteria "
    "(specific, measurable, achievable, relevant, time-bound).",
    key="m1_design_question",
)

st.subheader("1.2 The data plan")
channels = st.multiselect(
    "**Elements.** Which staining channels or compartments will your model see?",
    [
        "DNA",
        "Mitochondria",
        "Endoplasmic reticulum",
        "Golgi",
        "Cytoskeleton",
        "RNA",
    ],
    key="m1_design_elements",
)
st.text_area(
    "**Cohort.** Give your inclusion and exclusion criteria for images in two or three lines "
    "(cell type, focus quality, treatment, plate position).",
    key="m1_design_cohort",
)
st.text_area(
    "**Missingness and bias.** How will you handle failed wells and missing channels, and which "
    "acquisition bias — batch, plate edge, illumination, cell line — are you most worried about carrying "
    "into the model?",
    key="m1_design_missing",
)
st.text_area(
    "**Preprocessing.** Name the transformations you will apply — illumination correction, intensity "
    "normalization, feature extraction, and at least one biologically meaningful derived feature "
    "(e.g., nuclear-to-cytoplasmic ratio).",
    key="m1_design_prepro",
)

if channels:
    st.caption(f"Your model will see: {', '.join(channels)}.")
    if len(channels) == 1:
        st.caption(
            "Note: a single channel makes interpretation easier but forecloses any phenotype defined by "
            "the relationship *between* compartments."
        )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# Part 2 — The rigor lab (outliers)
# ═══════════════════════════════════════════════════════════════════════════
st.header("2. Rigor Lab: Outliers in a Measurement Table")

st.markdown(
    """
Your brief promised to handle failed wells and extreme values. This is where you actually do it.

The table below is a **simulated set of ICU vital signs** for 30 patients rather than a plate of images —
deliberately, for two reasons: it is small enough to inspect by eye, and the outlier logic is identical
whatever the measurement is. A saturated pixel intensity, a mis-segmented cell area, and a heart rate of 2
are the same statistical problem and the same scientific decision.

- `heart_rate` — beats per minute
- `map` — mean arterial pressure (mmHg)
- `temperature` — °C
"""
)


@st.cache_data
def load_vitals_sample():
    rng = np.random.default_rng(42)
    n = 30
    return pd.DataFrame(
        {
            "patient_id": np.arange(1, n + 1),
            "heart_rate": np.append(rng.normal(75, 10, n - 2), [150, 2]),  # two outliers
            "map": np.append(rng.normal(85, 12, n - 1), [210]),            # one outlier
            "temperature": np.append(rng.normal(37, 0.7, n - 1), [42]),    # one outlier
        }
    )


df = load_vitals_sample()
VARIABLES = ["heart_rate", "map", "temperature"]

st.dataframe(df, use_container_width=True)


def iqr_bounds(column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr, q1, q3, iqr


st.subheader("2.1 See them")
st.markdown("A boxplot makes an extreme value obvious before any arithmetic does.")

sel_plot = st.selectbox("Variable for boxplot:", VARIABLES, key="m1_rigor_plot_var")
fig = px.box(df, x=sel_plot, points="all", hover_data=["patient_id"])
fig.update_layout(
    height=320,
    xaxis_title=sel_plot,
    yaxis_title="",
    margin=dict(l=40, r=20, t=25, b=35),
)
st.plotly_chart(fig, use_container_width=True)
st.text_area(
    "Which points look like outliers, and which record IDs are they?", key="m1_rigor_visual_notes"
)

st.subheader("2.2 Measure them")
st.markdown(
    "The 1.5×IQR rule flags any value above Q3 + 1.5×IQR or below Q1 − 1.5×IQR. It is a convention, not "
    "a law — but it is a convention you can write down in a methods section."
)

sel_stat = st.selectbox("Variable for threshold calculation:", VARIABLES, key="m1_rigor_calc_var")
lower, upper, q1, q3, iqr = iqr_bounds(sel_stat)

bound_cols = st.columns(3)
bound_cols[0].metric("IQR", f"{iqr:.2f}", help=f"Q1 = {q1:.2f}, Q3 = {q3:.2f}")
bound_cols[1].metric("Lower bound", f"{lower:.2f}")
bound_cols[2].metric("Upper bound", f"{upper:.2f}")

outlier_mask = (df[sel_stat] < lower) | (df[sel_stat] > upper)
st.markdown("**Rows flagged by the IQR rule:**")
st.dataframe(df[outlier_mask], use_container_width=True)
st.text_area(
    "Do the flagged values look like instrument or entry errors, or like genuinely unusual samples? "
    "Your answer changes what you are allowed to do next.",
    key="m1_rigor_flagged_notes",
)

st.subheader("2.3 See what they cost you")
sel_compare = st.selectbox("Variable for comparison:", VARIABLES, key="m1_rigor_compare_var")
lwr2, upr2, *_ = iqr_bounds(sel_compare)
with_out = df[sel_compare]
wout_out = df[~((df[sel_compare] < lwr2) | (df[sel_compare] > upr2))][sel_compare]

comp_cols = st.columns(2)
with comp_cols[0]:
    st.markdown("**All data**")
    st.write(f"Mean: {with_out.mean():.2f}")
    st.write(f"Std: {with_out.std():.2f}")
    st.write(f"Median: {with_out.median():.2f}")
with comp_cols[1]:
    st.markdown("**Outliers excluded**")
    st.write(f"Mean: {wout_out.mean():.2f}")
    st.write(f"Std: {wout_out.std():.2f}")
    st.write(f"Median: {wout_out.median():.2f}")

st.text_area(
    "Which statistic moved most — mean, standard deviation, or median? Why does that matter when the "
    "number ends up in a paper?",
    key="m1_rigor_effect_notes",
)

st.subheader("2.4 Handle them")
st.markdown(
    """
Three defensible strategies, each with a different cost:

- **Remove** — honest about uncertainty, but throws away real samples and shrinks your dataset.
- **Winsorize** — keeps every row, at the price of a value that was never measured.
- **Impute with median** — keeps the row and the sample size, and erases the signal that made it unusual.
"""
)

sel_handle = st.selectbox("Variable for handling strategies:", VARIABLES, key="m1_rigor_handle_var")
approach = st.radio(
    "Strategy:",
    ["Remove (exclude outlier rows)", "Winsorize (cap at threshold)", "Impute with median"],
    key="m1_rigor_approach",
)
lwr, upr, *_ = iqr_bounds(sel_handle)
series = df[sel_handle]

if approach.startswith("Remove"):
    handled = series[(series >= lwr) & (series <= upr)]
elif approach.startswith("Winsor"):
    handled = series.clip(lwr, upr)
else:
    median = series[(series >= lwr) & (series <= upr)].median()
    handled = series.copy()
    handled[(handled < lwr) | (handled > upr)] = median

handle_cols = st.columns(3)
handle_cols[0].metric("Mean", f"{handled.mean():.2f}", f"{handled.mean() - series.mean():+.2f}")
handle_cols[1].metric("Std", f"{handled.std():.2f}", f"{handled.std() - series.std():+.2f}")
handle_cols[2].metric("N", f"{handled.count()}", f"{handled.count() - series.count():+d}")

st.text_area(
    "Pros and cons of the strategy you chose, and where it would be the wrong choice:",
    key="m1_rigor_handle_notes",
)

st.subheader("2.5 Report them")
st.markdown(
    """
Everything above is invisible to a reader unless you write it down. Transparent reporting is not a
courtesy — it is what makes the result reproducible, and what lets a reviewer tell a cleaning decision
from a result.
"""
)
st.text_area(
    "Write the outlier-handling sentence that would appear in your methods section. Name the rule, the "
    "variables it was applied to, how many records it affected, and what you did with them.",
    key="m1_rigor_reflection",
)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# Part 3 — Validation strategy
# ═══════════════════════════════════════════════════════════════════════════
st.header("3. A Validation Strategy You Can Defend")

st.markdown(
    """
**The situation:** your dataset is **10,000 images acquired over three years**, across three plate batches,
two microscopes, and four cell lines. The model will later be tested on images from a collaborating lab
using a different imaging platform.

Four decisions. Each one is a claim you will have to defend.
"""
)

st.subheader("Task 1 — Splitting")
split_issues = st.multiselect(
    "What makes a simple random split unsafe for *this* dataset? (choose all that apply)",
    [
        "Temporal leakage — later acquisitions end up in the training set",
        "Images of the same well or field appear in both train and test",
        "Phenotype class balance differs across batches",
        "Microscope and illumination batch effects are ignored",
        "Some cell lines are represented on only one plate",
        "Rare phenotypes may be absent from the test set entirely",
    ],
    key="m1_valid_split_issues",
)
split_strategy = st.radio(
    "Which splitting principle will you commit to?",
    [
        "Temporal split (train on earlier batches, test on the latest)",
        "Leave-one-batch-out (hold out an entire plate batch)",
        "Well-level split stratified by phenotype",
        "Hybrid (batch + cell line + phenotype stratification)",
    ],
    key="m1_valid_split_strategy",
)
st.text_area(
    "Which of the issues you selected does your chosen split actually solve — and which does it leave open?",
    key="m1_valid_split_notes",
)

st.subheader("Task 2 — Internal validation")
cv_cols = st.columns([2, 1])
with cv_cols[0]:
    cv_type = st.selectbox(
        "Cross-validation design:",
        [
            "K-fold (random)",
            "K-fold (stratified by phenotype)",
            "K-fold (grouped by cell line)",
            "Leave-one-batch-out",
            "Nested CV (tuning inside, evaluation outside)",
        ],
        key="m1_valid_cv_type",
    )
with cv_cols[1]:
    n_folds = st.slider("Folds:", 3, 10, 5, key="m1_valid_folds")

cv_metrics = st.multiselect(
    "Which metrics will you report per fold? (accuracy alone is not enough when phenotypes are rare)",
    [
        "Accuracy",
        "Macro F1",
        "Precision / recall per class",
        "AUROC",
        "Confusion matrix",
        "Biological enrichment (GO, pathways)",
        "Cluster purity / silhouette",
    ],
    key="m1_valid_metrics",
)
if cv_metrics and "Accuracy" in cv_metrics and len(cv_metrics) == 1:
    st.caption(
        "Worth reconsidering: with a rare phenotype, a model that never predicts it can still be 97% "
        "accurate. You need at least one per-class metric."
    )

st.subheader("Task 3 — External validation")
st.text_area(
    "Your model will be evaluated on images from a collaborating lab using a different microscope and "
    "staining protocol. What will you hold fixed, what will you allow to be re-fit, and what result would "
    "make you say the model does *not* generalize?",
    key="m1_valid_external",
)

st.subheader("Task 4 — Subgroup performance")
subgroups = st.multiselect(
    "Which strata will you report performance for, separately, before claiming the model works?",
    [
        "Cell line",
        "Plate batch",
        "Microscope / imaging platform",
        "Compound class",
        "Dose level",
        "Plate position (edge vs. interior wells)",
        "Rare vs. common phenotypes",
    ],
    key="m1_valid_subgroups",
)
st.text_area(
    "Pick the stratum you expect to perform worst and say why — mechanism, not guesswork. What would you "
    "do if you were right?",
    key="m1_valid_subgroup_notes",
)

if split_strategy and cv_type:
    st.info(
        f"**Your stated design:** {split_strategy.split(' (')[0]} · {cv_type} with {n_folds} folds · "
        f"{len(cv_metrics)} reported metric(s) · {len(subgroups)} stratum/strata audited."
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# Part 4 — Carrying it to the team
# ═══════════════════════════════════════════════════════════════════════════
st.header("4. Carrying the Decision to Your Team")

st.markdown(
    """
A design nobody understands does not get built. This study needs a cell biologist, a microscopist, a data
scientist, a software engineer, and someone who knows the compound library — and they do not share a
vocabulary.
"""
)

with st.expander("Terms this team will use differently without noticing", expanded=False):
    st.markdown(
        """
    Before you write anything, check that these mean the same thing to everyone in the room:

    | Term | Where the confusion comes from |
    | --- | --- |
    | *validation* | statistical out-of-sample testing vs. wet-lab confirmation |
    | *replicate* | technical replicate vs. biological replicate |
    | *significance* | p < 0.05 vs. "big enough to be a real phenotype" |
    | *model* | the fitted classifier vs. the model organism or system |
    | *bias* | statistical estimation bias vs. batch/acquisition bias |
    | *label* | the annotated class vs. the underlying biology it stands for |
    | *feature* | model input vs. a visible cellular structure |
    | *control* | negative control well vs. experimental control condition |
    | *normalization* | per-image intensity scaling vs. per-plate statistical normalization |
    | *accuracy* | the metric vs. "is it right" |
    """
    )

st.text_area(
    "**The team question.** Who do you need on this team, what will each of them catch that you would "
    "miss, and how will you keep the biology honest as the modelling work speeds up?",
    key="m1_team_plan",
)

st.subheader("The communication artefact")

with st.expander("The situation (click to expand)", expanded=True):
    st.markdown(
        """
    **You are Dr. Witmer**, an early-career research faculty member, mentored by **Dr. Antone**, a senior
    faculty member.

    Early meetings were productive, but over time Dr. Antone has become less available — often
    rescheduling or cutting meetings short. You feel unsupported, particularly while preparing an upcoming
    grant application.

    Dr. Antone, in turn, sees you as overly reliant and not proactive in solving problems independently.
    Tensions are rising and both of you are frustrated.
    """
    )

st.markdown(
    """
Write the message that requests a meeting and actually improves the situation. It has to do three things
at once: state the problem clearly, show you understand the other side, and propose a concrete change.
This is the same skill as defending your design to a study section or a sceptical collaborator — the
audience is busy and the ask has to be specific.
"""
)

st.text_area(
    "Your message to Dr. Antone:",
    height=220,
    key="m1_comm_email",
)

if st.button("Compare with a worked example", key="m1_comm_example_btn"):
    st.info(
        """\
Dear Dr. Antone,

I hope you're doing well. I'd like to request a meeting to discuss our working relationship and the
challenges that I have been facing recently. I truly value your expertise, and I have learned a lot from
you.

Over the past few months, I've noticed that our meetings have been less frequent, with some rescheduled or
cut short. I understand that you have many demands on your time, but I've felt unsupported, especially as
I prepare for the upcoming grant application. However, I recognize that I may have been overly reliant on
you, and I want to be more proactive in problem-solving going forward. Maybe we could schedule regular
check-ins, with clear agendas to make the most of our time together. Mainly, I want to find a way to be
more self-reliant while still benefiting from your mentorship.

I look forward to hearing your thoughts on this.

Best,
Dr. Witmer
"""
    )
    st.caption(
        "Notice what it does: names the specific change (frequency), credits the other side's constraints, "
        "concedes its own contribution to the problem, and asks for one concrete, cheap thing."
    )

st.markdown(
    """
---
**Key takeaways**

- A defensible study states its gap, its question, and its data plan *before* the modelling starts.
- Cleaning decisions are results. Report the rule, the count, and the consequence.
- Splitting, cross-validation, external validation, and subgroup performance are four separate claims —
  a strong answer to one does not cover the others.
- Open expectations prevent small misalignments from becoming ruptures.

**Further reading:** [Nature — How to be a good mentee](https://www.nature.com/articles/d41586-020-02927-0) ·
[Science — How to make the most of mentoring](https://www.science.org/content/article/how-make-most-mentoring)
"""
)
