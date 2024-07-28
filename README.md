# Prover-CLI

Prover-CLI is a command-line tool for processing and validating blockchain proofs.


## Prerequisites

- Python 3.6+
- Prometheus set up and running on your service
- Witness files generated using Jerigon


## Installation

git clone https://github.com/rebelArtists/prover_cli.git
cd prover_cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements && pip install -e .


# Usage

## Set Up Port Forwarding
Before running the CLI, set up port forwarding for Prometheus for metric tracking:

nohup kubectl port-forward --namespace kube-prometheus --address localhost svc/prometheus-operated 9090:9090 &


## Prove Range of Witnesses

prover-cli run --begin_block 123 --end_block 124 --witness_dir /path/to/witnesses


## Validate and Extract Proof

prover-cli validate --input_file /path/to/leader.out --output_file /path/to/cleaned_proof.json


## Plot Prover Metrics

prover-cli plot --csv_file metrics.csv --metric_name network_transmit --block_number 123


## Creating Final Performance Report

prover-cli report --witness_dir /tmp/prover_cli --metrics_csv /tmp/prover_cli/metrics.csv


## Review Metrics
Performance metrics are saved in metrics.csv in the current directory. Each row contains a unique metric
tagged by witness id


## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.


## License
This project is licensed under the MIT License.

