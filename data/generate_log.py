# data/generate_log.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, os

random.seed(42)
np.random.seed(42)

PROCESSES = {
    'Online': [
        ('Order Placed',         'Website',         2,    5),
        ('Payment Confirmed',    'PaymentGateway',  1,    3),
        ('SAP Booking',          'SAP_EWM',         5,   15),
        ('Warehouse Assignment', 'WMS',             2,    8),
        ('Picking',              'Warehouse_Staff', 20,  90),
        ('Packing',              'Warehouse_Staff', 10,  40),
        ('Dispatch',             'Logistics',        5,  20),
        ('Delivery Confirmed',   'Carrier',        720, 1440),
    ],
    'ClickCollect': [
        ('Order Placed',          'Website',         2,    5),
        ('Payment Confirmed',     'PaymentGateway',  1,    3),
        ('SAP Booking',           'SAP_EWM',         5,   15),
        ('Store Assignment',      'StoreSystem',     2,    5),
        ('Picking',               'Store_Staff',    30,  120),
        ('Ready for Collection',  'StoreSystem',     2,    5),
        ('Collected by Customer', 'POS_Terminal',   30,  480),
    ],
    'Marketplace': [
        ('Order Placed',         'Marketplace_API',  1,    3),
        ('Marketplace Sync',     'SAP_EWM',          5,   30),
        ('Payment Confirmed',    'PaymentGateway',   1,    3),
        ('SAP Booking',          'SAP_EWM',          5,   15),
        ('Warehouse Assignment', 'WMS',              2,    8),
        ('Picking',              'Warehouse_Staff', 20,   90),
        ('Packing',              'Warehouse_Staff', 10,   40),
        ('Dispatch',             'Logistics',        5,   20),
        ('Delivery Confirmed',   'Carrier',        720, 1440),
    ],
}

CHANNEL_WEIGHTS = {'Online': 0.60, 'ClickCollect': 0.25, 'Marketplace': 0.15}
REGIONS = ['North', 'South', 'East', 'West', 'Online']
START_DATE = datetime(2025, 1, 1)
N_ORDERS = 10000


def generate_log(n=N_ORDERS):
    rows = []
    channels = list(CHANNEL_WEIGHTS.keys())
    weights  = list(CHANNEL_WEIGHTS.values())

    for i in range(n):
        case_id = f'ORD-{i+1:05d}'
        channel = random.choices(channels, weights=weights)[0]
        region  = random.choice(REGIONS)
        order_start = START_DATE + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59))
        delay = 3.0 if random.random() < 0.05 else 1.0
        current_time = order_start

        for activity, resource, min_gap, max_gap in PROCESSES[channel]:
            rows.append({
                'case_id': case_id, 'activity': activity,
                'timestamp': current_time, 'resource': resource,
                'channel': channel, 'region': region
            })
            current_time += timedelta(minutes=random.uniform(min_gap, max_gap) * delay)

    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values(['case_id', 'timestamp']).reset_index(drop=True)


if __name__ == '__main__':
    print('Generating event log...')
    df = generate_log()
    os.makedirs('output', exist_ok=True)
    df.to_csv('output/event_log_clean.csv', index=False)
    print(f'Done! {len(df):,} events for {df.case_id.nunique():,} orders')
    print(df.channel.value_counts().to_string())
