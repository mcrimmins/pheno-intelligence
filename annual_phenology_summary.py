#!/usr/bin/env python3
"""
Script to generate annual phenology timing summaries from the phenology Parquet dataset using DuckDB.
"""

import os
import duckdb
import pandas as pd
from datetime import datetime

# Create output directory if it doesn't exist
output_dir = "/outputs/phenology-intelligence-v1/annual_summaries"
os.makedirs(output_dir, exist_ok=True)

def print_progress(message):
    """Print progress messages."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def create_annual_species_phenophase_summary():
    """Create annual species phenophase summary CSV."""
    print_progress("Creating annual species phenophase summary...")
    
    query = """
    SELECT 
        species_id,
        genus,
        species,
        common_name,
        phenophase_id,
        phenophase_description,
        state,
        CAST(strftime('%Y', CAST(observation_date AS DATE)) AS INTEGER) as year,
        COUNT(*) as observation_count,
        MEDIAN(CAST(day_of_year AS INTEGER)) as median_day_of_year,
        AVG(CAST(day_of_year AS INTEGER)) as mean_day_of_year,
        MIN(CAST(day_of_year AS INTEGER)) as min_day_of_year,
        MAX(CAST(day_of_year AS INTEGER)) as max_day_of_year,
        MIN(observation_date) as first_observation_date,
        MAX(observation_date) as last_observation_date,
        COUNT(DISTINCT site_id) as distinct_sites
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE day_of_year IS NOT NULL 
        AND day_of_year != ''
        AND CAST(day_of_year AS INTEGER) >= 1
        AND CAST(day_of_year AS INTEGER) <= 366
        AND observation_date IS NOT NULL
        AND observation_date != '1900-01-01'
        AND observation_date != '1900-01-01 00:00:00'
        AND observation_date != '0000-00-00'
        AND observation_date != '0000-00-00 00:00:00'
    GROUP BY species_id, genus, species, common_name, phenophase_id, phenophase_description, state, strftime('%Y', CAST(observation_date AS DATE))
    ORDER BY year, species_id, phenophase_id
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "annual_species_phenophase_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"Annual species phenophase summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating annual species phenophase summary: {str(e)}")
        return None

