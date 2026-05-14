
# Phenology Intelligence Baseline Diagnostics Report

## Dataset Overview
- Total entries processed: 511,394
- Unique species: 1,757
- Unique phenophases: 179
- Unique states: 97

## Reliability Tier Summary
- insufficient: 511,394 (100.0%)

## Data Quality Statistics
- Mean Years Observed: 1.0
- Mean Coverage Fraction: 1.00
- Mean Confidence Score: 0.494
- Mean MAD: 0.1 days
- Mean IQR: 0.1 days
- Mean Observation Density: 76.8

## Key Observations
### Top 5 Most Reliable Species
- Altai fescue: 0.627
- Canadian gooseberry: 0.627
- Cooley's bundleflower: 0.627
- Fendler's sandwort: 0.627
- Geyer's sedge: 0.627

## Data Sparsity Analysis
- Most common years observed: 1
- Median years observed: 1
- Most common coverage fraction: 1.0
- Most common confidence score: 0.627

## Implications for Anomaly Detection

- High confidence groups (score > 0.7): 0 (0.0%)
- Low confidence groups (score < 0.3): 0 (0.0%)

## Recommendations for Hierarchical Baselines

1. **Data Quality Filtering**: Only use groups with confidence scores > 0.5 for robust anomaly detection
2. **Multi-scale Approach**: Consider using groups with higher reliability as baselines for more sensitive detection in lower quality data
3. **State-based Adaptation**: Apply state-specific confidence thresholds based on available data coverage
4. **Phenophase-specific Considerations**: Different phenophase types may require different reliability thresholds

