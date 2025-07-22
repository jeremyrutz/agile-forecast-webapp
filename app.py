
from flask import Flask, render_template, request
import numpy as np
import random
from datetime import datetime, timedelta
import os
import csv
import tempfile

app = Flask(__name__)

def load_throughput_data(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    throughputs = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for value in row:
                value = value.strip()
                if value:
                    throughputs.append(float(value))
    if not throughputs:
        raise ValueError("No valid throughput values found in CSV.")
    return throughputs

def run_simulation(params):
    base_date = datetime.strptime(params['start_date'], "%Y-%m-%d") if params['start_date'] else datetime.today()
    throughput_data = load_throughput_data(params['csv_file_path'])
    num_items = params['num_items']
    num_completed = params['num_completed']
    timeframe_weeks = params.get('timeframe_weeks', 1)
    throughput_sigma = params.get('throughput_sigma', 10)
    num_simulations = 10000
    completion_dates = []
    for _ in range(num_simulations):
        completed = num_completed
        current_week = 0
        while completed < num_items:
            throughput = random.choice(throughput_data)
            completed += random.normalvariate(throughput / timeframe_weeks, throughput_sigma)
            current_week += 1
        completion_date = base_date + timedelta(weeks=current_week)
        completion_dates.append(completion_date)
    completion_dates_np = np.array([(date - base_date).days for date in completion_dates])
    projected_dates = {
        '95%': base_date + timedelta(days=int(np.percentile(completion_dates_np, 95))),
        '85%': base_date + timedelta(days=int(np.percentile(completion_dates_np, 85))),
        '60%': base_date + timedelta(days=int(np.percentile(completion_dates_np, 60))),
    }
    return projected_dates

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    error = None
    results = None
    csv_file_path = None
    try:
        # Validate and parse form fields
        try:
            num_items = int(request.form['num_items'])
            num_completed = int(request.form['num_completed'])
            timeframe_weeks = int(request.form['timeframe_weeks'])
            throughput_sigma = float(request.form['throughput_sigma'])
            start_date = request.form.get('start_date', '')
        except Exception as e:
            error = f"Invalid input: {str(e)}"
            return render_template('index.html', error=error)

        # Handle file upload
        csv_file = request.files.get('csv_file')
        if not csv_file or csv_file.filename == '':
            error = "No CSV file uploaded."
            return render_template('index.html', error=error)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            csv_file.save(tmp.name)
            csv_file_path = tmp.name

        params = {
            'num_items': num_items,
            'num_completed': num_completed,
            'timeframe_weeks': timeframe_weeks,
            'throughput_sigma': throughput_sigma,
            'start_date': start_date,
            'csv_file_path': csv_file_path
        }

        try:
            results = run_simulation(params)
        except Exception as e:
            error = f"Simulation error: {str(e)}"
        finally:
            if csv_file_path and os.path.exists(csv_file_path):
                os.remove(csv_file_path)

        return render_template('index.html', error=error, results=results)

    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)