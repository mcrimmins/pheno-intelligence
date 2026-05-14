#!/usr/bin/env python3
"""
Full dataset implementation of coverage-aware baseline and anomaly detection framework.
Processes the complete 522,585 row dataset with all required statistics.
"""

import pandas as pd
import numpy as np
import os
import warnings
import time
from datetime import datetime
from scipy import stats
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_dataset_structure(file_path):
    """Analyze the structure of the dataset to understand data types"""
    logger.info("Analyzing dataset structure...")
    
    # Read first few rows to understand data types
    sample_df = pd.read_csv(file_path, nrows=1000)
    
    logger.info(f"Dataset sample shape: {sample_df.shape}")
    logger.info("Column names and types:")
    for col, dtype in sample_df.dtypes.items():
        logger.info(f"  {col}: {dtype}")
    
    # Check for potential data quality issues
    logger.info(f"Null values per column:")
    for col in sample_df.columns:
        null_count = sample_df[col].isnull().sum()
        if null_count > 0:
            logger.info(f"  {col}: {null_count} null values")
    
    return sample_df.columns.tolist()

def compute_comprehensive_statistics(group_data):
    """Compute all required statistics for a group of data"""
    
    # Required basic statistics
    median_day_of_year = float(group_data['median_day_of_year'].median())
    mean_day_of_year = float(group_data['median_day_of_year'].mean())
    std_day_of_year = float(group_data['median_day_of_year'].std())
    
    # Additional statistics required
    day_of_year_values = group_data['median_day_of_year'].values
    
    # Ensure we have data
    if len(day_of_year_values) == 0:
        return None
    
    # Compute all required percentiles
    q10 = np.percentile(day_of_year_values, 10)
    q25 = np.percentile(day_of_year_values, 25) 
    q50 = np.percentile(day_of_year_values, 50)  # median
    q75 = np.percentile(day_of_year_values, 75)
    q90 = np.percentile(day_of_year_values, 90)
    
    # IQR
    iqr = q75 - q25
    
    # MAD (Median Absolute Deviation)
    mad = float(np.median(np.abs(day_of_year_values - np.median(day_of_year_values))))
    
    # Additional summary stats
    observation_density = group_data['observation_count'].mean()
    
    return {
        'median_day_of_year': median_day_of_year,
        'mean_day_of_year': mean_day_of_year,
        'std_day_of_year': std_day_of_year,
        'mad': mad,
        'iqr': iqr,
        'percentile_10': q10,
        'percentile_25': q25,
        'percentile_50': q50,   # median
        'percentile_75': q75,
        'percentile_90': q90,
        'observation_density': observation_density
    }

def assign_reliability_tier(row):
    """Assign reliability tier based on coverage and quality criteria"""
    years_observed = row['years_observed']
    coverage_fraction = row['coverage_fraction']
    median_observations = row['median_observations_per_year']
    
    if years_observed >= 10 and coverage_fraction >= 0.7 and median_observations >= 30:
        return 'high'
    elif years_observed >= 7 and coverage_fraction >= 0.5 and median_observations >= 15:
        return 'medium'
    elif years_observed >= 4:
        return 'low'
    else:
        return 'insufficient'

def compute_baseline_confidence_score(row):
    """
    Compute baseline confidence score based on:
    - years observed
    - coverage fraction
    - observation density
    
    Score: normalized weighted sum (0-1)
    """
    years_observed = row['years_observed']
    coverage_fraction = row['coverage_fraction'] 
    median_observations = row.get('median_observations_per_year', 0)
    observation_density = row.get('observation_density', 0)
    
    # Normalize years to 0-1 scale (using 15 years as max for normalization)
    years_norm = min(years_observed / 15.0, 1.0)
    
    # Coverage already 0-1
    coverage_norm = coverage_fraction
    
    # Normalize observation density (this would need some reasonable max, using 100)
    obs_density_norm = min(observation_density / 100.0, 1.0)
    
    # Weighted sum (adjust weights as needed)
    score = (0.4 * years_norm) + (0.4 * coverage_norm) + (0.2 * obs_density_norm)
    
    return score

