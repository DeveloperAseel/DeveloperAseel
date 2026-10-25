# Patch Compliance Reporter

A small Python automation tool that reviews patch age from a CSV asset inventory. It applies a configurable maximum age for each asset, highlights overdue or approaching deadlines, and reports records that need date verification. It reads local data only and does not install patches or change asset records.

## Requirements

- Python 3.10 or newer.
- No external packages, database, or network access.

## Run

Download this folder and open a terminal inside it. Run the fictional sample with a fixed date so your output matches the documented example:

```bash
python patch_compliance_reporter.py --as-of 2026-10-25
```

To analyze another CSV with the same columns:

```bash
python patch_compliance_reporter.py "your_assets.csv" --as-of 2026-10-25
```

Omit `--as-of` to use your computer's current local date. Change the due-soon window if needed:

```bash
python patch_compliance_reporter.py "your_assets.csv" --warning-days 10
```

Successful analysis exits with code 0, even when overdue assets exist. Invalid input or an unreadable file exits with code 2.

## CSV format

The header must contain exactly these columns, in any order:

```text
asset_id,hostname,owner,criticality,last_patch_date,max_age_days,active
```

- `asset_id` must be unique.
- `criticality` must be `low`, `medium`, `high`, or `critical`.
- `last_patch_date` must use `YYYY-MM-DD`.
- `max_age_days` must be a whole number of at least 1.
- `active` must be `true` or `false`.

The sample uses fictional assets and departments.

## Classification logic

- `OVERDUE`: active asset age is greater than its configured limit.
- `DUE_SOON`: active asset is within the warning window, including the boundary.
- `COMPLIANT`: active asset has more time remaining than the warning window.
- `REVIEW_DATE`: last patch date is later than the report date.
- `INACTIVE`: asset is excluded from active compliance counts but remains visible.

Age is calculated in whole calendar days as `report date - last patch date`. A patch age equal to the maximum is still compliant; it may be `DUE_SOON` depending on the warning window. Results are sorted by status, then criticality, remaining days, and asset ID so higher-priority review items appear first.

## Sample result

Using October 25, 2026, and the default seven-day warning window:

- 5 assets are read; 4 are active.
- 1 is overdue.
- 1 is due soon.
- 1 is compliant.
- 1 has a future date that requires review.
- 1 is inactive.

## Limitations

The configured limits are fictional examples, not universal patching requirements or proof that a device is secure. The tool evaluates dates in the supplied file; it does not verify whether patches were installed successfully, assess vulnerabilities, group assets by maintenance window, or connect to endpoint-management systems. Organizations should define patch timelines based on their own risk, technology, testing, and operational requirements. Treat real asset inventories as internal information and do not upload them to a public repository.

## Files

- `patch_compliance_reporter.py`: validation, classification, sorting, and terminal report.
- `sample_assets.csv`: fictional input data.
- `README.md`: requirements, operation, logic, and interview points.

## Interview explanation

> I built a Python tool that reviews patch-age compliance from a CSV asset inventory. Each asset has its own maximum patch age, and the tool classifies it as compliant, due soon, overdue, inactive, or requiring date review. I added strict input validation and deterministic sorting so the most urgent findings appear first. The report supports operational review without modifying systems.

## Validation

Executed with Python using the fictional sample. Checks cover all five statuses, exact age and warning boundaries, custom warning periods, duplicate assets, malformed dates, invalid values, reordered headers, empty datasets, missing or extra columns, arbitrary working directories, unchanged inputs, and no output files.

## Reference

- [NIST SP 800-40 Rev. 4: Guide to Enterprise Patch Management Planning](https://csrc.nist.gov/pubs/sp/800/40/r4/final)
