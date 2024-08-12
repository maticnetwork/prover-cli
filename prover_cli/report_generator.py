import pandas as pd
import datetime
import ast
import glob
import json
import os

def generate_report(witness_dir, metrics_csv_path):
    # Ensure metrics_csv_path is a file and not a directory
    if not os.path.isfile(metrics_csv_path):
        raise ValueError(f"The metrics_csv_path provided is not a file: {metrics_csv_path}")

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

        # Group by block_number
        grouped = df.groupby('block_number')

        for block_number, group in grouped:
            block_data = {
                'block_number': block_number,
                'num_transactions': None,
                'time_taken': None,
                'max_memory': None,
                'avg_memory': None,
                'max_cpu': None,
                'avg_cpu': None,
                'cost_per_proof': None
            }

            # Get witness file corresponding to the block number
            witness_file = next((file for file in witness_files if f'{block_number}.witness' in file), None)
            if witness_file:
                block_data['num_transactions'] = get_num_transactions(witness_file)

            # Initialize lists to calculate average metrics
            cpu_values = []
            memory_values = []

            # Iterate over each metric in the group
            for _, row in group.iterrows():
                metric_name = row['metric_name']
                metric_data = ast.literal_eval(row['data'])

                # Calculate the required metrics
                if metric_name == 'cpu_usage':
                    max_cpu = max([x[1] for x in metric_data])
                    avg_cpu = sum([x[1] for x in metric_data]) / len(metric_data)
                    block_data['max_cpu'] = max(block_data['max_cpu'], max_cpu) if block_data['max_cpu'] is not None else max_cpu
                    cpu_values.append(avg_cpu)
                elif metric_name == 'memory_usage':
                    max_memory = max([x[1] for x in metric_data])
                    avg_memory = sum([x[1] for x in metric_data]) / len(metric_data)
                    block_data['max_memory'] = max(block_data['max_memory'], max_memory) if block_data['max_memory'] is not None else max_memory
                    memory_values.append(avg_memory)

                # Calculate time_taken by comparing the first and last timestamps
                if block_data['time_taken'] is None:
                    block_data['time_taken'] = metric_data[-1][0] - metric_data[0][0]

            # Calculate the average CPU and memory usage across all pods
            if cpu_values:
                block_data['avg_cpu'] = sum(cpu_values) / len(cpu_values)
            if memory_values:
                block_data['avg_memory'] = sum(memory_values) / len(memory_values)

            # Calculate cost per proof
            if block_data['time_taken'] is not None:
                cost_per_second = 1221.28 / (30 * 24 * 60 * 60)
                block_data['cost_per_proof'] = block_data['time_taken'] * cost_per_second

            aggregated_data.append(block_data)

        return pd.DataFrame(aggregated_data)

    # List witness files
    witness_files = glob.glob(os.path.join(witness_dir, '*.json'))

    # Aggregate the metrics
    final_report_df = aggregate_metrics(df, witness_files)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create the output CSV path with the timestamp
    output_csv_path = os.path.join(os.path.dirname(metrics_csv_path), f"performance_report_{timestamp}.csv")

    # Save to CSV
    final_report_df.to_csv(output_csv_path, index=False)
    print(f"Final report saved to {output_csv_path}")
