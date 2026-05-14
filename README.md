# Phenology Intelligence v1

## Overview

This project contains scripts to generate annual phenology summaries and compute phenology anomalies based on ecological baseline data. The scripts process species observation data and produce statistical summaries and anomaly detection results.

## Scripts Overview

### 1. Annual Phenology Summary (`annual_phenology_summary.py`)
This script generates annual summaries of species phenophase data and creates aggregate datasets for analysis.

### 2. Phenology Anomaly Computation (`compute_phenology_anomalies.py`)
This script computes phenology anomalies by comparing current observations against a baseline dataset, generating anomaly reports and diagnostics.

## Prerequisites

Install required Python packages:
```bash
pip install duckdb pandas matplotlib seaborn numpy
```

## Running the Scripts

Both scripts must be run from the `/workspace/phenology-intelligence-v1` directory to ensure proper relative path resolution:

1. **Generate annual summaries:**
   ```bash
   cd /workspace/phenology-intelligence-v1
   python annual_phenology_summary.py
   ```

2. **Compute phenology anomalies:**
   ```bash
   cd /workspace/phenology-intelligence-v1
   python compute_phenology_anomalies.py
   ```

## Output Files

After running the scripts, you'll find:
- `annual_anomaly_summary.csv`: Contains anomaly detection results  
- `diagnostic_figures/`: Directory with visual diagnostic plots
- `validation_report.txt`: Validation report of the computation  
- `annual_summaries/` directory containing the annual summary files

## Troubleshooting

### Common Issues:
1. **Permission errors when writing to `/outputs/**`:**  
   These scripts create output files in the working directory, not in `/outputs/`. The `/outputs/` path might be a mount point with restricted access. 

2. **Baseline data not found:**  
   Make sure you run the scripts from the correct directory (`/workspace/phenology-intelligence-v1`) where baseline data files are expected.

### Error Fixes:
1. **DuckDB Syntax Errors:**  
   The scripts now properly use `INTEGER` instead of `INT` for DuckDB types, which resolves compatibility issues.

2. **Path Resolution:**  
   All scripts use relative paths from their execution location, so running from the correct directory is essential for success.