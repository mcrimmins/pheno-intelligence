#!/usr/bin/env python3
"""
Script to generate summary statistics from the phenology Parquet dataset using DuckDB.
"""

import os
import duckdb
import pandas as pd
from datetime import datetime

# Create output directory if it doesn't exist
output_dir = "/outputs/phenology-intelligence-v1/summaries"
os.makedirs(output_dir, exist_ok=True)

def print_progress(message):
    """Print progress messages."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def create_species_summary():
    """Create species summary CSV."""
    print_progress("Creating species summary...")
    
    query = """
    SELECT 
        species_id,
        genus,
        species,
        common_name,
        COUNT(*) as observation_count,
        COUNT(DISTINCT site_id) as distinct_sites,
        MIN(observation_date) as first_observation_date,
        MAX(observation_date) as last_observation_date
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE species_id IS NOT NULL AND species_id != ''
    GROUP BY species_id, genus, species, common_name
    ORDER BY observation_count DESC
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "species_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"Species summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating species summary: {str(e)}")
        return None

def create_phenophase_summary():
    """Create phenophase summary CSV."""
    print_progress("Creating phenophase summary...")
    
    query = """
    SELECT 
        phenophase_id,
        phenophase_description,
        COUNT(*) as observation_count,
        COUNT(DISTINCT species_id) as distinct_species,
        COUNT(DISTINCT site_id) as distinct_sites
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE phenophase_id IS NOT NULL AND phenophase_id != ''
    GROUP BY phenophase_id, phenophase_description
    ORDER BY observation_count DESC
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "phenophase_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"Phenophase summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating phenophase summary: {str(e)}")
        return None

def create_state_summary():
    """Create state summary CSV."""
    print_progress("Creating state summary...")
    
    query = """
    SELECT 
        state,
        COUNT(*) as observation_count,
        COUNT(DISTINCT species_id) as distinct_species,
        COUNT(DISTINCT site_id) as distinct_sites
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE state IS NOT NULL AND state != ''
    GROUP BY state
    ORDER BY observation_count DESC
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "state_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"State summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating state summary: {str(e)}")
        return None

def create_year_summary():
    """Create year summary CSV."""
    print_progress("Creating year summary...")
    
    query = """
    SELECT 
        strftime('%Y', CAST(observation_date AS DATE)) as year,
        COUNT(*) as observation_count,
        COUNT(DISTINCT species_id) as distinct_species,
        COUNT(DISTINCT site_id) as distinct_sites
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE observation_date IS NOT NULL 
        AND observation_date != '1900-01-01'
        AND observation_date != '1900-01-01 00:00:00'
    GROUP BY strftime('%Y', CAST(observation_date AS DATE))
    ORDER BY year
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "year_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"Year summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating year summary: {str(e)}")
        return None

def create_data_quality_summary():
    """Create data quality summary text file."""
    print_progress("Creating data quality summary...")
    
    try:
        conn = duckdb.connect()
        
        # Total rows
        total_rows = conn.execute("SELECT COUNT(*) as count FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'").fetchone()[0]
        
        # Null counts for key fields
        null_counts = conn.execute("""
            SELECT 
                COUNT(*) - COUNT(observation_id) as null_observation_id,
                COUNT(*) - COUNT(species_id) as null_species_id,
                COUNT(*) - COUNT(site_id) as null_site_id,
                COUNT(*) - COUNT(observation_date) as null_observation_date,
                COUNT(*) - COUNT(latitude) as null_latitude,
                COUNT(*) - COUNT(longitude) as null_longitude
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
        """).fetchone()
        
        # Duplicate observation_id count
        duplicate_observation_ids = conn.execute("""
            SELECT COUNT(*) as duplicate_count
            FROM (
                SELECT observation_id, COUNT(*) as cnt
                FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
                WHERE observation_id IS NOT NULL AND observation_id != ''
                GROUP BY observation_id
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]
        
        # Invalid/missing dates
        invalid_dates = conn.execute("""
            SELECT COUNT(*) as invalid_date_count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE observation_date IS NULL 
                OR observation_date = '1900-01-01'
                OR observation_date = '1900-01-01 00:00:00'
                OR observation_date = '0000-00-00'
                OR observation_date = '0000-00-00 00:00:00'
        """).fetchone()[0]
        
        # Invalid latitude/longitude
        invalid_lat_lon = conn.execute("""
            SELECT 
                COUNT(*) - COUNT(latitude) as invalid_latitude_count,
                COUNT(*) - COUNT(longitude) as invalid_longitude_count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE (latitude IS NULL OR CAST(latitude AS DOUBLE) < -90 OR CAST(latitude AS DOUBLE) > 90)
                OR (longitude IS NULL OR CAST(longitude AS DOUBLE) < -180 OR CAST(longitude AS DOUBLE) > 180)
        """).fetchone()
        
        conn.close()
        
        # Write to text file
        output_file = os.path.join(output_dir, "data_quality_summary.txt")
        with open(output_file, 'w') as f:
            f.write("Data Quality Summary\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Total rows: {total_rows}\n\n")
            f.write("Null counts for key fields:\n")
            f.write(f"  Null observation_id: {null_counts[0]}\n")
            f.write(f"  Null species_id: {null_counts[1]}\n")
            f.write(f"  Null site_id: {null_counts[2]}\n")
            f.write(f"  Null observation_date: {null_counts[3]}\n")
            f.write(f"  Null latitude: {null_counts[4]}\n")
            f.write(f"  Null longitude: {null_counts[5]}\n\n")
            f.write(f"Duplicate observation_id count: {duplicate_observation_ids}\n\n")
            f.write(f"Invalid/missing dates: {invalid_dates}\n\n")
            f.write("Invalid coordinate values:\n")
            f.write(f"  Invalid latitude count: {invalid_lat_lon[0]}\n")
            f.write(f"  Invalid longitude count: {invalid_lat_lon[1]}\n")
        
        print_progress(f"Data quality summary created: {output_file}")
        
    except Exception as e:
        print_progress(f"Error creating data quality summary: {str(e)}")
        return None

def main():
    """Main function to run all summaries."""
    print_progress("Starting summary generation...")
    
    # Create all summary files
    create_species_summary()
    create_phenophase_summary()
    create_state_summary()
    create_year_summary()
    create_data_quality_summary()
    
    print_progress("All summaries generated successfully!")

if __name__ == "__main__":
    main()
