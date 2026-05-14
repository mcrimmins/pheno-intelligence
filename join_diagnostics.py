#!/usr/bin/env python3
"""
Join Diagnostics Analysis for Phenology Intelligence Project
=========================================================

This script performs comprehensive join diagnostics between the annual phenology
data and baseline data to identify issues with the join process.

The analysis answers key questions:
1. How many annual rows successfully join to baseline rows?
2. How many fail to join?
3. What are the key failure patterns?
4. What normalization steps are needed?

Expected files:
- /workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv (baseline)
- /outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv (annual data)
"""

import pandas as pd
import numpy as np
import os
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def print_file_info(file_path, file_name):
    """Print basic file information."""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        df = pd.read_csv(file_path)
        rows = len(df)
        print(f"✓ {file_name} - {size} bytes, {rows} rows")
        return df
    else:
        print(f"✗ {file_name} - NOT FOUND")
        return None

def get_unique_values(df, columns):
    """Get unique values for specified columns."""
    unique_counts = {}
    for col in columns:
        if col in df.columns:
            unique_counts[col] = df[col].nunique()
        else:
            unique_counts[col] = "Column not found"
    return unique_counts

def analyze_data_structures():
    """Analyze the structure and content of available data files."""
    print("=== DATASET STRUCTURE ANALYSIS ===\n")
    
    # Load data files
    baseline_df = print_file_info(
        "/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv", 
        "Ecological Baseline"
    )
    
    anomaly_df = print_file_info(
        "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv", 
        "Annual Anomalies"
    )
    
    print("\n=== BASELINE DATASET COLUMNS ===")
    if baseline_df is not None:
        for col in baseline_df.columns:
            print(f"  {col}")
            
    print("\n=== ANNUAL ANOMALIES DATASET COLUMNS ===")
    if anomaly_df is not None:
        for col in anomaly_df.columns:
            print(f"  {col}")
    
    print("\n=== BASELINE DATASET STATISTICS ===")
    if baseline_df is not None:
        baseline_stats = get_unique_values(baseline_df, ['species_id', 'state', 'phenophase_description'])
        for col, count in baseline_stats.items():
            if isinstance(count, int):
                print(f"  {col}: {count} unique values")
        
        # Year range
        if 'year' in baseline_df.columns:
            print(f"  Year range: {baseline_df['year'].min()} - {baseline_df['year'].max()}")
        elif 'last_year' in baseline_df.columns:
            print(f"  Last year range: {baseline_df['last_year'].min()} - {baseline_df['last_year'].max()}")
            
    print("\n=== ANNUAL ANOMALIES DATASET STATISTICS ===")
    if anomaly_df is not None:
        anomaly_stats = get_unique_values(anomaly_df, ['species_id', 'state', 'phenophase_description', 'year'])
        for col, count in anomaly_stats.items():
            if isinstance(count, int):
                print(f"  {col}: {count} unique values")
        
        if 'year' in anomaly_df.columns:
            print(f"  Year range: {anomaly_df['year'].min()} - {anomaly_df['year'].max()}")

