# data/inject_issues.py
import pandas as pd, random, os
from datetime import timedelta

random.seed(99)


def inject_issues(inp='output/event_log_clean.csv',
                  out='output/event_log_dirty.csv'):
    df = pd.read_csv(inp)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['issue_type'] = None

    # Issue 1: Missing timestamps (2% of rows)
    idx = df.sample(frac=0.02, random_state=1).index
    df.loc[idx, 'timestamp'] = None
    df.loc[idx, 'issue_type'] = 'MISSING_TIMESTAMP'

    # Issue 2: Duplicate events (1% of orders)
    dup_cases = df['case_id'].drop_duplicates().sample(frac=0.01, random_state=2)
    dups = df[df['case_id'].isin(dup_cases)].copy()
    dups['issue_type'] = 'DUPLICATE_EVENT'
    df = pd.concat([df, dups], ignore_index=True)

    # Issue 3: Wrong activity sequence (0.5%)
    seq_idx = df[df['activity'] == 'Picking'].sample(frac=0.005, random_state=3).index
    df.loc[seq_idx, 'activity'] = 'Dispatch'
    df.loc[seq_idx, 'issue_type'] = 'WRONG_SEQUENCE'

    # Issue 4: NULL resource (1.5%)
    res_idx = df.sample(frac=0.015, random_state=4).index
    df.loc[res_idx, 'resource'] = None
    df.loc[res_idx, 'issue_type'] = 'NULL_RESOURCE'

    # Issue 5: Future timestamps (0.3%)
    fut_idx = df.sample(frac=0.003, random_state=5).index
    df.loc[fut_idx, 'timestamp'] = pd.Timestamp('2027-06-01')
    df.loc[fut_idx, 'issue_type'] = 'FUTURE_TIMESTAMP'

    df = df.sort_values(['case_id', 'timestamp']).reset_index(drop=True)
    os.makedirs('output', exist_ok=True)
    df.to_csv(out, index=False)
    print('Issues injected:')
    print(df['issue_type'].value_counts(dropna=False).to_string())


if __name__ == '__main__':
    inject_issues()
