# IT Audit Findings Tracker

A small SQL database for recording IT audits and tracking findings until remediation is completed.

## Features

- Stores audit name, department, date, and status
- Records findings with severity, owner, due date, and remediation status
- Links every finding to its audit using a foreign key
- Lists open findings in priority order
- Identifies overdue findings
- Calculates finding counts and closure percentages

## Files

- `database.sql` - tables and sample data
- `queries.sql` - useful audit and remediation reports
- `README.md` - setup and project explanation

## Requirements

- SQLite 3 or a SQLite database application

## Run the project

Open a terminal in this folder:

```bash
sqlite3 audit_tracker.db
```

Then run these commands inside SQLite:

```sql
.read database.sql
.headers on
.mode column
.read queries.sql
```

You can run `database.sql` again whenever you want to reset the sample database.

## Database design

The `audits` table stores each review. The `findings` table stores issues discovered during an audit. The `audit_id` foreign key creates a one-to-many relationship: one audit can have multiple findings.

`CHECK` constraints limit status and severity values, while `ON DELETE CASCADE` removes related findings if an audit is deleted.

## Interview explanation

I designed a small relational database for tracking IT audit findings. It stores audits and their findings in separate tables connected through a foreign key. The reporting queries help reviewers prioritize unresolved findings, identify overdue actions, and measure closure progress. The project demonstrates table design, primary and foreign keys, constraints, joins, aggregation, and conditional SQL logic in a practical IT audit scenario.

## Reference

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