## Data Coverage by State
- Milam: Mean confidence = 0.627, Coverage = 1.00
- Lajas: Mean confidence = 0.622, Coverage = 1.00
- Guánica: Mean confidence = 0.606, Coverage = 1.00
- TN: Mean confidence = 0.553, Coverage = 1.00
- MN: Mean confidence = 0.533, Coverage = 1.00
- MI: Mean confidence = 0.530, Coverage = 1.00
- MA: Mean confidence = 0.528, Coverage = 1.00
- AZ: Mean confidence = 0.517, Coverage = 1.00
- NY: Mean confidence = 0.513, Coverage = 1.00
- HI: Mean confidence = 0.513, Coverage = 1.00
- BC: Mean confidence = 0.511, Coverage = 1.00
- AL: Mean confidence = 0.511, Coverage = 1.00
- TX: Mean confidence = 0.510, Coverage = 1.00
- CA: Mean confidence = 0.509, Coverage = 1.00
- CO: Mean confidence = 0.507, Coverage = 1.00
- GA: Mean confidence = 0.502, Coverage = 1.00
- ME: Mean confidence = 0.501, Coverage = 1.00
- TG: Mean confidence = 0.499, Coverage = 1.00
- Guangdong Sheng: Mean confidence = 0.498, Coverage = 1.00
- OK: Mean confidence = 0.494, Coverage = 1.00
- NC: Mean confidence = 0.494, Coverage = 1.00
- NM: Mean confidence = 0.494, Coverage = 1.00
- Shandong Sheng: Mean confidence = 0.492, Coverage = 1.00
- VA: Mean confidence = 0.491, Coverage = 1.00
- AK: Mean confidence = 0.491, Coverage = 1.00
- NV: Mean confidence = 0.491, Coverage = 1.00
- FL: Mean confidence = 0.488, Coverage = 1.00
- MS: Mean confidence = 0.486, Coverage = 1.00
- NH: Mean confidence = 0.485, Coverage = 1.00
- LA: Mean confidence = 0.484, Coverage = 1.00
- CT: Mean confidence = 0.482, Coverage = 1.00
- Hubei Sheng: Mean confidence = 0.482, Coverage = 1.00
- WV: Mean confidence = 0.482, Coverage = 1.00
- Shanghai: Mean confidence = 0.482, Coverage = 1.00
- Tibet: Mean confidence = 0.481, Coverage = 1.00
- KS: Mean confidence = 0.481, Coverage = 1.00
- ND: Mean confidence = 0.479, Coverage = 1.00
- KY: Mean confidence = 0.478, Coverage = 1.00
- IA: Mean confidence = 0.478, Coverage = 1.00
- SC: Mean confidence = 0.476, Coverage = 1.00
- MD: Mean confidence = 0.475, Coverage = 1.00
- IL: Mean confidence = 0.475, Coverage = 1.00
- WY: Mean confidence = 0.474, Coverage = 1.00
- PA: Mean confidence = 0.473, Coverage = 1.00
- OR: Mean confidence = 0.473, Coverage = 1.00
- UT: Mean confidence = 0.472, Coverage = 1.00
- WA: Mean confidence = 0.470, Coverage = 1.00
- Yunnan Sheng: Mean confidence = 0.467, Coverage = 1.00
- IN: Mean confidence = 0.465, Coverage = 1.00
- WI: Mean confidence = 0.464, Coverage = 1.00
- VT: Mean confidence = 0.463, Coverage = 1.00
- Chongqing Shi: Mean confidence = 0.463, Coverage = 1.00
- ID: Mean confidence = 0.462, Coverage = 1.00
- MT: Mean confidence = 0.461, Coverage = 1.00
- SD: Mean confidence = 0.460, Coverage = 1.00
- ON: Mean confidence = 0.460, Coverage = 1.00
- OH: Mean confidence = 0.457, Coverage = 1.00
- Anhui Sheng: Mean confidence = 0.455, Coverage = 1.00
- Samarqand Region: Mean confidence = 0.454, Coverage = 1.00
- RI: Mean confidence = 0.454, Coverage = 1.00
- Jambyl Region: Mean confidence = 0.450, Coverage = 1.00
- MO: Mean confidence = 0.449, Coverage = 1.00
- MB: Mean confidence = 0.448, Coverage = 1.00
- AB: Mean confidence = 0.448, Coverage = 1.00
- County Offaly: Mean confidence = 0.447, Coverage = 1.00
- Kaohsiung City: Mean confidence = 0.447, Coverage = 1.00
- NJ: Mean confidence = 0.445, Coverage = 1.00
- NE: Mean confidence = 0.445, Coverage = 1.00
- DC: Mean confidence = 0.444, Coverage = 1.00
- AR: Mean confidence = 0.443, Coverage = 1.00
- Zhejiang Sheng: Mean confidence = 0.443, Coverage = 1.00
- QC: Mean confidence = 0.442, Coverage = 1.00
- Toscana: Mean confidence = 0.441, Coverage = 1.00
- DE: Mean confidence = 0.439, Coverage = 1.00
- Jiangsu: Mean confidence = 0.438, Coverage = 1.00
- Neimenggu Zizhiq: Mean confidence = 0.438, Coverage = 1.00
- Gyeonggi-do: Mean confidence = 0.433, Coverage = 1.00
- LP: Mean confidence = 0.432, Coverage = 1.00
- Son.: Mean confidence = 0.432, Coverage = 1.00
- Antioquia: Mean confidence = 0.432, Coverage = 1.00
- NS: Mean confidence = 0.430, Coverage = 1.00
- HE: Mean confidence = 0.430, Coverage = 1.00
- Liaoning Sheng: Mean confidence = 0.429, Coverage = 1.00
- Jabal Lubnan: Mean confidence = 0.429, Coverage = 1.00
- IB: Mean confidence = 0.429, Coverage = 1.00
- BY: Mean confidence = 0.429, Coverage = 1.00
- AP: Mean confidence = 0.429, Coverage = 1.00
- Hyogo: Mean confidence = 0.429, Coverage = 1.00
- Canada: Mean confidence = 0.429, Coverage = 1.00
- New Providence: Mean confidence = 0.429, Coverage = 1.00
- NB: Mean confidence = 0.429, Coverage = 1.00
- Lamiing: Mean confidence = 0.429, Coverage = 1.00
- Okinawa: Mean confidence = 0.429, Coverage = 1.00
- SK: Mean confidence = 0.429, Coverage = 1.00
- PR: Mean confidence = 0.429, Coverage = 1.00
- Tianjin Shi: Mean confidence = 0.429, Coverage = 1.00
- Western Region: Mean confidence = 0.429, Coverage = 1.00
