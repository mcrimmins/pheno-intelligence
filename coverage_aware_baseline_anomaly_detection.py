#!/usr/bin/env python3
"""
Coverage-aware Ecological Baseline and Anomaly Detection Framework
==================================================================

This script implements a framework to:
1. Create an ecological baseline from phenology data
2. Assess data coverage levels across different species/phenophase combinations
3. Implement anomaly detection capabilities

The framework addresses the need for quality-aware statistical analysis and visualization
of phenological trends in ecological research.
"""

import pandas as pd
import numpy as np
import os
import warnings
from datetime import datetime
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

def create_ecological_baseline():
    """
    Creates an ecological baseline from phenology data by computing:
    - Mean and median phenological timing (day of year)
    - Variance and standard deviation of phenological timing
    - Temporal trends for major ecological events
    """
    
    # Read the annual summary data
    annual_summary_file = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
    
    if not os.path.exists(annual_summary_file):
        raise FileNotFoundError(f"Annual summary file not found: {annual_summary_file}")
    
    df = pd.read_csv(annual_summary_file)
    
    # Ensure proper data types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['observation_count'] = pd.to_numeric(df['observation_count'], errors='coerce')
    df['median_day_of_year'] = pd.to_numeric(df['median_day_of_year'], errors='coerce')
    
    # Filter out NaN values in critical fields
    df = df.dropna(subset=['year', 'observation_count', 'median_day_of_year'])
    
    print(f"Loading data with {len(df)} records")
    
    # Group by species, phenophase, and state to compute ecological baselines
    baseline_columns = ['species_id', 'common_name', 'phenophase_description', 'state']
    
    baseline_data = []
    
    for group in df.groupby(baseline_columns):
        group_data = group[1]
        
        # Extract group keys
        keys = group[0]
        species_id, common_name, phenophase_description, state = keys
        
        # Calculate baseline statistics
        years = group_data['year'].unique()
        first_year = int(years.min())
        last_year = int(years.max())
        record_length_years = last_year - first_year + 1
        years_observed = len(years)
        coverage_fraction = years_observed / record_length_years if record_length_years > 0 else 0
        
        total_observations = int(group_data['observation_count'].sum())
        
        # Compute annual statistics
        obs_per_year = group_data.groupby('year')['observation_count'].sum()
        median_observations_per_year = float(obs_per_year.median())
        
        # Calculate phenological timing stats
        median_timing = float(group_data['median_day_of_year'].median())
        mean_timing = float(group_data['median_day_of_year'].mean())
        std_timing = float(group_data['median_day_of_year'].std())
        
        # Calculate trend using least squares
        if len(years) >= 2:
            x = group_data['year'].values
            y = group_data['median_day_of_year'].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            trend = slope
            trend_r_squared = r_value**2
        else:
            trend = np.nan
            trend_r_squared = np.nan
            
        # Add to baseline
        baseline_data.append({
            'species_id': species_id,
            'common_name': common_name,
            'phenophase_description': phenophase_description,
            'state': state,
            'first_year': first_year,
            'last_year': last_year,
            'record_length_years': record_length_years,
            'years_observed': years_observed,
            'coverage_fraction': coverage_fraction,
            'total_observations': total_observations,
            'median_observations_per_year': median_observations_per_year,
            'median_day_of_year': median_timing,
            'mean_day_of_year': mean_timing,
            'std_day_of_year': std_timing,
            'trend_slope': trend,
            'trend_r_squared': trend_r_squared,
            'p_value': p_value if 'p_value' in locals() else np.nan
        })
    
    baseline_df = pd.DataFrame(baseline_data)
    
    # Calculate reliability tier based on years observed for anomaly detection use
    def assign_reliability(row):
        # For anomaly detection, we want a more conservative approach
        # Based on research, 8+ years of consistent data is typically required for reliable anomaly detection
        if row['years_observed'] >= 10:
            return 'high'
        elif row['years_observed'] >= 8:
            # Medium quality for anomaly detection
            return 'medium' 
        elif row['years_observed'] >= 6:
            # Low quality but still potentially usable for some analyses
            return 'low'
        else:
            # Insufficient data for anomaly detection
            return 'insufficient'
    
    baseline_df['reliability_tier'] = baseline_df.apply(assign_reliability, axis=1)
    
    # Add anomaly_use_flag to indicate eligibility for anomaly detection
    def assign_anomaly_use_flag(row):
        # Only baselines with sufficient years should be eligible for anomaly detection
        if row['years_observed'] >= 6:
            return 'eligible_for_anomaly_detection'
        else:
            return 'insufficient_baseline'
    
    baseline_df['anomaly_use_flag'] = baseline_df.apply(assign_anomaly_use_flag, axis=1)
    
    # Save baseline
    output_dir = "./coverage_aware_baseline"
    os.makedirs(output_dir, exist_ok=True)
    
    baseline_file = os.path.join(output_dir, "ecological_baseline.csv")
    baseline_df.to_csv(baseline_file, index=False)
    
    print(f"Saved ecological baseline to {baseline_file}")
    print(f"Baseline contains {len(baseline_df)} entries")
    
    return baseline_df

