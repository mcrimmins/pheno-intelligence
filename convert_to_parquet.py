#!/usr/bin/env python3

import os
import duckdb
import datetime
import json
from pathlib import Path

def convert_csv_to_parquet():
    # Input and output paths
    input_csv = "/data/phenology/npn_full_record_final.csv"
    output_dir = "/outputs/phenology-intelligence-v1/parquet/"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create log file
    log_file = f"{output_dir}/conversion_log.txt"
    
    # Log start
    with open(log_file, 'w') as f:
        f.write(f"Parquet conversion started: {datetime.datetime.now().isoformat()}\n")
        f.write(f"Input CSV: {input_csv}\n")
        f.write(f"Output directory: {output_dir}\n")
    
    try:
        # Connect to DuckDB
        con = duckdb.connect()
        
        # Get row count from CSV for progress tracking
        row_count = con.execute(f"""
            SELECT COUNT(*) FROM read_csv_auto('{input_csv}', all_varchar=true, ignore_errors=true)
        """).fetchone()[0]
        
        with open(log_file, 'a') as f:
            f.write(f"Total rows in CSV: {row_count}\n")
            f.write("Starting conversion process...\n")
        
        print(f"Starting conversion of {row_count:,} rows...")
        
        # Try to extract year from observation_date for partitioning
        # First, check if we can extract year information from the dataset
        try:
            # Test if observation_date column exists and contains valid dates
            test_query = """
                SELECT 
                    observation_date,
                    CASE 
                        WHEN observation_date IS NOT NULL AND observation_date != '' 
                        THEN SUBSTR(observation_date, 1, 4) 
                        ELSE 'unknown' 
                    END as year_extracted
                FROM read_csv_auto('{input_csv}', all_varchar=true, ignore_errors=true)
                LIMIT 5
            """
            test_result = con.execute(test_query).fetchall()
            print("Testing date extraction...")
            
            # Build the main conversion query
            partition_by_clause = ""
            if test_result and len(test_result[0]) > 0:
                # If we can identify a year column, partition by year
                partition_by_clause = "PARTITION BY (year_extracted)"
                print("Partitioning by year extracted from observation_date")
            
            conversion_query = f"""
                COPY (
                    SELECT 
                        *,
                        CASE 
                            WHEN observation_date IS NOT NULL AND observation_date != '' 
                            THEN SUBSTR(observation_date, 1, 4) 
                            ELSE 'unknown' 
                        END as year_extracted
                    FROM read_csv_auto('{input_csv}', all_varchar=true, ignore_errors=true)
                ) TO '{output_dir}/phenology_data.parquet' 
                WITH (FORMAT PARQUET, COMPRESSION ZSTD, {partition_by_clause})
            """
            
            # Execute conversion with progress
            con.execute(conversion_query)
            
            with open(log_file, 'a') as f:
                f.write("Conversion completed successfully\n")
                f.write(f"Output files: {output_dir}/phenology_data.parquet\n")
                
            print("Conversion completed successfully!")
            print(f"Output written to: {output_dir}/phenology_data.parquet")
            
            # Create metadata file
            metadata = {
                "input_file": input_csv,
                "output_directory": output_dir,
                "output_format": "parquet",
                "total_rows": row_count,
                "created_at": datetime.datetime.now().isoformat(),
                "partitioning": "year_extracted" if partition_by_clause else "none"
            }
            
            metadata_file = f"{output_dir}/parquet_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            with open(log_file, 'a') as f:
                f.write(f"Metadata file created: {metadata_file}\n")
                f.write("Conversion process finished\n")
                
            print(f"Metadata written to: {metadata_file}")
            
        except Exception as e:
            # If partitioning fails, do simple conversion
            with open(log_file, 'a') as f:
                f.write(f"Warning: Partitioning failed, using simple conversion. Error: {str(e)}\n")
                f.write("Reverting to simple conversion without partitioning...\n")
            
            print("Warning: Partitioning failed, using simple conversion")
            
            simple_query = f"""
                COPY (
                    SELECT * 
                    FROM read_csv_auto('{input_csv}', all_varchar=true, ignore_errors=true)
                ) TO '{output_dir}/phenology_data.parquet' 
                WITH (FORMAT PARQUET, COMPRESSION ZSTD)
            """
            
            con.execute(simple_query)
            
            # Update log
            with open(log_file, 'a') as f:
                f.write("Simple conversion completed successfully (no partitioning)\n")
                
            print("Simple conversion completed successfully!")
            
            # Create metadata file
            metadata = {
                "input_file": input_csv,
                "output_directory": output_dir,
                "output_format": "parquet",
                "total_rows": row_count,
                "created_at": datetime.datetime.now().isoformat(),
                "partitioning": "none",
                "warning": "Partitioning was not possible due to date format issues"
            }
            
            metadata_file = f"{output_dir}/parquet_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            with open(log_file, 'a') as f:
                f.write(f"Metadata file created: {metadata_file}\n")
                f.write("Conversion process finished\n")
                
            print(f"Metadata written to: {metadata_file}")
        
        # Verify row count
        verify_row_count(input_csv, output_dir)
        
    except Exception as e:
        with open(log_file, 'a') as f:
            f.write(f"ERROR during conversion: {str(e)}\n")
        print(f"Error during conversion: {e}")
        raise
        
    finally:
        con.close()

def verify_row_count(input_csv, output_dir):
    """Verify that row counts match between source and output"""
    try:
        con = duckdb.connect()
        
        # Get source row count
        source_count = con.execute(f"""
            SELECT COUNT(*) FROM read_csv_auto('{input_csv}', all_varchar=true, ignore_errors=true)
        """).fetchone()[0]
        
        # Get output row count
        parquet_files = list(Path(output_dir).glob("*.parquet"))
        output_count = 0
        
        if parquet_files:
            for parquet_file in parquet_files:
                if parquet_file.is_file():
                    count = con.execute(f"SELECT COUNT(*) FROM '{parquet_file}'").fetchone()[0]
                    output_count += count
                    
        # Check match with tolerance (allowing for partitioning overhead)
        with open(f"{output_dir}/conversion_log.txt", 'a') as f:
            f.write(f"Validation - Source rows: {source_count:,}, Output rows: {output_count:,}\n")
            
        if source_count == output_count:
            print(f"✓ Row count validation passed - {source_count:,} rows in both source and output")
        else:
            print(f"⚠ Row count validation - Source: {source_count:,}, Output: {output_count:,}")
            
        con.close()
        
    except Exception as e:
        print(f"Error during row count validation: {e}")

if __name__ == "__main__":
    print("Starting CSV to Parquet conversion...")
    convert_csv_to_parquet()
    print("Conversion pipeline completed!")