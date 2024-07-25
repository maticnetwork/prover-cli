import os
import pandas as pd
import json

def parse_witness_file(witness_file):
    with open(witness_file, 'r') as f:
        witness_data = json.load(f)

    # Extract the necessary information
    if isinstance(witness_data, list) and len(witness_data) > 0:
        data = witness_data[0]
        num_transactions = len(data.get('transactions', []))
        withdrawals = len(data.get('withdrawals', []))
    else:
        num_transactions = 0
        withdrawals = 0

    return num_transactions, withdrawals

def generate_report(csv_file, witness_dir, durations):
    data = pd.read_csv(csv_file)
    report_data = []

    for witness_file in os.listdir(witness_dir):
        if witness_file.endswith('.witness.json'):
            witness_path = os.path.join(witness_dir, witness_file)
            block_number = int(os.path.basename(witness_file).split('.')[0])

            # Get the duration for this block
            time_taken = durations.get(block_number, 0) if durations else 0

            num_transactions, withdrawals = parse_witness_file(witness_path)

            block_data = data[data['block_number'] == block_number]

            max_memory = 0
            max_cpu = 0

            for _, row in block_data.iterrows():
                if row['metric_name'] == 'memory_usage':
                    max_memory = max(max_memory, max(map(float, eval(row['values']))))
                if row['metric_name'] == 'cpu_usage':
                    max_cpu = max(max_cpu, max(map(float, eval(row['values']))))

            # Calculate cost per proof (example calculation, adjust as needed)
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
