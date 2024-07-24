# Prover CLI

Prover CLI is a tool for running block proving tasks and collecting performance metrics. It interacts with Prometheus to fetch metrics and processes proofs for a range of witnesses.


## Prerequisites

- Python 3.x
- jq 1.7 or higher
- Prometheus set up and running
- Witness files generated using Jerigon


## Installation

# Clone the repository
git clone https://github.com/rebelArtists/prover_cli.git

# Navigate to your project directory
cd prover_cli

# Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package in editable mode
pip install -e .

# Run unit tests
python -m unittest discover -s tests


## Usage

## Set Up Port Forwarding
Before running the CLI, set up port forwarding for Prometheus for metric tracking:

kubectl port-forward --namespace kube-prometheus --address localhost svc/prometheus-operated 9090:9090


## Run the CLI
To run the CLI tool:

prover-cli --begin_block 20362226 --end_block 20362237 --witness_dir /tmp/witnesses


## Review Metrics
Performance metrics are saved in metrics.csv in the current directory. Each row contains metrics for a specific witness.


## Validate Proofs
The CLI tool automatically validates and extracts proofs for each witness. The proofs are saved in the /tmp/proofs directory.


## Example
kubectl port-forward --namespace kube-prometheus --address localhost svc/prometheus-operated 9090:9090
prover-cli --begin_block 20362226 --end_block 20362237 --witness_dir /tmp/witnesses


## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License.

