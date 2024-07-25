import json
import os
import csv
from datetime import datetime

def parse_witness_file(witness_path):
    with open(witness_path, 'r') as file:
        witness_data = json.load(file)
    
    num_transactions = len(witness_data[0].get('transactions', []))
    withdrawals = witness_data[0].get('block_trace', {}).get('withdrawals', 0)

    return num_transactions, withdrawals

def generate_report(csv_file, witness_dir, duration):
    report_data = []

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            block_number = row['block_number']
            timestamp = row['timestamp']
            max_memory = 0.0
            max_cpu = 0.0

            if row['metric_name'] == 'memory_usage':
                max_memory = max(max_memory, max(eval(row['values'])))
            elif row['metric_name'] == 'cpu_usage':
                max_cpu = max(max_cpu, max(eval(row['values'])))

            witness_file = os.path.join(witness_dir, f"{block_number}.witness.json")
            num_transactions, withdrawals = parse_witness_file(witness_file)

            cost_per_proof = duration * 0.01  # Assuming $0.01 per second for t2d-60 high-mem node

            report_data.append([
                block_number, 
                timestamp, 
                num_transactions, 
                duration, 
                max_memory, 
                max_cpu, 
                withdrawals, 
                cost_per_proof
            ])

    report_file = os.path.join(witness_dir, 'report.csv')
    with open(report_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'block_number', 
            'timestamp', 
            'num_transactions', 
            'time_taken', 
            'max_memory', 
            'max_cpu', 
            'withdrawals', 
            'cost_per_proof'
        ])
        writer.writerows(report_data)
