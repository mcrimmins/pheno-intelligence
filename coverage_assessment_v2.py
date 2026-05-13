import pandas as pd
import numpy as np
import os
from datetime import datetime
import duckdb

def assess_coverage():
    # Read the input data
    input_file = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
    print(f"Loading data from {input_file}")
    
    # Use DuckDB for better performance with large datasets
    conn = duckdb.connect()
    
    # Load data into DuckDB
    conn.execute("CREATE TABLE data AS SELECT * FROM read_csv_auto(?)", [input_file])
    
    # Get data info
    result = conn.execute("SELECT COUNT(*) as row_count FROM data").fetchone()
    print(f"Data loaded. Shape: {result[0]} rows")
    
    # Create output directory
    output_dir = "/tmp/coverage_assessment"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Computing coverage metrics using DuckDB...")
    
    # Run the aggregation query in DuckDB
    query = """
    WITH yearly_counts AS (
        SELECT 
            species_id,
            common_name,
            phenophase_id,
            phenophase_description,
            state,
            year,
            SUM(observation_count) as observations_per_year
        FROM data
        WHERE year IS NOT NULL AND observation_count IS NOT NULL
        GROUP BY species_id, common_name, phenophase_id, phenophase_description, state, year
    ),
    coverage_stats AS (
        SELECT 
            species_id,
            common_name,
            phenophase_id,
            phenophase_description,
            state,
            MIN(year) as first_year,
            MAX(year) as last_year,
            COUNT(DISTINCT year) as years_observed,
            (MAX(year) - MIN(year) + 1) as record_length_years,
            SUM(observations_per_year) as total_observations,
            AVG(observations_per_year) as mean_observations_per_year,
            MEDIAN(observations_per_year) as median_observations_per_year,
            MIN(observations_per_year) as min_observations_per_year,
            MAX(observations_per_year) as max_observations_per_year,
            COUNT(CASE WHEN observations_per_year >= 30 THEN 1 END) as years_with_30plus_observations,
            COUNT(CASE WHEN observations_per_year >= 50 THEN 1 END) as years_with_50plus_observations,
            COUNT(CASE WHEN observations_per_year >= 100 THEN 1 END) as years_with_100plus_observations
        FROM yearly_counts
        GROUP BY species_id, common_name, phenophase_id, phenophase_description, state
    )
    SELECT 
        species_id,
        common_name,
        phenophase_id,
        phenophase_description,
        state,
        first_year,
        last_year,
        record_length_years,
        years_observed,
        (record_length_years - years_observed) as years_missing,
        (years_observed * 1.0 / NULLIF(record_length_years, 0)) as coverage_fraction,
        total_observations,
        median_observations_per_year,
        min_observations_per_year,
        max_observations_per_year,
        years_with_30plus_observations,
        years_with_50plus_observations,
        years_with_100plus_observations
    FROM coverage_stats
    ORDER BY coverage_fraction DESC
    """
    
    # Execute and fetch results
    coverage_df = conn.execute(query).fetchdf()
    
    # Add reliability tier
    def assign_reliability(row):
        if row['years_observed'] >= 10 and row['coverage_fraction'] >= 0.7 and row['median_observations_per_year'] >= 30:
            return 'high'
        elif row['years_observed'] >= 7 and row['coverage_fraction'] >= 0.5 and row['median_observations_per_year'] >= 15:
            return 'medium'
        elif row['years_observed'] >= 4:
            return 'low'
        else:
            return 'insufficient'
    
    coverage_df['reliability_tier'] = coverage_df.apply(assign_reliability, axis=1)
    
    # Save coverage results
    output_file = os.path.join(output_dir, "coverage_site_species_phenophase_state.csv")
    coverage_df.to_csv(output_file, index=False)
    print(f"Saved coverage metrics to {output_file}")
    
    # Summary statistics by reliability tier
    tier_counts = coverage_df['reliability_tier'].value_counts()
    
    # Top 20 best-covered combinations (based on coverage_fraction)
    best_covered = coverage_df.nlargest(20, 'coverage_fraction')
    
    # Top 20 sparse combinations (based on years_missing)
    sparse_combinations = coverage_df.nlargest(20, 'years_missing')
    
    # Create summary report
    summary_text = f"""Coverage Assessment Summary
==========================

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total combinations analyzed: {len(coverage_df)}
Total observations: {int(coverage_df['total_observations'].sum())}

Reliability Tier Distribution:
{tier_counts.to_string()}

Top 20 Best-Covered Combinations (by coverage_fraction):
{best_covered[['species_id', 'common_name', 'phenophase_description', 'state', 'coverage_fraction']].to_string(index=False)}

Top 20 Sparse Combinations (by years_missing):
{sparse_combinations[['species_id', 'common_name', 'phenophase_description', 'state', 'years_missing']].to_string(index=False)}
"""
    
    # Save summary report
    summary_file = os.path.join(output_dir, "coverage_assessment_summary.txt")
    with open(summary_file, 'w') as f:
        f.write(summary_text)
    
    print(f"Summary report saved to {summary_file}")
    
    # Save reliability summary
    reliability_summary = coverage_df.groupby('reliability_tier').agg({
        'total_observations': 'sum',
        'years_observed': 'mean',
        'coverage_fraction': 'mean'
    }).round(3)
    
    reliability_summary_file = os.path.join(output_dir, "coverage_reliability_summary.csv")
    reliability_summary.to_csv(reliability_summary_file)
    print(f"Reliability summary saved to {reliability_summary_file}")
    
    # Close DuckDB connection
    conn.close()
    
    print("Coverage assessment completed successfully!")

if __name__ == "__main__":
    assess_coverage()