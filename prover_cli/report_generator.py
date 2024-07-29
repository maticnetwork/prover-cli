import pandas as pd
import datetime
import ast
import glob
import json
import os

def generate_report(metrics_csv_path, witness_dir:
    # Read the metrics CSV file
    df = pd.read_csv(metrics_csv_path)
    
    # Function to parse and aggregate data for each block number
    def aggregate_metrics(df, witness_files):
        # Initialize a list to store aggregated results
        aggregated_data = []

        # Function to get the number of transactions from witness files
        def get_num_transactions(witness_file):
            with open(witness_file, 'r') as file:
                data = json.load(file)
            return len(data[0]['block_trace']['txn_info'])

        # Function to get withdrawals from witness files
        def get_withdrawals(witness_file):
            with open(witness_file, 'r') as file:
                data = json.load(file)
            # Placeholder: replace with actual logic to extract withdrawals
            return data[0]['withdrawals'] if 'withdrawals' in data[0] else 0

        # Group by block_number
        grouped = df.groupby('block_number')

        for block_number, group in grouped:
            block_data = {
                'block_number': block_number,
                'num_transactions': None,  # Placeholder, replace with actual computation if available
                'time_taken': None,  # Placeholder, replace with actual computation if available
                'max_memory': None,
                'max_cpu': None,
                'withdrawals': None,  # Placeholder, replace with actual computation if available
                'cost_per_proof': None  # Placeholder, replace with actual computation if available
            }

            # Get witness file corresponding to the block number
            witness_file = next((file for file in witness_files if f'block_{block_number}' in file), None)
            if witness_file:
                block_data['num_transactions'] = get_num_transactions(witness_file)
                block_data['withdrawals'] = get_withdrawals(witness_file)

            # Iterate over each metric in the group
            for _, row in group.iterrows():
                metric_name = row['metric_name']
                metric_data = ast.literal_eval(row['data'])

                # Calculate the required metrics
                if metric_name == 'cpu_usage':
                    block_data['max_cpu'] = max([x[1] for x in metric_data])
                elif metric_name == 'memory_usage':
                    block_data['max_memory'] = max([x[1] for x in metric_data])

                # Calculate time_taken by comparing the first and last timestamps
                if block_data['time_taken'] is None:
                    block_data['time_taken'] = metric_data[-1][0] - metric_data[0][0]

            aggregated_data.append(block_data)

        return pd.DataFrame(aggregated_data)

    # List witness files
    witness_files = glob.glob(os.path.join(witness_dir, '*.json'))

    # Aggregate the metrics
    final_report_df = aggregate_metrics(df, witness_files)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create the output CSV path with the timestamp
    output_csv_path = f"performance_report_{timestamp}.csv"

    # Save to CSV
    final_report_df.to_csv(output_csv_path, index=False)
    print(f"Final report saved to {output_csv_path}")
