import pandas as pd
import json
import os
from datetime import datetime, timedelta

def parse_witness_file(witness_file):
    with open(witness_file, 'r') as file:
        witness_data = json.load(file)
    
    num_transactions = len(witness_data.get('transactions', []))
    withdrawals = len(witness_data.get('withdrawals', []))
    return num_transactions, withdrawals

def calculate_cost(time_taken_minutes):
    # Average cost of t2d-64 high-mem node in GCP
    cost_per_minute = 0.084  # Example cost, you should update it with the actual cost
    return time_taken_minutes * cost_per_minute

def generate_report(csv_file, witness_dir):
    # Load the CSV file
    headers = ['block_number', 'timestamp', 'metric_name', 'values']
    data = pd.read_csv(csv_file, header=0, names=headers)
    
    # Initialize a summary dictionary
    summary = {}

    for _, row in data.iterrows():
        block_number = row['block_number']
        timestamp = row['timestamp']
        metric_name = row['metric_name']
        values = [float(value.strip().strip("'")) for value in row['values'].strip('[]').split(',')]

        if block_number not in summary:
            witness_file = os.path.join(witness_dir, f"{block_number}.witness.json")
            num_transactions, withdrawals = parse_witness_file(witness_file)
            summary[block_number] = {
                'timestamp': timestamp,
                'num_transactions': num_transactions,
                'time_taken': 0,  # Placeholder, will be calculated later
                'max_memory': 0,
                'max_cpu': 0,
                'withdrawals': withdrawals,
                'cost_per_proof': 0  # Placeholder, will be calculated later
            }
        
        if metric_name == 'memory_usage':
            summary[block_number]['max_memory'] = max(values)
        elif metric_name == 'cpu_usage':
            summary[block_number]['max_cpu'] = max(values)
    
    # Calculate time taken and cost per proof
    for block_number, metrics in summary.items():
        start_time = datetime.strptime(metrics['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        end_time = datetime.utcnow()
        time_taken = (end_time - start_time).total_seconds() / 60  # Convert to minutes
        summary[block_number]['time_taken'] = time_taken
        summary[block_number]['cost_per_proof'] = calculate_cost(time_taken)

    # Create a DataFrame for the summary
    summary_df = pd.DataFrame.from_dict(summary, orient='index')
    
    # Save the summary report to a CSV file
    summary_csv_file = 'summary_report.csv'
    summary_df.to_csv(summary_csv_file, index_label='witness_id')
    print(f"Summary report saved to {summary_csv_file}")

    return summary_csv_file
