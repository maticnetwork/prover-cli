import subprocess
import os

def execute_task(witness_file, previous_proof=None):
    output_file = witness_file.replace('/tmp/witnesses/', '/tmp/proofs/proof-').replace('.witness.json', '.leader.out')
    
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

def validate_and_extract_proof(witness_file):
    proof_file = witness_file.replace('.witness.json', '.witness.json.proof')
    output_file = witness_file.replace('/tmp/witnesses/', '/tmp/proofs/proof-').replace('.witness.json', '.leader.out')
    
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
        json_start_index = None
        for i, line in enumerate(lines):
            if line.startswith('['):
                json_start_index = i
                break
        if json_start_index is not None:
            json_content = ''.join(lines[json_start_index:])
        else:
            raise ValueError("No JSON content found in the output file.")
        
        proof = subprocess.run(
            ['jq', '.[0]'],
            input=json_content,
            text=True,
            capture_output=True,
            check=True
        ).stdout
        
        with open(proof_file, 'w') as f:
            f.write(proof)
        
        return proof_file
    except Exception as e:
        print(f"Failed to process proof: {e}")
        return None

def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'error_{starting_block}.log', mode='w') as file:
        file.write(error_log)

