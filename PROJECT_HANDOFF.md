# Phenology Intelligence Project Handoff Document

## 1. Project Purpose

The Phenology Intelligence project is designed to analyze and visualize species phenology data to understand seasonal timing patterns and their variations over time. This platform provides insights into how climate and environmental factors affect biological events like flowering, migration, and leaf emergence.

### Current Analytical Goals
- Monitor phenological trends across species, states, and time periods
- Identify significant changes in seasonal timing patterns
- Provide spatial context for phenology observations
- Support climate change impact assessments
- Enable species and regional comparisons
- Visualize temporal and spatial patterns for research and policy making

## 2. Data Sources

### Raw Data
- **Raw CSV Path**: `/workspace/phenology-intelligence-v1/data/phenology_data.csv`

### Parquet Data
- **Parquet Path**: `/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet`

### Summary Output Paths
- **Summaries Path**: `/outputs/phenology-intelligence-v1/summaries/`
- **Annual Summaries Path**: `/outputs/phenology-intelligence-v1/annual_summaries/`

### Dashboard Script
- **Streamlit App**: `/workspace/phenology-intelligence-v1/streamlit_app.py`

## 3. Dataset Characteristics Learned

### File Size & Structure
- **Parquet File Row Count**: ~235MB file with numerous observations
- **Column Count**: Approximately 20+ columns in original dataset
- **Date Range**: Years from 2000-2020 (based on data exploration)
- **Key Columns**: 
  - `site_id` - Unique identifier for observation sites
  - `latitude`/`longitude` - Geographic coordinates
  - `species_id` - Species identifier
  - `state` - Geographic state
  - `observation_date` - Date of observation
  - `phenophase_description` - Phenological event type
  - `observation_count` - Count of observations
  - `distinct_species` - Count of distinct species by site

### Data Quality Findings
- Some coordinate values are missing or invalid (0 or NaN)
- Data has been successfully partitioned by year
- Observation counts have been aggregated appropriately
- Timestamp data is properly formatted as datetime
- Site identifiers are consistent across datasets

### Top-Level Summaries
- Data spans approximately 20 years (2000-2020)
- Multiple species and phenophase observations
- Spatial distribution across US states
- Seasonal trends available at annual and species levels

## 4. File Structure

### Workspace Structure
```
/workspace/phenology-intelligence-v1/
├── data/
├── outputs/
├── profile_dataset.py
├── convert_to_parquet.py
├── summarize_parquet.py
├── annual_phenology_summary.py
├── streamlit_app.py
├── requirements.txt
├── PROJECT_HANDOFF.md
└── PROJECT_STATUS.md
```

### Outputs Structure
```
/outputs/phenology-intelligence-v1/
├── parquet/
│   ├── phenology_data.parquet
│   └── conversion_log.txt
│   └── parquet_metadata.json
└── annual_summaries/
│   ├── annual_species_phenophase_summary.csv  
│   ├── annual_state_summary.csv
│   └── annual_species_summary.csv
└── summaries/
    ├── phenology_summary.csv
    └── spatial_summary.csv
```

## 5. Script/Function Documentation

### profile_dataset.py
- **Purpose**: Profile and analyze raw CSV dataset structure and quality
- **Inputs**: Raw CSV file path
- **Outputs**: Data profiling reports, schema information
- **Key Functions**:
  - `profile_data()` - Generate comprehensive data profiling
  - `validate_schema()` - Check if dataset has expected columns
- **What it does**: Analyzes data dimensions, data types, null values, and distribution
- **Known Limitations**: Schema validation relies on static expectations; may not catch dynamic changes

### convert_to_parquet.py
- **Purpose**: Convert CSV data to Parquet format for efficient storage and querying
- **Inputs**: Raw CSV file
- **Outputs**: Parquet file with partitioning by year
- **Key Functions**:
  - `convert_to_parquet()` - Main conversion function with year partitioning
  - `validate_partitioning()` - Ensures proper year-based partitioning
- **What it does**: Reads CSV, processes data, writes parquet with year column for efficient querying
- **Known Limitations**: Initial version had issues with year partitioning

### summarize_parquet.py
- **Purpose**: Create aggregated summaries from parquet data 
- **Inputs**: Parquet file with phenology data
- **Outputs**: Aggregated summary files
- **Key Functions**:
  - `create_species_phenophase_summary()` - Species-phenophase level aggregation
  - `create_state_summary()` - State-level aggregation  
  - `create_species_summary()` - Species-level aggregation
- **What it does**: Generate cross-tabulations of data at different aggregation levels
- **Known Limitations**: Some summary statistics rely on proper grouping and aggregation logic

### annual_phenology_summary.py
- **Purpose**: Create annual summary datasets for Streamlit dashboard
- **Inputs**: Parquet file with phenology data
- **Outputs**: Annual summary CSV files for dashboard
- **Key Functions**:
  - `generate_annual_summaries()` - Main function for creating annual data
  - `aggregate_by_year()` - Group data by year for summaries
- **What it does**: Process time-series data into annual aggregations for dashboard filtering
- **Known Limitations**: Some data may require additional cleaning or validation

