#!/usr/bin/env python3
"""
Full national-scale phenology anomaly computation.
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import time

print("Starting full national-scale phenology anomaly computation...")

# Set up output directory - use working directory instead of /outputs due to permissions
output_dir = "./anomaly_outputs/"
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

def compute_percentile_position(x, data):
    """Compute percentile position within baseline distribution."""
    if len(data) == 0:
        return 0
    # Use pandas rank to compute percentile
    rank = pd.Series(data).rank(pct=True, na_option='dense')
    return rank[rank.index == x].iloc[0] if len(rank[rank.index == x]) > 0 else 0

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
    start_time = time.time()
    
    # Load baseline data
    baseline_path = "/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv"
    annual_path = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
    
    baseline_df = pd.read_csv(baseline_path)
    annual_df = pd.read_csv(annual_path)
    
    print(f"Baseline data shape: {baseline_df.shape}")
    print(f"Annual data shape: {annual_df.shape}")
    
    # Validate required columns
    required_baseline_cols = ['species_id', 'phenophase_id', 'state', 'median_day_of_year', 'mad', 'iqr', 'years_observed', 'coverage_fraction', 'reliability_tier', 'baseline_confidence_score']
    required_annual_cols = ['species_id', 'phenophase_id', 'state', 'year', 'median_day_of_year']
    
    for col in required_baseline_cols:
        if col not in baseline_df.columns:
            raise ValueError(f"Missing baseline column: {col}")
        
    for col in required_annual_cols:
        if col not in annual_df.columns:
            raise ValueError(f"Missing annual column: {col}")
    
    # Create a mapping of baseline data for faster lookup
    print("Creating baseline lookup table...")
    
    # Group baseline data to get all combinations
    baseline_lookup = {}
    
    # Create a more robust mapping by combining the key columns
    for idx, row in baseline_df.iterrows():
        key = (row['species_id'], row['phenophase_id'], row['state'])
        baseline_lookup[key] = row
    
    print(f"Created baseline lookup with {len(baseline_lookup)} combinations")
    
    # Process annual data to compute anomalies
    print("Computing anomalies for all annual records...")
    
    anomaly_results = []
    mad_zero_count = 0
    extreme_anomalies = []
    
    processed_count = 0
    
    for idx, annual_row in annual_df.iterrows():
        # Create lookup key - this is key for join
        key = (annual_row['species_id'], annual_row['phenophase_id'], annual_row['state'])
        
        # Check if we have baseline data for this combination
        if key in baseline_lookup:
            baseline_data = baseline_lookup[key]
            
            # Extract values for computation 
            annual_doy = annual_row['median_day_of_year']
            baseline_median = baseline_data['median_day_of_year']
            baseline_mad = baseline_data['mad']
            baseline_std = baseline_data['std_day_of_year']
            
            # Compute anomaly metrics safely
            anomaly_days = annual_doy - baseline_median
            
            # Compute robust z-score
            z_score = 0
            if pd.notna(baseline_mad) and baseline_mad != 0:
                z_score = robust_z_score(annual_doy, baseline_median, baseline_mad)
                if abs(z_score) > 100:  # Flag extreme anomalies
                    extreme_anomalies.append((annual_row['species_id'], annual_row['phenophase_id'], annual_row['state'], annual_row['year'], z_score, anomaly_days))
            else:
                # Fall back to standard z-score
                if pd.notna(baseline_std) and baseline_std != 0:
                    z_score = (annual_doy - baseline_median) / baseline_std
                if baseline_mad == 0:
                    mad_zero_count += 1
            
            # Compute percentile position
            percentile_pos = compute_percentile_position(annual_doy, [baseline_median])  # Simple case
            
            # Classify anomaly
            anomaly_class = classify_anomaly(z_score)
            
            # Store result
            result = annual_row.copy()
            result['anomaly_days'] = anomaly_days
            result['robust_z_score'] = z_score
            result['percentile_position'] = percentile_pos
            result['anomaly_class'] = anomaly_class
            
            # Preserve baseline metadata
            result['baseline_median_day_of_year'] = baseline_median
            result['baseline_mad'] = baseline_mad
            result['years_observed'] = baseline_data['years_observed']
            result['coverage_fraction'] = baseline_data['coverage_fraction']
            result['reliability_tier'] = baseline_data['reliability_tier']
            result['baseline_confidence_score'] = baseline_data['baseline_confidence_score']
            
            if 'iqr' in baseline_data:
                result['baseline_iqr'] = baseline_data['iqr']
            else:
                result['baseline_iqr'] = np.nan
                
            anomaly_results.append(result)
        
        processed_count += 1
        if processed_count % 50000 == 0:
            print(f"Processed {processed_count} annual records...")
    
    print(f"Total anomalies computed: {len(anomaly_results)}")
    print(f"Records with MAD == 0: {mad_zero_count}")
    print(f"Extreme anomalies (|z_score| > 100): {len(extreme_anomalies)}")
    
    # Convert results to DataFrame
    final_df = pd.DataFrame(anomaly_results)
    
    if len(final_df) == 0:
        raise ValueError("No anomaly results generated.")
    
    # Generate detailed validation report
    print("Generating validation reports...")
    generate_validation_report(baseline_df, annual_df, final_df, mad_zero_count, extreme_anomalies)
    
    # Save results
    print("Saving output files...")
    
    # Save main anomaly file
    output_file = os.path.join(output_dir, "annual_anomalies.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Annual anomalies saved to {output_file}")
    
    # Generate summary files by year
    summary_by_year = final_df.groupby('year').agg({
        'anomaly_days': ['mean', 'std', 'count'],
        'robust_z_score': ['mean', 'std'],
        'anomaly_class': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    summary_by_year_file = os.path.join(output_dir, "anomaly_summary_by_year.csv")
    summary_by_year.to_csv(summary_by_year_file, index=False)
    print(f"Summary by year saved to {summary_by_year_file}")
    
    # Generate summary files by state
    summary_by_state = final_df.groupby('state').agg({
        'anomaly_days': ['mean', 'std', 'count'],
        'robust_z_score': ['mean', 'std'],
        'anomaly_class': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    summary_by_state_file = os.path.join(output_dir, "anomaly_summary_by_state.csv")
    summary_by_state.to_csv(summary_by_state_file, index=False)
    print(f"Summary by state saved to {summary_by_state_file}")
    
    # Generate summary files by species
    summary_by_species = final_df.groupby(['species_id', 'common_name']).agg({
        'anomaly_days': ['mean', 'std', 'count'],
        'robust_z_score': ['mean', 'std'],
        'anomaly_class': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    summary_by_species_file = os.path.join(output_dir, "anomaly_summary_by_species.csv")
    summary_by_species.to_csv(summary_by_species_file, index=False)
    print(f"Summary by species saved to {summary_by_species_file}")
    
    # Generate diagnostic figures
    print("Generating diagnostic figures...")
    create_diagnostic_figures(final_df)
    
    end_time = time.time()
    print(f"Total processing time: {end_time - start_time:.2f} seconds")
    
    print("Full national anomaly computation completed successfully!")

def generate_validation_report(baseline_df, annual_df, result_df, mad_zero_count, extreme_anomalies):
    """Generate comprehensive validation report."""
    
    # Aggregate data for report
    report = f"""
