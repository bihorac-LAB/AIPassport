import pandas as pd
import os
import logging


def _find_registry_header_row(registry_fp: str, sheet_name: str) -> int:
    """Finds the header row in an enrollment workbook by scanning for key fields."""

    preview = pd.read_excel(registry_fp, sheet_name=sheet_name, header=None, nrows=30)
    for row_idx, row in preview.iterrows():
        row_values = {
            str(value).strip().lower()
            for value in row.tolist()
            if pd.notna(value) and str(value).strip()
        }

        has_first = "first name" in row_values
        has_last = "last name" in row_values
        has_email = any("email" in value for value in row_values)
        if has_first and has_last and has_email:
            return int(row_idx)

    # Historical default in the existing pipeline.
    return 8


def _build_full_name_series(first_name_series: pd.Series, last_name_series: pd.Series) -> pd.Series:
    return (
        first_name_series.fillna("").astype(str).str.strip()
        + " "
        + last_name_series.fillna("").astype(str).str.strip()
    ).str.replace(r"\s+", " ", regex=True).str.strip()


def _select_best_name_column_pair(
    qualtrics_df: pd.DataFrame,
    first_name_candidates: list[str],
    last_name_candidates: list[str],
) -> tuple[str, str, int, int] | None:
    best_pair: tuple[str, str] | None = None
    best_score = (-1, -1)

    for first_name_col in first_name_candidates:
        for last_name_col in last_name_candidates:
            combined = _build_full_name_series(qualtrics_df[first_name_col], qualtrics_df[last_name_col])
            nonblank = combined[combined.str.len() > 1]
            score = (int(len(nonblank)), int(nonblank.nunique()))
            if score > best_score:
                best_score = score
                best_pair = (first_name_col, last_name_col)

    if not best_pair:
        return None

    return best_pair[0], best_pair[1], best_score[0], best_score[1]


def _find_case_insensitive_column(df: pd.DataFrame, expected: str) -> str | None:
    expected_lower = expected.strip().lower()
    for col in df.columns:
        if str(col).strip().lower() == expected_lower:
            return col
    return None

def load_module_names(end_of_module_files: list[str], pre_survey_files: list[str], logger: logging.Logger) -> list[dict]:
    """
    Finds all unique names for the pre survey and end of module files. Logs the findings, and returns
    a list of objects containing 'name' and 'source' as the key.

    Parameters
    ----------
    end_of_module_files: list[str]
        The list of raw post module survey file paths.
    pre_survey_files: list[str]
        The list of raw pre module survey file paths.
    logger: logging.Logger
        The logger object

    Returns
    -------
    all_module_rows: list[dict]
        A list of objects with a name, source, and canvas_id key. Used to create a dataframe downstream.
    """
    
    all_module_rows: list[dict] = []

    for file_type, files in {
        "end of module" : end_of_module_files,
        "pre module" : pre_survey_files
    }.items():
        names: set[str] = set()

        for file in files:
            df = pd.read_csv(file)
            name_col = _find_case_insensitive_column(df, "name")
            id_col = _find_case_insensitive_column(df, "id")

            if name_col is None or id_col is None:
                logger.warning(
                    "Skipping %s for name loading; expected name/id columns (case-insensitive)",
                    os.path.basename(file),
                )
                continue

            this_file_names = set(df[name_col].astype(str))
            names |= this_file_names

            logger.info(f" - {os.path.basename(file)} has {len(this_file_names):,} unique names")

            for name, canvas_id in df[[name_col, id_col]].dropna().drop_duplicates().itertuples(index=False):
                if name:
                    all_module_rows.append({"name": name, "source": os.path.basename(file), "canvas_id" : canvas_id})

        logger.info(f"Found {len(names):,} unqiue names for {file_type} surveys.\n")

    return all_module_rows


