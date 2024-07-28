from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Performance Report', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_table(self, data):
        self.set_font('Arial', 'B', 10)
        col_widths = [30, 45, 45, 30, 25, 35, 35]  # Adjust these widths as needed
        headers = ['Block Number', 'Start Time', 'End Time', 'Duration (s)', 'Max CPU', 'Max Memory', 'Transaction Count']
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()
        
        self.set_font('Arial', '', 10)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, str(item), 1)
            self.ln()

def generate_report(witness_dir, metrics_csv):
    import pandas as pd
    import os
    import glob
    import json

    # Load metrics data
    df = pd.read_csv(metrics_csv, names=['block_number', 'metric_name', 'data'])

    # Collect data for the report
    report_data = []
    witness_files = glob.glob(os.path.join(witness_dir, '*.witness.json'))

    for witness_file in witness_files:
        block_number = os.path.basename(witness_file).replace('.witness.json', '')
        block_df = df[df['block_number'] == int(block_number)]
        if block_df.empty:
            continue
        
        # Initialize variables for start_time, end_time, and max values
        start_time = None
        end_time = None
        max_cpu = 0
        max_memory = 0

        for index, row in block_df.iterrows():
            data = json.loads(row['data'])
            if not data:
                continue

            # Calculate start_time and end_time
            if start_time is None or data[0][0] < start_time:
                start_time = data[0][0]
            if end_time is None or data[-1][0] > end_time:
                end_time = data[-1][0]

            # Update max values for CPU and memory
            if row['metric_name'] == 'cpu_usage':
                max_cpu = max(max_cpu, max(value[1] for value in data))
            elif row['metric_name'] == 'memory_usage':
                max_memory = max(max_memory, max(value[1] for value in data))

        # Convert start_time and end_time to datetime objects
        start_time = datetime.utcfromtimestamp(start_time)
        end_time = datetime.utcfromtimestamp(end_time)
        duration = (end_time - start_time).total_seconds()

        with open(witness_file, 'r') as f:
            witness_data = json.load(f)
            txn_count = len(witness_data[0]['block_trace']['txn_info'])

        report_data.append([block_number, start_time, end_time, duration, max_cpu, max_memory, txn_count])

    # Generate PDF in landscape mode
    pdf = PDF(orientation='L')
    pdf.add_page()
    pdf.add_table(report_data)
    output_filename = f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(output_filename)
    print(f"Report generated: {output_filename}")
