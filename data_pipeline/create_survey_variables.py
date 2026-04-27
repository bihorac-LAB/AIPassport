import pandas as pd
import logging
import os
import re

from .tools.consts import module_names, EXPECTED_QUESTIONS, survey_responses


MODULE_NUMBER_PATTERN = re.compile(r"module\s*(\d+)", flags=re.IGNORECASE)


def _extract_module_number_from_path(file_path: str) -> int:
    match = MODULE_NUMBER_PATTERN.search(os.path.basename(file_path))
    if not match:
        raise ValueError(f"Unable to parse module number from file name: {file_path}")
    return int(match.group(1))


def _find_case_insensitive_column(df: pd.DataFrame, expected: str) -> str | None:
    expected_lower = expected.strip().lower()
    for col in df.columns:
        if str(col).strip().lower() == expected_lower:
            return col
    return None

def get_variable_name(variable_type: str, module_num: int, survey_type: str = None, microskill_num: int = None) -> str:
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


def create_survey_variables(
    pre_survey_files: list[str], 
    end_of_module_files: list[str], 
    reflection_journal_fp: str | None,
    output_dir: str, 
    logger: logging.Logger
) -> tuple[str, str]:
    """
    Creates the final data file summarizing all user module interactions, along with a microskill table that maps
    variable names to modules and descriptions.

    Parameters
    ----------
    pre_survey_files: list[str]
        The sorted list of all pre module survey files. The index in the list is expected
        to represent the module number - 1 that it belongs to.
    end_of_module_files: list[str]
        The sorted list of all post module survey files. The index in the list is also
        expected to represent module number -1, just like pre survey files.
    output_dir: str
        The directory the output files are written to
    logger: logging.Logger
        The logger object.

    Returns
    -------
    final_data_fp: str
        The full path to the file that maps name / id to pre and post module surveys. Also includes numeric values
        for survey responses, mean, standard deviations, and deltas.
    microskill_fp: str
        THe full path to the file that maps variable name to a description. All values in the 'variable' column exist
        in final_data_fp's csv file.
    """

    microskill_rows: list[dict] = []

    module_dfs: list[pd.DataFrame] = []
    user_dfs: list[pd.DataFrame] = [] # 'id' and 'name' columns

    pre_by_module = { _extract_module_number_from_path(path): path for path in pre_survey_files }
    post_by_module = { _extract_module_number_from_path(path): path for path in end_of_module_files }

    for module_num in sorted(pre_by_module):
        pre_survey_file = pre_by_module[module_num]
        module_name: str = module_names.get(module_num, f"Module {module_num}")
        logger.info(f" ----- COLLECTING MODULE {module_name.upper()} RESULTS ----- ")

        survey_type_to_survey: dict[str, pd.DataFrame] = { "Pre" : pd.read_csv(pre_survey_file) }

        # Saving this to merge into post if applicable
        pre_module_df: pd.DataFrame = None
        module_result_df: pd.DataFrame | None = None

        # The end of module is not guaranteed to exist for the latest one
        if module_num in post_by_module:
            survey_type_to_survey["Post"] = pd.read_csv(post_by_module[module_num])

        for survey_type, survey_df in survey_type_to_survey.items():
            name_col = _find_case_insensitive_column(survey_df, "name")
            id_col = _find_case_insensitive_column(survey_df, "id")
            if name_col is None or id_col is None:
                logger.warning(
                    "Skipping %s %s-survey: expected name/id columns (case-insensitive)",
                    module_name,
                    survey_type,
                )
                continue

            user_df = survey_df[[name_col, id_col]].copy(deep=True).dropna(subset=[name_col, id_col])
            user_df = user_df.rename(columns={name_col: "name", id_col: "id"})
            user_df["name"] = user_df["name"].astype(str).str.strip()
            user_df["id"] = pd.to_numeric(user_df["id"], errors="coerce")
            user_df = user_df.dropna(subset=["name", "id"])
            user_df["id"] = user_df["id"].astype(int)
            user_df = user_df.drop_duplicates(subset=["name", "id"])
            user_dfs.append(user_df[["name", "id"]])

            logger.info(f" - {survey_type}-survey has responses from {user_df['id'].nunique():,} unique users")

            # They all should have seven, and the order seems to be relevant.
            question_cols: list[str] = [col for col in survey_df.columns if "please rate" in str(col).lower()]
            if len(question_cols) != EXPECTED_QUESTIONS:
                logger.warning(
                    "Skipping variable derivation for %s %s-survey: expected %s confidence questions, found %s",
                    module_name,
                    survey_type,
                    EXPECTED_QUESTIONS,
                    len(question_cols),
                )
                continue

            module_df: pd.DataFrame = survey_df[[name_col, id_col] + question_cols].copy(deep=True).dropna(subset=[name_col, id_col])
            module_df = module_df.rename(columns={name_col: "name", id_col: "id"})
            module_df["name"] = module_df["name"].astype(str)
            module_df["id"] = pd.to_numeric(module_df["id"], errors="coerce")
            module_df = module_df.dropna(subset=["id"])
            module_df["id"] = module_df["id"].astype(int)

            # Merging pre columns to calculate deltas
            if survey_type == "Post":
                if pre_module_df is None:
                    logger.warning(
                        "Skipping %s post-survey variable derivation because pre-survey confidence schema was unavailable",
                        module_name,
                    )
                    continue
                # If the module has a post survey, it will have a delta mean variable
                delta_mean_variable = get_variable_name(variable_type="delta_mean", module_num=module_num)
                microskill_rows.append({
                    "Variable" : delta_mean_variable,
                    "Module" : f"Post mean minus Pre mean for M{module_num} (composite confidence change)",
                    "Module Number" : module_num,
                })
                module_df = pre_module_df.merge(module_df, how="outer", on=["name", "id"])

            # Each module has a mean and SD variable
            mean_variable = get_variable_name(variable_type="mean", module_num=module_num, survey_type=survey_type)
            microskill_rows.append({
                "Variable" : mean_variable,
                "Module" : f"Mean of {len(question_cols)} numeric microskill scores for M{module_num}_{survey_type}",
                "Module Number" : module_num,
            })
            standard_deviation_variable = get_variable_name(variable_type="standard_deviation", module_num=module_num, survey_type=survey_type)
            microskill_rows.append({
                "Variable" : standard_deviation_variable,
                "Module" : f"Standard deviation of {len(question_cols)} numeric microskill scores for M{module_num}_{survey_type}",
                "Module Number" : module_num,
            })

            numeric_microskill_variables: list[str] = []

            # Each question is a microskill, and there are there columns for each
            for j, question_col in enumerate(question_cols):
                # This exists in microskill_key sheet in master data excel. This is the variable
                microskill_num = j + 1
                phase: str = survey_type
                full_question_text: str = question_col.split("\n\n", 1)[-1].strip()
                
                microskill_variable = get_variable_name(
                    variable_type="microskill", 
                    module_num=module_num, 
                    survey_type=survey_type, 
                    microskill_num=microskill_num
                )
                microskill_rows.append({
                    "Variable" : microskill_variable,
                    "Module" : module_name,
                    "Phase" : phase,
                    "Full Question Text" : full_question_text,
                    "Module Number" : module_num,
                    "Microskill Number" : microskill_num
                })
                numeric_microskill_variable = get_variable_name(
                    variable_type="numeric_microskill", 
                    module_num=module_num, 
                    survey_type=survey_type, 
                    microskill_num=microskill_num
                )
                # Appending to calculate mean and standard deviation after the for loop
                numeric_microskill_variables.append(numeric_microskill_variable)
                microskill_rows.append({
                    "Variable" : numeric_microskill_variable,
                    "Module" : f"Numeric encoding (1-5) of {microskill_variable}",
                    "Module Number" : module_num,
                    "Microskill Number" : microskill_num
                })

                module_df = module_df.rename(columns={question_col : microskill_variable})
                module_df[numeric_microskill_variable] = pd.to_numeric(module_df[microskill_variable].astype(str).map(survey_responses, na_action="ignore"))

                # Each microskill gets a delta if there is a post variable
                if survey_type == "Post":
                    delta_microskill_variable: str = get_variable_name(variable_type="delta_microskill", module_num=module_num, microskill_num=microskill_num)

                    microskill_rows.append({
                        "Variable" : delta_microskill_variable,
                        "Module" : f"Post minus Pre for M{module_num} MS{microskill_num}",
                        "Module Number" : module_num,
                        "Microskill Number" : microskill_num
                    })
                    pre_numeric_microskill_variable: str = get_variable_name(
                        variable_type="numeric_microskill", 
                        module_num=module_num, 
                        survey_type="Pre", 
                        microskill_num=microskill_num
                    )
                    module_df[delta_microskill_variable] = module_df[numeric_microskill_variable] - module_df[pre_numeric_microskill_variable]
                elif survey_type != "Pre":
                    raise ValueError("Expected only 'Pre' or 'Post' survey type")

            module_df[mean_variable] = module_df[numeric_microskill_variables].mean(axis=1).round(2)
            module_df[standard_deviation_variable] = module_df[numeric_microskill_variables].std(axis=1).round(2)
            if survey_type == "Pre":
                pre_module_df = module_df.copy(deep=True)
                module_result_df = module_df.copy(deep=True)
            elif survey_type == "Post":
                pre_mean_variable: str = get_variable_name(variable_type="mean", module_num=module_num, survey_type="Pre")
                module_df[delta_mean_variable] = (module_df[mean_variable] - module_df[pre_mean_variable]).round(2)
                module_result_df = module_df.copy(deep=True)

        if module_result_df is not None:
            module_dfs.append(module_result_df)

    if user_dfs:
        all_users = pd.concat(user_dfs).drop_duplicates().sort_values(by=["name"], ascending=True)
    else:
        all_users = pd.DataFrame(columns=["name", "id"])

    for module_df in module_dfs:
        all_users = all_users.merge(module_df, how="left", on=["name", "id"])

    if isinstance(reflection_journal_fp, str):
        reflection_journal = pd.read_csv(reflection_journal_fp).drop(columns=["user_name"]).rename(columns={"user_id" : "id"})
        all_users = all_users.merge(reflection_journal, how="left", on=["id"], validate="one_to_one")
        logger.info("Appended reflection journal to all_users")
    else:
        logger.warning("No reflection journal to append to all_users")

    final_data_fp = os.path.join(output_dir, "final_data.csv")
    all_users.to_csv(final_data_fp, index=False)

    microskill_df = pd.DataFrame(microskill_rows)
    microskill_fp = os.path.join(output_dir, "microskill_key.csv")
    microskill_df.to_csv(microskill_fp, index=False)

    logger.info(f"Wrote {len(microskill_df):,} microskill variables to {microskill_fp}")
    # for each microskill key, there should be a column in the final data file.

    return final_data_fp, microskill_fp
