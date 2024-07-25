import matplotlib.pyplot as plt
import pandas as pd

def plot_metrics(data, metric_name, block_number, threshold):
    print("Data for plotting:", data)  # Debug statement
    print(f"Filtering for block_number: {block_number}, metric_name: {metric_name}")  # Debug statement
    
    data['block_number'] = data['block_number'].astype(str)
    subset = data[(data['block_number'] == str(block_number)) & (data['metric_name'] == metric_name)]
    
    if subset.empty:
        print(f"No data found for block {block_number} and metric {metric_name}")
        return

    for index, row in subset.iterrows():
        values = row['values']
        try:
            values = [float(value.strip().strip("'")) for value in values.strip('[]').split(',')]
        except ValueError as e:
            print(f"Failed to convert values to float: {e}")
            continue

        plt.plot(values, label=f"Block {block_number}")

    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    plt.xlabel('Time')
    plt.ylabel(metric_name)
    plt.title(f"{metric_name} over Time for Block {block_number}")
    plt.legend()

    # Save the plot as an image
    output_file = f"plot_{metric_name}_{block_number}.png"
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

def plot_and_analyze(csv_file, metric_name, block_number, threshold):
    headers = ['block_number', 'timestamp', 'metric_name', 'values']
    data = pd.read_csv(csv_file, header=0, names=headers)
    print("CSV data:", data)  # Debug statement
    plot_metrics(data, metric_name, block_number, threshold)
