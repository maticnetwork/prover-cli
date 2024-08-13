import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

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
        'memory_usage': 'container_memory_usage_bytes / (1073741824)', # memory use in GB
        'cpu_usage': 'rate (container_cpu_usage_seconds_total{image!=""}[1m])' # percent of cpu usage
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
