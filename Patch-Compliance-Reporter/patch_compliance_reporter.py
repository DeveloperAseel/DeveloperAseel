"""Report patch-age compliance from a local CSV asset inventory."""

import argparse
import csv
from datetime import date
from pathlib import Path
import sys


REQUIRED_COLUMNS = {
    "asset_id", "hostname", "owner", "criticality",
    "last_patch_date", "max_age_days", "active"
}
CRITICALITIES = {"low", "medium", "high", "critical"}


def nonempty(row, field, line):
    value = (row.get(field) or "").strip()
    if not value:
        raise ValueError(f"line {line}: '{field}' cannot be empty")
    return value


def read_assets(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")
        headers = {name.strip() for name in reader.fieldnames if name is not None}
        if headers != REQUIRED_COLUMNS:
            missing = sorted(REQUIRED_COLUMNS - headers)
            extra = sorted(headers - REQUIRED_COLUMNS)
            raise ValueError(f"CSV columns do not match; missing={missing}, extra={extra}")
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        assets = []
        seen_ids = set()
        for line, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"line {line}: column count does not match the header")
            asset_id = nonempty(row, "asset_id", line)
            if asset_id in seen_ids:
                raise ValueError(f"line {line}: duplicate asset_id '{asset_id}'")
            seen_ids.add(asset_id)
            criticality = nonempty(row, "criticality", line).lower()
            if criticality not in CRITICALITIES:
                raise ValueError(f"line {line}: invalid criticality '{criticality}'")
            active_text = nonempty(row, "active", line).lower()
            if active_text not in {"true", "false"}:
                raise ValueError(f"line {line}: active must be true or false")
            try:
                patched = date.fromisoformat(nonempty(row, "last_patch_date", line))
            except ValueError:
                raise ValueError(f"line {line}: last_patch_date must be YYYY-MM-DD") from None
            try:
                max_age = int(nonempty(row, "max_age_days", line))
            except ValueError:
                raise ValueError(f"line {line}: max_age_days must be a whole number") from None
            if max_age < 1:
                raise ValueError(f"line {line}: max_age_days must be at least 1")
            assets.append({
                "asset_id": asset_id,
                "hostname": nonempty(row, "hostname", line),
                "owner": nonempty(row, "owner", line),
                "criticality": criticality,
                "last_patch_date": patched,
                "max_age_days": max_age,
                "active": active_text == "true",
            })
    return assets


def evaluate(asset, as_of, warning_days):
    age = (as_of - asset["last_patch_date"]).days
    remaining = asset["max_age_days"] - age
    if not asset["active"]:
        status = "INACTIVE"
    elif age < 0:
        status = "REVIEW_DATE"
    elif remaining < 0:
        status = "OVERDUE"
    elif remaining <= warning_days:
        status = "DUE_SOON"
    else:
        status = "COMPLIANT"
    return {**asset, "age_days": age, "days_remaining": remaining, "status": status}


def build_report(assets, as_of, warning_days):
    results = [evaluate(asset, as_of, warning_days) for asset in assets]
    order = {"OVERDUE": 0, "REVIEW_DATE": 1, "DUE_SOON": 2,
             "COMPLIANT": 3, "INACTIVE": 4}
    results.sort(key=lambda item: (
        order[item["status"]],
        {"critical": 0, "high": 1, "medium": 2, "low": 3}[item["criticality"]],
        item["days_remaining"], item["asset_id"]
    ))
    counts = {status: 0 for status in order}
    for result in results:
        counts[result["status"]] += 1
    return results, counts


def print_report(results, counts, as_of, warning_days):
    print("PATCH COMPLIANCE REPORT")
    print(f"As of: {as_of} | Due-soon window: {warning_days} days")
    print(f"Assets: {len(results)} | Active: {len(results) - counts['INACTIVE']}")
    print(" | ".join(f"{name}: {counts[name]}" for name in
                     ("OVERDUE", "DUE_SOON", "COMPLIANT", "REVIEW_DATE", "INACTIVE")))
    print()
    for item in results:
        detail = "inactive asset excluded from compliance"
        if item["status"] == "REVIEW_DATE":
            detail = "patch date is after the report date"
        elif item["active"]:
            detail = (f"{abs(item['days_remaining'])} days overdue" if item["days_remaining"] < 0
                      else f"{item['days_remaining']} days remaining")
        print(f"{item['status']:11} | {item['asset_id']} | {item['hostname']} | "
              f"{item['criticality'].upper()} | owner={item['owner']}")
        print(f"  last_patch={item['last_patch_date']} | age={item['age_days']} days | "
              f"limit={item['max_age_days']} days | {detail}")
    print("\nReporting only: no assets or patch settings were changed.")


def main():
    parser = argparse.ArgumentParser(description="Report patch-age compliance from CSV data.")
    parser.add_argument("csv_file", nargs="?", type=Path,
                        default=Path(__file__).with_name("sample_assets.csv"))
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(),
                        metavar="YYYY-MM-DD", help="report date (default: today)")
    parser.add_argument("--warning-days", type=int, default=7,
                        help="due-soon window, including the boundary (default: 7)")
    args = parser.parse_args()
    if args.warning_days < 0:
        parser.error("--warning-days must be 0 or greater")
    try:
        assets = read_assets(args.csv_file)
        results, counts = build_report(assets, args.as_of, args.warning_days)
        print_report(results, counts, args.as_of, args.warning_days)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
