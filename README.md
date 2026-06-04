# Absolute-Multidimensional-Sustainability-Sssessment-AMSA-_graphical-representation
This repository contains the Python code and Excel input template used to generate the figures reported in the manuscript "Towards Absolute Multidimensional Sustainability Integrating Environmental and Social Planetary Boundaries".

## Overview

The repository was developed to support transparency and reproducibility of the graphical outputs presented in the manuscript. It includes Python scripts for figure generation and an Excel template (`data_empty.xlsx`) that must be completed before running the code.

## Repository structure

- `data_empty.xlsx` – Excel template to be populated with input data
- `src/` – Python scripts used to generate the figures
- `output/` – Folder where the generated figures are saved
- `requirements.txt` – Python dependencies

## Input data

The Excel template is provided as `data_empty.xlsx` and contains two sheets:

- `AESA` – input sheet for the Absolute Environmental Sustainability Assessment
- `ASSA` – input sheet for the Absolute Social Sustainability Assessment

Before running the code, users should open `data_empty.xlsx` and complete the relevant columns in the appropriate sheet. Sheet names, column headers, and the overall file structure should not be modified, as the Python code expects this exact layout.

## Requirements

The code was developed and tested in Python 3.11.

Required Python packages include:
- pandas
- numpy
- matplotlib
- openpyxl

Dependencies can be installed with:

```bash
pip install -r requirements.txt
```

## How to run

After completing the input data in `data_empty.xlsx`, run the main Python script from the project directory:

```bash
python src/generate_figures.py
```

The script reads the Excel file and generates the figures automatically.

## Outputs

Depending on the script settings, outputs may be exported in one or more of the following formats:
- PNG
- PDF
- SVG

## Reproducibility note

This repository is intended to enable reproduction of the graphical outputs associated with the manuscript. To ensure successful execution, input data should be entered in the Excel template using the expected structure and units.

## License

This repository is provided for academic and research purposes only.