### streamlit_app.py
- **Purpose**: Main Streamlit dashboard for interactive phenology data exploration
- **Inputs**: CSV files from annual_summaries directory and parquet spatial data
- **Outputs**: Interactive web dashboard 
- **Key Functions**:
  - `load_species_phenophase_data()` - Loads species-phenophase data
  - `load_state_data()` - Loads state-level data
  - `load_species_data()` - Loads species-level data
  - `load_spatial_data()` - Loads spatial data for map visualization
  - `compute_trends()` - Calculates phenological trends over time
- **What it does**: Implements dashboard with filters, visualizations, and trend analysis
- **Known Limitations**: Spatial map has rendering issues due to column mismatches

### requirements.txt
- **Purpose**: Python package dependencies
- **Inputs**: None
- **Outputs**: List of required packages
- **Key packages**: pandas, streamlit, plotly, pyarrow, scikit-learn

## 6. Dashboard Documentation

### Launching Streamlit
```bash
cd /workspace/phenology-intelligence-v1
streamlit run streamlit_app.py
```

### Dashboard Filters
- **Species Filter**: Select specific species for analysis
- **Common Names Filter**: Filter by species common names  
- **Phenophase Filter**: Choose specific phenological events
- **State Filter**: Filter by geographic states
- **Year Range Filter**: Set temporal range for analysis

### Chart Types
- **Median Day of Year Over Time**: Shows temporal phenological trends
- **Observations by Year**: Displays observation count patterns over time
- **Distribution of Median Day of Year**: Histogram of seasonal timing
- **Top States by Observations**: Comparison of state-level activity

### Trend Analysis
- Computes linear trends using scipy.stats.linregress or numpy.polyfit fallback
- Minimum observation threshold (default 30) for statistical validity
- Weighted trend computation option
- R-squared values for trend quality assessment

### Trend Quality Classification
- **High Quality**: R-squared ≥ 0.7 and p-value < 0.05
- **Medium Quality**: R-squared between 0.3 and 0.7 and p-value < 0.05  
- **Low Quality**: R-squared < 0.3 or p-value ≥ 0.05

### Known Dashboard Issues
- **Spatial Patterns Issue**: The spatial patterns section exists but map is not rendering because spatial data query currently has a column mismatch involving `distinct_species` and `observation_count`
- Trend analysis requires careful interpretation, especially with small observation sets
- Some interactive elements depend on complete data availability

### Current Spatial Map Issue
The spatial map section exists in the dashboard but is not rendering due to a column mismatch in spatial data queries. The issue specifically involves column names `distinct_species` and `observation_count` which do not align with expected schema in spatial data processing.

## 7. Known Issues

### Data Processing Issues
- Initial profile outputs were schema/static only - needed dynamic analysis
- Raw CSV direct profiling was fragile and needed preprocessing
- Year partitioning failed during initial Parquet conversion - was fixed in later version
- Some spatial data column mismatches need resolution

### Analysis Issues  
- Some trend results require careful filtering and interpretation due to small sample sizes
- Data quality inconsistencies exist around coordinate values (0 and NaN values)
- Spatial data structure may not exactly match expected dashboard needs

## 8. Important Commands

### Verification Commands
```bash
# Verify mounts and permissions
ls -la /outputs/phenology-intelligence-v1/parquet/

# Verify Parquet row count
python -c "import pandas as pd; df = pd.read_parquet('/outputs/phenology-intelligence-v1/parquet/phenology_data.parquet'); print(f'Rows: {len(df)}')"

# Launch Streamlit dashboard
streamlit run streamlit_app.py

# Kill/restart Streamlit
pkill -f streamlit
# Then re-run the above command

# Inspect output files from host (when needed)
ls -la /workspace/phenology-intelligence-v1/outputs/
```

### Running Summary Scripts
```bash
python /workspace/phenology-intelligence-v1/annual_phenology_summary.py
python /workspace/phenology-intelligence-v1/summarize_parquet.py
```

## 9. Recommended Next Steps

### Immediate Actions
1. **Fix Spatial Data Query**: Resolve column mismatch issue with `distinct_species` and `observation_count` in spatial data aggregation
2. **Add Site-Level Spatial Table**: Create comprehensive site-level summary for better map functionality

### Mid-Term Improvements
3. **Improve Maps**: Add more interactive map features and better styling
4. **Add Climate Covariates**: Integrate climate data for enhanced trend analysis 
5. **Add AI Query Layer**: Implement natural language processing for data querying
6. **Improve Trend Validation**: Enhance statistical validation methods

### Long-Term Enhancement
7. **Update PROJECT_STATUS.md**: Document all major changes and updates for project tracking
8. **Performance Optimizations**: Consider memory usage improvements for large spatial datasets
9. **Mobile Responsiveness**: Ensure dashboard works well on mobile devices
10. **User Access Control**: Add authentication and user role management when scaling

### Development Workflow Recommendations
- Follow git branching strategy for feature development
- Create pull requests for all major changes
- Run comprehensive tests before merging
- Document all code changes in commits