def process_full_dataset(file_path, chunk_size=10000):
    """Process the full dataset in chunks to manage memory"""
    
    logger.info(f"Starting full dataset processing with chunk size: {chunk_size}")
    start_time = time.time()
    
    # Create output directory
    output_dir = "./coverage_aware_baseline_full"
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the file in chunks and process
    processed_groups = []
    total_groups = 0
    total_rows = 0
    excluded_groups = 0
    reliability_counts = {'high': 0, 'medium': 0, 'low': 0, 'insufficient': 0}
    largest_group = 0
    smallest_group = float('inf')
    
    # Initialize chunk processing
    for chunk_num, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
        logger.info(f"Processing chunk {chunk_num + 1} with {len(chunk)} rows")
        
        # Update total rows
        total_rows += len(chunk)
        
        # Process chunk
        # Group by species_id, common_name, phenophase_id, phenophase_description, state
        group_columns = ['species_id', 'common_name', 'phenophase_id', 'phenophase_description', 'state']
        
        # Check if necessary columns exist
        missing_cols = [col for col in group_columns if col not in chunk.columns]
        if missing_cols:
            logger.warning(f"Missing columns in chunk: {missing_cols}")
            for col in missing_cols:
                if col == 'phenophase_id':
                    chunk['phenophase_id'] = chunk['phenophase_id'].fillna(0).astype(int)
                elif col == 'state':
                    chunk['state'] = chunk['state'].fillna('Unknown')
                elif col == 'common_name':
                    chunk['common_name'] = chunk['common_name'].fillna('Unknown')
                    
        # Process groups for this chunk
        chunk_grouped = chunk.groupby(group_columns)
        
        for group_keys, group_data in chunk_grouped:
            # Ensure we have valid data
            if len(group_data) < 1:
                continue
                
            total_groups += 1
            
            # Extract group keys
            species_id, common_name, phenophase_id, phenophase_description, state = group_keys
            
            # Compute years covered and coverage metrics
            years = group_data['year'].unique()
            
            if len(years) == 0:
                excluded_groups += 1
                continue
                
            first_year = int(years.min())
            last_year = int(years.max())
            record_length_years = last_year - first_year + 1
            years_observed = len(years)
            coverage_fraction = years_observed / record_length_years if record_length_years > 0 else 0
            
            # Observations per year calculations
            obs_per_year = group_data.groupby('year')['observation_count'].sum()
            median_observations_per_year = float(obs_per_year.median()) if len(obs_per_year) > 0 else 0
            
            # Compute comprehensive statistics for this group
            stats_dict = compute_comprehensive_statistics(group_data)
            
            if stats_dict is None:
                excluded_groups += 1
                continue
                
            # Store the results
            group_result = {
                'species_id': species_id,
                'common_name': common_name,
                'phenophase_id': phenophase_id,
                'phenophase_description': phenophase_description,
                'state': state,
                'first_year': first_year,
                'last_year': last_year,
                'record_length_years': record_length_years,
                'years_observed': years_observed,
                'coverage_fraction': coverage_fraction,
                'median_observations_per_year': median_observations_per_year,
                'median_day_of_year': stats_dict['median_day_of_year'],
                'mean_day_of_year': stats_dict['mean_day_of_year'],
                'std_day_of_year': stats_dict['std_day_of_year'],
                'mad': stats_dict['mad'],
                'iqr': stats_dict['iqr'],
                'percentile_10': stats_dict['percentile_10'],
                'percentile_25': stats_dict['percentile_25'],
                'percentile_50': stats_dict['percentile_50'],
                'percentile_75': stats_dict['percentile_75'],
                'percentile_90': stats_dict['percentile_90'],
                'observation_density': stats_dict['observation_density'],
            }
            
            # Add reliability tier
            group_result['reliability_tier'] = assign_reliability_tier(group_result)
            reliability_counts[group_result['reliability_tier']] += 1
            
            # Add baseline confidence score
            group_result['baseline_confidence_score'] = compute_baseline_confidence_score(group_result)
            
            # Track group sizes
            group_size = len(group_data)
            if group_size > largest_group:
                largest_group = group_size
            if group_size < smallest_group:
                smallest_group = group_size
                
            # Add to results
            processed_groups.append(group_result)
            
        # Progress update
        if (chunk_num + 1) % 5 == 0:
            logger.info(f"Processed {chunk_num + 1} chunks, {len(processed_groups)} groups so far")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    logger.info(f"Processing completed in {processing_time:.2f} seconds")
    logger.info(f"Total groups processed: {len(processed_groups)}")
    logger.info(f"Total rows processed: {total_rows}")
    logger.info(f"Groups excluded for insufficient data: {excluded_groups}")
    
    if len(processed_groups) == 0:
        logger.warning("No groups were successfully processed!")
        return pd.DataFrame(), {}
    
    # Create final dataframe
    results_df = pd.DataFrame(processed_groups)
    
    logger.info(f"Final results: {len(results_df)} rows")
    
    # Summary statistics
    summary_stats = {
        'total_groups_processed': len(processed_groups),
        'total_rows_processed': total_rows,
        'excluded_groups': excluded_groups,
        'largest_group_size': largest_group,
        'smallest_group_size': smallest_group,
        'reliability_counts': reliability_counts,
        'processing_time_seconds': processing_time
    }
    
    return results_df, summary_stats

