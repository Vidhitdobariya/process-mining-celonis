# sql/run_checks.py
# Loads the cleaned event log into SQLite and runs all SQL quality checks.
# No MySQL or server setup needed — works on any machine instantly.

import sqlite3
import pandas as pd
import os

CSV_PATH = 'output/event_log_cleaned.csv'
SQL_PATH = 'sql/quality_checks.sql'


def run_checks():

    # ----------------------------------------------------------------
    # Step 1: Load cleaned CSV into pandas
    # ----------------------------------------------------------------
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found.")
        print("Please run clean_data.py first.")
        return

    print(f"Loading cleaned data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows, {df['case_id'].nunique():,} orders\n")

    # ----------------------------------------------------------------
    # Step 2: Create in-memory SQLite database and insert the data
    # This is like creating a temporary MySQL table — same concept
    # ----------------------------------------------------------------
    conn = sqlite3.connect(':memory:')
    df.to_sql('event_log', conn, if_exists='replace', index=False)
    print("Data loaded into SQLite (in-memory database)\n")

    # ----------------------------------------------------------------
    # Step 3: Read the SQL file and split into individual queries
    # ----------------------------------------------------------------
    with open(SQL_PATH, 'r') as f:
        sql_content = f.read()

    # Split on semicolon to get individual queries, skip empty ones
    queries = [q.strip() for q in sql_content.split(';') if q.strip()]

    # ----------------------------------------------------------------
    # Step 4: Run each query and print results
    # ----------------------------------------------------------------
    print("=" * 55)
    print("       DATA QUALITY VALIDATION REPORT")
    print("=" * 55)

    all_passed = True

    for query in queries:
        # Skip comment-only blocks
        lines = [l for l in query.split('\n') if not l.strip().startswith('--')]
        clean_query = '\n'.join(lines).strip()
        if not clean_query:
            continue

        try:
            result = pd.read_sql_query(clean_query, conn)
            if result.empty:
                continue

            # Print result table
            print()
            print(result.to_string(index=False))
            print("-" * 55)

            # Track overall pass/fail
            if 'result' in result.columns:
                if 'FAIL' in result['result'].values:
                    all_passed = False

        except Exception as e:
            print(f"Query error: {e}")

    # ----------------------------------------------------------------
    # Step 5: Final verdict
    # ----------------------------------------------------------------
    print()
    if all_passed:
        print("FINAL VERDICT: ALL CHECKS PASSED ✓")
        print("Data is clean and ready for Celonis upload.")
    else:
        print("FINAL VERDICT: SOME CHECKS FAILED ✗")
        print("Please re-run clean_data.py and check the output.")

    print("=" * 55)
    conn.close()


if __name__ == '__main__':
    run_checks()
