# Wargaming Home Task — Automation QA Engineer

## Overview
This repository contains a Python-based solution for Wargaming's Home Task for the Automation QA Engineer role.
The project includes database creation, randomized data generation, and a full automated validation suite using `pytest`.

All code is compatible with **Python 3.8+** and follows a clean, readable structure.

---

## Project Structure

config.py
cli.py
warships_database.py
conftest.py
test_warships_full_suite.py
requirements.txt

## Tasks Implemented

### **Task 1 — Database schema creation**
SQLite database with four tables:
- `weapons`
- `hulls`
- `engines`
- `ships` (with FK references)

### **Task 2 — Data population**
- Random generation of component attributes
- 200 ships linked to random weapons, hulls, and engines

### **Task 3 — Randomized copy**
Session-scoped fixture creates a randomized DB copy inside a temporary directory using pytest.

### **Task 4 — Automated validation tests**
A parametrized pytest suite verifying for all 200 ships:
1. Component attributes match the original
2. FK references were not reassigned
(600+ checks based on total combinations)


## How to Run

### Generate the database:

```bash
python cli.py
```

### Run the full validation suite:
```bash
pytest -v
```

## Requirements

pytest>=7.0

## Author

Mirko Milanovic
Automation QA Engineer
