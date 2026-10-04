import csv
import re
import sys
from collections import Counter
from pathlib import Path


EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)


def load_csv(file_path):
    with file_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("The CSV file has no header row.")

        fieldnames = [name.strip() for name in reader.fieldnames]
        rows = []

        for row in reader:
            cleaned_row = {
                field: (row.get(original_name) or "").strip()
                for field, original_name in zip(fieldnames, reader.fieldnames)
            }
            rows.append(cleaned_row)

    return fieldnames, rows


def normalized_row(row, fieldnames):
    return tuple(row[field].casefold() for field in fieldnames)


def analyze_data(fieldnames, rows):
    missing_by_column = {
        field: sum(1 for row in rows if not row[field])
        for field in fieldnames
    }

    row_counts = Counter(normalized_row(row, fieldnames) for row in rows)
    duplicate_rows = sum(count - 1 for count in row_counts.values() if count > 1)

    email_columns = [field for field in fieldnames if "email" in field.casefold()]
    invalid_emails = []

    for row_number, row in enumerate(rows, start=2):
        for column in email_columns:
            value = row[column]
            if value and not EMAIL_PATTERN.fullmatch(value):
                invalid_emails.append((row_number, column, value))

    total_cells = len(rows) * len(fieldnames)
    missing_cells = sum(missing_by_column.values())
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells else 0
    complete_rows = sum(1 for row in rows if all(row[field] for field in fieldnames))

    return {
        "missing_by_column": missing_by_column,
        "duplicate_rows": duplicate_rows,
        "invalid_emails": invalid_emails,
        "completeness": completeness,
        "complete_rows": complete_rows,
    }


def print_report(file_path, fieldnames, rows, results):
    print("\n=== CSV Data Quality Report ===")
    print(f"File: {file_path.name}")
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(fieldnames)}")
    print(f"Complete rows: {results['complete_rows']}")
    print(f"Duplicate rows: {results['duplicate_rows']}")
    print(f"Data completeness: {results['completeness']:.1f}%")

    print("\nMissing values by column:")
    for column, count in results["missing_by_column"].items():
        print(f"- {column}: {count}")

    print("\nInvalid email values:")
    if not results["invalid_emails"]:
        print("- None found")
    else:
        for row_number, column, value in results["invalid_emails"]:
            print(f"- Row {row_number}, {column}: {value}")


def main():
    default_file = Path(__file__).with_name("sample_companies.csv")
    file_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_file

    try:
        fieldnames, rows = load_csv(file_path)
        results = analyze_data(fieldnames, rows)
        print_report(file_path, fieldnames, rows, results)
    except (FileNotFoundError, PermissionError, ValueError, csv.Error) as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
