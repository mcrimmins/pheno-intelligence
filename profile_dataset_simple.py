#!/usr/bin/env python3

import csv
import json
from datetime import datetime
import os

def profile_dataset():
    # Dataset path
    csv_path = '/data/phenology/npn_full_record_final.csv'
    
    # Ensure output directory exists
    output_dir = './outputs/phenology-intelligence-v1'
    os.makedirs(output_dir, exist_ok=True)
    
    # Read CSV header to understand column structure
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        
        # Count rows and gather column statistics
        row_count = 1  # Start with 1 to account for header
        column_info = {}
        
        # Initialize column tracking for statistics
        for col_name in header:
            column_info[col_name] = {
                'type': 'VARCHAR',  # Default to string type
                'total_count': 0,
                'not_null_count': 0,
                'data_values': []
            }
        
        # Process rows to get statistics
        for row in reader:
            row_count += 1
            for i, value in enumerate(row):
                col_name = header[i]
                column_info[col_name]['total_count'] += 1
                if value and value.strip() not in ['', 'NA']:
                    column_info[col_name]['not_null_count'] += 1
                    column_info[col_name]['data_values'].append(value)
        
        # Calculate more detailed statistics
        column_summaries = []
        schema_dict = []
        
        for col_name, info in column_info.items():
            # Get basic data type info
            data_type = info['type']
            
            # Basic row counts
            total_count = info['total_count']
            not_null_count = info['not_null_count']
            
            # Calculate simple statistics
            if info['data_values']:
                # For string data, we'll measure lengths
                if data_type == 'VARCHAR':
                    avg_length = sum(len(str(val)) for val in info['data_values']) / len(info['data_values']) if info['data_values'] else 0
                    max_length = max(len(str(val)) for val in info['data_values']) if info['data_values'] else 0
                    min_length = min(len(str(val)) for val in info['data_values']) if info['data_values'] else 0
                    avg_value = avg_length
                    max_value = max_length
                    min_value = min_length
                else:
                    # Attempt to convert to numeric if possible
                    numeric_values = []
                    for val in info['data_values']:
                        try:
                            if '.' in val:
                                numeric_values.append(float(val))
                            else:
                                numeric_values.append(int(val))
                        except:
                            pass  # Skip non-numeric values
                    
                    if numeric_values:
                        avg_value = sum(numeric_values) / len(numeric_values)
                        max_value = max(numeric_values)
                        min_value = min(numeric_values)
                    else:
                        avg_value = 0
                        max_value = 0
                        min_value = 0
            else:
                avg_value = 0
                max_value = 0
                min_value = 0
            
            # Create summary row
            column_summaries.append((
                col_name, 
                data_type, 
                total_count, 
                not_null_count, 
                avg_value, 
                max_value, 
                min_value
            ))
            
            # Create schema entry
            schema_dict.append({
                "column_name": col_name,
                "data_type": data_type,
                "nullable": True  # Conservative assumption
            })
    
    # Write schema.json
    schema_path = os.path.join(output_dir, 'schema.json')
    with open(schema_path, 'w') as f:
        json.dump(schema_dict, f, indent=2)
    
    # Write column_summary.csv
    summary_path = os.path.join(output_dir, 'column_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['column_name', 'data_type', 'total_count', 'not_null_count', 'avg_value', 'max_value', 'min_value'])
        # Write data
        for row in column_summaries:
            writer.writerow(row)
    
    # Write run_log.txt
    log_path = os.path.join(output_dir, 'run_log.txt')
    with open(log_path, 'w') as f:
        f.write(f"Profile dataset run\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Total rows: {row_count}\n")
        f.write(f"Number of columns: {len(header)}\n")
        f.write("Schema details:\n")
        for col_name in header:
            f.write(f"  {col_name}: {column_info[col_name]['type']} (nullable)\n")
    
    print(f"Dataset profile completed:")
    print(f"  Total rows: {row_count}")
    print(f"  Total columns: {len(header)}")
    print(f"  Output files created in {output_dir}/")

if __name__ == "__main__":
    profile_dataset()