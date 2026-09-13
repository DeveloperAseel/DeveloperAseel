import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = {"campaign", "total_sent", "opened", "clicked", "reported"}


def percentage(value, total):
    return (value / total * 100) if total else 0


def attention_level(click_rate):
    if click_rate >= 15:
        return "High"
    if click_rate >= 5:
        return "Moderate"
    return "Low"


def load_campaigns(file_path):
    campaigns = []

    with file_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing CSV columns: {missing}")

        for row_number, row in enumerate(reader, start=2):
            try:
                campaign = {
                    "name": row["campaign"].strip(),
                    "total_sent": int(row["total_sent"]),
                    "opened": int(row["opened"]),
                    "clicked": int(row["clicked"]),
                    "reported": int(row["reported"]),
                }
            except ValueError as error:
                raise ValueError(f"Invalid number in row {row_number}") from error

            if not campaign["name"]:
                raise ValueError(f"Campaign name is empty in row {row_number}")

            total = campaign["total_sent"]
            results = (campaign["opened"], campaign["clicked"], campaign["reported"])

            if total <= 0 or any(value < 0 or value > total for value in results):
                raise ValueError(f"Invalid campaign totals in row {row_number}")

            campaigns.append(campaign)

    return campaigns


def print_report(campaigns):
    print("\nPhishing Campaign Metrics")
    print("-" * 90)
    print(f"{'Campaign':<28} {'Sent':>7} {'Open %':>9} {'Click %':>9} {'Report %':>10} {'Attention':>12}")
    print("-" * 90)

    total_sent = 0
    total_opened = 0
    total_clicked = 0
    total_reported = 0

    for campaign in campaigns:
        sent = campaign["total_sent"]
        open_rate = percentage(campaign["opened"], sent)
        click_rate = percentage(campaign["clicked"], sent)
        report_rate = percentage(campaign["reported"], sent)

        print(
            f"{campaign['name'][:28]:<28} {sent:>7} {open_rate:>8.1f}% "
            f"{click_rate:>8.1f}% {report_rate:>9.1f}% {attention_level(click_rate):>12}"
        )

        total_sent += sent
        total_opened += campaign["opened"]
        total_clicked += campaign["clicked"]
        total_reported += campaign["reported"]

    print("-" * 90)
    print(f"Total emails sent: {total_sent}")
    print(f"Overall open rate: {percentage(total_opened, total_sent):.1f}%")
    print(f"Overall click rate: {percentage(total_clicked, total_sent):.1f}%")
    print(f"Overall report rate: {percentage(total_reported, total_sent):.1f}%")


def main():
    default_file = Path(__file__).with_name("sample_campaigns.csv")
    file_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_file

    try:
        campaigns = load_campaigns(file_path)
        if not campaigns:
            print("The CSV file contains no campaigns.")
            return
        print_report(campaigns)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