def load_qualtrics_names(inmd_dir: str, qualtrics_files: list[str], logger: logging.Logger) -> list[dict]:
    """
    Finds all unique names for the qualtrics files. Logs the findings, and returns
    a list of objects containing 'name' and 'source' as the key. Also creates cleaned
    versions of each qualtrics file at the intermediate directory.

    Parameters
    ----------
    inmd_dir: str
        The intermediate path containing cleaned qualtrics files.
    qualtrics_files: list[str]
        The list of full file paths for all qualtrics surveys.
    logger: logging.Logger
        The logger object

    Returns
    -------
    all_qualtrics_rows: list[dict]
        A list of objects with a name and source key. Used to create a dataframe downstream.
    """

    all_qualtrics_rows: list[dict] = []

    for qualtrics_fp in qualtrics_files:
        qualtrics_basename = os.path.basename(qualtrics_fp)
        qualtrics_df = pd.read_csv(qualtrics_fp, header=1)
        logger.info(f"Read {len(qualtrics_df):,} rows from {qualtrics_basename}")
        qualtrics_df = qualtrics_df.iloc[1:].reset_index(drop=True)  # Dropping the metadata row

        first_name_candidates = [col for col in qualtrics_df.columns if "first name" in str(col).lower()]
        last_name_candidates = [col for col in qualtrics_df.columns if "last name" in str(col).lower()]

        if not first_name_candidates or not last_name_candidates:
            logger.warning(f"Skipping {qualtrics_basename}: unable to find first/last name columns")
            continue

        best_pair = _select_best_name_column_pair(
            qualtrics_df=qualtrics_df,
            first_name_candidates=first_name_candidates,
            last_name_candidates=last_name_candidates,
        )
        if best_pair is None:
            logger.warning(f"Skipping {qualtrics_basename}: unable to select a usable first/last name pair")
            continue

        first_name_col, last_name_col, nonblank_name_rows, unique_names = best_pair

        if len(qualtrics_df) >= 10 and unique_names <= 1:
            raise ValueError(
                "Qualtrics name QA gate failed for "
                f"{qualtrics_basename}: selected columns '{first_name_col}' + '{last_name_col}' "
                f"produced only {unique_names} unique names across {nonblank_name_rows} nonblank rows."
            )

        assert "name" not in qualtrics_df.columns

        logger.info(
            " - Using %s + %s for names (%s nonblank rows, %s unique names)",
            first_name_col,
            last_name_col,
            nonblank_name_rows,
            unique_names,
        )

        qualtrics_df["name"] = _build_full_name_series(
            qualtrics_df[first_name_col],
            qualtrics_df[last_name_col],
        )
        qualtrics_df = qualtrics_df[qualtrics_df["name"].str.len() > 1].copy()
        logger.info(f" - Found {qualtrics_df['name'].nunique():,} names in {qualtrics_basename}\n")
        for name in qualtrics_df["name"].dropna().unique():
            if name and str(name).strip():
                all_qualtrics_rows.append({"name": name, "source": qualtrics_basename})

        qualtrics_df.to_csv(os.path.join(inmd_dir, f"cleaned_{qualtrics_basename}"), index=False)

    return all_qualtrics_rows


def load_registry_names(registry_fp: str | None, inmd_dir: str, logger: logging.Logger) -> list[dict]:
    """
    Finds all unique names from the registry file. Logs the findings, and returns
    a list of objects containing 'name' and 'source' as the key. Also creates a cleaned
    version of the registry file at the intermediate directory.

    Parameters
    ----------
    registry_fp: str
        The full path to the registry file
    inmd_dir: str
        The intermediate path containing cleaned qualtrics files.
    logger: logging.Logger
        The logger object

    Returns
    -------
    registry_rows: list[dict]
        A list of objects with a name and source key. Used to create a dataframe downstream.
    """

    if not registry_fp or not os.path.exists(registry_fp):
        logger.warning("No registry file found; continuing without enrollment roster")
        return []

    registry_basename = os.path.basename(registry_fp)
    registry_basename_no_ext = os.path.splitext(registry_basename)[0]
    
    registry_rows: list[dict] = []

    sheet_names = pd.ExcelFile(registry_fp).sheet_names
    sheet_name = next((sheet for sheet in sheet_names if "enrollment" in sheet.lower()), sheet_names[0])
    header_row = _find_registry_header_row(registry_fp=registry_fp, sheet_name=sheet_name)
    registry = pd.read_excel(registry_fp, sheet_name=sheet_name, header=header_row)

    name_parts = [col for col in ["First Name", "Middle Name", "Last Name"] if col in registry.columns]
    if not name_parts:
        logger.warning(f"Registry file {registry_basename} does not include expected name columns")
        return []

    registry["name"] = registry[name_parts].fillna("").agg(" ".join, axis=1).str.replace(r"\s+", " ", regex=True).str.strip()

    id_col_candidates = ["Canvas ID", "Canvas_ID"]
    id_col = next((col for col in id_col_candidates if col in registry.columns), None)

    if id_col:
        registry["canvas_id"] = registry[id_col]
    else:
        if "School ID" in registry.columns or "Student Number" in registry.columns:
            logger.warning(
                "Registry has School ID/Student Number, but these are not used for Canvas IDs. "
                "Expected 'Canvas ID' or 'Canvas_ID' column."
            )
        registry["canvas_id"] = pd.NA

    cleaned_fp = os.path.join(inmd_dir, f"{registry_basename_no_ext}.csv")
    registry.to_csv(cleaned_fp, index=False)
    logger.info(f"Wrote {len(registry):,} rows to {cleaned_fp}")

    for name, canvas_id in registry[["name", "canvas_id"]].drop_duplicates().itertuples(index=False):
        if name and str(name).strip():
            registry_rows.append({"name": name, "source": registry_basename, "canvas_id": canvas_id})

    return registry_rows


