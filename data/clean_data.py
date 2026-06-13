# data/clean_data.py
# Step 3 in the pipeline: reads the dirty event log, saves flagged records,
# fixes all 5 issue types, saves cleaned version ready for SQL validation and Celonis.

import pandas as pd
import os

def clean(inp='output/event_log_dirty.csv',
          out='output/event_log_cleaned.csv'):

    df = pd.read_csv(inp)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    print(f"Loaded dirty data: {len(df):,} rows")
    print(f"Issues before cleaning: {df['issue_type'].notna().sum():,} flagged rows\n")

    # ------------------------------------------------------------------
    # Save flagged records BEFORE cleaning
    # Why: we want to keep a record of what was wrong in the dirty data
    # before we fix anything — this is our audit trail
    # ------------------------------------------------------------------
    flagged = df[df['issue_type'].notna()].copy()
    os.makedirs('output', exist_ok=True)
    flagged.to_csv('output/flagged_records.csv', index=False)
    print(f"Flagged records saved: {len(flagged):,} rows → output/flagged_records.csv\n")

    # ------------------------------------------------------------------
    # Fix 1: Missing timestamps
    # Method: sort each order by timestamp, then forward-fill the gap.
    # Why: if Order #1001 has steps at 10:00, NaT, 10:30 — we fill the
    # missing one with the previous valid timestamp (10:00).
    # ------------------------------------------------------------------
    df = df.sort_values(['case_id', 'timestamp'])
    df['timestamp'] = df.groupby('case_id')['timestamp'].transform(
        lambda x: x.ffill().bfill()
    )
    missing_fixed = df['issue_type'].eq('MISSING_TIMESTAMP').sum()
    print(f"Fix 1 — Missing timestamps filled:   {missing_fixed:,} rows")

    # ------------------------------------------------------------------
    # Fix 2: Future timestamps
    # Method: cap any timestamp beyond today to the last valid timestamp
    # seen for that order.
    # Why: a timestamp of 2027-06-01 is clearly a system error — we
    # replace it with the previous real event time for that order.
    # ------------------------------------------------------------------
    cutoff = pd.Timestamp.now()
    future_mask = df['timestamp'] > cutoff
    df.loc[future_mask, 'timestamp'] = pd.NaT
    df['timestamp'] = df.groupby('case_id')['timestamp'].transform(
        lambda x: x.ffill().bfill()
    )
    future_fixed = df['issue_type'].eq('FUTURE_TIMESTAMP').sum()
    print(f"Fix 2 — Future timestamps corrected: {future_fixed:,} rows")

    # ------------------------------------------------------------------
    # Fix 3: Duplicate events
    # Method: drop rows where case_id + activity + timestamp are identical,
    # keeping the first occurrence.
    # Why: exact duplicates add no information and inflate cycle times.
    # ------------------------------------------------------------------
    before = len(df)
    df = df.drop_duplicates(subset=['case_id', 'activity', 'timestamp'], keep='first')
    dupes_removed = before - len(df)
    print(f"Fix 3 — Duplicate rows removed:      {dupes_removed:,} rows")

    # ------------------------------------------------------------------
    # Fix 4: NULL resource
    # Method: fill missing resource using the most common (mode) resource
    # for that activity across the whole dataset.
    # Why: each activity is almost always done by the same system/team
    # (e.g. Picking is always Warehouse_Staff), so the mode is a safe fill.
    # ------------------------------------------------------------------
    activity_mode = (
        df.groupby('activity')['resource']
        .agg(lambda x: x.mode()[0] if not x.mode().empty else 'Unknown')
    )
    null_mask = df['resource'].isna()
    df.loc[null_mask, 'resource'] = df.loc[null_mask, 'activity'].map(activity_mode)
    null_fixed = df['issue_type'].eq('NULL_RESOURCE').sum()
    print(f"Fix 4 — Null resources filled:       {null_fixed:,} rows")

    # ------------------------------------------------------------------
    # Fix 5: Wrong sequence (WRONG_SEQUENCE)
    # Method: for each order, re-sort activities by timestamp.
    # Why: if Dispatch appears before Picking in an order, sorting by
    # timestamp restores the natural process order.
    # ------------------------------------------------------------------
    df = df.sort_values(['case_id', 'timestamp']).reset_index(drop=True)
    seq_fixed = df['issue_type'].eq('WRONG_SEQUENCE').sum()
    print(f"Fix 5 — Sequence issues reordered:   {seq_fixed:,} rows")

    # ------------------------------------------------------------------
    # Final: drop the issue_type column (cleaned data should be clean)
    # and save
    # ------------------------------------------------------------------
    df = df.drop(columns=['issue_type'])
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df.to_csv(out, index=False)

    print(f"\nCleaning complete!")
    print(f"Cleaned rows saved: {len(df):,}")
    print(f"Output: {out}")


if __name__ == '__main__':
    clean()
