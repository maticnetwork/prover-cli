import os
import pandas as pd
import json
from datetime import datetime
from fpdf import FPDF

def get_tx_count(witness_file):
    with open(witness_file, 'r') as f:
        data = json.load(f)
    return len(data[0]['block_trace']['txn_info'])

def generate_report(witness_dir, metrics_csv):
    data = pd.read_csv(metrics_csv)
    summary_data = []

    for witness_file in os.listdir(witness_dir):
        if witness_file.endswith('.witness.json'):
            witness_path = os.path.join(witness_dir, witness_file)
            block_number = witness_file.replace('.witness.json', '')

            # Filter metrics for the current witness
            subset = data[data['block_number'] == int(block_number)]

            if subset.empty:
                continue

            start_time = min([datetime.utcfromtimestamp(ts) for metric in subset['data'] for ts, _ in json.loads(metric)])
            end_time = max([datetime.utcfromtimestamp(ts) for metric in subset['data'] for ts, _ in json.loads(metric)])
            duration = (end_time - start_time).total_seconds()

            max_cpu = max([max([val for _, val in json.loads(metric) if 'cpu_usage' in metric_name]) for metric_name, metric in zip(subset['metric_name'], subset['data']) if 'cpu_usage' in metric_name])
            max_memory = max([max([val for _, val in json.loads(metric) if 'memory_usage' in metric_name]) for metric_name, metric in zip(subset['metric_name'], subset['data']) if 'memory_usage' in metric_name])

            tx_count = get_tx_count(witness_path)

            summary_data.append({
                'block_number': block_number,
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': duration,
                'max_cpu': max_cpu,
                'max_memory': max_memory,
                'tx_count': tx_count
            })

    # Generate PDF report in a table format
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Performance Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    col_width = pdf.w / 7
    row_height = pdf.font_size * 1.5

    headers = ['Block Number', 'Start Time', 'End Time', 'Duration (s)', 'Max CPU', 'Max Memory', 'Transaction Count']
    for header in headers:
        pdf.cell(col_width, row_height, txt=header, border=1, align='C')

    pdf.ln(row_height)

    for summary in summary_data:
        pdf.cell(col_width, row_height, txt=str(summary['block_number']), border=1)
        pdf.cell(col_width, row_height, txt=summary['start_time'], border=1)
        pdf.cell(col_width, row_height, txt=summary['end_time'], border=1)
        pdf.cell(col_width, row_height, txt=str(summary['duration']), border=1)
        pdf.cell(col_width, row_height, txt=str(summary['max_cpu']), border=1)
        pdf.cell(col_width, row_height, txt=str(summary['max_memory']), border=1)
        pdf.cell(col_width, row_height, txt=str(summary['tx_count']), border=1)
        pdf.ln(row_height)

    report_file = f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(report_file)
    print(f"Report saved to {report_file}")
