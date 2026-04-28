from typing import Literal

module_names: dict[int, str] = {
    1 : "Module 1: Fundamentals of Biomedical AI Research",
    2 : "Module 2: Biomedical AI Alignment",
    3 : "Module 3: Data-Centric Biomedical AI",
    4 : "Module 4: Fundamentals of Biomedical ML",
    5 : "Module 5: Biomedical Image Analysis",
    6 : "Module 6: Generative AI in Biomedicine",
    7 : "Module 7: Impact Project"
}

survey_responses: dict[str, int] = {
    "Not at all confident": 1,
    "Slightly confident": 2,
    "Slight confident": 2, # This was an extra
    "Moderately confident": 3,
    "Very confident": 4,
    "Extremely confident": 5
}

EXPECTED_QUESTIONS = 7

def get_microskill_description(module_num: int, microskill_num: int) -> str:
    """
    Returns a description of the microskill for the given module number. Used in the personalized reports.
    """

    # Module number - microskill number
    description_map = {
        # Module 1
        "1-1": "Capabilities & limits of biomedical AI",
        "1-2": "End-to-end AI project lifecycle",
        "1-3": "Designing AI experiments",
        "1-4": "AI model development & evaluation",
        "1-5": "Forming effective research teams",
        "1-6": "Scientific rigor & reproducibility",
        "1-7": "Mentor/mentee navigation",

        # Module 2
        "2-1": "Four principles of bioethics",
        "2-2": "Medical product & practice regulation",
        "2-3": "Bias & fairness in AI",
        "2-4": "FDA regulation & tort liability",
        "2-5": "MLOps & Model Cards",
        "2-6": "Human-AI interaction",
        "2-7": "Biological variables in AI",

        # Module 3
        "3-1": "Overfitting & underfitting",
        "3-2": "Acquiring biomedical data",
        "3-3": "Annotation tools & evaluation",
        "3-4": "FAIR principles & standardization",
        "3-5": "Outliers & preprocessing",
        "3-6": "Secure data & model sharing",
        "3-7": "Informed consent",

        # Module 4
        "4-1": "Fundamental AI concepts",
        "4-2": "ML & deep learning fundamentals",
        "4-3": "Classic ML models (SVM, etc.)",
        "4-4": "Classic deep learning models",
        "4-5": "Critically evaluating biomedical ML",
        "4-6": "Designing generalizable ML",
        "4-7": "Ethics of black-box algorithms",

        # Module 5
        "5-1": "Biomedical imaging modalities",
        "5-2": "Image preprocessing & transformation",
        "5-3": "Traditional image analysis",
        "5-4": "Biomedical computer vision",
        "5-5": "Advanced / emerging imaging AI",
        "5-6": "Consistency in biomedical imaging",
        "5-7": "Privacy protection in imaging",

        # Module 6
        "6-1": "Generative biomedical AI fundamentals",
        "6-2": "Transformer-based LLM concepts",
        "6-3": "LLMs in healthcare applications",
        "6-4": "Prompt engineering for biomedical AI",
        "6-5": "LLMs for biomedical research",
        "6-6": "Reliability & reproducibility of AI outputs",
        "6-7": "Ethics of AI-generated biomedical information",

        # Module 7
        "7-1": "AI research design & feasibility assessment",
        "7-2": "AI innovation, ethics, and NIH proposal development",
        "7-3": "Scientific communication & presentation skills",
        "7-4": "Integrating AI into scientific research domains",
        "7-5": "Peer review, feedback, and collaboration",
        "7-6": "Reproducibility & documentation in biomedical AI",
        "7-7": "Responsible conduct of research & teamwork",
    }

    return description_map.get(f"{module_num}-{microskill_num}")


def reflection_journal_col(module_num: str, col_type: Literal["post", "reply", "passed"]) -> str:
    if col_type == "post":
        return f"M{module_num}_RJ_Posted"
    elif col_type == "reply":
        return f"M{module_num}_RJ_Reply_Count"
    elif col_type == "passed":
        return f"M{module_num}_RJ_Passed"


def get_variable_name(
    variable_type: Literal["delta_mean", "mean", "standard_deviation", "microskill", "numeric_microskill", "delta_microskill"],
    module_num: int,
    survey_type: Literal["Pre", "Post"] | None = None, 
    microskill_num: int = None
) -> str:
    """ 
    Returns the name of the variable for the given parameters.

    Variables types are listed as follows:
        - delta_mean: The change in mean between post and pre survey mean for the given module
        - mean: The mean response value of the survey type for the given module
        - standard_deviation: The standard deviation of the survey type for the given module
        - microskill: The response provided for the microskill of the survey type for the given module
        - numeric_microskill: The numeric version (1-5) of the response provided for the microskill of the survey type for the given module
        - delta_microskill: The difference between the post and pre surveys' numeric microskill value
    """

    variable_type_to_variable_name = {
        "delta_mean" : f"M{module_num}_Delta_Mean",
        "mean" : f"M{module_num}_{survey_type}_Mean",
        "standard_deviation" : f"M{module_num}_{survey_type}_SD",
        "microskill": f"M{module_num}_{survey_type}_MS{microskill_num}",
        "numeric_microskill": f"M{module_num}_{survey_type}_MS{microskill_num}_N",
        "delta_microskill": f"M{module_num}_Delta_MS{microskill_num}"
    }

    if variable_type not in variable_type_to_variable_name.keys():
        raise ValueError("Invalid variable type.")

    if "microskill" in variable_type and microskill_num is None:
        raise ValueError("Must provide microskill_num for a microskill variable name.")

    if survey_type is None and "delta" not in variable_type:
        raise ValueError("Must provide survey_type for non-delta variable names.")

    return variable_type_to_variable_name.get(variable_type)

