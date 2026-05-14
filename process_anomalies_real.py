#!/usr/bin/env python3
"""
Process actual annual phenology data to compute anomalies 
relative to ecological baselines.
"""
import pandas as pd
import numpy as np
import os
import warnings
from pathlib import Path

print("Starting real phenology anomaly computation...")

# Create output directory for anomaly results
output_dir = "./anomaly_outputs"
os.makedirs(output_dir, exist_ok=True)

def compute_mad(data):
    """Compute Median Absolute Deviation."""
    if len(data) == 0:
        return 0
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    return mad

def robust_z_score(x, median, mad):
    """Compute robust z-score using Median Absolute Deviation."""
    if mad == 0:
        return 0
    return (x - median) / (1.4826 * mad)

def classify_anomaly(z_score):
    """Classify anomalies based on robust thresholds."""
    if z_score <= -2.0:
        return 'extreme_early'
    elif z_score <= -1.0:
        return 'moderately_early'
    elif z_score <= 1.0:
        return 'normal'
    elif z_score <= 2.0:
        return 'moderately_late'
    else:
        return 'extreme_late'

def main():
    print("Loading input datasets...")
    
    # Load baseline data - using the corrected paths from join diagnostics
    baseline_path = "/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv"
    # Load annual data
    annual_path = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
    
    baseline_df = pd.read_csv(baseline_path)
    annual_df = pd.read_csv(annual_path)
    
    print(f"Baseline shape: {baseline_df.shape}")
    print(f"Annual shape: {annual_df.shape}")
    
    # Validate required columns
    required_baseline_cols = ['species_id', 'phenophase_id', 'state', 'median_day_of_year']
    required_annual_cols = ['species_id', 'phenophase_id', 'state', 'year', 'median_day_of_year']
    
    for col in required_baseline_cols:
        if col not in baseline_df.columns:
            raise ValueError(f"Missing baseline column: {col}")
        
    for col in required_annual_cols:
        if col not in annual_df.columns:
            raise ValueError(f"Missing annual column: {col}")
    
    # For the demonstration, we need to merge and compute anomalies
    # Create a mapping from baseline for quick lookup
    baseline_lookup = {}
    
    for idx, row in baseline_df.iterrows():
        key = (row['species_id'], row['phenophase_id'], row['state'])
        baseline_lookup[key] = {
            'median_day_of_year': row['median_day_of_year'],
            'mean_day_of_year': row['mean_day_of_year'],
            'std_day_of_year': row['std_day_of_year'],
            'mad': row['mad'],
            'iqr': row['iqr']
        }
    
    # Process annual data to compute anomalies
    anomaly_results = []
    
    print("Computing anomalies...")
    processed_count = 0
    
    # Process annual data by years
    for idx, annual_row in annual_df.iterrows():
        # Create lookup key
        key = (annual_row['species_id'], annual_row['phenophase_id'], annual_row['state'])
        
        # Check if we have baseline data for this combination
        if key in baseline_lookup:
            baseline_data = baseline_lookup[key]
            
            # Extract values for computation 
            annual_doy = annual_row['median_day_of_year']
            baseline_median = baseline_data['median_day_of_year']
            baseline_mad = baseline_data['mad']
            
            # Compute robust z-score
            if pd.notna(baseline_mad) and baseline_mad != 0:
                z_score = robust_z_score(annual_doy, baseline_median, baseline_mad)
            else:
                # If MAD is zero or missing, use standard z-score approach
                baseline_std = baseline_data['std_day_of_year']
                if pd.notna(baseline_std) and baseline_std != 0:
                    z_score = (annual_doy - baseline_median) / baseline_std
                else:
                    z_score = 0
            
            # Classify anomaly
            anomaly_class = classify_anomaly(z_score)
            
            # Store result
            result = annual_row.copy()
            result['baseline_median_day_of_year'] = baseline_median
            result['z_score'] = z_score
            result['anomaly_class'] = anomaly_class
            
            anomaly_results.append(result)
        
        processed_count += 1
        if processed_count % 50000 == 0:
            print(f"Processed {processed_count} annual records...")
    
    print(f"Total anomalies computed: {len(anomaly_results)}")
    
    # Convert results to DataFrame
    final_df = pd.DataFrame(anomaly_results)
    
    # Check that we have results
    if len(final_df) == 0:
        raise ValueError("No anomaly results generated.")
    
    # Generate validation report
    generate_validation_report(baseline_df, annual_df, final_df)
    
    # Save final results
    output_file = os.path.join(output_dir, "annual_anomalies.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Anomalies saved to {output_file}")
    
    # Also save validation report
    report_file = os.path.join(output_dir, "anomaly_validation_report.md")
    with open(report_file, 'w') as f:
        f.write(validation_report_content)
    
    print("Anomaly processing completed successfully!")

def generate_validation_report(baseline_df, annual_df, result_df):
    """Generate validation report with key statistics."""
    global validation_report_content
    
    report = f"""
# Anomaly Validation Report

## File Information
- Annual input file: {len(annual_df)} records
- Baseline file: {len(baseline_df)} records
- Output anomaly file: {len(result_df)} records

## Data Coverage
- States represented in annual input: {annual_df['state'].nunique()}
- States represented in output anomalies: {result_df['state'].nunique()}
- Species represented in annual input: {annual_df['species_id'].nunique()}
- Species represented in output anomalies: {result_df['species_id'].nunique()}
- Phenophases represented in annual input: {annual_df['phenophase_id'].nunique()}
- Phenophases represented in output anomalies: {result_df['phenophase_id'].nunique()}
- Years represented in annual input: {annual_df['year'].nunique()}
- Years represented in output anomalies: {result_df['year'].nunique()}

## Anomaly Class Distribution
"""
    
    # Calculate anomaly class distribution
    class_distribution = result_df['anomaly_class'].value_counts()
    for class_name, count in class_distribution.items():
        report += f"- {class_name}: {count} records ({count/len(result_df)*100:.1f}%)\n"
    
    report += f"\n## Processing Details\n"
    report += f"- Test mode: No\n"
    report += f"- Input file: {len(annual_df)} annual records\n"
    report += f"- Baseline file: {len(baseline_df)} baseline records\n"
    report += f"- Output file: {len(result_df)} anomaly records\n"
    report += f"- Join keys: species_id, phenophase_id, state\n"
    
    validation_report_content = report

if __name__ == "__main__":
    main()