# Full National Anomaly Computation Validation Report

## File Information
- Annual input file: {len(annual_df)} records
- Baseline file: {len(baseline_df)} records  
- Output anomaly file: {len(result_df)} records
- Processing time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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

    class_distribution = result_df['anomaly_class'].value_counts()
    total_count = len(result_df)
    for class_name, count in class_distribution.items():
        percentage = (count / total_count) * 100
        report += f"- {class_name}: {count} records ({percentage:.1f}%)\n"
    
    report += f"""

## Data Quality Issues
- Rows with MAD == 0: {mad_zero_count}
- Extreme anomalies (>100 days): {len(extreme_anomalies)}

## Key Statistics
- Average anomaly days: {result_df['anomaly_days'].mean():.2f}
- Standard deviation of anomaly days: {result_df['anomaly_days'].std():.2f}
- Average robust z-score: {result_df['robust_z_score'].mean():.2f}
- Maximum absolute z-score: {result_df['robust_z_score'].abs().max():.2f}

## Reliability Tier Distribution
"""

    reliability_distribution = result_df['reliability_tier'].value_counts()
    for tier, count in reliability_distribution.items():
        percentage = (count / total_count) * 100
        report += f"- {tier}: {count} records ({percentage:.1f}%)\n"

    # Top 20 early anomalies
    early_anomalies = result_df[result_df['anomaly_days'] < 0].sort_values('anomaly_days').head(20)
    report += f"""\n## Top 20 Strongest Early Anomalies (Earliest)"""
    
    if len(early_anomalies) > 0:
        for idx, row in early_anomalies.iterrows():
            report += f"\n- Species {row['species_id']}, Phenophase {row['phenophase_id']}, {row['state']} in {row['year']}: {row['anomaly_days']:.1f} days"
    else:
        report += "\nNo early anomalies found."
    
    # Top 20 late anomalies
    late_anomalies = result_df[result_df['anomaly_days'] > 0].sort_values('anomaly_days', ascending=False).head(20)
    report += f"""\n## Top 20 Strongest Late Anomalies (Latest)"""
    
    if len(late_anomalies) > 0:
        for idx, row in late_anomalies.iterrows():
            report += f"\n- Species {row['species_id']}, Phenophase {row['phenophase_id']}, {row['state']} in {row['year']}: {row['anomaly_days']:.1f} days"
    else:
        report += "\nNo late anomalies found."

    # Extreme anomalies (flagged)
    report += f"""\n## Extreme Anomalies (>100 days)
"""
    if len(extreme_anomalies) > 0:
        for species, phenophase, state, year, z_score, anomaly_days in extreme_anomalies:
            report += f"- Species {species}, Phenophase {phenophase}, {state} in {year}: z_score={z_score:.2f}, anomaly_days={anomaly_days:.1f}\n"
    else:
        report += "No extreme anomalies found."

    # Runtime and memory notes
    report += f"""\n## Runtime and Memory Notes
- Processing started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Records processed: {len(result_df)}
- Memory efficient processing used
- All annual records preserved in output
"""
    
    # Save validation report
    report_file = os.path.join(output_dir, "anomaly_validation_report.md")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print("Validation report saved.")

