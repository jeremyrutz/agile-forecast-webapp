import os
import csv
import random
from datetime import datetime, timedelta
import numpy as np

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

def calculate_completion_dates(base_date, num_items, num_completed, throughput_data, num_simulations=10000, throughput_sigma=10, timeframe_weeks=1):
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
    return completion_dates

def run_simulation(params):
    base_date = datetime.strptime(params['start_date'], "%Y-%m-%d") if params['start_date'] else datetime.today()
    throughput_data = load_throughput_data(params['csv_file_path'])
    num_items = params['num_items']
    num_completed = params['num_completed']
    num_simulations = 10000
    throughput_sigma = params.get('throughput_sigma', 10)
    timeframe_weeks = params.get('timeframe_weeks', 1)
    completion_dates = calculate_completion_dates(
        base_date,
        num_items,
        num_completed,
        throughput_data,
        num_simulations=num_simulations,
        throughput_sigma=throughput_sigma,
        timeframe_weeks=timeframe_weeks
    )
    
    completion_dates_np = np.array([(date - base_date).days for date in completion_dates])
    projected_dates = {
        '95%': base_date + timedelta(days=int(np.percentile(completion_dates_np, 95))),
        '85%': base_date + timedelta(days=int(np.percentile(completion_dates_np, 85))),
        '60%': base_date + timedelta(days=int(np.percentile(completion_dates_np, 60))),
    }
    
    return projected_dates