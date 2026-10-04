# CSV Data Quality Checker

A small Python tool that checks CSV files for common data quality problems before the data is used in reports, databases, or other applications.

## Features

- Counts rows and columns
- Finds missing values in every column
- Detects duplicate rows
- Checks values in email columns
- Calculates the overall data completeness percentage
- Uses only Python's standard library

## Files

- `data_quality_checker.py` - the complete checker
- `sample_companies.csv` - fictional sample data using reserved example domains
- `README.md` - setup and project explanation

## Requirements

- Python 3.9 or later

No external packages are required.

## Run the project

Open a terminal in this folder and run:

```bash
python data_quality_checker.py
```

To check another CSV file:

```bash
python data_quality_checker.py your_file.csv
```

Columns containing the word `email` are automatically checked for email format.

## How it works

The program reads the file with `csv.DictReader`, removes extra spaces, and analyzes every row. A normalized version of each row is used to identify duplicates without being affected by letter case. Empty cells are counted per column, and a regular expression checks non-empty email values.

The completeness percentage is calculated as:

```text
non-empty cells / total cells x 100
```

## Interview explanation

I built a Python tool that performs basic data quality checks on CSV files. It identifies missing values, duplicate rows, and incorrectly formatted email addresses, then calculates a completeness score. The project demonstrates file handling, dictionaries, collections, validation, regular expressions, and practical data preparation.

## Reference

- [Python documentation: CSV File Reading and Writing](https://docs.python.org/3/library/csv.html)