def perform_join_analysis():
    """Main join analysis function."""
    print("\n=== JOIN PROCESS ANALYSIS ===\n")
    
    # Load data
    baseline_df = pd.read_csv("/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv")
    anomaly_df = pd.read_csv("/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv")
    
    print("Join Key Analysis:")
    print("-" * 40)
    print("Baseline keys: species_id, state, phenophase_description")
    print("Anomaly keys: species_id, state, phenophase_description, year")
    print()
    
    # Key columns for matching (what we'd normally join on)
    join_keys = ['species_id', 'state', 'phenophase_description']  # Note: no year in the baseline
    
    # Create a join key for baseline 
    baseline_unique = baseline_df[join_keys].drop_duplicates()
    print(f"Baseline records: {len(baseline_df)}")
    print(f"Unique baseline combinations: {len(baseline_unique)}")
    
    # Create a join key for anomaly data
    anomaly_unique = anomaly_df[join_keys].drop_duplicates()
    print(f"Anomaly records: {len(anomaly_df)}")
    print(f"Unique anomaly combinations: {len(anomaly_unique)}")
    
    # Create sets for efficient lookups
    baseline_set = set(map(tuple, baseline_unique[join_keys].values))
    anomaly_set = set(map(tuple, anomaly_unique[join_keys].values))
    
    # Find matches
    matched_combinations = baseline_set.intersection(anomaly_set)
    unmatched_baseline = baseline_set.difference(anomaly_set)
    unmatched_anomaly = anomaly_set.difference(baseline_set)
    
    print(f"\nJoin Results:")
    print("-" * 40)
    print(f"Total baseline combinations: {len(baseline_set)}")
    print(f"Total anomaly combinations: {len(anomaly_set)}")
    print(f"Successfully matched combinations: {len(matched_combinations)}")
    print(f"Failed to match in baseline: {len(unmatched_baseline)}")
    print(f"Successfully matched in anomaly: {len(anomaly_set) - len(unmatched_anomaly)}")
    
    if len(baseline_set) > 0:
        percentage_matched = (len(matched_combinations) / len(baseline_set)) * 100
        print(f"Percentage matched: {percentage_matched:.2f}%")
    
    # Analyze failures
    print(f"\nFailure Analysis:")
    print("-" * 40)
    
    # Analyze unmatched baseline combinations
    if unmatched_baseline:
        unmatched_df = pd.DataFrame(list(unmatched_baseline), columns=join_keys)
        print(f"Top 5 unmatched baseline combinations:")
        for i, (_, row) in enumerate(unmatched_df.head().iterrows()):
            print(f"  {row['species_id']}, {row['state']}, {row['phenophase_description']}")
            if i >= 4:
                break
    
    # Analyze unmatched anomaly combinations
    if unmatched_anomaly:
        unmatched_df = pd.DataFrame(list(unmatched_anomaly), columns=join_keys)
        print(f"Top 5 unmatched anomaly combinations:")
        for i, (_, row) in enumerate(unmatched_df.head().iterrows()):
            print(f"  {row['species_id']}, {row['state']}, {row['phenophase_description']}")
            if i >= 4:
                break
    
    return baseline_df, anomaly_df, matched_combinations, unmatched_baseline, unmatched_anomaly

def analyze_join_failures():
    """Analyze the causes of join failures."""
    print("\n=== JOIN FAILURE ANALYSIS ===\n")
    
    # Load data
    baseline_df = pd.read_csv("/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv")
    anomaly_df = pd.read_csv("/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv")
    
    # Analyze mismatched key types and issues
    print("Key Analysis:")
    print("-" * 40)
    
    # Check data types
    print("Baseline column data types:")
    for col in baseline_df.columns:
        if col in ['species_id', 'state', 'phenophase_description']:
            print(f"  {col}: {baseline_df[col].dtype}")
    
    print("Anomaly column data types:")
    for col in anomaly_df.columns:
        if col in ['species_id', 'state', 'phenophase_description']:
            print(f"  {col}: {anomaly_df[col].dtype}")
    
    # Check for whitespace or case issues
    print("\nData Quality Issues:")
    print("-" * 40)
    
    def check_whitespace(df, column):
        if column in df.columns:
            # Only check string columns for whitespace issues
            if df[column].dtype == 'object' or df[column].dtype == 'string':
                original_unique = df[column].nunique()
                # Check for leading/trailing whitespace
                df_no_ws = df[column].str.strip()
                stripped_unique = df_no_ws.nunique() 
                if original_unique != stripped_unique:
                    print(f"  {column}: whitespace found - {original_unique} vs {stripped_unique} unique values after strip")
                    return True
            return False
        return False
    
    whitespace_found = False
    whitespace_found |= check_whitespace(baseline_df, 'state')
    whitespace_found |= check_whitespace(anomaly_df, 'state')
    whitespace_found |= check_whitespace(baseline_df, 'species_id')
    whitespace_found |= check_whitespace(anomaly_df, 'species_id')
    whitespace_found |= check_whitespace(baseline_df, 'phenophase_description')
    whitespace_found |= check_whitespace(anomaly_df, 'phenophase_description')
    
    if not whitespace_found:
        print("  No whitespace issues detected")
    
    # Check case sensitivity in state names
    if 'state' in baseline_df.columns and 'state' in anomaly_df.columns:
        baseline_states = set(baseline_df['state'].str.upper().dropna())
        anomaly_states = set(anomaly_df['state'].str.upper().dropna())
        print(f"\nState Name Analysis:")
        print(f"  Baseline unique states: {len(baseline_states)}")
        print(f"  Anomaly unique states: {len(anomaly_states)}")
        print(f"  Baseline states: {sorted(list(baseline_states))}")
        print(f"  Anomaly states: {sorted(list(anomaly_states))}")
        
        if baseline_states - anomaly_states:
            print(f"  States in baseline but not in anomaly: {baseline_states - anomaly_states}")
        if anomaly_states - baseline_states:
            print(f"  States in anomaly but not in baseline: {anomaly_states - baseline_states}")

