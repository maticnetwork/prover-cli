import argparse
from prover_cli.prometheus import test_prometheus_connection, fetch_prometheus_metrics
from prover_cli.proof_processor import execute_task, process_proof, validate_and_extract_proof
from prover_cli.setup_environment import setup_environment
import os
from datetime import datetime, timedelta
import time

BUFFER_WAIT_TIME = 20  # buffer time before, after task, and time to wait after task completion for metrics to land

def main():
    parser = argparse.ArgumentParser(description='Run block proving tasks and collect performance metrics.')
    parser.add_argument('--begin_block', type=int, required=True, help='Beginning block number.')
    parser.add_argument('--end_block', type=int, required=True, help='Ending block number.')
    parser.add_argument('--witness_dir', type=str, required=True, help='Directory where witness files are stored.')

    args = parser.parse_args()
    run_prover(args.begin_block, args.end_block, args.witness_dir)

def run_prover(begin_block, end_block, witness_dir):
    test_prometheus_connection()
    setup_environment()

    previous_proof = None
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

def log_metrics_to_csv(witness_file, metrics):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open('metrics.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        for metric_name, metric_data in metrics:
            row = [starting_block, datetime.now(), metric_name]
            for metric in metric_data:
                values = [value[1] for value in metric['values']]
                row.extend(values)
            writer.writerow(row)

def log_error(witness_file, error_log):
    starting_block = os.path.basename(witness_file).replace('.witness.json', '')
    with open(f'error_{starting_block}.log', mode='w') as file:
        file.write(error_log)