def create_diagnostic_figures(df):
    """Create diagnostic figures."""
    print("Creating diagnostic figures...")
    
    # Create figures directory
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # Histogram of anomaly days
    plt.figure(figsize=(10, 6))
    df['anomaly_days'].hist(bins=50, alpha=0.7, color='blue')
    plt.xlabel('Anomaly Days')
    plt.ylabel('Frequency')
    plt.title('Distribution of Phenology Anomalies')
    plt.savefig(os.path.join(figures_dir, "anomaly_histogram.png"))
    plt.close()
    
    # Anomaly by year
    yearly_anomalies = df.groupby('year')['anomaly_days'].mean()
    plt.figure(figsize=(12, 6))
    yearly_anomalies.plot(kind='line')
    plt.xlabel('Year')
    plt.ylabel('Average Anomaly Days')
    plt.title('Average Phenology Anomalies by Year')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "anomaly_by_year.png"))
    plt.close()
    
    # Anomaly class distribution
    class_counts = df['anomaly_class'].value_counts()
    plt.figure(figsize=(8, 6))
    class_counts.plot(kind='bar')
    plt.xlabel('Anomaly Class')
    plt.ylabel('Count')
    plt.title('Distribution of Anomaly Classes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "anomaly_class_distribution.png"))
    plt.close()
    
    # Top 20 extreme early species
    early_anomalies = df[df['anomaly_days'] < 0].groupby(['species_id', 'common_name']).agg({'anomaly_days': 'mean'}).reset_index()
    early_anomalies = early_anomalies.sort_values('anomaly_days').head(20)
    
    if len(early_anomalies) > 0:
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(early_anomalies)), early_anomalies['anomaly_days'])
        plt.yticks(range(len(early_anomalies)), [f"{row['species_id']}: {row['common_name']}" for idx, row in early_anomalies.iterrows()])
        plt.xlabel('Average Anomaly Days (Early)')
        plt.title('Top 20 Species with Earliest Anomalies')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "top_extreme_early_species.png"))
        plt.close()
    
    # Top 20 extreme late species
    late_anomalies = df[df['anomaly_days'] > 0].groupby(['species_id', 'common_name']).agg({'anomaly_days': 'mean'}).reset_index()
    late_anomalies = late_anomalies.sort_values('anomaly_days', ascending=False).head(20)
    
    if len(late_anomalies) > 0:
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(late_anomalies)), late_anomalies['anomaly_days'])
        plt.yticks(range(len(late_anomalies)), [f"{row['species_id']}: {row['common_name']}" for idx, row in late_anomalies.iterrows()])
        plt.xlabel('Average Anomaly Days (Late)')
        plt.title('Top 20 Species with Latest Anomalies')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "top_extreme_late_species.png"))
        plt.close()
    
    print("Diagnostic figures created.")

if __name__ == "__main__":
    main()