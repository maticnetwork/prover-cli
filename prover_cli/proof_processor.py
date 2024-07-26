import subprocess
import json
import os
from datetime import datetime
import csv

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
        for metric_name, metric_data in metrics:
            # Debug print to inspect metric_data
            print(f"Metric Name: {metric_name}")
            print(f"Metric Data: {metric_data}")
            
            # Handle the case where metric_data might not be a list
            if isinstance(metric_data, dict) and 'values' in metric_data:
                values = [[value[0], value[1]] for value in metric_data['values']]
            else:
                # If metric_data is not in the expected format, skip or handle it
                print(f"Unexpected format for metric_data: {metric_data}")
                continue
            
            row = [starting_block, datetime.now(), metric_name, values, start_time.isoformat(), end_time.isoformat()]
            writer.writerow(row)

def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'error_{starting_block}.log', mode='w') as file:
        file.write(error_log)
