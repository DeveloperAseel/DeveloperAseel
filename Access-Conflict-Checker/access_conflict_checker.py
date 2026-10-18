"""Find explicitly configured separation-of-duties conflicts in local access data."""

import argparse
import json
from pathlib import Path
import sqlite3
import sys


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE users (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);
CREATE TABLE roles (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
);
CREATE TABLE user_roles (
    user_id TEXT NOT NULL REFERENCES users(id),
    role_id TEXT NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);
CREATE TABLE conflicts (
    role_a TEXT NOT NULL REFERENCES roles(id),
    role_b TEXT NOT NULL REFERENCES roles(id),
    reason TEXT NOT NULL,
    PRIMARY KEY (role_a, role_b),
    CHECK (role_a < role_b)
);
"""

FINDINGS_SQL = """
SELECT u.id AS user_id, u.name, u.active,
       ra.name AS role_a, rb.name AS role_b, c.reason
FROM users u
JOIN user_roles a ON a.user_id = u.id
JOIN user_roles b ON b.user_id = u.id
JOIN conflicts c ON c.role_a = a.role_id AND c.role_b = b.role_id
JOIN roles ra ON ra.id = a.role_id
JOIN roles rb ON rb.id = b.role_id
WHERE u.active = 1 OR ? = 1
ORDER BY u.id, c.role_a, c.role_b
"""


def text(row, field):
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' must be a nonempty string.")
    return value.strip()


def rows(data, field):
    value = data.get(field)
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError(f"'{field}' must be an array of objects.")
    return value


def load_database(connection, data):
    if not isinstance(data, dict):
        raise ValueError("The JSON root must be an object.")
    users, roles, assignments, rules = (
        rows(data, key) for key in ("users", "roles", "assignments", "conflicts")
    )
    connection.executescript(SCHEMA)
    with connection:
        for user in users:
            if type(user.get("active")) is not bool:
                raise ValueError("Each user's 'active' value must be true or false.")
            connection.execute("INSERT INTO users VALUES (?, ?, ?)",
                               (text(user, "id"), text(user, "name"), int(user["active"])))
        for role in roles:
            connection.execute("INSERT INTO roles VALUES (?, ?)",
                               (text(role, "id"), text(role, "name")))
        for assignment in assignments:
            connection.execute("INSERT INTO user_roles VALUES (?, ?)",
                               (text(assignment, "user_id"), text(assignment, "role_id")))
        for rule in rules:
            role_a, role_b = sorted((text(rule, "role_a"), text(rule, "role_b")))
            if role_a == role_b:
                raise ValueError("A conflict rule must contain two different role IDs.")
            connection.execute("INSERT INTO conflicts VALUES (?, ?, ?)",
                               (role_a, role_b, text(rule, "reason")))


def check_access(data, include_inactive=False):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    try:
        load_database(connection, data)
        findings = [dict(row) for row in connection.execute(FINDINGS_SQL, (int(include_inactive),))]
        users_checked = connection.execute(
            "SELECT COUNT(*) FROM users WHERE active = 1 OR ? = 1", (int(include_inactive),)
        ).fetchone()[0]
        return {"findings": findings, "users_checked": users_checked,
                "users_flagged": len({row["user_id"] for row in findings}),
                "rules_checked": connection.execute("SELECT COUNT(*) FROM conflicts").fetchone()[0]}
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description="Review conflicting role assignments using SQLite.")
    parser.add_argument("input", nargs="?", type=Path,
                        default=Path(__file__).with_name("sample_access.json"), help="Local access JSON file")
    parser.add_argument("--include-inactive", action="store_true", help="Also review inactive users")
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8-sig") as file:
            data = json.load(file)
        result = check_access(data, args.include_inactive)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        print("Check JSON fields, duplicate IDs/assignments/rules and referenced user/role IDs.", file=sys.stderr)
        return 2
    print("ACCESS CONFLICT REVIEW")
    print("Scope:", "all users" if args.include_inactive else "active users only")
    print(f"Users checked: {result['users_checked']} | Rules: {result['rules_checked']}")
    print(f"Users flagged: {result['users_flagged']} | Conflicting role pairs: {len(result['findings'])}\n")
    for row in result["findings"]:
        status = "ACTIVE" if row["active"] else "INACTIVE"
        print(f"{row['user_id']} | {row['name']} | {status}")
        print(f"  {row['role_a']} + {row['role_b']}")
        print(f"  Review reason: {row['reason']}\n")
    if not result["findings"]:
        print("No configured role-pair conflicts found in the selected scope.")
    print("Review candidates only. No permissions were changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
