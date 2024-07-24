import argparse
from prover_cli.proof_processor import process_proof, validate_and_extract_proof, execute_task
from prover_cli.prometheus import test_prometheus_connection, fetch_prometheus_metrics
from prover_cli.setup_environment import setup_environment
import os
import time
from datetime import datetime, timedelta

def run_proofs(begin_block, end_block, witness_dir, previous_proof=None):
    setup_environment()

    previous_proof = previous_proof
    for current_block in range(begin_block, end_block + 1):
        current_witness = f"{witness_dir}/{current_block}.witness.json"
        print(f"Starting task with witness file {current_witness}")

        # Determine the time range for metrics collection
        start_time = datetime.utcnow() - timedelta(seconds=BUFFER_WAIT_TIME)
        end_time = datetime.utcnow() + timedelta(seconds=BUFFER_WAIT_TIME)

        # Execute the task
        task_start_time = datetime.utcnow()
        output, error = execute_task(current_witness, previous_proof if current_block != begin_block else None)
        task_end_time = datetime.utcnow()

        # Check if command was executed successfully
        if output:
            print(f"Task with witness file {current_witness} executed successfully.")
            previous_proof = process_proof(current_witness)
        else:
            print(f"Task with witness file {current_witness} failed to execute.")

        # Wait for metrics to land
        time.sleep(BUFFER_WAIT_TIME)

        # Fetch Prometheus metrics
        metrics = fetch_prometheus_metrics(current_witness, start_time, end_time)

        # Log metrics to CSV
        log_metrics_to_csv(current_witness, metrics)

        # Log errors if any
        if error:
            log_error(current_witness, error)

        print(f"Completed task with witness file {current_witness}")

        # Cool-down period
        time.sleep(BUFFER_WAIT_TIME)

def validate_proof(input_file, output_file):
    with open(input_file, 'r') as f:
        raw_json = f.read()
    
    proof = validate_and_extract_proof(raw_json)
    
    if proof is not None:
        with open(output_file, 'w') as f:
            f.write(proof)
        print(f"Proof successfully validated and written to {output_file}")
    else:
        print(f"Failed to validate and extract proof from {input_file}")

def main():
    parser = argparse.ArgumentParser(description='Prover CLI tool for processing and validating proofs.')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run block proving tasks')
    run_parser.add_argument('--begin_block', type=int, required=True, help='Beginning block number.')
    run_parser.add_argument('--end_block', type=int, required=True, help='Ending block number.')
    run_parser.add_argument('--witness_dir', type=str, required=True, help='Directory where witness files are stored.')
    run_parser.add_argument('--previous-proof', type=str, help='File location of a previous proof for single block processing.')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a proof from leader.out')
    validate_parser.add_argument('--input_file', type=str, required=True, help='Input leader.out file to be validated and processed.')
    validate_parser.add_argument('--output_file', type=str, required=True, help='Output proof file to be generated.')

    args = parser.parse_args()

    if args.command == 'run':
        run_proofs(args.begin_block, args.end_block, args.witness_dir, args.previous_proof)
    elif args.command == 'validate':
        validate_proof(args.input_file, args.output_file)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

