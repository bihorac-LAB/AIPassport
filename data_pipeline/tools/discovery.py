import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


MODULE_NUMBER_PATTERN = re.compile(r"module\s*(\d+)", flags=re.IGNORECASE)


@dataclass(frozen=True)
class DiscoveredInputs:
    pre_survey_files: list[str]
    end_of_module_files: list[str]
    qualtrics_files: list[str]
    combined_survey_workbook: str | None
    registry_file: str | None
    master_workbook_template: str | None
    data_dictionary_file: str | None
    dropout_file: str | None


def _extract_module_number(file_path: str) -> int:
    match = MODULE_NUMBER_PATTERN.search(os.path.basename(file_path))
    if not match:
        return 10_000
    return int(match.group(1))


def _is_pre_module_file(file_name: str) -> bool:
    lower = file_name.lower()
    return (
        "module" in lower
        and "survey" in lower
        and (
            "pre" in lower
            or "kick-off" in lower
            or "kick off" in lower
            or "kickoff" in lower
        )
    )


def _is_post_module_file(file_name: str) -> bool:
    lower = file_name.lower()
    return ("module" in lower) and ("end-of-module" in lower) and ("survey" in lower)


def _looks_like_qualtrics(file_path: str) -> bool:
    """Qualtrics exports have a question-text row with first/last name prompts."""

    try:
        preview = pd.read_csv(file_path, header=None, nrows=2, dtype=str)
    except Exception:
        return False

    if len(preview) < 2:
        return False

    second_row_values = [str(value).strip().lower() for value in preview.iloc[1].tolist() if pd.notna(value)]
    has_first = any("first name" in value for value in second_row_values)
    has_last = any("last name" in value for value in second_row_values)
    return has_first and has_last


def _pick_first_matching(files: list[str], patterns: list[str]) -> str | None:
    for file_path in files:
        base = os.path.basename(file_path).lower()
        if any(pattern in base for pattern in patterns):
            return file_path
    return None


def _preference_score(file_path: str) -> tuple[int, int]:
    """Lower score is better."""

    lower_path = file_path.lower()
    base = os.path.basename(lower_path)

    score = 0

    if "archive" in lower_path:
        score += 20
    if "data masterfile and dictionary" in lower_path:
        score -= 10
    if "updated" in base:
        score -= 5

    return score, len(file_path)


def _pick_preferred_workbook(candidates: list[str]) -> str | None:
    if not candidates:
        return None
    return sorted(candidates, key=_preference_score)[0]


def discover_input_files(input_dir: str, logger: logging.Logger) -> DiscoveredInputs:
    """Discovers raw input files and metadata templates"""

    root = Path(input_dir)

    csv_files = sorted(
        [str(path) for path in root.glob("*.csv") if path.is_file() and not path.name.startswith("~$")],
        key=lambda value: value.lower(),
    )

    pre_survey_files: list[str] = []
    end_of_module_files: list[str] = []
    qualtrics_files: list[str] = []

    for csv_file in csv_files:
        file_name = os.path.basename(csv_file)
        if _is_pre_module_file(file_name):
            pre_survey_files.append(csv_file)
        elif _is_post_module_file(file_name):
            end_of_module_files.append(csv_file)
        elif _looks_like_qualtrics(csv_file):
            qualtrics_files.append(csv_file)

    pre_survey_files = sorted(pre_survey_files, key=lambda value: (_extract_module_number(value), value.lower()))
    end_of_module_files = sorted(end_of_module_files, key=lambda value: (_extract_module_number(value), value.lower()))
    qualtrics_files = sorted(qualtrics_files, key=lambda value: value.lower())

    root_xlsx_files = sorted(
        [str(path) for path in root.glob("*.xlsx") if path.is_file() and not path.name.startswith("~$")],
        key=lambda value: value.lower(),
    )
    combined_candidates = [
        file_path
        for file_path in root_xlsx_files
        if "combined" in os.path.basename(file_path).lower() and "survey" in os.path.basename(file_path).lower()
    ]
    combined_survey_workbook = combined_candidates[0] if combined_candidates else None

    spreadsheet_files = sorted(
        [
            str(path)
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".xls", ".xlsx", ".csv"} and not path.name.startswith("~$")
        ],
        key=lambda value: value.lower(),
    )

    enrollment_candidates = [
        file_path
        for file_path in spreadsheet_files
        if Path(file_path).suffix.lower() in {".xls", ".xlsx"}
        and ("enroll" in os.path.basename(file_path).lower() or "roster" in os.path.basename(file_path).lower())
    ]
    registry_file = enrollment_candidates[0] if enrollment_candidates else None

    # Keep these optional artifact fields disabled so the runtime build depends only on raw survey/registry inputs.
    master_workbook_template = None
    data_dictionary_file = None
    dropout_file = None

    logger.info(
        "Discovered files: pre=%s, post=%s, qualtrics=%s, combined=%s, registry=%s, template=%s, dictionary=%s, dropout=%s",
        len(pre_survey_files),
        len(end_of_module_files),
        len(qualtrics_files),
        os.path.basename(combined_survey_workbook) if combined_survey_workbook else "None",
        os.path.basename(registry_file) if registry_file else "None",
        os.path.basename(master_workbook_template) if master_workbook_template else "None",
        os.path.basename(data_dictionary_file) if data_dictionary_file else "None",
        os.path.basename(dropout_file) if dropout_file else "None",
    )

    return DiscoveredInputs(
        pre_survey_files=pre_survey_files,
        end_of_module_files=end_of_module_files,
        qualtrics_files=qualtrics_files,
        combined_survey_workbook=combined_survey_workbook,
        registry_file=registry_file,
        master_workbook_template=master_workbook_template,
        data_dictionary_file=data_dictionary_file,
        dropout_file=dropout_file,
    )