# Phishing Campaign Metrics Analyzer

A small Python program that reads phishing simulation results from a CSV file and calculates useful awareness metrics for each campaign.

## Features

- Calculates open, click, and report rates
- Compares multiple phishing campaigns
- Displays combined campaign results
- Validates missing columns and incorrect values
- Uses only Python's standard library

The program assigns an attention level based on the click rate:

- Low: below 5%
- Moderate: 5% to 14.9%
- High: 15% or more

These levels are simple project thresholds and can be changed to match an organization's awareness targets.

## Files

- `phishing_metrics.py` - reads the data and prints the report
- `sample_campaigns.csv` - sample campaign results
- `README.md` - setup and project explanation

## Requirements

- Python 3.9 or later

No external packages are required.

## Run the project

Open a terminal in this folder and run:

```bash
python phishing_metrics.py
```

To analyze another CSV file:

```bash
python phishing_metrics.py your_campaigns.csv
```

The CSV file must contain these columns:

```text
campaign,total_sent,opened,clicked,reported
```

## How it works

The program uses `csv.DictReader` to read each campaign. It checks that the required columns and values are valid, calculates each percentage, and prints a formatted comparison table. It also combines all rows to calculate the overall rates.

## Interview explanation

I built a Python tool that analyzes phishing simulation results. It reads campaign data from a CSV file and calculates open, click, and report rates for each campaign and for all campaigns combined. I included input validation to catch incomplete or incorrect data. The project demonstrates Python functions, file handling, dictionaries, calculations, and a practical cybersecurity awareness use case.

## Reference

- [CISA: Recognize and Report Phishing](https://www.cisa.gov/secure-our-world/recognize-and-report-phishing)
