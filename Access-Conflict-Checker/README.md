# Access Conflict Checker

A small Python and SQLite tool for reviewing separation-of-duties role conflicts. It compares users' assigned roles against explicit conflicting-role pairs and reports candidates for review. It does not change access rights or connect to any live system.

## Requirements

- Python 3.10 or newer with its `sqlite3` module (included in standard Python distributions).
- No external packages or network access.

## Run

Download this folder and open a terminal inside it:

```bash
python access_conflict_checker.py
```

This reads `sample_access.json` next to the script, regardless of your working directory. All sample identities and policy rules are fictional.

To check a different local JSON file with the same structure:

```bash
python access_conflict_checker.py "your_access.json"
```

By default, only users with `active: true` are reviewed. To include inactive users:

```bash
python access_conflict_checker.py --include-inactive
```

Successful analysis exits with code 0, including when conflicts are found. Invalid input or a file/database error exits with code 2.

## How it works

1. Read the four required JSON arrays: `users`, `roles`, `assignments` and `conflicts`.
2. Create an in-memory SQLite database with four corresponding tables. Primary keys prevent duplicate records; foreign keys reject unknown user/role references.
3. Insert all values using SQL parameters rather than string interpolation.
4. Normalize each conflict pair by sorting its two role IDs. Reversing a rule therefore does not change its meaning; duplicate/reversed rules are rejected.
5. Join the assignment table to itself for each user, then join the configured conflict rules and role names. The scope filter excludes inactive users unless requested.
6. Print the affected user, conflicting role names, rule reason and summary counts. Close the temporary database after analysis.

The tool validates nonempty strings, boolean active flags, duplicate IDs and assignments, distinct roles in each rule and references to known users/roles. IDs are case-sensitive and surrounding whitespace is removed. Empty arrays are allowed, but all four arrays must exist. Inactive users still require valid input records.

## Sample results

| Scope | Users checked | Users flagged | Conflicting pairs |
| --- | ---: | ---: | ---: |
| Active users (default) | 3 | 2 | 2 |
| Include inactive users | 4 | 3 | 3 |

The example flags combining payment creation with payment approval and vendor creation with vendor approval. A user assigned only the payment-approval role is not flagged.

## Limitations

These are example rules, not universal prohibitions or a certification of compliance. Your organization must define the actual conflicting duties and any exceptions. The program checks direct role assignments only, not inherited roles, transaction-level actions, cross-system permissions or compensating controls. No findings means only that no configured pair was found in the selected data and scope. Treat real access exports as internal information; do not upload them to a public repository.

## Files

- `access_conflict_checker.py`: JSON validation, database schema, SQL joins and report.
- `sample_access.json`: fictional users, roles, assignments and rules.
- `README.md`: setup, behavior and interview points.

## Interview explanation

> I built a small access-review tool using Python and SQLite. It loads users and role assignments, applies configured separation-of-duties rules and reports conflicting role pairs. I used a self-join to identify role combinations, foreign keys to validate relationships and parameterized inserts to keep data separate from SQL. The results support a review decision rather than automatically revoking access.

## Validation

Executed against the fictional sample in both scopes. Additional checks cover no-conflict input, multiple rules affecting one user, reversed pairs, duplicate records, unknown references, invalid active flags, missing fields and names containing SQL-like text. The input remains unchanged and no database file is created.

## References

- [NIST: Separation of Duty glossary](https://csrc.nist.gov/glossary/term/separation_of_duty)
- [Python: sqlite3 and parameterized queries](https://docs.python.org/3/library/sqlite3.html)
