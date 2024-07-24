import argparse
import os
import json
import time
from datetime import datetime, timedelta
from prover_cli.prometheus import test_prometheus_connection, fetch_prometheus_metrics
from prover_cli.proof_processor import execute_task, process_proof, validate_and_extract_proof, log_metrics_to_csv, log_error
from prover_cli.setup_environment import setup_environment
from prover_cli.plotting import plot_and_analyze

BUFFER_WAIT_TIME = 20

def run_proofs(begin_block, end_block, witness_dir, previous_proof):
    test_prometheus_connection()
    setup_environment()

    for current_block in range(begin_block, end_block + 1):
        current_witness = os.path.join(witness_dir, f"{current_block}.witness.json")
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
    try:
        proof_file = process_proof(input_file)
        if proof_file:
            with open(proof_file, 'r') as pf:
                proof = json.load(pf)
            with open(output_file, 'w') as f:
                json.dump(proof, f, indent=2)
            print(f"Extracted proof: {proof}")
        else:
            print(f"Failed to validate and extract proof from {input_file}")
    except Exception as e:
        print(f"Failed to validate and extract proof: {e}")

def main():
    parser = argparse.ArgumentParser(description='Prover CLI Tool')
    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser('run', help='Run block proving tasks and collect performance metrics.')
    run_parser.add_argument('--begin_block', type=int, required=True, help='Beginning block number.')
    run_parser.add_argument('--end_block', type=int, required=True, help='Ending block number.')
    run_parser.add_argument('--witness_dir', type=str, required=True, help='Directory containing witness files.')
    run_parser.add_argument('--previous-proof', type=str, help='Previous proof file for validation.')

    validate_parser = subparsers.add_parser('validate', help='Validate and extract proof from leader.out file.')
    validate_parser.add_argument('--input_file', type=str, required=True, help='Input leader.out file.')
    validate_parser.add_argument('--output_file', type=str, required=True, help='Output cleaned proof file.')

    plot_parser = subparsers.add_parser('plot', help='Plot and analyze metrics data.')
    plot_parser.add_argument('--csv_file', type=str, required=True, help='CSV file containing metrics data.')
    plot_parser.add_argument('--metric_name', type=str, required=True, help='Metric name to plot and analyze.')
    plot_parser.add_argument('--block_number', type=int, required=True, help='Block number to plot and analyze.')
    plot_parser.add_argument('--threshold', type=float, required=True, help='Threshold for anomaly detection.')

    args = parser.parse_args()

    if args.command == 'run':
        run_proofs(args.begin_block, args.end_block, args.witness_dir, args.previous_proof)
    elif args.command == 'validate':
        validate_proof(args.input_file, args.output_file)
    elif args.command == 'plot':
        plot_and_analyze(args.csv_file, args.metric_name, args.block_number, args.threshold)

if __name__ == "__main__":
    main()
