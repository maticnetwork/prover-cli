import pandas as pd
from datetime import datetime

def generate_report(csv_file):
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
            summary[block_number] = {
                'timestamp': timestamp,
                'num_transactions': 0,  # Placeholder
                'time_taken': 0,        # Placeholder
                'max_memory': 0,
                'max_cpu': 0,
                'withdrawals': 0,       # Placeholder
                'cost_per_proof': 0     # Placeholder
            }
        
        if metric_name == 'memory_usage':
            summary[block_number]['max_memory'] = max(values)
        elif metric_name == 'cpu_usage':
            summary[block_number]['max_cpu'] = max(values)

    # Create a DataFrame for the summary
    summary_df = pd.DataFrame.from_dict(summary, orient='index')
    
    # Save the summary report to a CSV file
    summary_csv_file = 'summary_report.csv'
    summary_df.to_csv(summary_csv_file, index_label='witness_id')
    print(f"Summary report saved to {summary_csv_file}")

    return summary_csv_file
