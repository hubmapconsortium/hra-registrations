# RUI Registration Daily Tracker

This script automatically tracks RUI location registration coverage for both HuBMAP and SenNet datasets over time. It collects daily counts for total, supported, and registered datasets and saves them to a CSV file for trend analysis.

## Files

- `combined_daily_tracker.py` - Main script that collects data
- `setup_cron.sh` - Script to setup automatic daily execution via cron
- `test_tracker.sh` - Test script to verify environment and dependencies
- `README.md` - This documentation

## Features

- **Interactive Token Input**: Prompts for API tokens each time (no stored credentials)
- **Dual Consortium Support**: Tracks both HuBMAP and SenNet datasets
- **Time Series Data**: Saves results as CSV with dates as columns
- **Automatic Scheduling**: Runs weekdays at 5 PM via cron job
- **Error Handling**: Robust error handling and logging
- **Coverage Calculation**: Displays registration percentages

## Quick Start

### 1. Test the Environment
```bash
./test_tracker.sh
```

### 2. Setup Automatic Execution
```bash
./setup_cron.sh
```

### 3. Manual Testing (Optional)
```bash
python3 combined_daily_tracker.py
```

## Requirements

- Python 3.6+
- `requests` library (`pip3 install requests`)
- Valid HuBMAP and SenNet API tokens
- macOS/Linux with cron support

## Cron Schedule

The script is configured to run:
- **Time**: 5:00 PM (17:00)
- **Days**: Monday through Friday (weekdays only)
- **Logs**: Saved to `tracker.log`

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
