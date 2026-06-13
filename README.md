# Process Mining — Thalia Order Fulfillment

An end-to-end Process Mining pipeline simulating the data engineering challenges Thalia faces during its **Log25** supply chain transformation — including SAP S/4HANA EWM migration, AutoStore warehouse rollout in Marl, and omnichannel order fulfillment across Online, Click & Collect, and Marketplace channels.

---

## Pipeline Overview

```
generate_log.py        →   Synthetic SAP-style event log (10,000 orders)
inject_issues.py       →   5 data quality issues injected (real SAP migration problems)
clean_data.py          →   All issues detected, fixed, and flagged records exported
quality_checks.sql     →   SQL validation in MySQL — 5/5 checks PASS, quality score 100%
Celonis                →   Process map discovered from cleaned event log
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Orders simulated | 10,000 |
| Total events | 78,968 |
| Channels | Online (60%), Click & Collect (25%), Marketplace (15%) |
| Avg cycle time | 2.15 hrs |
| Most used channel | Online |
| Issues injected | 5 types — missing timestamps, duplicates, null resources, future timestamps, wrong sequence |
| Data quality score (after cleaning) | **100%** |
| SQL checks passed | **5 / 5** |

---

## Process Map (Celonis)

![Celonis Process Map](docs/Screenshot_2026-06-12_163640.png)

> Live Celonis view (requires Academic Alliance login):
> [Open in Celonis](https://academic-celonis-7aarj9.eu-2.celonis.cloud/package-manager/ui/studio/ui/spaces/d2a19d67-50b4-4d6f-b6ab-93a7a6ba65ea/packages/8c222a15-c59d-410e-bad0-b7e1b9e94a9d/nodes/f67237c0-0ee8-4e34-82d6-f50ae5716a0c?share=7f74bc84-8c8f-43e6-8940-2d7e2ed963a3&bookmark=false)

---

## Repo Structure

```
process-mining-celonis/
├── data/
│   ├── generate_log.py       ← generates synthetic SAP event log
│   ├── inject_issues.py      ← injects 5 data quality issues
│   └── clean_data.py         ← cleans issues + exports flagged_records.csv
├── sql/
│   └── quality_checks.sql    ← MySQL validation queries (5 checks)
├── output/
│   ├── event_log_clean.csv       ← original clean log
│   ├── event_log_dirty.csv       ← log with injected issues
│   ├── event_log_cleaned.csv     ← final cleaned log (Celonis-ready)
│   └── flagged_records.csv       ← audit trail of all fixed rows
└── docs/
    └── Screenshot_2026-06-12_163640.png  ← Celonis process map
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic event log
python data/generate_log.py

# 3. Inject data quality issues
python data/inject_issues.py

# 4. Clean issues + export flagged records
python data/clean_data.py

# 5. Validate in MySQL Workbench
#    Import output/event_log_cleaned.csv into MySQL as table: event_log
#    Run: sql/quality_checks.sql
```

---

## Data Quality Issues Simulated

| Issue Type | Method | How it was fixed |
|------------|--------|-----------------|
| Missing timestamps | 2% of rows set to NULL | Forward-fill from previous event in same order |
| Future timestamps | 0.3% set to 2027-06-01 | Replaced with last valid timestamp |
| Duplicate events | 1% of orders duplicated | Drop exact duplicates, keep first |
| Null resources | 1.5% of rows set to NULL | Fill with mode resource for that activity |
| Wrong sequence | 0.5% activity labels swapped | Re-sort events by timestamp within each order |

---

## SQL Validation (MySQL)

All 5 checks run against `event_log_cleaned` table in MySQL:

```sql
-- CHECK 1: Missing timestamps → 0 issues → PASS
-- CHECK 2: Future timestamps  → 0 issues → PASS
-- CHECK 3: Duplicate events   → 0 issues → PASS
-- CHECK 4: Null resources     → 0 issues → PASS
-- CHECK 5: Quality score      → 100.0%   → PASS
```

---

## Business Context

Thalia is mid-way through **Log25** — a full redesign of their omnichannel supply chain including SAP S/4HANA EWM, a new AutoStore hub in Marl (Westfalen), and RELEX AI-driven demand forecasting. This creates a high-risk data environment where ETL pipelines break as old and new SAP systems run in parallel. This project simulates that exact scenario and builds the tooling to detect, fix, and validate it.

---

## Tech Stack

`Python` · `pandas` · `SQLite` · `MySQL` · `SQL` · `Celonis` · `Git`

---

*Built for Thalia Praktikum Process Mining interview preparation. All data is synthetic.*
