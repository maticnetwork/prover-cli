import pandas as pd
import matplotlib.pyplot as plt

def read_metrics(csv_file):
    return pd.read_csv(csv_file)

def plot_metrics(data, metric_name, block_number):
    subset = data[(data['block_number'] == block_number) & (data['metric_name'] == metric_name)]
    timestamps = pd.to_datetime(subset['timestamp'])
    values = subset.drop(['block_number', 'timestamp', 'metric_name'], axis=1).values.flatten()

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, values, marker='o', linestyle='-')
    plt.title(f'{metric_name} for block {block_number}')
    plt.xlabel('Timestamp')
    plt.ylabel(metric_name)
    plt.grid(True)
    plt.show()

def detect_anomalies(data, metric_name, threshold):
    anomalies = data[(data['metric_name'] == metric_name) & (data.iloc[:, 3:].max(axis=1) > threshold)]
    return anomalies

def plot_and_analyze(csv_file, metric_name, block_number, threshold):
    data = read_metrics(csv_file)
    plot_metrics(data, metric_name, block_number)
    anomalies = detect_anomalies(data, metric_name, threshold)
    print(f'Anomalies detected for {metric_name} above threshold {threshold}:\n', anomalies)

