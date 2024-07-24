import subprocess
import os
import json
import tempfile

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
        print(f"Command error: {result.stderr}")
        return result.stdout, result.stderr if result.stderr else None
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        return None, e.stderr

def process_proof(witness_file):
    output_file = witness_file.replace('.witness.json', '.leader.out')
    proof_file = witness_file.replace('.witness.json', '.proof.json')

    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
            json_content = ''.join(lines[3:])
            json.loads(json_content)  # Validate JSON format
            with open(proof_file, 'w') as proof_f:
                proof_f.write(json_content)
        return proof_file
    except (json.JSONDecodeError, IndexError, FileNotFoundError) as e:
        print(f"Failed to process proof: {e}")
        return None

def validate_and_extract_proof(raw_json):
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_input:
            temp_input.write(raw_json)
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path + ".proof"

        # Use shell command to process the proof
        command = f'tail -n1 {temp_input_path} | jq \'.[0]\' > {temp_output_path}'
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Failed to process proof: {result.stderr}")
            return None
        
        with open(temp_output_path, 'r') as temp_output:
            proof = temp_output.read().strip()

        return proof
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        return None