def create_name_master_file(
    inmd_dir: str,
    output_dir: str,
    registry_fp: str | None,
    end_of_module_files: list[str], 
    pre_survey_files: list[str], 
    qualtrics_files: list[str],
    logger: logging.Logger
) -> None:
    """ 
    Creates an 'all_names.csv' file at the output directory containing all the names found from module, qualtrics, and registry
    files. The sources each name was found in is included, as well as a canvas id if applicable.

    Parameters
    ----------   
    inmd_dir: str
        The intermediate path containing cleaned qualtrics files.
    output_dir: str
        The path all output files are written to.
    registry_fp: str
        The full path to the registry file
    pre_survey_files: list[str]
        The list of raw pre module survey file paths.
    end_of_module_files: list[str]
        The list of raw post module survey file paths.
    qualtrics_files: list[str]
        The list of full file paths for all qualtrics surveys.
    logger: logging.Logger
        The logger object
    """
    
    all_rows: list[dict] = []

    module_survey_rows = load_module_names(end_of_module_files=end_of_module_files, pre_survey_files=pre_survey_files, logger=logger)
    all_rows += module_survey_rows

    qualtrics_rows = load_qualtrics_names(inmd_dir=inmd_dir, qualtrics_files=qualtrics_files, logger=logger)
    all_rows += qualtrics_rows

    registry_rows = load_registry_names(registry_fp=registry_fp, inmd_dir=inmd_dir, logger=logger)
    all_rows += registry_rows

    tracking_df = pd.DataFrame(all_rows)
    logger.info(f"Final tracking df has {len(tracking_df):,} rows")
    os.makedirs(output_dir, exist_ok=True)

    if tracking_df.empty:
        tracking_df.to_csv(os.path.join(output_dir, "all_names.csv"), index=False)
        logger.warning("No rows found while building all_names.csv")
        return

    if "canvas_id" not in tracking_df.columns:
        tracking_df["canvas_id"] = pd.NA

    # Create a master_only column if the name is not anywhere else
    tracking_df["name"] = tracking_df["name"].astype(str).str.strip()
    tracking_df = tracking_df[tracking_df["name"].str.len() > 5] # removing names like '..' that are impossibly short

    tracking_df = tracking_df.drop_duplicates().sort_values(by=["name", "source"])

    name_sources: pd.Series = tracking_df.groupby("name")["source"].agg(set)
    tracking_df["has_canvas_id_yn"] = tracking_df["canvas_id"].notna().groupby(tracking_df["name"]).transform("any").astype(int)

    if registry_fp and os.path.exists(registry_fp):
        registry_basename = os.path.basename(registry_fp)
        tracking_df["not_in_registry_yn"] = tracking_df["name"].map({
            name: (registry_basename not in sources)
            for name, sources in name_sources.items()
        }).astype(int)
    else:
        tracking_df["not_in_registry_yn"] = pd.NA

    tracking_df.to_csv(os.path.join(output_dir, "all_names.csv"), index=False)
