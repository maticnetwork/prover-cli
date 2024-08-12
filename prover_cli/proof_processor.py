import csv
import json
import os
import subprocess
from datetime import datetime
from metrics_logger import log_metrics_to_csv

def execute_task(witness_file, previous_proof=None):
    output_file = witness_file.replace('.witness.json', '.leader.out')
    
    if previous_proof:
        command = f"""
        env RUST_BACKTRACE=full RUST_LOG=info leader --runtime=amqp --amqp-uri=amqp://guest:guest@rabbitmq-cluster.zk-evm.svc.cluster.local:5672 stdio --previous-proof {previous_proof} < {witness_file} | tee {output_file}
        """
    else:
        command = f"""
        env RUST_BACKTRACE=full RUST_LOG=debug leader --runtime=amqp --amqp-uri=amqp://guest:guest@rabbitmq-cluster.zk-evm.svc.cluster.local:5672 stdio < {witness_file} | tee {output_file}
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
    
    command = f"tail -n1 {output_file} | jq '.'"
    try:
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to process proof: {result.stderr}")
            return None
        else:
            proof_json = json.loads(result.stdout)
            with open(proof_file, 'w') as pf:
                json.dump(proof_json, pf, indent=2)
            return proof_file
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Failed to process proof: {e}")
        return None

def log_metrics_to_csv(witness_file, metrics):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file_path = f'metrics_{timestamp}.csv'
    file_exists = os.path.isfile(csv_file_path)
    
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['block_number', 'metric_name', 'data'])
            
        for metric_name, metric_data in metrics:
            for metric in metric_data:
                values = [[int(value[0]), float(value[1])] for value in metric['values']]
            row = [starting_block, metric_name, json.dumps(values)]
            writer.writerow(row)

def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'error_{starting_block}.log', mode='w') as file:
        file.write(error_log)

def validate_and_extract_proof(raw_json):
    try:
        # Use subprocess to process the raw JSON and extract proof
        result = subprocess.run(['sh', '-c', f'echo \'{raw_json}\' | jq .'], capture_output=True, text=True)
        if result.returncode == 0:
            proof_json = json.loads(result.stdout)
            return proof_json  # Return the cleaned proof
        else:
            print(f"Failed to process proof: {result.stderr}")
            return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Failed to decode JSON: {e}")
        return None