def create_annual_state_summary():
    """Create annual state summary CSV."""
    print_progress("Creating annual state summary...")
    
    query = """
    SELECT 
        state,
        CAST(strftime('%Y', CAST(observation_date AS DATE)) AS INTEGER) as year,
        COUNT(*) as observation_count,
        COUNT(DISTINCT species_id) as distinct_species,
        COUNT(DISTINCT site_id) as distinct_sites,
        MEDIAN(CAST(day_of_year AS INTEGER)) as median_day_of_year
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE day_of_year IS NOT NULL 
        AND day_of_year != ''
        AND CAST(day_of_year AS INTEGER) >= 1
        AND CAST(day_of_year AS INTEGER) <= 366
        AND observation_date IS NOT NULL
        AND observation_date != '1900-01-01'
        AND observation_date != '1900-01-01 00:00:00'
        AND observation_date != '0000-00-00'
        AND observation_date != '0000-00-00 00:00:00'
        AND state IS NOT NULL
        AND state != ''
    GROUP BY state, strftime('%Y', CAST(observation_date AS DATE))
    ORDER BY year, state
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "annual_state_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"Annual state summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating annual state summary: {str(e)}")
        return None

def create_annual_species_summary():
    """Create annual species summary CSV."""
    print_progress("Creating annual species summary...")
    
    query = """
    SELECT 
        species_id,
        common_name,
        CAST(strftime('%Y', CAST(observation_date AS DATE)) AS INTEGER) as year,
        COUNT(*) as observation_count,
        COUNT(DISTINCT state) as distinct_states,
        COUNT(DISTINCT site_id) as distinct_sites,
        MEDIAN(CAST(day_of_year AS INTEGER)) as median_day_of_year
    FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
    WHERE day_of_year IS NOT NULL 
        AND day_of_year != ''
        AND CAST(day_of_year AS INTEGER) >= 1
        AND CAST(day_of_year AS INTEGER) <= 366
        AND observation_date IS NOT NULL
        AND observation_date != '1900-01-01'
        AND observation_date != '1900-01-01 00:00:00'
        AND observation_date != '0000-00-00'
        AND observation_date != '0000-00-00 00:00:00'
        AND species_id IS NOT NULL
        AND species_id != ''
    GROUP BY species_id, common_name, strftime('%Y', CAST(observation_date AS DATE))
    ORDER BY year, species_id
    """
    
    try:
        conn = duckdb.connect()
        df = conn.execute(query).fetchdf()
        conn.close()
        
        # Write to CSV
        output_file = os.path.join(output_dir, "annual_species_summary.csv")
        df.to_csv(output_file, index=False)
        print_progress(f"Annual species summary created: {output_file} with {len(df)} rows")
        
        return df
    except Exception as e:
        print_progress(f"Error creating annual species summary: {str(e)}")
        return None

def create_annual_data_quality_summary():
    """Create data quality summary text file."""
    print_progress("Creating annual data quality summary...")
    
    try:
        conn = duckdb.connect()
        
        # Total rows processed
        total_rows = conn.execute("SELECT COUNT(*) as count FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'").fetchone()[0]
        
        # Rows missing day_of_year
        rows_missing_day_of_year = conn.execute("""
            SELECT COUNT(*) as count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE day_of_year IS NULL OR day_of_year = ''
        """).fetchone()[0]
        
        # Rows missing observation_date
        rows_missing_observation_date = conn.execute("""
            SELECT COUNT(*) as count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE observation_date IS NULL OR observation_date = '' OR 
                  observation_date = '1900-01-01' OR observation_date = '1900-01-01 00:00:00' OR
                  observation_date = '0000-00-00' OR observation_date = '0000-00-00 00:00:00'
        """).fetchone()[0]
        
        # Rows with invalid day_of_year
        rows_invalid_day_of_year = conn.execute("""
            SELECT COUNT(*) as count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE day_of_year IS NOT NULL AND day_of_year != ''
                AND (CAST(day_of_year AS INTEGER) < 1 OR CAST(day_of_year AS INTEGER) > 366)
        """).fetchone()[0]
        
        # Rows excluded from summaries
        rows_excluded = rows_missing_day_of_year + rows_missing_observation_date + rows_invalid_day_of_year
        
        # Distinct years found
        distinct_years = conn.execute("""
            SELECT COUNT(DISTINCT strftime('%Y', CAST(observation_date AS DATE))) as count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE observation_date IS NOT NULL 
                AND observation_date != '1900-01-01'
                AND observation_date != '1900-01-01 00:00:00'
                AND observation_date != '0000-00-00'
                AND observation_date != '0000-00-00 00:00:00'
        """).fetchone()[0]
        
        # Distinct species found
        distinct_species = conn.execute("""
            SELECT COUNT(DISTINCT species_id) as count
            FROM '/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'
            WHERE species_id IS NOT NULL AND species_id != ''
        """).fetchone()[0]
        
        conn.close()
        
        # Write to text file
        output_file = os.path.join(output_dir, "annual_data_quality_summary.txt")
        with open(output_file, 'w') as f:
            f.write("Annual Data Quality Summary\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Total rows processed: {total_rows}\n\n")
            f.write(f"Rows missing day_of_year: {rows_missing_day_of_year}\n")
            f.write(f"Rows missing observation_date: {rows_missing_observation_date}\n")
            f.write(f"Rows with invalid day_of_year: {rows_invalid_day_of_year}\n")
            f.write(f"Rows excluded from summaries: {rows_excluded}\n\n")
            f.write(f"Distinct years found: {distinct_years}\n")
            f.write(f"Distinct species found: {distinct_species}\n")
        
        print_progress(f"Annual data quality summary created: {output_file}")
        
    except Exception as e:
        print_progress(f"Error creating annual data quality summary: {str(e)}")
        return None

def main():
    """Main function to run all summaries."""
    print_progress("Starting annual summary generation...")
    
    # Create all summary files
    create_annual_species_phenophase_summary()
    create_annual_state_summary()
    create_annual_species_summary()
    create_annual_data_quality_summary()
    
    print_progress("All annual summaries generated successfully!")

if __name__ == "__main__":
    main()