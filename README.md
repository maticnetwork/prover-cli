
# Prover-CLI

Prover-CLI is a command-line tool for processing and validating blockchain proofs.

## General Prerequisites

- Python 3.6+
- Prometheus set up and running on your service
- Witness files generated using Jerigon

## Required Package Dependencies and Installation

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
&& install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
&& echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
| tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

apt-get update \
&& apt-get install -y python3 python3-pip python3-venv screen google-cloud-cli google-cloud-cli-gke-gcloud-auth-plugin

git clone https://github.com/rebelArtists/prover_cli.git /opt/prover_cli
cd /opt/prover_cli
pip install -r requirements.txt && pip install -e .
```

## Required Auth Setup

```bash
gcloud auth login
gcloud container clusters get-credentials <your_cluster> --region=europe-west3
screen -dmS prometheus-port-forward bash -c 'kubectl port-forward --namespace kube-prometheus --address localhost svc/prometheus-operated 9090:9090'
```

## Usage

### Prove Range of Witnesses

```bash
prover-cli run --begin_block 123 --end_block 124 --witness_dir /path/to/witnesses
```

### Validate and Extract Proof

```bash
prover-cli validate --input_file /path/to/leader.out --output_file /path/to/cleaned_proof.json
```

### Plot Prover Metrics

```bash
prover-cli plot --csv_file metrics.csv --metric_name memory_usage --block_number 123
```

### Creating Final Performance Report

```bash
prover-cli report --witness_dir /tmp/prover_cli --metrics_csv /tmp/prover_cli/metrics.csv
```

## Review Metrics

CPU and memory metrics, per worker pod, are saved in `metrics_{timestamp}.csv` in the current directory. Each row contains a unique metric tagged by witness ID.

## Performance Report

A per-witness summary performance report is auto-generated after each job. It is found in `performance_report_{timestamp}.csv`, detailing the average and max CPU/memory used to prove each witness ID.

## Plots

A series of Matplotlib visuals are auto-generated after each run, depicting the timeseries change of CPU/memory per witness ID, per worker.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.
