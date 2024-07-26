import subprocess
import json
import os
import requests
from datetime import datetime
import csv

def fetch_prometheus_metrics(prometheus_url, queries, start_time, end_time):
    results = {}
    for metric, query in queries.items():
        response = requests.get(prometheus_url, params={'query': query})
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                results[metric] = [
                    {
                        "timestamp": value[0],
                        "value": value[1]
                    } for value in data['data']['result'][0]['values']
                ]
            else:
                print(f"Failed to retrieve data for {metric}: {data['error']}")
        else:
            print(f"Failed to retrieve data for {metric}: HTTP {response.status_code}")
    return results

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
    
    print(f"Executing command: {command}")

    try:
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
        if result.stderr:
            print(f"Command error: {result.stderr}")
        return result.stdout, result.stderr if result.stderr else None
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        return None, e.stderr

def process_proof(witness_file):
    output_file = witness_file.replace('.witness.json', '.leader.out')
    proof_file = witness_file.replace('.witness.json', '.proof.json')
    cleaned_proof_file = witness_file.replace('.witness.json', '.cleaned.proof.json')
    command = f"tail -n1 {output_file} | jq '.'"
    try:
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to process proof: {result.stderr}")
            return None, None
        else:
            proof_json = json.loads(result.stdout)
            with open(proof_file, 'w') as pf:
                json.dump(proof_json, pf, indent=2)
            with open(cleaned_proof_file, 'w') as cpf:
                json.dump(proof_json, cpf, indent=2)
            return proof_file, cleaned_proof_file
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Failed to process proof: {e}")
        return None, None

def log_metrics_to_csv(witness_file, metrics, start_time, end_time):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open('metrics.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        for metric_name, values in metrics.items():
            row = [starting_block, metric_name, start_time.isoformat(), end_time.isoformat(), (end_time - start_time).total_seconds(), json.dumps(values)]
            writer.writerow(row)
    print(f"Metrics for witness file {witness_file} logged successfully.")


def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'error_{starting_block}.log', mode='w') as file:
        file.write(error_log)
