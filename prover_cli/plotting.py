import matplotlib.pyplot as plt
import pandas as pd

def plot_metrics(data, metric_name, block_number):
    subset = data[(data['block_number'] == block_number) & (data['metric_name'] == metric_name)]
    if subset.empty:
        print(f"No data found for block {block_number} and metric {metric_name}")
        return

    for index, row in subset.iterrows():
        timestamp = row['timestamp']
        values = row['values'].strip("[]").split(", ")
        try:
            values = [float(value.strip("'")) for value in values]  # Remove quotes and convert to float
        except ValueError as e:
            print(f"Failed to convert values to float: {e}")
            continue

        plt.plot(values, label=f"Block {block_number}")

    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    plt.xlabel('Time')
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over Time for Block {block_number}")
    plt.legend()
    plt.show()

def plot_and_analyze(csv_file, metric_name, block_number, threshold):
    headers = ['block_number', 'timestamp', 'metric_name', 'values']
    data = pd.read_csv(csv_file, header=None, names=headers)
    plot_metrics(data, metric_name, block_number)