def generate_join_diagnostics_report():
    """Generate comprehensive join diagnostic report."""
    print("\n\n" + "="*60)
    print("JOIN DIAGNOSTIC REPORT")
    print("="*60)
    
    # Load data
    baseline_df = pd.read_csv("/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv")
    anomaly_df = pd.read_csv("/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv")
    
    # Get file sizes
    baseline_size = os.path.getsize("/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv")
    anomaly_size = os.path.getsize("/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv")
    
    # Calculate statistics
    baseline_records = len(baseline_df)
    anomaly_records = len(anomaly_df)
    
    # Create diagnostic summary
    report_lines = [
        "# Join Diagnostics Report",
        "",
        "## File Information",
        f"- Baseline file: {baseline_size} bytes, {baseline_records} records",
        f"- Anomaly file: {anomaly_size} bytes, {anomaly_records} records",
        "",
        "## Key Statistics",
    ]
    
    # Join analysis results
    join_keys = ['species_id', 'state', 'phenophase_description']
    
    # Create unique combinations
    baseline_unique = baseline_df[join_keys].drop_duplicates()
    anomaly_unique = anomaly_df[join_keys].drop_duplicates()
    
    matched = len(set(map(tuple, baseline_unique[join_keys].values)).intersection(
        set(map(tuple, anomaly_unique[join_keys].values))
    ))
    
    total_baseline = len(baseline_unique)
    total_anomaly = len(anomaly_unique)
    
    report_lines.extend([
        f"- Total baseline combinations: {total_baseline}",
        f"- Total anomaly combinations: {total_anomaly}",
        f"- Successfully matched combinations: {matched}",
        f"- Failed to match combinations: {total_baseline - matched}",
        f"- Percentage matched: {100 * matched / total_baseline if total_baseline > 0 else 0:.2f}%",
        "",
        "## Top Causes of Failed Joins",
        "- Incomplete baseline data coverage",
        "- Missing species or phenophase combinations",
        "- Mismatched state identifiers (whitespace, case, abbreviations)",
        "- Data quality inconsistencies",
        "",
        "## Data Quality Issues",
    ])
    
    # Data type checking
    type_issues = []
    for col in join_keys:
        if col in baseline_df.columns and col in anomaly_df.columns:
            if str(baseline_df[col].dtype) != str(anomaly_df[col].dtype):
                type_issues.append(f"- Column '{col}' has different data types: baseline={baseline_df[col].dtype}, anomaly={anomaly_df[col].dtype}")
    
    if type_issues:
        report_lines.extend(type_issues)
    else:
        report_lines.append("- No data type mismatches found")
    
    # Missing values
    missing_baseline = baseline_df[join_keys].isnull().sum()
    missing_anomaly = anomaly_df[join_keys].isnull().sum()
    
    report_lines.append("  Missing values:")
    for col in join_keys:
        if col in missing_baseline.index and missing_baseline[col] > 0:
            report_lines.append(f"  - Baseline '{col}': {missing_baseline[col]}")
        if col in missing_anomaly.index and missing_anomaly[col] > 0:
            report_lines.append(f"  - Anomaly '{col}': {missing_anomaly[col]}")
    
    if all([missing_baseline[col] == 0 for col in join_keys if col in missing_baseline.index]) and \
       all([missing_anomaly[col] == 0 for col in join_keys if col in missing_anomaly.index]):
        report_lines.append("  - No missing values in join keys")
    
    # Save the report
    with open("/workspace/phenology-intelligence-v1/join_diagnostics_report.md", "w") as f:
        f.write("\n".join(report_lines))
    
    print("\n".join(report_lines))
    
    return True

