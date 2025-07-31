from flask import Flask, render_template, request
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server environments
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import tempfile

# === Import the simulation logic from your src directory ===
from src.simulation import run_simulation  # assumes project structure is correct

app = Flask(__name__)

# Utility functions to extract values from the form
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

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    error = None
    results = None
    plot_filename = None  # This will hold the *relative URL* for the template
    csv_file_path = None

    try:
        # Parse form input
        try:
            num_items = int(request.form['num_items'])
            # num_completed = int(request.form['num_completed'])
            num_completed = get_int_form_value(request.form, 'num_completed', 0)
            if num_completed > num_items:
                raise ValueError("Number of completed items cannot exceed total number of items.")
            if num_completed < 0:
                raise ValueError("Number of completed items cannot be negative.")
            if num_items <= 0:
                raise ValueError("Number of items must be a positive integer.")
            
            timeframe_weeks = get_int_form_value(request.form, 'timeframe_weeks', 1)
            throughput_sigma = get_float_form_value(request.form, 'throughput_sigma', 10)
            start_date = request.form.get('start_date') or datetime.today().strftime('%Y-%m-%d')
        except Exception as e:
            error = f"Invalid input: {str(e)}"
            return render_template('index.html', error=error)

        # Handle CSV upload
        csv_file = request.files.get('csv_file')
        if not csv_file or csv_file.filename == '':
            error = "No CSV file uploaded."
            return render_template('index.html', error=error)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            csv_file.save(tmp.name)
            csv_file_path = tmp.name

        # Prepare simulation parameters
        params = {
            'num_items': num_items,
            'num_completed': num_completed,
            'timeframe_weeks': timeframe_weeks,
            'throughput_sigma': throughput_sigma,
            'start_date': start_date,
            'csv_file_path': csv_file_path
        }

        try:
            # Run simulation
            results, completion_dates = run_simulation(params)

            # Plot histogram
            base_date = datetime.strptime(start_date, "%Y-%m-%d")
            completion_dates_np = np.array([(date - base_date).days for date in completion_dates])

            # Absolute path on disk to save the plot
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
            os.makedirs(static_dir, exist_ok=True)
            plot_filename_abs = os.path.join(static_dir, 'completion_histogram.png')

            # Relative URL path to use in HTML template
            plot_filename = 'completion_histogram.png'

            # Remove existing plot file if exists
            if os.path.exists(plot_filename_abs):
                os.remove(plot_filename_abs)

            plt.figure(figsize=(10, 6))
            plt.hist([base_date + timedelta(days=int(d)) for d in completion_dates_np], bins=50, color='skyblue', edgecolor='black')
            plt.axvline(results['95%'], color='yellow', linestyle='--', label='{} (95%)'.format(results['95%'].date()))
            plt.axvline(results['85%'], color='red', linestyle='--', label='{} (85%)'.format(results['85%'].date()))
            plt.axvline(results['60%'], color='green', linestyle='--', label='{} (60%)'.format(results['60%'].date()))
            plt.title(f'Estimated Completion Date for All {num_items} Items')
            plt.xlabel('Estimated Completion Date')
            plt.ylabel('Frequency')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.savefig(plot_filename_abs)  # Save to absolute path
            plt.close()

        except Exception as e:
            error = f"Simulation error: {str(e)}"
            plot_filename = None
        finally:
            if csv_file_path and os.path.exists(csv_file_path):
                os.remove(csv_file_path)

        return render_template(
            'index.html',
            error=error,
            results=results,
            plot_filename=plot_filename,  # Pass relative URL here
            params=params
        )

    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
