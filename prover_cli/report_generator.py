import json
import os
import csv
from datetime import datetime

def parse_witness_file(witness_file):
    with open(witness_file, 'r') as file:
        witness_data = json.load(file)
    num_transactions = len(witness_data[0].get('transactions', []))
    withdrawals = len(witness_data[0].get('withdrawals', []))
    return num_transactions, withdrawals

def generate_report(csv_file, witness_dir):
    report_data = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            block_number = row['block_number']
            timestamp = row['timestamp']
            metric_name = row['metric_name']
            values = eval(row['values'])
            start_time = datetime.fromisoformat(row['start_time'])
            end_time = datetime.fromisoformat(row['end_time'])
            duration = (end_time - start_time).total_seconds()

            max_memory = 0
            max_cpu = 0
            if metric_name == 'memory_usage':
                max_memory = max(values)
            elif metric_name == 'cpu_usage':
                max_cpu = max(values)

            witness_file = os.path.join(witness_dir, f"{block_number}.witness.json")
            num_transactions, withdrawals = parse_witness_file(witness_file)

            cost_per_proof = duration * 0.012  # Approximation for t2d-64 nodes in GCP

            report_data.append({
                'block_number': block_number,
                'timestamp': timestamp,
                'num_transactions': num_transactions,
                'time_taken': duration,
                'max_memory': max_memory,
                'max_cpu': max_cpu,
                'withdrawals': withdrawals,
                'cost_per_proof': cost_per_proof
            })

    report_file = 'report.csv'
    with open(report_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=report_data[0].keys())
        writer.writeheader()
        writer.writerows(report_data)
    print(f"Report generated: {report_file}")
