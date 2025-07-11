# RUI Registration Daily Tracker

This script tracks RUI location registration coverage for both HuBMAP and SenNet datasets over time.

## What it does

The script generates daily counts for:
- **Total datasets** - All datasets in each consortium
- **Supported datasets** - Datasets from organs covered by reference anatomy
- **Registered datasets** - Datasets with RUI locations

Results are saved to a CSV file with dates as columns and metrics as rows for time-series analysis.

## How to run

1. Make sure you have your API tokens ready:
   - HuBMAP API Token
   - SenNet API Token

2. Run the script:
   ```bash
   ./combined_daily_tracker.py
   ```

3. When prompted, enter your API tokens securely (they won't be displayed as you type)

4. The script will:
   - Query both consortium APIs
   - Display current counts and coverage percentages
   - Save results to `combined_daily_counts.csv` in the main hra-registrations folder

## Output

- **CSV File**: `/Users/dequeue/Desktop/RUI.nosync/hra-registrations/combined_daily_counts.csv`
- **Format**: Each row is a metric, each column is a date
- **Metrics tracked**:
  - HuBMAP Total Datasets
  - HuBMAP Supported Datasets  
  - HuBMAP Registered Datasets
  - SenNet Total Datasets
  - SenNet Supported Datasets
  - SenNet Registered Datasets

## Dependencies

- Python 3.6+
- `requests` library (install with `pip install requests`)
- `metadata.js` file in the same directory

## Security

- API tokens are entered securely using `getpass` (no echo to terminal)
- Tokens are not stored anywhere
- You'll need to enter them each time you run the script

## Output

Results are saved to:
```
/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/combined_daily_counts.csv
```

CSV format:
```
Metric,2025-01-01,2025-01-02,2025-01-03,...
HuBMAP Total Datasets,1234,1240,1245,...
HuBMAP Supported Datasets,456,460,465,...
HuBMAP Registered Datasets,123,125,128,...
SenNet Total Datasets,567,570,572,...
SenNet Supported Datasets,234,236,238,...
SenNet Registered Datasets,67,68,70,...
```

## Security

- API tokens are entered interactively (not stored in files)
- Tokens are only held in memory during execution
- No credentials are logged or saved

## Monitoring

### View Logs
```bash
tail -f /Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/tracker.log
```

### Check Cron Status
```bash
crontab -l | grep combined_daily_tracker
```

### Manual Execution
```bash
cd "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/RUI Reporter"
python3 combined_daily_tracker.py
```

## Troubleshooting

### Common Issues

1. **"Permission denied"**
   ```bash
   chmod +x combined_daily_tracker.py
   chmod +x setup_cron.sh
   chmod +x test_tracker.sh
   ```

2. **"Module not found"**
   ```bash
   pip3 install requests
   ```

3. **"Cron job not running"**
   - Check cron is enabled: `sudo launchctl list | grep cron`
   - Verify crontab: `crontab -l`
   - Check logs: `tail tracker.log`

4. **"API errors"**
   - Verify tokens are valid and active
   - Check network connectivity
   - Confirm API endpoints are accessible

### Remove Cron Job
```bash
crontab -e
# Delete the line containing "combined_daily_tracker.py"
```

## Data Analysis

The CSV output can be imported into:
- Excel/Google Sheets for basic charts
- Python pandas for advanced analysis
- R for statistical analysis
- Tableau/Power BI for dashboards

Example Python analysis:
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('combined_daily_counts.csv', index_col=0)
df = df.T  # Transpose to have dates as rows
df.index = pd.to_datetime(df.index)

# Plot trends
df.plot(figsize=(12, 8))
plt.title('RUI Registration Trends Over Time')
plt.ylabel('Dataset Count')
plt.show()
```

## Support

For issues or questions:
1. Check the logs first: `tail tracker.log`
2. Test manually: `python3 combined_daily_tracker.py`
3. Verify environment: `./test_tracker.sh`
