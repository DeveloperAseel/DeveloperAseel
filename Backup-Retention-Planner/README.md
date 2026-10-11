# Backup Retention Planner

A small Java command-line tool for reviewing backup-file retention. It reads file metadata, protects the newest files and identifies older files for manual review. It never deletes or modifies files.

## Requirements

- JDK 17 or newer, with `java` available in your terminal.
- No external packages, database or network access.

## Run

Download this folder and open a terminal inside it. Try the built-in fictional example:

```bash
java BackupRetentionPlanner.java --demo
```

To inspect a local folder:

```bash
java BackupRetentionPlanner.java "C:/Users/YourName/Backups"
```

On macOS/Linux, replace the path with your folder, for example `"/home/yourname/backups"`.

Optional arguments are positional, in this order:

```bash
java BackupRetentionPlanner.java "C:/Users/YourName/Backups" 30 3 2026-10-11
```

This keeps files whose UTC age is at most 30 days, protects the three newest non-future files regardless of age, and evaluates dates as of October 11, 2026. Omit the date to use today's UTC date. This configurable policy is an educational example, not an organization's mandated retention policy.

Single-file source mode compiles and runs the program in memory. You can also use the conventional commands:

```bash
javac BackupRetentionPlanner.java
java BackupRetentionPlanner --demo
```

## How it works

1. Inspect immediate regular files ending in `.zip` or `.bak`, case-insensitively. Subfolders, symbolic links and other extensions are ignored. A symbolic-link input folder is rejected.
2. Read last-modified timestamp and byte size; do not open archive contents.
3. Sort newest first by exact timestamp, then filename to break ties.
4. Convert timestamps to UTC calendar dates and calculate whole calendar-day age.
5. Keep the newest requested number of non-future files **or** any file within the age limit. Flag the remainder as `REVIEW`.
6. Keep files with future UTC dates as `KEEP_CHECK_DATE`; exclude them from the protected-file count so an incorrect timestamp does not displace older files.
7. Print counts and the combined size of files marked for review, in MiB.

The age boundary is inclusive: age 30 is retained with a 30-day setting. A notice appears when fewer non-future files exist than the requested minimum. An unreadable matching file causes the scan to fail rather than print a partial plan.

## Demo result

The demo has five fictional 10 MiB files aged 1, 7, 45, 46 and 70 days. With defaults:

- The three newest are retained, including the 45-day file.
- Two older files are marked for review.
- Review size is 20 MiB.

## Limits

Use a folder containing copies of the **same backup set**. The tool does not group different systems or backup chains: a database's incremental backup may depend on other files. File modification dates can change when copying files. Extensions do not prove a file is a valid or restorable backup. Review the report alongside your actual backup policy, dependencies and restore checks before acting on it. The program performs no deletion and predicts no guaranteed recoverable storage.

## Files

- `BackupRetentionPlanner.java`: scanning, retention decisions and demo.
- `README.md`: setup and explanation.

## Interview points

> I built a Java tool that reviews backup files using a configurable age limit and a minimum protected-file count. It sorts file metadata and keeps the newest files even if they are older than the age limit. I handled future timestamps, ignored symbolic links and reported review candidates without changing files. The project demonstrates Java NIO, records, collections, comparators, date calculations and input validation.

## Validation

Executed with Java 17 using source-file mode. Checks cover the demo, the inclusive age boundary, minimum-copy protection, future dates, filename filtering, symbolic links, invalid arguments, an empty directory and unchanged file contents/timestamps.

## References

- [Oracle: Java single-file source mode](https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html#using-source-file-mode-to-launch-single-file-source-code-programs)
- [Oracle: Files API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html)
