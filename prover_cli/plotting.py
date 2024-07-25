import pandas as pd
import matplotlib.pyplot as plt

def plot_metrics(data, metric_name, block_number):
    subset = data[(data['block_number'] == block_number) & (data['metric_name'] == metric_name)]
    if subset.empty:
        print(f"No data found for block {block_number} and metric {metric_name}")
        return

    values = subset.iloc[0]['values']
    if isinstance(values, str):
        values = values.strip('[]').split(', ')

    values = [float(value) for value in values]

    plt.figure(figsize=(10, 6))
    plt.plot(values, marker='o')
    plt.title(f'Metric: {metric_name} for Block: {block_number}')
    plt.xlabel('Time')
    plt.ylabel(metric_name)
    plt.grid(True)
    plt.show()

def plot_and_analyze(csv_file, metric_name, block_number, threshold):
    headers = ['block_number', 'timestamp', 'metric_name', 'values']
    data = pd.read_csv(csv_file, header=0, names=headers)

    plot_metrics(data, metric_name, block_number)

    subset = data[(data['block_number'] == block_number) & (data['metric_name'] == metric_name)]
    if not subset.empty:
        values = subset.iloc[0]['values']
        if isinstance(values, str):
            values = values.strip('[]').split(', ')
        values = [float(value) for value in values]
        
        spikes = [value for value in values if value > threshold]
        if spikes:
            print(f"Spike detected in metric {metric_name} for block {block_number}: {spikes}")
        else:
            print(f"No spikes detected in metric {metric_name} for block {block_number}.")
    else:
        print(f"No data found for block {block_number} and metric {metric_name}")
