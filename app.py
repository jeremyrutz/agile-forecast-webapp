def get_int_form_value(form, key, default):
    value = form.get(key)
    if value is None or value.strip() == '':
        return default
    return int(value)

def get_float_form_value(form, key, default):
    value = form.get(key)
    if value is None or value.strip() == '':
        return default
    return float(value)

from flask import Flask, render_template, request
import numpy as np
import random
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server environments
import matplotlib.pyplot as plt
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
    projected_completion_date_95 = base_date + timedelta(days=int(np.percentile(completion_dates_np, 95)))
    projected_completion_date_85 = base_date + timedelta(days=int(np.percentile(completion_dates_np, 85)))
    projected_completion_date_60 = base_date + timedelta(days=int(np.percentile(completion_dates_np, 60)))
    projected_dates = {
        '95%': projected_completion_date_95,
        '85%': projected_completion_date_85,
        '60%': projected_completion_date_60,
    }

    # Plot histogram and save to static folder (absolute path)
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    plot_filename = os.path.join(static_dir, 'completion_histogram.png')
    # Delete previous plot if exists
    if os.path.exists(plot_filename):
        os.remove(plot_filename)
    plt.figure(figsize=(10,6))
    plt.hist([base_date + timedelta(days=int(d)) for d in completion_dates_np], bins=50, color='skyblue', edgecolor='black')
    plt.axvline(projected_completion_date_95, color='yellow', linestyle='--', label='{} (95%)'.format(projected_completion_date_95.date()))
    plt.axvline(projected_completion_date_85, color='red', linestyle='--', label='{} (85%)'.format(projected_completion_date_85.date()))
    plt.axvline(projected_completion_date_60, color='green', linestyle='--', label='{} (60%)'.format(projected_completion_date_60.date()))
    plt.title('Estimated Completion Dates of All {} Items'.format(num_items))
    plt.xlabel('Estimated Completion Date')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()
    # Return relative path for Flask template usage
    return projected_dates, 'static/completion_histogram.png'

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
            timeframe_weeks = get_int_form_value(request.form, 'timeframe_weeks', 1)
            throughput_sigma = get_float_form_value(request.form, 'throughput_sigma', 10)
            start_date = request.form.get('start_date') or datetime.today().strftime('%Y-%m-%d')
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
            results, plot_filename = run_simulation(params)
        except Exception as e:
            error = f"Simulation error: {str(e)}"
            plot_filename = None
        finally:
            if csv_file_path and os.path.exists(csv_file_path):
                os.remove(csv_file_path)

        return render_template('index.html', error=error, results=results, plot_filename=plot_filename, params=params)

    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)