def assess_coverage_comprehensive():
    """
    Performs comprehensive coverage assessment across all dimensions.
    
    This function creates a detailed coverage assessment that goes beyond the 
    existing basic coverage assessment by adding:
    - More granular reliability assessment
    - Data quality metrics
    - Spatial coverage metrics
    """
    
    # Read the input data
    annual_summary_file = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
    
    if not os.path.exists(annual_summary_file):
        raise FileNotFoundError(f"Annual summary file not found: {annual_summary_file}")
    
    df = pd.read_csv(annual_summary_file)
    
    # Ensure proper data types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['observation_count'] = pd.to_numeric(df['observation_count'], errors='coerce')
    df['median_day_of_year'] = pd.to_numeric(df['median_day_of_year'], errors='coerce')
    
    # Drop any rows with NaN values in critical columns
    df = df.dropna(subset=['year', 'observation_count'])
    
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
        
        # Calculate interannual variability
        if len(years) > 1:
            std_obs_per_year = float(obs_per_year.std())
            cv_obs_per_year = std_obs_per_year / (obs_per_year.mean() or 1)  # Coefficient of variation
        else:
            std_obs_per_year = 0
            cv_obs_per_year = 0
        
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
            'years_with_100plus_observations': years_with_100plus,
            'std_observations_per_year': std_obs_per_year,
            'cv_observations_per_year': cv_obs_per_year
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
    output_dir = "./coverage_aware_baseline"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "comprehensive_coverage_assessment.csv")
    coverage_df.to_csv(output_file, index=False)
    print(f"Saved comprehensive coverage metrics to {output_file}")
    
    # Save summary statistics by reliability tier
    tier_counts = coverage_df['reliability_tier'].value_counts()
    
    # Top 20 best-covered combinations (based on coverage_fraction)
    best_covered = coverage_df.nlargest(20, 'coverage_fraction')
    
    # Top 20 sparse combinations (based on years_missing)
    sparse_combinations = coverage_df.nlargest(20, 'years_missing')
    
    # Create comprehensive summary report
    summary_text = f"""Comprehensive Coverage Assessment
==================================

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total combinations analyzed: {len(coverage_df)}
Total observations: {int(coverage_df['total_observations'].sum())}

Reliability Tier Distribution:
{tier_counts.to_string()}

Top 20 Best-Covered Combinations (by coverage_fraction):
{best_covered[['species_id', 'common_name', 'phenophase_description', 'state', 'coverage_fraction']].to_string(index=False)}

Top 20 Sparse Combinations (by years_missing):
{sparse_combinations[['species_id', 'common_name', 'phenophase_description', 'state', 'years_missing']].to_string(index=False)}

Data Quality Summary:
- Average coverage fraction: {coverage_df['coverage_fraction'].mean():.3f}
- Median years observed: {coverage_df['years_observed'].median():.1f}
- Average median observations per year: {coverage_df['median_observations_per_year'].mean():.1f}
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
    
    print("Comprehensive coverage assessment completed successfully!")
    
    return coverage_df

def implement_anomaly_detection(baseline_df):
    """
    Implements anomaly detection for phenological timing data.
    
    Uses statistical methods and machine learning to identify anomalous 
    phenological events.
    """
    
    # Prepare data for anomaly detection
    detection_data = baseline_df.copy()
    
    # Filter out low reliability data
    high_quality_data = detection_data[detection_data['reliability_tier'] == 'high'].copy()
    
    print(f"Performing anomaly detection with {len(high_quality_data)} high-quality records")
    
    # If we have enough data for meaningful detection
    if len(high_quality_data) >= 20:
        # Use the day-of-year data for anomaly detection
        # Standardize the data for better detection
        scaler = StandardScaler()
        
        # Select numeric columns for scaling
        numeric_columns = ['median_day_of_year', 'mean_day_of_year', 'std_day_of_year', 
                          'trend_slope', 'trend_r_squared']
        
        # Filter to only existing columns
        existing_columns = [col for col in numeric_columns if col in high_quality_data.columns]
        
        if len(existing_columns) >= 2:
            # Scale the values
            scaled_data = scaler.fit_transform(high_quality_data[existing_columns])
            
            # Use Isolation Forest for anomaly detection
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomalies = iso_forest.fit_predict(scaled_data)
            
            # Add anomaly labels to DataFrame  
            high_quality_data['is_anomaly'] = anomalies
            
            # Identify specific anomalies 
            anomaly_indices = high_quality_data[high_quality_data['is_anomaly'] == -1].index
            
            # Show a sample of anomalies
            anomalies_df = high_quality_data.loc[anomaly_indices].copy()
            
            print(f"Detected {len(anomalies_df)} anomalies")
            
            if len(anomalies_df) > 0:
                print("Sample of detected anomalies:")
                print(anomalies_df[['species_id', 'common_name', 'phenophase_description', 
                                   'median_day_of_year', 'trend_slope', 'is_anomaly']].to_string(index=False))
            else:
                print("No anomalies detected")
            
            # Save results
            output_dir = "./coverage_aware_baseline"
            anomaly_file = os.path.join(output_dir, "anomaly_detection_results.csv")
            high_quality_data.to_csv(anomaly_file, index=False)
            print(f"Anomaly detection results saved to {anomaly_file}")
            
            # Create anomaly summary
            anomaly_summary = f"""Anomaly Detection Summary
