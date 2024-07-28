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
        col_widths = [25, 40, 40, 25, 25, 40, 30]  # Adjust these widths as needed
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
    df = pd.read_csv(metrics_csv)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Collect data for the report
    report_data = []
    witness_files = glob.glob(os.path.join(witness_dir, '*.witness.json'))

    for witness_file in witness_files:
        block_number = os.path.basename(witness_file).replace('.witness.json', '')
        block_df = df[df['block_number'] == int(block_number)]
        if block_df.empty:
            continue
        
        start_time = block_df['timestamp'].min()
        end_time = block_df['timestamp'].max()
        duration = (end_time - start_time).total_seconds()
        max_cpu = block_df[block_df['metric_name'] == 'cpu_usage']['values'].apply(lambda x: max(json.loads(x), key=lambda y: y[1])[1] if x else 0).max()
        max_memory = block_df[block_df['metric_name'] == 'memory_usage']['values'].apply(lambda x: max(json.loads(x), key=lambda y: y[1])[1] if x else 0).max()

        with open(witness_file, 'r') as f:
            witness_data = json.load(f)
            txn_count = len(witness_data[0]['block_trace']['txn_info'])

        report_data.append([block_number, start_time, end_time, duration, max_cpu, max_memory, txn_count])

    # Generate PDF
    pdf = PDF()
    pdf.add_page()
    pdf.add_table(report_data)
    output_filename = f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(output_filename)
    print(f"Report generated: {output_filename}")
