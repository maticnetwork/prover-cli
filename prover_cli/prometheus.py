import requests
from urllib.parse import urlencode

PROMETHEUS_URL = 'http://localhost:9090/api/v1/query_range'

def test_prometheus_connection():
    try:
        response = requests.get(PROMETHEUS_URL.replace("/query_range", "/targets"))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error connecting to Prometheus:", e)
        exit(1)

def fetch_prometheus_metrics(witness_file, start_time, end_time):
    queries = {
        'cpu_usage': 'rate(container_cpu_user_seconds_total[30s]) * 100',
        'memory_usage': 'container_memory_usage_bytes',
        'disk_read': 'node_disk_read_bytes_total',
        'disk_write': 'node_disk_written_bytes_total',
        'network_receive': 'node_network_receive_bytes_total',
        'network_transmit': 'node_network_transmit_bytes_total'
    }
    
    metrics = []
    for name, query in queries.items():
        start_str = start_time.replace(microsecond=0).isoformat() + "Z"
        end_str = end_time.replace(microsecond=0).isoformat() + "Z"
        params = {
            'query': query,
            'start': start_str,
            'end': end_str,
            'step': '15s'
        }
        url = PROMETHEUS_URL + '?' + urlencode(params)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        metrics.append((name, data['data']['result']))
    
    return metrics

def log_metrics_to_csv(witness_file, metrics):
    import csv
    import os
    from datetime import datetime
    
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open('metrics.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        for metric_name, metric_data in metrics:
            row = [starting_block, datetime.now(), metric_name]
            for metric in metric_data:
                values = [value[1] for value in metric['values']]
                row.extend(values)
            writer.writerow(row)

