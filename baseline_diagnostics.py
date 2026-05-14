#!/usr/bin/env python3
"""
Baseline Diagnostics Script for Phenology Intelligence System
Generates scientific validation diagnostics and visualizations for the full ecological baseline system.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Setup directories
INPUT_FILE = '/workspace/phenology-intelligence-v1/coverage_aware_baseline_full/coverage_aware_baseline_full.csv'
OUTPUT_DIR = '/workspace/phenology-intelligence-v1/baseline_diagnostics_output/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Load the baseline data"""
    print("Loading baseline data...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Data loaded. Shape: {df.shape}")
    return df

def create_reliability_summary(df):
    """Generate reliability tier summary table"""
    print("Creating reliability tier summary...")
    summary = df['reliability_tier'].value_counts().reset_index()
    summary.columns = ['reliability_tier', 'count']
    summary['percentage'] = (summary['count'] / len(df)) * 100
    summary = summary.sort_values('count', ascending=False)
    
    # Save summary
    summary.to_csv(os.path.join(OUTPUT_DIR, 'reliability_tier_summary.csv'), index=False)
    print("Reliability tier summary saved to CSV")
    
    return summary

def plot_years_observed(df):
    """Plot histogram of years_observed"""
    print("Creating years_observed histogram...")
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    plt.hist(df['years_observed'].dropna(), bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    
    plt.title('Distribution of Years Observed', fontsize=14, fontweight='bold')
    plt.xlabel('Years Observed', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_years = df['years_observed'].mean()
    plt.axvline(mean_years, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_years:.1f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'years_observed_distribution.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Years observed histogram saved")

def plot_coverage_fraction(df):
    """Plot histogram of coverage_fraction"""
    print("Creating coverage_fraction histogram...")
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    plt.hist(df['coverage_fraction'].dropna(), bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
    
    plt.title('Distribution of Coverage Fraction', fontsize=14, fontweight='bold')
    plt.xlabel('Coverage Fraction', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_coverage = df['coverage_fraction'].mean()
    plt.axvline(mean_coverage, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_coverage:.2f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'coverage_fraction_distribution.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Coverage fraction histogram saved")

def plot_confidence_scores(df):
    """Plot histogram of baseline_confidence_score"""
    print("Creating baseline_confidence_score histogram...")
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    plt.hist(df['baseline_confidence_score'].dropna(), bins=50, alpha=0.7, color='orange', edgecolor='black')
    
    plt.title('Distribution of Baseline Confidence Scores', fontsize=14, fontweight='bold')
    plt.xlabel('Confidence Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_score = df['baseline_confidence_score'].mean()
    plt.axvline(mean_score, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_score:.2f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confidence_scores_distribution.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Confidence scores histogram saved")

def plot_mad_iqr(df):
    """Plot histograms of MAD and IQR"""
    print("Creating MAD and IQR distributions...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # MAD histogram
    ax1.hist(df['mad'].dropna(), bins=50, alpha=0.7, color='coral', edgecolor='black')
    ax1.set_title('Distribution of MAD (Median Absolute Deviation)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('MAD (days)', fontsize=10)
    ax1.set_ylabel('Frequency', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Add mean line
    mean_mad = df['mad'].mean()
    ax1.axvline(mean_mad, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_mad:.1f}')
    ax1.legend()
    
    # IQR histogram
    ax2.hist(df['iqr'].dropna(), bins=50, alpha=0.7, color='lightblue', edgecolor='black')
    ax2.set_title('Distribution of IQR (Interquartile Range)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('IQR (days)', fontsize=10)
    ax2.set_ylabel('Frequency', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Add mean line
    mean_iqr = df['iqr'].mean()
    ax2.axvline(mean_iqr, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_iqr:.1f}')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'mad_iqr_distributions.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("MAD and IQR distributions saved")

def plot_median_day_of_year(df):
    """Plot distribution of median_day_of_year"""
    print("Creating median_day_of_year distribution...")
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    plt.hist(df['median_day_of_year'].dropna(), bins=50, alpha=0.7, color='purple', edgecolor='black')
    
    plt.title('Distribution of Median Day of Year', fontsize=14, fontweight='bold')
    plt.xlabel('Median Day of Year', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_day = df['median_day_of_year'].mean()
    plt.axvline(mean_day, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_day:.1f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'median_day_of_year_distribution.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Median day of year distribution saved")

def get_top_confidence_groups(df, n=50):
    """Get top n highest and lowest confidence groups"""
    print(f"Finding top {n} confidence groups...")
    
    # Top n highest confidence
    top_high = df.nlargest(n, 'baseline_confidence_score')
    top_high.to_csv(os.path.join(OUTPUT_DIR, 'top_50_highest_confidence.csv'), index=False)
    
    # Top n lowest confidence
    top_low = df.nsmallest(n, 'baseline_confidence_score')
    top_low.to_csv(os.path.join(OUTPUT_DIR, 'top_50_lowest_confidence.csv'), index=False)
    
    print(f"Top {n} confidence groups saved to CSV")
    return top_high, top_low

def get_species_variability(df):
    """Get species with largest and smallest phenological variability"""
    print("Calculating species variability...")
    
    # Group by species and calculate variability (using MAD)
    species_var = df.groupby('common_name')['mad'].agg(['mean', 'count']).reset_index()
    species_var.columns = ['common_name', 'avg_mad', 'observation_count']
    species_var = species_var.sort_values('avg_mad', ascending=False)
    
    # Save results
    species_var.to_csv(os.path.join(OUTPUT_DIR, 'species_mad_variability.csv'), index=False)
    
    # Top 10 most variable species
    top_var = species_var.head(10)
    top_var.to_csv(os.path.join(OUTPUT_DIR, 'top_10_most_variable_species.csv'), index=False)
    
    # Top 10 least variable species
    least_var = species_var.tail(10)
    least_var.to_csv(os.path.join(OUTPUT_DIR, 'top_10_least_variable_species.csv'), index=False)
    
    print("Species variability calculations saved")
    return species_var, top_var, least_var

def create_state_summary(df):
    """Create state-level coverage summary"""
    print("Creating state-level coverage summary...")
    
    state_summary = df.groupby('state').agg({
        'baseline_confidence_score': 'mean',
        'years_observed': 'mean',
        'coverage_fraction': 'mean',
        'mad': 'mean'
    }).reset_index()
    
    state_summary.columns = ['state', 'avg_confidence', 'avg_years_observed', 'avg_coverage_fraction', 'avg_mad']
    
    # Sort by average confidence to see which states have the most reliable data
    state_summary = state_summary.sort_values('avg_confidence', ascending=False)
    
    state_summary.to_csv(os.path.join(OUTPUT_DIR, 'state_coverage_summary.csv'), index=False)
    print("State coverage summary saved")
    
    return state_summary

def create_reliability_by_state(df):
    """Create reliability tier distribution by state"""
    print("Creating reliability tier by state...")
    
    state_reliability = df.groupby(['state', 'reliability_tier']).size().reset_index(name='count')
    
    # Pivot for easier plotting
    pivot_data = state_reliability.pivot(index='state', columns='reliability_tier', values='count').fillna(0)
    pivot_data.to_csv(os.path.join(OUTPUT_DIR, 'reliability_tier_by_state.csv'))
    
    print("Reliability tier by state saved")
    return pivot_data

def create_reliability_by_phenophase(df):
    """Create reliability tier distribution by phenophase"""
    print("Creating reliability tier by phenophase...")
    
    phenophase_reliability = df.groupby(['phenophase_description', 'reliability_tier']).size().reset_index(name='count')
    
    # Pivot for easier plotting
    pivot_data = phenophase_reliability.pivot(index='phenophase_description', columns='reliability_tier', values='count').fillna(0)
    pivot_data.to_csv(os.path.join(OUTPUT_DIR, 'reliability_tier_by_phenophase.csv'))
    
    print("Reliability tier by phenophase saved")
    return pivot_data

def plot_observation_density(df):
    """Plot observation density distributions"""
    print("Creating observation density distribution...")
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    plt.hist(df['observation_density'].dropna(), bins=50, alpha=0.7, color='green', edgecolor='black')
    
    plt.title('Distribution of Observation Density', fontsize=14, fontweight='bold')
    plt.xlabel('Observation Density', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_density = df['observation_density'].mean()
    plt.axvline(mean_density, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_density:.1f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'observation_density_distribution.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    print("Observation density distribution saved")

def generate_diagnostics_report(df):
    """Generate the comprehensive diagnostic report"""
    print("Generating diagnostic report...")
    
    report_content = f"""
# Phenology Intelligence Baseline Diagnostics Report

## Dataset Overview
- Total entries processed: {len(df):,}
- Unique species: {df['common_name'].nunique():,}
- Unique phenophases: {df['phenophase_description'].nunique():,}
- Unique states: {df['state'].nunique():,}

## Reliability Tier Summary
"""
    
    reliability_summary = df['reliability_tier'].value_counts()
    for tier, count in reliability_summary.items():
        percentage = (count / len(df)) * 100
        report_content += f"- {tier}: {count:,} ({percentage:.1f}%)\n"
    
    # Data quality stats
    report_content += f"""
## Data Quality Statistics
- Mean Years Observed: {df['years_observed'].mean():.1f}
- Mean Coverage Fraction: {df['coverage_fraction'].mean():.2f}
- Mean Confidence Score: {df['baseline_confidence_score'].mean():.3f}
- Mean MAD: {df['mad'].mean():.1f} days
- Mean IQR: {df['iqr'].mean():.1f} days
- Mean Observation Density: {df['observation_density'].mean():.1f}

## Key Observations
"""

    # Top 5 most reliable species
    top_reliable = df.groupby('common_name')['baseline_confidence_score'].mean().nlargest(5)
    report_content += f"### Top 5 Most Reliable Species\n"
    for species, score in top_reliable.items():
        report_content += f"- {species}: {score:.3f}\n"

    # Data sparsity observations
    report_content += f"""
## Data Sparsity Analysis
- Most common years observed: {df['years_observed'].mode()[0]}
- Median years observed: {df['years_observed'].median():.0f}
- Most common coverage fraction: {df['coverage_fraction'].mode()[0]}
- Most common confidence score: {df['baseline_confidence_score'].mode()[0]:.3f}

## Implications for Anomaly Detection
"""

    # Analyze confidence and reliability for anomaly detection
    high_confidence = df[df['baseline_confidence_score'] > 0.7]
    low_confidence = df[df['baseline_confidence_score'] < 0.3]
    
    report_content += f"""
- High confidence groups (score > 0.7): {len(high_confidence):,} ({len(high_confidence)/len(df)*100:.1f}%)
- Low confidence groups (score < 0.3): {len(low_confidence):,} ({len(low_confidence)/len(df)*100:.1f}%)

## Recommendations for Hierarchical Baselines

1. **Data Quality Filtering**: Only use groups with confidence scores > 0.5 for robust anomaly detection
2. **Multi-scale Approach**: Consider using groups with higher reliability as baselines for more sensitive detection in lower quality data
3. **State-based Adaptation**: Apply state-specific confidence thresholds based on available data coverage
4. **Phenophase-specific Considerations**: Different phenophase types may require different reliability thresholds

## Data Coverage by State
"""
    
    state_summary = df.groupby('state').agg({
        'baseline_confidence_score': 'mean',
        'coverage_fraction': 'mean'
    }).sort_values('baseline_confidence_score', ascending=False)
    
    for state, row in state_summary.iterrows():
        report_content += f"- {state}: Mean confidence = {row['baseline_confidence_score']:.3f}, Coverage = {row['coverage_fraction']:.2f}\n"
    
    # Save report
    with open(os.path.join(OUTPUT_DIR, 'baseline_diagnostics_report.md'), 'w') as f:
        f.write(report_content)
    
    print("Diagnostic report generated")

def main():
    """Main execution function"""
    print("Starting baseline diagnostics generation...")
    
    # Load data
    df = load_data()
    
    # Generate all diagnostics
    create_reliability_summary(df)
    plot_years_observed(df)
    plot_coverage_fraction(df)
    plot_confidence_scores(df) 
    plot_mad_iqr(df)
    plot_median_day_of_year(df)
    get_top_confidence_groups(df)
    get_species_variability(df)
    create_state_summary(df)
    create_reliability_by_state(df)
    create_reliability_by_phenophase(df)
    plot_observation_density(df)
    generate_diagnostics_report(df)
    
    print("Baseline diagnostics complete!")

if __name__ == "__main__":
    main()