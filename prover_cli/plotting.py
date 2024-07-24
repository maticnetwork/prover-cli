import pandas as pd
import matplotlib.pyplot as plt

def plot_metrics(data, metric_name, block_number):
    subset = data[(data['begin_block'] == block_number) & (data['metric_name'] == metric_name)]
    if subset.empty:
        print(f"No data found for block {block_number} and metric {metric_name}")
        return
    
    plt.figure(figsize=(10, 6))
    for column in subset.columns[3:]:  # Skip the first three columns: begin_block, timestamp, metric_name
        plt.plot(subset['timestamp'], subset[column], label=column)
    plt.xlabel('Timestamp')
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over time for block {block_number}")
    plt.legend()
    plt.show()

def plot_and_analyze(csv_file, metric_name, block_number, threshold):
    data = pd.read_csv(csv_file)
    
    plot_metrics(data, metric_name, block_number)
    
    subset = data[(data['begin_block'] == block_number) & (data['metric_name'] == metric_name)]
    if not subset.empty:
        anomalies = subset[subset.max(axis=1) > threshold]
        if not anomalies.empty:
            print("Anomalies detected:")
            print(anomalies)
        else:
            print("No anomalies detected above the threshold.")
    else:
        print(f"No data found for block {block_number} and metric {metric_name}")

