import argparse
import os
import json
import time
import threading
from datetime import datetime, timedelta
from prover_cli.prometheus import test_prometheus_connection, fetch_prometheus_metrics
from prover_cli.proof_processor import execute_task, process_proof, log_metrics_to_csv, log_error
from prover_cli.setup_environment import setup_environment

BUFFER_WAIT_TIME = 20
COLLECTION_INTERVAL = 60  # Interval in seconds for metrics collection

class MetricsCollector(threading.Thread):
    def __init__(self, witness_file, stop_event):
        threading.Thread.__init__(self)
        self.witness_file = witness_file
        self.stop_event = stop_event
        self.start_time = datetime.utcnow() - timedelta(seconds=BUFFER_WAIT_TIME)
        self.end_time = datetime.utcnow() + timedelta(seconds=BUFFER_WAIT_TIME)

    def run(self):
        while not self.stop_event.is_set():
            # Fetch Prometheus metrics
            metrics = fetch_prometheus_metrics(self.start_time, self.end_time)
            # Log metrics to CSV
            log_metrics_to_csv(self.witness_file, metrics)
            print(f"Logged metrics to CSV for {self.witness_file}")

            # Update time range for the next collection
            self.start_time = datetime.utcnow() - timedelta(seconds=BUFFER_WAIT_TIME)
            self.end_time = datetime.utcnow() + timedelta(seconds=BUFFER_WAIT_TIME)

            # Wait for the next collection interval or until stopped
            self.stop_event.wait(COLLECTION_INTERVAL)

def run_proofs(begin_block, end_block, witness_dir, previous_proof=None):
    test_prometheus_connection()
    setup_environment()

    for current_block in range(begin_block, end_block + 1):
        current_witness = os.path.join(witness_dir, f"{current_block}.witness.json")
        print(f"Starting task with witness file {current_witness}")

        # Event to signal the metrics collector to stop
        stop_event = threading.Event()

        # Start the metrics collector thread
        metrics_collector = MetricsCollector(current_witness, stop_event)
        metrics_collector.start()

        # Execute the task
        task_start_time = datetime.utcnow()
        output, error = execute_task(current_witness, previous_proof if current_block != begin_block else None)
        task_end_time = datetime.utcnow()

        # Signal the metrics collector to stop
        stop_event.set()
        metrics_collector.join()  # Wait for the metrics collector thread to finish

        # Check if command was executed successfully
        if output:
            print(f"Task with witness file {current_witness} executed successfully.")
            proof_file, cleaned_proof_file = process_proof(current_witness)
        else:
            print(f"Task with witness file {current_witness} failed to execute.")

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

    args = parser.parse_args()

    if args.command == 'run':
        run_proofs(args.begin_block, args.end_block, args.witness_dir, args.previous_proof)
    elif args.command == 'validate':
        validate_proof(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
