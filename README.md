# Wargaming Home Task — Automation QA Engineer

## Overview

This repository contains the Home Task solution for the Automation QA Engineer position at Wargaming.
Implemented in **Python 3.8**, fully **PEP8-compliant**, using **pytest** for automated testing.

## Project Structure

config.py
cli.py
warships_database.py
conftest.py
test_warships_full_suite.py
requirements.txt

## Tasks Covered

- **Task 1:** Database creation (SQLite tables: ships, weapons, hulls, engines)
- **Task 2:** Randomized data population (200 ships, 20 weapons, 5 hulls, 6 engines)
- **Task 3:** Session-scoped fixture for randomized database
- **Task 4:** Automated pytest suite comparing original and randomized data (600 tests)

## How to Run

```bash
python cli.py
pytest -v
```

## Requirements

pytest>=7.0

## Author

Mirko Milanovic
Senior Automation QA Engineer
