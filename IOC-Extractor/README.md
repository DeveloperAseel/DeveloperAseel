# IOC Extractor

A small Java command-line tool that extracts common indicators of compromise from a security alert or investigation note.

## Features

- Extracts HTTP and HTTPS URLs
- Extracts and validates IPv4 addresses
- Extracts email addresses
- Extracts SHA-256 file hashes
- Removes duplicate indicators while keeping their original order
- Uses only the Java standard library

## Files

- `IOCExtractor.java` - the complete application
- `sample_alert.txt` - a fictional sample using reserved documentation values
- `README.md` - setup and project explanation

## Requirements

- Java 11 or later

## Run the project

Open a terminal in this folder and run:

```bash
javac IOCExtractor.java
java IOCExtractor sample_alert.txt
```

You can replace `sample_alert.txt` with another plain-text alert or investigation note.

## How it works

The program reads the input file with `Files.readString`. Regular expressions identify possible URLs, IPv4 addresses, email addresses, and SHA-256 hashes. IPv4 candidates are checked to make sure every number is between 0 and 255. A `LinkedHashSet` removes duplicates without changing the order in which indicators appeared.

The tool extracts indicators for review; it does not decide whether an indicator is malicious. Analysts should validate the results using trusted threat intelligence sources and organizational procedures.

## Interview explanation

I built a Java tool that extracts common indicators of compromise from unstructured security text. It uses regular expressions for pattern matching, validates IPv4 addresses, and stores results in sets to remove duplicates. The project demonstrates file handling, regular expressions, collections, validation, and a practical cyber threat intelligence workflow.

## Reference

- [CISA: Automated Indicator Sharing](https://www.cisa.gov/topics/cyber-threats-and-advisories/information-sharing/automated-indicator-sharing-ais)
