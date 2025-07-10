#!/bin/bash

# Test script for the RUI Registration Daily Tracker

SCRIPT_PATH="/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/RUI Reporter/combined_daily_tracker.py"

echo "=================================="
echo "Testing RUI Registration Daily Tracker"
echo "=================================="
echo ""

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

echo "✅ Script found: $SCRIPT_PATH"
echo ""

# Check Python version
echo "Python version:"
python3 --version
echo ""

# Check required modules
echo "Checking required Python modules..."
python3 -c "
import sys
modules = ['requests', 're', 'csv', 'os', 'datetime', 'getpass']
missing = []
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module} (missing)')
        missing.append(module)

if missing:
    print(f'\\nMissing modules: {missing}')
    print('Install with: pip3 install requests')
    sys.exit(1)
else:
    print('\\n✅ All required modules available')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Missing required Python modules"
    echo "Install missing modules and try again"
    exit 1
fi

echo ""
echo "✅ Environment check passed"
echo ""
echo "To run the tracker manually:"
echo "  python3 \"$SCRIPT_PATH\""
echo ""
echo "To setup the cron job:"
echo "  ./setup_cron.sh"
echo ""
echo "Test complete!"