def generate_failure_examples():
    """Generate sample failure examples."""
    print("\n=== FAILED JOIN EXAMPLES ===\n")
    
    # Load data files
    baseline_df = pd.read_csv("/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv")
    anomaly_df = pd.read_csv("/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv")
    
    # Key columns for matching
    join_keys = ['species_id', 'state', 'phenophase_description']
    
    # Create sets for lookups
    baseline_set = set(map(tuple, baseline_df[join_keys].drop_duplicates().values))
    anomaly_set = set(map(tuple, anomaly_df[join_keys].drop_duplicates().values))
    
    # Find unmatched combinations  
    unmatched_baseline = baseline_set.difference(anomaly_set)
    unmatched_anomaly = anomaly_set.difference(baseline_set)
    
    print("Examples of unmatched baseline combinations (what's in baseline but not matched):")
    print("-" * 80)
    
    examples_printed = 0
    for i, combo in enumerate(unmatched_baseline):
        if examples_printed >= 5:  # Limit to 5 examples
            break
        print(f"  Example {i+1}: species={combo[0]}, state={combo[1]}, phenophase={combo[2]}")
        examples_printed += 1
    
    if examples_printed == 0:
        print("  No unmatched baseline combinations found - all baseline entries matched")
    
    print("\nExamples of unmatched anomaly combinations (what's in anomalies but not matched):")
    print("-" * 80)
    
    # Find samples from unmatched anomaly combinations
    examples_printed = 0
    for i, combo in enumerate(unmatched_anomaly):
        if examples_printed >= 5:  # Limit to 5 examples
            break
        print(f"  Example {i+1}: species={combo[0]}, state={combo[1]}, phenophase={combo[2]}")
        examples_printed += 1
    
    if examples_printed == 0:
        print("  No unmatched anomaly combinations found")
    
    # Create failure examples CSV file
    failure_examples_data = []
    
    # Add unmatched baseline examples
    baseline_count = 0
    for combo in unmatched_baseline:
        example = {
            'type': 'baseline_mismatch',
            'species_id': combo[0],
            'state': combo[1],
            'phenophase_description': combo[2],
            'notes': 'Exists in baseline but not in anomalies'
        }
        failure_examples_data.append(example)
        baseline_count += 1
        if baseline_count >= 5:
            break
            
    # Add unmatched anomaly examples  
    anomaly_count = 0
    for combo in unmatched_anomaly:
        example = {
            'type': 'anomaly_mismatch',
            'species_id': combo[0],
            'state': combo[1],
            'phenophase_description': combo[2],
            'notes': 'Exists in anomalies but not in baseline'
        }
        failure_examples_data.append(example)
        anomaly_count += 1
        if anomaly_count >= 5:
            break
    
    if failure_examples_data:
        failure_df = pd.DataFrame(failure_examples_data)
        failure_df.to_csv("/workspace/phenology-intelligence-v1/join_failure_examples.csv", index=False)
        print(f"\nSaved {len(failure_examples_data)} failure examples to join_failure_examples.csv")
    else:
        print("\nNo failure examples to save")
    
    return True

def print_summary():
    """Print summary of the analysis."""
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("Analysis completed successfully!")
    print()
    print("Key findings:")
    print("- Files analyzed: baseline and anomalies")
    print("- Join keys: species_id, state, phenophase_description")
    print("- Report generated: join_diagnostics_report.md")
    print("- Examples saved: join_failure_examples.csv")
    print()
    print("Next steps:")
    print("1. Review join_diagnostics_report.md for comprehensive analysis")
    print("2. Examine join_failure_examples.csv for specific failure patterns")
    print("3. Consider data normalization strategies based on findings")
    print("4. Re-run anomaly processing with corrected joins")

if __name__ == "__main__":
    print("Phenology Intelligence Join Diagnostics Analysis")
    print("="*50)
    print("Analyzing join process between baseline and anomaly datasets\n")
    
    analyze_data_structures()
    perform_join_analysis()
    analyze_join_failures()  
    generate_join_diagnostics_report()
    generate_failure_examples()
    print_summary()