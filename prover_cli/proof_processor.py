import json
import subprocess
import csv
from datetime import datetime
from urllib.parse import urlencode
import requests

PROMETHEUS_URL = 'http://localhost:9090/api/v1/query_range'

def execute_task(witness_file, previous_proof=None):
    output_file = witness_file.replace('.witness.json', '.leader.out')
    if previous_proof:
        command = f"""
        env RUST_BACKTRACE=full RUST_LOG=debug leader --runtime=amqp --amqp-uri=amqp://guest:guest@test-rabbitmq-cluster.zero.svc.cluster.local:5672 stdio --previous-proof {previous_proof} < {witness_file} | tee {output_file}
        """
    else:
        command = f"""
        env RUST_BACKTRACE=full RUST_LOG=debug leader --runtime=amqp --amqp-uri=amqp://guest:guest@test-rabbitmq-cluster.zero.svc.cluster.local:5672 stdio < {witness_file} | tee {output_file}
        """
    try:
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
        if result.stderr:
            return result.stdout, result.stderr
        return result.stdout, None
    except subprocess.CalledProcessError as e:
        return None, e.stderr
    except subprocess.TimeoutExpired:
        return None, "Task execution exceeded the cutoff time."


def process_proof(witness_file):
    output_file = witness_file.replace('.witness.json', '.leader.out')
    proof_file = witness_file.replace('.witness.json', '.proof.json')
    command = f"tail -n1 {output_file} | jq '.[0]' > {proof_file}"
    try:
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to process proof: {result.stderr}")
            return None
        else:
            print(f"Proof successfully processed and saved to {proof_file}")
            return proof_file
    except subprocess.CalledProcessError as e:
        print(f"Failed to process proof: {e.stderr}")
        return None


def fetch_prometheus_metrics(witness_file, start_time, end_time):
    queries = {
        'cpu_usage': 'rate(container_cpu_usage_seconds_total[1m])',
        'memory_usage': 'container_memory_usage_bytes',
        'disk_read': 'rate(node_disk_read_bytes_total[1m])',
        'disk_write': 'rate(node_disk_written_bytes_total[1m])',
        'network_receive': 'rate(node_network_receive_bytes_total[1m])',
        'network_transmit': 'rate(node_network_transmit_bytes_total[1m])'
    }

    metrics = []
    for name, query in queries.items():
        start_str = start_time.replace(microsecond=0).isoformat() + "Z"
        end_str = end_time.replace(microsecond=0).isoformat() + "Z"
        params = {
            'query': query,
            'start': start_str,
            'end': end_str,
            'step': '15s'  # Adjust the step interval as needed
        }
        url = PROMETHEUS_URL + '?' + urlencode(params)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        metrics.append((name, data['data']['result']))

    return metrics


def log_metrics_to_csv(witness_file, metrics):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open('metrics.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        for metric_name, metric_data in metrics:
            row = [starting_block, datetime.now(), metric_name]
            for metric in metric_data:
                values = [value[1] for value in metric['values']]
                row.extend(values)
            writer.writerow(row)


def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'error_{starting_block}.log', mode='w') as file:
        file.write(error_log)
