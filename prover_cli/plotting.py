import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os
import argparse

def plot_metrics(csv_file, metric_name, block_number, save_dir='plots'):
    # Load the CSV data
    df = pd.read_csv(csv_file)

    # Convert the 'data' column from JSON strings to lists of tuples
    df['data'] = df['data'].apply(lambda x: json.loads(x))

    # Expand the 'data' column into separate rows
    df_expanded = df.explode('data').reset_index(drop=True)

    # Split the 'data' column into separate 'timestamp' and 'value' columns
    df_expanded['timestamp'] = df_expanded['data'].apply(lambda x: x[0])
    df_expanded['value'] = df_expanded['data'].apply(lambda x: x[1])

    # Convert 'timestamp' from Unix time to datetime
    df_expanded['timestamp'] = pd.to_datetime(df_expanded['timestamp'], unit='s')

    # Drop the now-unnecessary 'data' column
    df_expanded = df_expanded.drop(columns=['data'])

    # Filter by block number and metric name
    filtered_df = df_expanded[(df_expanded['block_number'] == block_number) & (df_expanded['metric_name'] == metric_name)]

    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)

    plt.figure(figsize=(12, 6))
    for pod in filtered_df['pod_name'].unique():
        pod_data = filtered_df[filtered_df['pod_name'] == pod]
        plt.plot(pod_data['timestamp'], pod_data['value'], label=pod)
    
    plt.title(f'{metric_name} Over Time for Block {block_number}')
    plt.xlabel('Time')
    plt.ylabel(metric_name)
    plt.legend()
    plt.grid(True)
    
    # Save the plot as a file
    filename = f'{save_dir}/{metric_name}_block_{block_number}.png'
    plt.savefig(filename)
    plt.close()
    print(f'Plot saved as {filename}')
