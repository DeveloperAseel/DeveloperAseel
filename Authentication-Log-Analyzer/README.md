# Authentication Log Analyzer

A small Java command-line tool that reviews local authentication events for two patterns: repeated failures for the same username and source, and a successful login after the failure threshold. It produces review indicators only and does not connect to accounts or change systems.

## Requirements

- JDK 17 or newer with `java` available in the terminal.
- No external packages, database, or network access.

## Run

Download this folder and open a terminal inside it. Run the fictional sample:

```bash
java AuthenticationLogAnalyzer.java sample_auth.log
```

The default rule is at least five failures within an inclusive ten-minute window. To use a different local file, threshold, and window:

```bash
java AuthenticationLogAnalyzer.java your_auth.log 4 15
```

The arguments mean: log file, failure threshold, and window length in minutes. The threshold must be at least 2 and the window at least 1 minute.

Single-file source mode compiles and runs the program in memory. You can also compile it conventionally:

```bash
javac AuthenticationLogAnalyzer.java
java AuthenticationLogAnalyzer sample_auth.log
```

## Input format

The first line must be exactly:

```text
timestamp|username|source_ip|result
```

Each following nonblank line contains four pipe-separated fields. Timestamps must be ISO-8601 UTC instants, and results must be `SUCCESS` or `FAILURE`. Example:

```text
2026-11-01T06:00:00Z|demo.user|192.0.2.10|FAILURE
```

The included sample uses fictional usernames and documentation-only IP address ranges.

## How it works

1. Validate and parse every event, then sort events by timestamp.
2. Group failures by the exact username and source pair.
3. Use a sliding window to find the largest failure count within the configured period for each pair. Report at most one peak failure burst per pair.
4. Review every successful event and count preceding failures for the same pair inside the configured period, including events exactly on the window boundary.
5. Print summary counts and findings without writing output files or changing the source log.

Events with the same timestamp are counted as separate records. Usernames and source values are compared exactly and case-sensitively. The program stops on a malformed nonblank line instead of producing a partial report.

## Sample result

With the default rule, the sample contains:

- 12 events: 10 failures and 2 successes.
- 1 failure burst with five failures.
- 1 successful login following five failures.
- A four-failure sequence that stays below the configured threshold.

## Limitations

A finding is an indicator for review, not proof of account compromise. Repeated failures may come from user mistakes, cached credentials, or automated services. The tool analyzes one file and exact username/source pairs; it does not correlate devices, locations, user-agent data, inherited identities, or events across multiple systems. It also does not detect password spraying across many accounts. Real logs may contain sensitive information and should not be uploaded to a public repository.

## Files

- `AuthenticationLogAnalyzer.java`: parsing, validation, sliding-window analysis, and report.
- `sample_auth.log`: fictional authentication events.
- `README.md`: setup, behavior, limitations, and interview points.

## Interview explanation

> I built a Java tool that analyzes authentication logs using configurable thresholds and time windows. It groups failed logins by username and source, uses a sliding-window algorithm to identify bursts, and detects successful logins that follow repeated failures. I added strict validation, deterministic sorting, and clear limitations so the findings support investigation without claiming that an incident occurred.

## Validation

Executed with Java 17 source-file mode. Checks cover unsorted input, the inclusive time boundary, below-threshold activity, separate users and sources, success-after-failure detection, empty logs, malformed fields, invalid timestamps and results, invalid arguments, unchanged input, and no output files.

## Reference

- [NIST SP 800-92: Guide to Computer Security Log Management](https://csrc.nist.gov/pubs/sp/800/92/final)