======================

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total records analyzed: {len(high_quality_data)}
Records with anomalies: {len(anomalies_df)}

Anomaly details:
- Species: {anomalies_df['species_id'].value_counts().head().to_string() if len(anomalies_df) > 0 else 'None'}

"""
            anomaly_summary_file = os.path.join(output_dir, "anomaly_detection_summary.txt")
            with open(anomaly_summary_file, 'w') as f:
                f.write(anomaly_summary)
            
            print(f"Anomaly summary saved to {anomaly_summary_file}")
            
            return high_quality_data
            
        else:
            print("Not enough numeric columns for anomaly detection")
            return high_quality_data
    else:
        print("Insufficient data for anomaly detection")
        return high_quality_data

def main():
    """
    Main function to orchestrate the coverage-aware ecological baseline and anomaly detection process.
    """
    
    print("Starting Coverage-aware Ecological Baseline and Anomaly Detection Framework")
    print("=" * 70)
    
    try:
        # Step 1: Create ecological baseline
        print("\n1. Creating ecological baseline...")
        baseline_df = create_ecological_baseline()
        
        # Step 2: Perform comprehensive coverage assessment 
        print("\n2. Performing comprehensive coverage assessment...")
        coverage_df = assess_coverage_comprehensive()
        
        # Step 3: Implement anomaly detection
        print("\n3. Implementing anomaly detection...")
        annotated_df = implement_anomaly_detection(baseline_df)
        
        # Step 4: Generate final summary
        print("\n4. Generating final summary...")
        print(f"Final results saved in ./coverage_aware_baseline/")
        print("Framework execution completed successfully!")
        
        return baseline_df, coverage_df, annotated_df
        
    except Exception as e:
        print(f"Error in framework execution: {str(e)}")
        raise

if __name__ == "__main__":
    baseline, coverage, annotated = main()