import pandas as pd
import os
import logging

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
            df = pd.read_csv(file, usecols=["name", "id"])
            this_file_names = set(df["name"].astype(str))
            names |= this_file_names

            logger.info(f" - {os.path.basename(file)} has {len(this_file_names):,} unique names")

            for name, canvas_id in df[["name", "id"]].dropna().drop_duplicates().itertuples(index=False):
                if name:
                    all_module_rows.append({"name": name, "source": os.path.basename(file), "canvas_id" : canvas_id})

        logger.info(f"Found {len(names):,} unqiue names for {file_type} surveys.\n")

    return all_module_rows


def load_qualtrics_names(input_dir: str, inmd_dir: str, qualtrics_file_names: list[str], logger: logging.Logger) -> list[dict]:
    """
    Finds all unique names for the qualtrics files. Logs the findings, and returns
    a list of objects containing 'name' and 'source' as the key. Also creates cleaned
    versions of each qualtrics file at the intermediate directory.

    Parameters
    ----------
    input_dir: str
        The full path to the input directory containing all raw qualtrics survey files
    inmd_dir: str
        The intermediate path containing cleaned qualtrics files.
    qualtrics_file_names: list[str]
        The list of file names for all qualtrics surveys. These files should be located at the input directory.
    logger: logging.Logger
        The logger object

    Returns
    -------
    all_qualtrics_rows: list[dict]
        A list of objects with a name and source key. Used to create a dataframe downstream.
    """

    all_qualtrics_rows: list[dict] = []

    for qualtrics_file_name in qualtrics_file_names:
        qualtrics_df = pd.read_csv(os.path.join(input_dir, qualtrics_file_name), header=1)
        logger.info(f"Read {len(qualtrics_df):,} rows from cohort survey")
        qualtrics_df = qualtrics_df.iloc[1:].reset_index(drop=True) # Dropping the metadata row

        first_name_col = [col for col in qualtrics_df.columns if "- First Name" in col][0]
        last_name_col = [col for col in qualtrics_df.columns if "- Last Name" in col][0]
        
        assert "name" not in qualtrics_df.columns

        logger.info(f" - Using {first_name_col}, {last_name_col} for names")

        qualtrics_df["name"] = qualtrics_df[first_name_col].str.strip() + " " + qualtrics_df[last_name_col].str.strip()
        logger.info(f" - Found {qualtrics_df["name"].nunique():,} names in {qualtrics_file_name}\n")
        for name in qualtrics_df["name"].dropna().unique():
            if name:
                all_qualtrics_rows.append({"name": name, "source": qualtrics_file_name})
        qualtrics_df.to_csv(os.path.join(inmd_dir, f"cleaned_{qualtrics_file_name}"), index=False)

    return all_qualtrics_rows


def load_registry_names(registry_fp: str, inmd_dir: str, logger: logging.Logger) -> list[dict]:
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

    registry_basename = os.path.basename(registry_fp)
    registry_basename_no_ext = os.path.splitext(registry_basename)[0]
    
    registry_rows: list[dict] = []
    registry = pd.read_excel(registry_fp, sheet_name="Student Enrollments Section", header=8)

    registry["name"] = registry[["First Name", "Middle Name", "Last Name"]].fillna("")\
        .agg(" ".join, axis=1).str.replace(r"\s+", " ", regex=True).str.strip()

    cleaned_fp = os.path.join(inmd_dir, f"{registry_basename_no_ext}.csv")
    registry.to_csv(cleaned_fp, index=False)
    logger.info(f"Wrote {len(registry):,} rows to {cleaned_fp}")

    for name in registry["name"].unique():
        registry_rows.append({"name" : name, "source" : registry_basename})

    return registry_rows


def create_name_master_file(
    input_dir: str,
    inmd_dir: str,
    output_dir: str,
    registry_fp: str,
    end_of_module_files: list[str], 
    pre_survey_files: list[str], 
    qualtrics_file_names: list[str],
    logger: logging.Logger
) -> None:
    """ 
    Creates an 'all_names.csv' file at the output directory containing all the names found from module, qualtrics, and registry
    files. The sources each name was found in is included, as well as a canvas id if applicable.

    Parameters
    ----------   
    input_dir: str
        The full path to the input directory containing all raw qualtrics survey files.
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
    qualtrics_file_names: list[str]
        The list of file names for all qualtrics surveys. These files should be located at the input directory.
    logger: logging.Logger
        The logger object
    """
    
    all_rows: list[dict] = []

    module_survey_rows = load_module_names(end_of_module_files=end_of_module_files, pre_survey_files=pre_survey_files, logger=logger)
    all_rows += module_survey_rows

    qualtrics_rows = load_qualtrics_names(input_dir=input_dir, inmd_dir=inmd_dir, qualtrics_file_names=qualtrics_file_names, logger=logger)
    all_rows += qualtrics_rows

    registry_rows = load_registry_names(registry_fp=registry_fp, inmd_dir=inmd_dir, logger=logger)
    all_rows += registry_rows

    tracking_df = pd.DataFrame(all_rows)
    logger.info(f"Final tracking df has {len(tracking_df):,} rows")
    os.makedirs(output_dir, exist_ok=True)

    # Create a master_only column if the name is not anywhere else
    #tracking_df["name"] = tracking_df["name"].str.lower()
    tracking_df = tracking_df[tracking_df["name"].str.len() > 5] # removing names like '..' that are impossibly short

    tracking_df = tracking_df.drop_duplicates().sort_values(by=["name", "source"])

    name_sources: pd.Series = tracking_df.groupby("name")["source"].agg(set)
    tracking_df["has_canvas_id_yn"] = tracking_df["canvas_id"].notna().groupby(tracking_df["name"]).transform("any").astype(int)
    tracking_df["not_in_registry_yn"] = tracking_df["name"].map({
        name: (os.path.basename(registry_fp) not in sources) 
        for name, sources in name_sources.items()
    }).astype(int)

    tracking_df.to_csv(os.path.join(output_dir, "all_names.csv"), index=False)
