import json
import csv
import os

def parse_witness_file(witness_file):
    with open(witness_file, 'r') as wf:
        witness_data = json.load(wf)
        num_transactions = len(witness_data[0].get('transactions', []))
        withdrawals = sum(len(tx.get('withdrawals', [])) for tx in witness_data[0].get('transactions', []))
    return num_transactions, withdrawals

def generate_report(csv_file, witness_dir, total_duration):
    headers = ['block_number', 'timestamp', 'num_transactions', 'time_taken', 'max_memory', 'max_cpu', 'withdrawals', 'cost_per_proof']
    report_data = []

    # Read the metrics CSV
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            block_number = row['block_number']
            witness_file = os.path.join(witness_dir, f"{block_number}.witness.json")
            
            if not os.path.exists(witness_file):
                print(f"Witness file {witness_file} not found.")
                continue

            num_transactions, withdrawals = parse_witness_file(witness_file)
            
            max_memory = 0
            max_cpu = 0
            
            # Process metrics
            for metric_name, values in json.loads(row['values']).items():
                if metric_name == 'memory_usage':
                    max_memory = max(max_memory, max(map(float, values)))
                elif metric_name == 'cpu_usage':
                    max_cpu = max(max_cpu, max(map(float, values)))
            
            # Assuming duration is calculated and passed here
            duration = total_duration if total_duration else 3600  # Example duration in seconds
            
            # Assuming the cost per second of a t2d-64 high-mem node is $0.11
            cost_per_proof = duration * 0.11 / 3600
            
            report_row = {
                'block_number': block_number,
                'timestamp': row['timestamp'],
                'num_transactions': num_transactions,
                'time_taken': duration,
                'max_memory': max_memory,
                'max_cpu': max_cpu,
                'withdrawals': withdrawals,
                'cost_per_proof': cost_per_proof
            }
            
            report_data.append(report_row)

    # Write the report CSV
    with open('report.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(report_data)

    print("Report generated successfully.")
