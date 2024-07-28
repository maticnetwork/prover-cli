import matplotlib.pyplot as plt
import pandas as pd
import json
from datetime import datetime

def plot_metrics(data, metric_name, block_number):
    print("Data for plotting:", data)  # Debug statement
    print(f"Filtering for block_number: {block_number}, metric_name: {metric_name}")  # Debug statement
    
    data['block_number'] = data['block_number'].astype(str)
    subset = data[(data['block_number'] == str(block_number)) & (data['metric_name'] == metric_name)]
    
    if subset.empty:
        print(f"No data found for block {block_number} and metric {metric_name}")
        return

    for index, row in subset.iterrows():
        values = json.loads(row['data'])
        timestamps = [datetime.utcfromtimestamp(value[0]).strftime('%m/%d/%Y %H:%M:%S') for value in values]
        data_points = [value[1] / (1024**3) for value in values]  # Convert bytes to GB

        plt.plot(timestamps, data_points, label=f"Block {block_number}")

    plt.xlabel('Timestamp')
    plt.ylabel(f'{metric_name} (GB)')
    plt.title(f"{metric_name} over Time for Block {block_number}")
    plt.xticks(rotation=45)
    plt.legend()

    # Save the plot as an image
    output_file = f"plot_{metric_name}_{block_number}.png"
    plt.savefig(output_file, bbox_inches='tight')
    print(f"Plot saved to {output_file}")

def plot_and_analyze(csv_file, metric_name, block_number):
    headers = ['block_number', 'metric_name', 'data']
    data = pd.read_csv(csv_file, header=0, names=headers)
    print("CSV data:", data)  # Debug statement
    plot_metrics(data, metric_name, block_number)
