import pandas as pd
import numpy as np
import os
from datetime import datetime

def assess_coverage():
    # Read the input data
    input_file = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
    print(f"Loading data from {input_file}")
    
    df = pd.read_csv(input_file)
    print(f"Data loaded. Shape: {df.shape}")
    
    # Ensure proper data types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['observation_count'] = pd.to_numeric(df['observation_count'], errors='coerce')
    df['median_day_of_year'] = pd.to_numeric(df['median_day_of_year'], errors='coerce')
    
    # Drop any rows with NaN values in critical columns
    df = df.dropna(subset=['year', 'observation_count'])
    
    # Create output directory (using current working directory instead of /outputs)
    output_dir = "./coverage_assessment"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Computing coverage metrics...")
    
    # Group by multiple dimensions and compute metrics for each combination
    coverage_metrics = []
    
    # Group by species_id, common_name, phenophase_id, phenophase_description, state
    group_columns = ['species_id', 'common_name', 'phenophase_id', 'phenophase_description', 'state']
    
    for group in df.groupby(group_columns):
        group_data = group[1]
        
        # Extract group keys
        keys = group[0]
        species_id, common_name, phenophase_id, phenophase_description, state = keys
        
        # Compute metrics
        years = group_data['year'].unique()
        first_year = int(years.min())
        last_year = int(years.max())
        record_length_years = last_year - first_year + 1
        years_observed = len(years)
        years_missing = record_length_years - years_observed
        coverage_fraction = years_observed / record_length_years if record_length_years > 0 else 0
        
        total_observations = int(group_data['observation_count'].sum())
        
        # Calculate observation statistics per year
        obs_per_year = group_data.groupby('year')['observation_count'].sum()
        median_observations_per_year = float(obs_per_year.median())
        min_observations_per_year = int(obs_per_year.min())
        max_observations_per_year = int(obs_per_year.max())
        
        # Count years with thresholds
        years_with_30plus = int((obs_per_year >= 30).sum())
        years_with_50plus = int((obs_per_year >= 50).sum())
        years_with_100plus = int((obs_per_year >= 100).sum())
        
        # Add to results
        coverage_metrics.append({
            'species_id': species_id,
            'common_name': common_name,
            'phenophase_id': phenophase_id,
            'phenophase_description': phenophase_description,
            'state': state,
            'first_year': first_year,
            'last_year': last_year,
            'record_length_years': record_length_years,
            'years_observed': years_observed,
            'years_missing': years_missing,
            'coverage_fraction': coverage_fraction,
            'total_observations': total_observations,
            'median_observations_per_year': median_observations_per_year,
            'min_observations_per_year': min_observations_per_year,
            'max_observations_per_year': max_observations_per_year,
            'years_with_30plus_observations': years_with_30plus,
            'years_with_50plus_observations': years_with_50plus,
            'years_with_100plus_observations': years_with_100plus
        })
    
    # Convert to DataFrame
    coverage_df = pd.DataFrame(coverage_metrics)
    
    # Calculate reliability tier based on criteria
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
    
    print("Coverage assessment completed successfully!")

if __name__ == "__main__":
    assess_coverage()