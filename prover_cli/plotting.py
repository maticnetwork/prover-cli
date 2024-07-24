import pandas as pd
import matplotlib.pyplot as plt

def plot_metrics(data, metric_name, block_number):
    subset = data[(data['block_number'] == block_number) & (data['metric_name'] == metric_name)]
    if subset.empty:
        print(f"No data found for block {block_number} and metric {metric_name}")
        return
    
    plt.figure(figsize=(10, 6))
    for column in subset.columns[3:]:  # Skip the first three columns: block_number, timestamp, metric_name
        plt.plot(subset['timestamp'], subset[column], label=column)
    plt.xlabel('Timestamp')
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over time for block {block_number}")
    plt.legend()
    plt.show()

def plot_and_analyze(csv_file, metric_name, block_number, threshold):
    headers = ['block_number', 'timestamp', 'metric_name'] + [f'metric_{i}' for i in range(1, 100)]  # Adjust range as needed
    data = pd.read_csv(csv_file, header=None, names=headers)
    
    plot_metrics(data, metric_name, block_number)
    
    subset = data[(data['block_number'] == block_number) & (data['metric_name'] == metric_name)]
    if not subset.empty:
        anomalies = subset[subset.iloc[:, 3:].max(axis=1) > threshold]  # Check columns from the 4th onwards for threshold
        if not anomalies.empty:
            print("Anomalies detected:")
            print(anomalies)
        else:
            print("No anomalies detected above the threshold.")
    else:
        print(f"No data found for block {block_number} and metric {metric_name}")
