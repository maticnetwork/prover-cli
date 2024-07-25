from datetime import datetime, timedelta
import time
import argparse
import os
import pandas as pd
from prover_cli.prometheus import test_prometheus_connection, fetch_prometheus_metrics
from prover_cli.proof_processor import execute_task, process_proof, validate_and_extract_proof, log_metrics_to_csv, log_error
from prover_cli.setup_environment import setup_environment
from prover_cli.report_generator import generate_report

BUFFER_WAIT_TIME = 20

def run_proofs(begin_block, end_block, witness_dir, previous_proof):
    test_prometheus_connection()
    setup_environment()

    durations = {}  # Dictionary to store durations for each block

    for current_block in range(begin_block, end_block + 1):
        current_witness = os.path.join(witness_dir, f"{current_block}.witness.json")
        print(f"Starting task with witness file {current_witness}")

        # Determine the time range for metrics collection
        start_time = datetime.utcnow() - timedelta(seconds=BUFFER_WAIT_TIME)
        end_time = datetime.utcnow() + timedelta(seconds=BUFFER_WAIT_TIME)

        # Execute the task
        output, error, duration = execute_task(current_witness, previous_proof if current_block != begin_block else None)

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

        # Store the duration for the current block
        durations[current_block] = duration

        print(f"Completed task with witness file {current_witness}")

        # Cool-down period
        time.sleep(BUFFER_WAIT_TIME)

    return durations

def main():
    parser = argparse.ArgumentParser(description='Prover CLI')
    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run', help='Run proofs')
    run_parser.add_argument('--begin_block', type=int, required=True, help='Beginning block number.')
    run_parser.add_argument('--end_block', type=int, required=True, help='Ending block number.')
    run_parser.add_argument('--witness_dir', type=str, required=True, help='Directory containing witness files.')
    run_parser.add_argument('--previous-proof', type=str, help='File containing previous proof for validation.')

    validate_parser = subparsers.add_parser('validate', help='Validate and extract proof from leader.out file')
    validate_parser.add_argument('--input_file', type=str, required=True, help='Path to the input leader.out file.')
    validate_parser.add_argument('--output_file', type=str, required=True, help='Path to the output proof file.')

    report_parser = subparsers.add_parser('report', help='Generate a metrics summary report')
    report_parser.add_argument('--csv_file', type=str, required=True, help='CSV file with metrics data')
    report_parser.add_argument('--witness_dir', type=str, required=True, help='Directory containing witness files')

    args = parser.parse_args()

    if args.command == 'run':
        durations = run_proofs(args.begin_block, args.end_block, args.witness_dir, args.previous_proof)
        generate_report(args.csv_file, args.witness_dir, durations)
    elif args.command == 'validate':
        validate_proof(args.input_file, args.output_file)
    elif args.command == 'report':
        generate_report(args.csv_file, args.witness_dir, None)

if __name__ == "__main__":
    main()
