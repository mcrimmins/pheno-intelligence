#!/usr/bin/env python3

import duckdb
import json
import csv
from datetime import datetime

def profile_dataset():
    # Connect to DuckDB
    conn = duckdb.connect(':memory:')
    
    # Read the CSV file with explicit type handling
    csv_path = '/data/phenology/npn_full_record_final.csv'
    
    # Create table from CSV with explicit schema to handle NA values properly
    query = f"""
    CREATE TABLE phenology_data AS 
    SELECT * FROM read_csv('{csv_path}', 
        header=true, 
        delim=',', 
        quote='"', 
        escape='"',
        nullstr='NA',
        sample_size=-1
    )
    """
    
    try:
        conn.execute(query)
    except Exception as e:
        # If that fails, try to create with explicit schema
        print(f"Error with automatic schema detection: {e}")
        # Let's try a more careful approach
        query = f"""
        CREATE TABLE phenology_data AS 
        SELECT * FROM read_csv('{csv_path}', 
            header=true, 
            delim=',', 
            quote='"', 
            escape='"',
            nullstr='NA',
            all_varchar=true
        )
        """
        conn.execute(query)
    
    # Count rows
    row_count = conn.execute("SELECT COUNT(*) FROM phenology_data").fetchone()[0]
    
    # Get schema information
    schema_info = conn.execute("DESCRIBE phenology_data").fetchall()
    
    # Get column summaries
    column_summaries = []
    for col_name, col_type, nullability in schema_info:
        # Get basic statistics for each column
        if col_type == 'VARCHAR':
            # For string columns, get length info
            stats_query = f"""
            SELECT 
                '{col_name}' as column_name,
                '{col_type}' as data_type,
                COUNT(*) as total_count,
                COUNT({col_name}) as not_null_count,
                AVG(LENGTH({col_name})) as avg_length,
                MAX(LENGTH({col_name})) as max_length,
                MIN(LENGTH({col_name})) as min_length
            FROM phenology_data
            """
        else:
            stats_query = f"""
            SELECT 
                '{col_name}' as column_name,
                '{col_type}' as data_type,
                COUNT(*) as total_count,
                COUNT({col_name}) as not_null_count,
                AVG({col_name}) as avg_value,
                MAX({col_name}) as max_value,
                MIN({col_name}) as min_value
            FROM phenology_data
            """
        
        try:
            stats = conn.execute(stats_query).fetchone()
            column_summaries.append(stats)
        except Exception as e:
            # Handle columns that cause issues in statistics calculation
            print(f"Warning: Could not calculate statistics for {col_name}: {e}")
            column_summaries.append((col_name, col_type, row_count, 0, 0, 0, 0))
    
    # Write schema.json
    schema_dict = []
    for col_name, col_type, nullability in schema_info:
        schema_dict.append({
            "column_name": col_name,
            "data_type": col_type,
            "nullable": nullability == 'YES'
        })
    
    with open('./outputs/phenology-intelligence-v1/schema.json', 'w') as f:
        json.dump(schema_dict, f, indent=2)
    
    # Write column_summary.csv
    with open('./outputs/phenology-intelligence-v1/column_summary.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['column_name', 'data_type', 'total_count', 'not_null_count', 'avg_value', 'max_value', 'min_value'])
        # Write data
        for row in column_summaries:
            writer.writerow(row)
    
    # Write run_log.txt
    with open('./outputs/phenology-intelligence-v1/run_log.txt', 'w') as f:
        f.write(f"Profile dataset run\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Total rows: {row_count}\n")
        f.write(f"Number of columns: {len(schema_info)}\n")
        f.write("Schema details:\n")
        for col_name, col_type, nullability in schema_info:
            f.write(f"  {col_name}: {col_type} ({nullability})\n")
    
    print(f"Dataset profile completed:")
    print(f"  Total rows: {row_count}")
    print(f"  Total columns: {len(schema_info)}")
    print(f"  Output files created in ./outputs/phenology-intelligence-v1/")

if __name__ == "__main__":
    profile_dataset()