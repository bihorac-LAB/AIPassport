import logging
import sys

import os

from .tools.discovery import discover_input_files
from .load_names import create_name_master_file
from .create_survey_variables import create_survey_variables
from .create_reflection_journal_results import create_reflection_journal_results
from .create_personalized_reports import create_personalized_reports
from .create_master_workbook import create_master_workbook

logging.basicConfig(
    level=logging.INFO, 
    format="[%(levelname)s]: %(message)s",
    stream=sys.stdout
)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--input", type=str)
    args=parser.parse_args()

    input_dir = args.input

    inmd_dir = os.path.join(input_dir, "intermediate")
    output_dir = os.path.join(input_dir, "output")

    for dir in [inmd_dir, output_dir]:
        os.makedirs(dir, exist_ok=True)

    logger = logging.getLogger(__name__)

    logger.info(f"Running on directories:\n\tINPUT: {input_dir}\n\tINTERMEDIATE: {inmd_dir}\n\tOUTPUT: {output_dir}")

    discovered_inputs = discover_input_files(input_dir=input_dir, logger=logger)

    end_of_module_files = discovered_inputs.end_of_module_files
    pre_survey_files = discovered_inputs.pre_survey_files
    qualtrics_files = discovered_inputs.qualtrics_files
    registry_file = discovered_inputs.registry_file

    if not pre_survey_files:
        raise ValueError(f"No module pre-survey files discovered under input directory: {input_dir}")

    logger.info(
        "Found %s end-of-module files, %s pre-survey files, and %s Qualtrics files",
        len(end_of_module_files),
        len(pre_survey_files),
        len(qualtrics_files),
    )

    # Creates a file containing the names of everyone found from all sources, and which sources they were found in
    create_name_master_file(
        inmd_dir=inmd_dir, 
        output_dir=output_dir, 
        registry_fp=registry_file,
        end_of_module_files=end_of_module_files, 
        pre_survey_files=pre_survey_files, 
        qualtrics_files=qualtrics_files,
        logger=logger
    )

    # 2. Obtain reflection journal results. Can return None if there is an issue with Canvas API
    reflection_journal_fp, reflection_journal_keys_fp = create_reflection_journal_results(inmd_dir=inmd_dir, logger=logger)
    
    # 3. Create the latest, most updated survey variables using all module pre/post surveys.
    final_data_fp, microskill_fp = create_survey_variables(
        pre_survey_files=pre_survey_files, end_of_module_files=end_of_module_files, 
        reflection_journal_fp=reflection_journal_fp,
        output_dir=output_dir, logger=logger
    )
    
    # 4. Create a personalized report document for each student that took at least one module survey.
    create_personalized_reports(final_data_fp=final_data_fp, microskill_fp=microskill_fp, output_dir=output_dir, logger=logger)

    # 5. Build a copy of the master workbook and auto-populate Master_Data + Microskill_Key.
    create_master_workbook(
        input_dir=input_dir,
        output_dir=output_dir,
        final_data_fp=final_data_fp,
        microskill_fp=microskill_fp,
        reflection_journal_keys_fp=reflection_journal_keys_fp, 
        discovered_inputs=discovered_inputs,
        logger=logger,
    )
