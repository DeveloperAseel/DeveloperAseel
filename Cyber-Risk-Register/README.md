# Cyber Risk Register

A small Java console application for recording and reviewing cybersecurity risks. It calculates a risk score from likelihood and impact, then groups each risk into a priority level.

## Features

- Add a risk with its affected asset
- Rate likelihood and impact from 1 to 5
- Calculate the score using `likelihood x impact`
- Classify risks as Low, Medium, or High
- Display all risks and a simple summary
- Validate menu and rating inputs

The score thresholds in this learning project are:

- Low: 1-5
- Medium: 6-14
- High: 15-25

Organizations can change these thresholds to match their own risk methodology and risk appetite.

## Files

- `CyberRiskRegister.java` - the complete application
- `README.md` - setup and project explanation

## Requirements

- Java 11 or later

## Run the project

Open a terminal in this folder and run:

```bash
javac CyberRiskRegister.java
java CyberRiskRegister
```

The program begins with two sample risks. Use the menu to add another risk, view the full register, or display the summary.

## How it works

The `Risk` class stores the title, affected asset, likelihood, and impact. The score is calculated by multiplying likelihood by impact. An `ArrayList` keeps the risks while the program is running, and the menu calls separate methods for adding, listing, and summarizing them.

Data is stored in memory, so newly added risks are cleared when the program closes. This keeps the project focused on Java fundamentals and risk scoring.

## Interview explanation

I built a Java console application that represents a basic cybersecurity risk register. A user records a risk, identifies the affected asset, and rates its likelihood and impact. The program calculates a score and assigns a priority level so high risks can be reviewed first. The project demonstrates classes, objects, collections, methods, loops, input validation, and a practical GRC concept.

## Reference

- [NIST SP 800-30 Rev. 1: Guide for Conducting Risk Assessments](https://csrc.nist.gov/pubs/sp/800/30/r1/final)
