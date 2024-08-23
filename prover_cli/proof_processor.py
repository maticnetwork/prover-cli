import csv
import json
import os
import subprocess
from datetime import datetime

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
    proof_sequence_file = witness_file.replace('.witness.json', '.proof.sequence')
    proof_file = witness_file.replace('.witness.json', '.proof.json')
    
    # Validate the JSON structure
    validate_command = f"tail -n1 {output_file} | jq empty"
    validate_result = subprocess.run(['sh', '-c', validate_command], capture_output=True, text=True)
    if validate_result.returncode != 0:
        print(f"Failed to validate proof: {validate_result.stderr}")
        return None

    # Save the entire JSON content to .proof.sequence
    sequence_command = f"tail -n1 {output_file} | jq '.'"
    sequence_result = subprocess.run(['sh', '-c', sequence_command], capture_output=True, text=True)
    if sequence_result.returncode != 0:
        print(f"Failed to process proof sequence: {sequence_result.stderr}")
        return None
    
    # Extract the first element of the JSON array and save to .proof
    proof_command = f"tail -n1 {output_file} | jq '.[0]'"
    proof_result = subprocess.run(['sh', '-c', proof_command], capture_output=True, text=True)
    if proof_result.returncode != 0:
        print(f"Failed to extract proof: {proof_result.stderr}")
        return None
    else:
        with open(f'proofs/{proof_file}', 'w') as pf:
            pf.write(proof_result.stdout)
            
    # If everything was successful, delete the .leader.out file
    try:
        os.remove(output_file)
        print(f"Deleted {output_file} successfully.")
    except OSError as e:
        print(f"Error deleting {output_file}: {e.strerror}")
    
    return proof_file

def log_metrics_to_csv(witness_file, metrics, csv_file_path):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    file_exists = os.path.isfile(csv_file_path)
    
    # Ensure the save directory exists
    save_dir = "metrics"
    os.makedirs(save_dir, exist_ok=True)
    metrics_path = f"{save_dir}/{csv_file_path}"
    
    with open(metrics_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['block_number', 'pod_name', 'metric_name', 'data'])
        
        for metric_name, metric_data in metrics:
            for metric in metric_data:
                # Filter for 'zk-evm-worker' pods with the specified image
                if (
                    'pod' in metric['metric'] 
                    and 'zk-evm-worker' in metric['metric']['pod']
                    and metric['metric'].get('image') == 'docker.io/leovct/zk_evm:v0.6.0'
                ):
                    values = [[int(value[0]), float(value[1])] for value in metric['values']]
                    pod_name = metric['metric']['pod']
                    row = [starting_block, pod_name, metric_name, json.dumps(values)]
                    writer.writerow(row)

def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'{errors_logs}/error_{starting_block}.log', mode='w') as file:
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