def generate_validation_summary(summary_stats, results_df, output_dir):
    """Generate validation summary file"""
    
    logger.info("Generating validation summary...")
    
    # Create summary statistics
    summary_output = []
    summary_output.append("=== BASELINE VALIDATION SUMMARY ===")
    summary_output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_output.append("")
    
    # Basic stats
    summary_output.append("=== BASIC STATISTICS ===")
    summary_output.append(f"Total groups processed: {summary_stats['total_groups_processed']}")
    summary_output.append(f"Total rows processed: {summary_stats['total_rows_processed']}")
    summary_output.append(f"Groups excluded for insufficient data: {summary_stats['excluded_groups']}")
    summary_output.append(f"Processing time: {summary_stats['processing_time_seconds']:.2f} seconds")
    summary_output.append("")
    
    # Reliability tiers
    summary_output.append("=== RELIABILITY TIER DISTRIBUTION ===")
    for tier, count in summary_stats['reliability_counts'].items():
        percentage = (count / summary_stats['total_groups_processed']) * 100 if summary_stats['total_groups_processed'] > 0 else 0
        summary_output.append(f"{tier}: {count} ({percentage:.1f}%)")
    summary_output.append("")
    
    # Group size distribution
    summary_output.append("=== GROUP SIZE DISTRIBUTION ===")
    summary_output.append(f"Largest group: {summary_stats['largest_group_size']} observations")
    summary_output.append(f"Smallest group: {summary_stats['smallest_group_size']} observations")
    summary_output.append("")
    
    # Observation density distribution
    if not results_df.empty:
        obs_density = results_df['observation_density'].dropna()
        if len(obs_density) > 0:
            summary_output.append("=== OBSERVATION DENSITY DISTRIBUTION ===")
            summary_output.append(f"Average observation density: {obs_density.mean():.2f}")
            summary_output.append(f"Median observation density: {obs_density.median():.2f}")
            summary_output.append(f"Standard deviation: {obs_density.std():.2f}")
            summary_output.append(f"Min: {obs_density.min():.2f}")
            summary_output.append(f"Max: {obs_density.max():.2f}")
            summary_output.append("")
    
    # Confidence score distribution  
    if not results_df.empty:
        confidence_scores = results_df['baseline_confidence_score'].dropna()
        if len(confidence_scores) > 0:
            summary_output.append("=== BASELINE CONFIDENCE SCORE DISTRIBUTION ===")
            summary_output.append(f"Average confidence score: {confidence_scores.mean():.3f}")
            summary_output.append(f"Median confidence score: {confidence_scores.median():.3f}")
            summary_output.append(f"Min: {confidence_scores.min():.3f}")
            summary_output.append(f"Max: {confidence_scores.max():.3f}")
            summary_output.append("")
    
    # Memory usage notes
    if not results_df.empty:
        mem_usage = results_df.memory_usage(deep=True).sum()
        summary_output.append("=== MEMORY USAGE ===")
        summary_output.append(f"Memory usage: {mem_usage / (1024*1024):.2f} MB")
        summary_output.append("")
    
    # Write to file
    summary_file = os.path.join(output_dir, "baseline_validation_summary.txt")
    with open(summary_file, 'w') as f:
        f.write('\n'.join(summary_output))
    
    logger.info(f"Validation summary written to {summary_file}")
    return summary_file

def main():
    """
    Main function to process full dataset and generate outputs.
    """
    print("Starting Full Dataset Coverage-aware Framework")
    print("=" * 70)
    
    try:
        # Analyze dataset structure
        dataset_path = "/outputs/phenology-intelligence-v1/annual_summaries/annual_species_phenophase_summary.csv"
        logger.info(f"Loading dataset from: {dataset_path}")
        
        file_columns = analyze_dataset_structure(dataset_path)
        logger.info(f"Dataset columns: {file_columns}")
        
        # Process full dataset
        logger.info("Processing full dataset...")
        results_df, summary_stats = process_full_dataset(dataset_path, chunk_size=10000)
        
        if results_df.empty:
            logger.error("No data was processed successfully!")
            return None, None
        
        # Save the results
        output_dir = "./coverage_aware_baseline_full"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main results
        output_file = os.path.join(output_dir, "coverage_aware_baseline_full.csv")
        results_df.to_csv(output_file, index=False)
        logger.info(f"Full results saved to {output_file}")
        
        # Generate validation summary
        summary_file = generate_validation_summary(summary_stats, results_df, output_dir)
        logger.info(f"Validation summary saved to {summary_file}")
        
        # Additional verification
        print(f"Total groups processed: {summary_stats['total_groups_processed']}")
        print(f"Total rows processed: {summary_stats['total_rows_processed']}")
        print(f"Processing completed in {summary_stats['processing_time_seconds']:.2f} seconds")
        print(f"Output files: {output_file}, {summary_file}")
        
        # Show sample of results
        print("\nSample of results:")
        print(results_df.head().to_string())
        
        return results_df, summary_stats
        
    except Exception as e:
        logger.error(f"ERROR during full dataset processing: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    results, summary = main()