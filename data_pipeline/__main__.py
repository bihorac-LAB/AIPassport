import logging
import sys

import os
import glob

from .load_names import create_name_master_file
from .create_survey_variables import create_survey_variables
from .create_personalized_reports import create_personalized_reports

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

    # 1. Obtain the names of all users that took any pre/post module surveys, and any qualtrics survey.
    end_of_module_files = sorted(glob.glob(os.path.join(input_dir, "Module*End-of-Module*.csv"))) # 22 users
    pre_survey_files = sorted(glob.glob(os.path.join(input_dir, "Module*Pre-Survey*.csv"))) # 33 users
    logger.info(f"Found {len(end_of_module_files):,} end of module files and {len(pre_survey_files):,} pre survey files")

    # assert len(end_of_module_files) == 6
    # assert len(pre_survey_files) == 6

    # These are the miscellaneous input survey files, and they are very messy
    qualtrics_file_names = [
        "AI Passport Cohort Survey_April 8, 2026_14.04.csv",  # 42 names
        "AI Passport Learner Needs Survey_April 8, 2026_14.05.csv",  # 50 names
        "AI Passport SNAIL Self-Assessment Informal Tool_April 8, 2026_14.05.csv" # 47 names
    ]

    # sheet name is 'Student Enrollments Section'
    registry_file = os.path.join(input_dir, "AIP_Sp 26_StudentEnrollment.xls")

    # Creates a file containing the names of everyone found from all sources, and which sources they were found in
    create_name_master_file(
        input_dir=input_dir, 
        inmd_dir=inmd_dir, 
        output_dir=output_dir, 
        registry_fp=registry_file,
        end_of_module_files=end_of_module_files, 
        pre_survey_files=pre_survey_files, 
        qualtrics_file_names=qualtrics_file_names, 
        logger=logger
    )


    # 2. Create the latest, most updated survey variables using all module pre/post surveys.
    final_data_fp, microskill_fp = create_survey_variables(pre_survey_files=pre_survey_files, end_of_module_files=end_of_module_files, output_dir=output_dir, logger=logger)
    
    # 3. Create a personalized report document for each student that took at least one module survey.
    create_personalized_reports(final_data_fp=final_data_fp, microskill_fp=microskill_fp, output_dir=output_dir, logger=logger)
