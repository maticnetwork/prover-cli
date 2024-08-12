import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
from prover_cli.proof_processor import log_metrics_to_csv

PROMETHEUS_URL = 'http://localhost:9090/api/v1/query_range'

def test_prometheus_connection():
    try:
        response = requests.get(PROMETHEUS_URL.replace("/query_range", "/targets"))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error connecting to Prometheus:", e)
        exit(1)

def fetch_prometheus_metrics(start_time, end_time):
    queries = {
        'memory_usage': 'container_memory_usage_bytes',
    }
    
    metrics = []
    for name, query in queries.items():
        start_str = start_time.replace(microsecond=0).isoformat() + "Z"
        end_str = end_time.replace(microsecond=0).isoformat() + "Z"
        params = {
            'query': query,
            'start': start_str,
            'end': end_str,
            'step': '5s'
        }
        url = PROMETHEUS_URL + '?' + urlencode(params)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        metrics.append((name, data['data']['result']))
    
    return metrics
    
if __name__ == "__main__":
    test_prometheus_connection()
    # Set the time range for the query
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=10)
    
    # Simulate a witness file name for testing
    witness_file = "123.witness.json"

    metrics = fetch_prometheus_metrics(start_time, end_time)
    print(metrics)
    log_metrics_to_csv(witness_file, metrics)
    print("Fetched metrics:", metrics)
