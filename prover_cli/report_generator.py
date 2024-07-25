import json
import os
import csv
from datetime import datetime
import pandas as pd

def parse_witness_file(witness_file):
    with open(witness_file, 'r') as file:
        witness_data = json.load(file)

    # Assuming witness_data is a list of dictionaries
    num_transactions = len(witness_data[0].get('transactions', []))
    withdrawals = len(witness_data[0].get('withdrawals', []))

    return num_transactions, withdrawals

def log_metrics_to_csv(witness_file, metrics, csv_file):
    headers = ['block_number', 'timestamp', 'metric_name', 'values']
    starting_block = os.path.basename(witness_file).split('.')[0]
    rows = []

    for metric_name, metric in metrics.items():
        values = [value[1] for value in metric['values']]
        timestamp = datetime.now()
        rows.append([starting_block, timestamp, metric_name, values])

    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def generate_report(csv_file, witness_dir):
    data = pd.read_csv(csv_file)
    report_data = []

    for witness_file in os.listdir(witness_dir):
        if witness_file.endswith('.witness.json'):
            witness_path = os.path.join(witness_dir, witness_file)
            block_number = os.path.basename(witness_file).split('.')[0]

            # Calculate time taken (assuming it's the time to generate this witness)
            time_taken = 0  # Placeholder for actual time calculation
            num_transactions, withdrawals = parse_witness_file(witness_path)

            block_data = data[data['block_number'] == int(block_number)]

            max_memory = 0
            max_cpu = 0

            for _, row in block_data.iterrows():
                if row['metric_name'] == 'memory_usage':
                    max_memory = max(max_memory, max(map(float, eval(row['values']))))
                if row['metric_name'] == 'cpu_usage':
                    max_cpu = max(max_cpu, max(map(float, eval(row['values']))))

            cost_per_proof = time_taken * 0.0123  # Placeholder cost calculation

            report_data.append([
                block_number,
                row['timestamp'],
                num_transactions,
                time_taken,
                max_memory,
                max_cpu,
                withdrawals,
                cost_per_proof
            ])

    report_df = pd.DataFrame(report_data, columns=[
        'block_number', 'timestamp', 'num_transactions', 'time_taken',
        'max_memory', 'max_cpu', 'withdrawals', 'cost_per_proof'
    ])

    report_file = os.path.join(witness_dir, 'report.csv')
    report_df.to_csv(report_file, index=False)
    print(f'Report generated: {report_file}')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prover CLI Report Generator")
    parser.add_argument('--csv_file', type=str, required=True, help='CSV file with metrics data')
    parser.add_argument('--witness_dir', type=str, required=True, help='Directory with witness files')

    args = parser.parse_args()
    generate_report(args.csv_file, args.witness_dir)
