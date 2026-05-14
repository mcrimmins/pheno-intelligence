#!/usr/bin/env python3
"""Modify existing baseline file to update reliability thresholds and add anomaly_use_flag."""

import pandas as pd
import os

def modify_baseline_file():
    # Load existing baseline
    baseline_file = "./coverage_aware_baseline/ecological_baseline.csv"
    baseline_df = pd.read_csv(baseline_file)
    
    print(f"Original baseline has {len(baseline_df)} records")
    
    # Update reliability tier based on years observed for anomaly detection use
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
    
    # Save modified baseline
    output_dir = "./coverage_aware_baseline"
    os.makedirs(output_dir, exist_ok=True)
    
    baseline_file_modified = os.path.join(output_dir, "ecological_baseline.csv")
    baseline_df.to_csv(baseline_file_modified, index=False)
    
    print(f"Saved modified ecological baseline to {baseline_file_modified}")
    print(f"Baseline contains {len(baseline_df)} entries")
    
    # Show summary
    print("\n=== MODIFIED BASELINE SUMMARY ===")
    print("Reliability Tier Distribution:")
    print(baseline_df['reliability_tier'].value_counts())
    print("\nAnomaly Use Flag Distribution:")
    print(baseline_df['anomaly_use_flag'].value_counts())
    
    return baseline_df

if __name__ == "__main__":
    modify_baseline_file()