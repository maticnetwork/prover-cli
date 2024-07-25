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

    start_time = datetime.utcnow()

    try:
        result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        print(f"Command output: {result.stdout}")
        if result.stderr:
            print(f"Command error: {result.stderr}")

        return result.stdout, result.stderr if result.stderr else None, duration
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        return None, e.stderr, 0
