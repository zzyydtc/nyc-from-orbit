# Contributing

Thanks for your interest. This is an independent research project.

## Ground rules

- Open an issue before large changes.
- Work on a branch and open a pull request, including for maintainers. Fill in the PR template.
- Keep raw data out of git. Fetch scripts must record the source URL, retrieval date and checksum.
- Every new dataset needs a row in the data sources table with its license and terms.
- Results must be reported with uncertainty. A null or negative result is a valid result.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check .
pytest
```

## Responsible use

Reported crime reflects reporting and enforcement as well as offending. Analyses here are
tract-level, annual and associational. Contributions that target individuals or demographic
groups will not be accepted.
