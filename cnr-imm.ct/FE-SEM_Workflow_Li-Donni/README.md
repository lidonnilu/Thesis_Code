# FE-SEM Data Processing Pipeline

This repository describe the pipeline to extract, transform and combine data from Excel files, TIFF images metadata, and ultimately preparing data for NeXus format generation. It includes the following scripts:

- `excel_to_json.py`: Converts Excel sheets into structured JSON files.
- `combine_json.py`: Merges sample and experiment data into unified JSON files.
- `extract_metadata.py`: Extracts and structures metadata from SEM TIFF image files.
- `generate_nexus.ipynb`: (Notebook) Final processing for Nexus file generation (details inside notebook).

The output and input files in this directories contains mock\test data, just for the purpose of showing how the workflow performs.

## Directory Structure

```
/input_files/
    file_name.xlsx
    /tiff_images/
      *.tiff
/output_files/
    experiment.json
    samples.json
    original_samples.json
    Test.json
    Test.nxs
    JSON_metadata/
      *.json
/scripts/
```

---

## Script Descriptions

### 1. `excel_to_json.py`

**Purpose**: Converts experimental data from an Excel file into three structured JSON files.

**Input**:
- Excel file with sheets named `SAMPLES`, `EXPERIMENT`, and `ORIGINAL POWDERS SAMPLE`.

**Output**:
- `experiment.json`: Contains experiment metadata with instrument info.
- `samples.json`: Contains individual sample information, which has been characterized via SEM.
- `original_samples.json`: Contains raw powder sample data.

**Instructions**:
Update:
```python
file_path = "path\\to\\file_name.xlsx"
output_folder = "path\\to\\output_folder"
```

Run:
```bash
python excel_to_json.py
```

---

### 2. `combine_json.py`

**Purpose**: Combines `samples.json` and `experiment.json` into per-sample files that group experiment and sample data.

**Input**:
- `experiment.json`
- `samples.json`

**Output**:
- One combined JSON per sample, named `<sample_name>.json`.

**Instructions**:
Update:
```python
EXPERIMENT_FILE = "path\\to\\experiment.json"
SAMPLES_FILE = "path\\to\\samples.json"
OUTPUT_DIR = "path\\to\\output_folder"
```

Run:
```bash
python combine_json.py
```

---

### 3. `extract_metadata.py`

**Purpose**: Extracts and processes TIFF metadata coming from Carl Zeiss FE-SEM Supra 35, especially custom `CZ_SEM` tags, into JSON format.

**Input**:
- Folder containing `.tif` or `.tiff` files.

**Output**:
- JSON metadata files saved in a subfolder `/JSON metadata/`.

**Instructions**:
Update:
```python
INPUT_FOLDER = "path\\to\\tiff_files"
```

Run:
```bash
python extract_metadata.py
```

---

### 4. `generate_nexus.ipynb`

**Purpose**: Processes JSON metadata and combined sample files into the final Nexus format.

**Instructions**:
- Open the notebook with Jupyter.
- Follow the steps sequentially to load, parse, and convert the data.

---

## Workflow Summary

1. **Convert Excel to JSON**  
   ➤ `excel_to_json.py`

2. **Merge Experiment and Sample Data**  
   ➤ `combine_json.py`

3. **Extract Image Metadata**  
   ➤ `extract_metadata.py`

4. **Generate Nexus Format**  
   ➤ `generate_nexus.ipynb`

---

## Requirements

Install required packages:
```bash
pip install pandas tifffile numpy h5py 
```

---

## Notes

- Ensure all paths are correctly configured before execution.
- TIFF files should contain custom tags for full metadata extraction.
- The instrument metadata is hardcoded into the `excel_to_json.py` and can be adjusted as needed.

---

## License

Check the file LICENSE
