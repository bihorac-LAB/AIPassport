
### How to Run

1. Download all qualtrics, pre survey, post survey, and registry data locally. Save it to a single input directory

2. Create a virtual environment and install packages from requirements.txt

```bash
python -m venv venv
Venv/Scripts/Activate # if you are on linux, do `source venv/bin/activate` instead
pip install -r requirements.txt
```
3. Execute the following command with the correct path:

```bash
python -m data_pipeline --input "path_to_raw_input_folder"
```

### Notes

- The pipeline discovers module surveys, Qualtrics exports, the enrollment workbook, and the optional combined survey workbook automatically.
- It creates an auto-filled workbook copy in `<input>/output/` named like:
	- `*_Master_Data_AUTOFILLED.xlsx`
- It also writes matching/mapping audits to help review identity resolution decisions:
	- `name_match_audit.csv`
	- `qualtrics_column_mapping.csv`

