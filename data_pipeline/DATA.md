
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

