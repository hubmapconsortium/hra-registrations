#!/bin/bash

# Setup script for RUI Registration Daily Tracker cron job
# This script helps configure the cron job to run at 5 PM on weekdays

SCRIPT_PATH="/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/RUI Reporter/combined_daily_tracker.py"
LOG_PATH="/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/tracker.log"

echo "=================================="
echo "RUI Registration Tracker Cron Setup"
echo "=================================="
echo ""
echo "This will setup a cron job to run the tracker at 5 PM on weekdays (Monday-Friday)"
echo ""
echo "Script location: $SCRIPT_PATH"
echo "Log file: $LOG_PATH"
echo ""

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Make sure script is executable
chmod +x "$SCRIPT_PATH"

# Create the cron job entry
CRON_ENTRY="0 17 * * 1-5 cd \"$(dirname "$SCRIPT_PATH")\" && python3 \"$SCRIPT_PATH\" >> \"$LOG_PATH\" 2>&1"

echo "Cron job entry to be added:"
echo "$CRON_ENTRY"
echo ""

# Ask for confirmation
read -p "Do you want to add this cron job? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup existing crontab
    echo "Backing up existing crontab..."
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    
    # Add the new cron job
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job added successfully!"
        echo ""
        echo "The tracker will now run:"
        echo "  - Every weekday (Monday-Friday)"
        echo "  - At 5:00 PM (17:00)"
        echo "  - Logs will be saved to: $LOG_PATH"
        echo ""
        echo "Current crontab:"
        crontab -l | grep -E "(combined_daily_tracker|RUI)"
        echo ""
        echo "To remove this cron job later, run:"
        echo "  crontab -e"
        echo "  (then delete the line containing 'combined_daily_tracker.py')"
        echo ""
        echo "To view logs:"
        echo "  tail -f \"$LOG_PATH\""
    else
        echo "❌ Error adding cron job"
        exit 1
    fi
else
    echo "Cron job setup cancelled."
    echo ""
    echo "To manually add the cron job later:"
    echo "1. Run: crontab -e"
    echo "2. Add this line:"
    echo "   $CRON_ENTRY"
fi

echo ""
echo "To test the script manually:"
echo "  python3 \"$SCRIPT_PATH\""
echo ""
echo "Setup complete!"
