import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility

def generate_resource_data(num_resources=50):
    """
    Generates data for 'Resource Allocation' view.
    Columns: Consultant Name, Role, Department, Project, Start Date, End Date, Utilization %
    """
    roles = ['Data Analyst', 'Project Manager', 'Software Engineer', 'UX Designer', 'Business Analyst']
    departments = ['IT', 'Operations', 'Product', 'Marketing', 'Finance']
    projects = [f'Project {char}' for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    
    data = []
    
    for _ in range(num_resources):
        start_date = fake.date_between(start_date='-6m', end_date='today')
        # End date is between 1 and 6 months from start date
        end_date = start_date + timedelta(days=random.randint(30, 180))
        
        row = {
            'Resource ID': fake.unique.uuid4()[:8],
            'Name': fake.name(),
            'Role': random.choice(roles),
            'Department': random.choice(departments),
            'Project': random.choice(projects),
            'Start Date': start_date,
            'End Date': end_date,
            'Utilization (%)': random.randint(50, 120),  # >100% means overutilized
            'Status': random.choice(['Active', 'On Bench', 'On Leave'])
        }
        data.append(row)
        
    return pd.DataFrame(data)

def generate_delay_data(num_shipments=200):
    """
    Generates data for 'Delay Anticipation' view.
    Columns: Shipment ID, Origin, Destination, Expected Arrival, Actual Arrival, Status, Risk Factor
    """
    origins = ['New York', 'London', 'Shanghai', 'Berlin', 'Tokyo', 'Mumbai']
    destinations = ['Paris', 'Los Angeles', 'Sydney', 'Dubai', 'Toronto', 'Singapore']
    
    data = []
    
    for _ in range(num_shipments):
        expected_date = fake.date_between(start_date='-3m', end_date='+1m')
        
        # Determine if delayed based on some probability
        is_delayed = random.random() < 0.35  # 35% chance of delay
        
        if is_delayed:
            delay_days = random.randint(1, 15)
            actual_date = expected_date + timedelta(days=delay_days)
            status = 'Delayed'
            risk_factor = random.choice(['High', 'Critical']) if delay_days > 7 else 'Medium'
            reason = random.choice(['Customs Hold', 'Weather Conditions', 'Port Congestion', 'Carrier Issue', 'Documentation Error'])
        else:
            actual_date = expected_date
            status = 'On Time'
            risk_factor = 'Low'
            reason = 'None'
            
        # If expected date is in future, actual date might be unknown/estimated
        if expected_date > datetime.now().date():
            if is_delayed:
                status = 'At Risk' # Future shipment already flagged
            else:
                status = 'Scheduled'
            actual_date = None # Not arrived yet

        row = {
            'Shipment ID': f'SHP-{fake.unique.random_number(digits=5)}',
            'Origin': random.choice(origins),
            'Destination': random.choice(destinations),
            'Expected Arrival': expected_date,
            'Actual Arrival': actual_date,
            'Status': status,
            'Delay Days': (actual_date - expected_date).days if actual_date and expected_date else 0,
            'Risk Score': random.randint(1, 100) if status != 'On Time' else random.randint(1, 20),
            'Primary Delay Reason': reason
        }
        data.append(row)
        
    return pd.DataFrame(data)

def main():
    print("Generating data...")
    
    # Create data directory
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Generate and save
    resources_df = generate_resource_data()
    resources_df.to_csv(os.path.join(output_dir, 'resources.csv'), index=False)
    print(f"Created resources.csv with {len(resources_df)} records.")
    
    delays_df = generate_delay_data()
    delays_df.to_csv(os.path.join(output_dir, 'delays.csv'), index=False)
    print(f"Created delays.csv with {len(delays_df)} records.")
    
    print("Data generation complete.")

if __name__ == "__main__":
    main()
