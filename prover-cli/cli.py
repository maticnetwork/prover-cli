#!/usr/bin/env python3

import argparse
from prover_cli.prometheus import test_prometheus_connection, fetch_prometheus_metrics, log_metrics_to_csv
from prover_cli.setup_environment import setup_environment
from prover_cli.proof_processor import execute_task, validate_and_extract_proof, log_error
import time
from datetime import datetime, timedelta

BUFFER_WAIT_TIME = 20

def main(begin_block, end_block, witness_dir):
    test_prometheus_connection()
    setup_environment()

    previous_proof = None
    for current_block in range(begin_block, end_block + 1):
        current_witness = f"{witness_dir}/{current_block}.witness.json"
        print(f"Starting task with witness file {current_witness}")

        start_time = datetime.utcnow() - timedelta(seconds=BUFFER_WAIT_TIME)
        end_time = datetime.utcnow() + timedelta(seconds=BUFFER_WAIT_TIME)

        task_start_time = datetime.utcnow()
        output, error = execute_task(current_witness, previous_proof if current_block != begin_block else None)
        task_end_time = datetime.utcnow()

        if output:
            print(f"Task with witness file {current_witness} executed successfully.")
            previous_proof = validate_and_extract_proof(current_witness)
        else:
            print(f"Task with witness file {current_witness} failed to execute.")

        time.sleep(BUFFER_WAIT_TIME)

        metrics = fetch_prometheus_metrics(current_witness, start_time, end_time)
        log_metrics_to_csv(current_witness, metrics)

        if error:
            log_error(current_witness, error)

        print(f"Completed task with witness file {current_witness}")

        time.sleep(BUFFER_WAIT_TIME)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run block proving tasks and collect performance metrics.')
    parser.add_argument('--begin_block', type=int, required=True, help='Beginning block number.')
    parser.add_argument('--end_block', type=int, required=True, help='Ending block number.')
    parser.add_argument('--witness_dir', type=str, required=True, help='Directory where witness files are stored.')

    args = parser.parse_args()
    main(args.begin_block, args.end_block, args.witness_dir)

